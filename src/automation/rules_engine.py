import logging
import json
import os
from datetime import datetime
import pandas as pd
from src.config import config

class RulesEngine:
    """
    Akıllı ev için kural tabanlı otomasyon motoru.
    Sensör verilerine ve kullanıcı davranışlarına göre cihazları kontrol eder.
    """
    
    def __init__(self, use_ml_model=True):
        """
        RulesEngine sınıfını başlatır
        
        Args:
            use_ml_model (bool): ML modeli kullanılıp kullanılmayacağı
        """
        self.logger = logging.getLogger(__name__)
        self.rules = []
        self.use_ml_model = use_ml_model
        self.ml_model = None
        self.decision_history = []
        self.last_device_states = {}
        self.ml_confidence_threshold = 0.7  # ML tahminleri için minimum güven eşiği
    
    def set_ml_model(self, model):
        """
        ML modelini ayarlar
        
        Args:
            model: SmartHomeModelManager nesnesi
        """
        self.ml_model = model
        self.use_ml_model = True if model else False
    
    def add_rule(self, name, condition_func, action_func, priority=1, description=None):
        """
        Kural motoruna yeni bir kural ekler
        
        Args:
            name (str): Kural adı
            condition_func (callable): Koşul değerlendiren fonksiyon (state -> bool)
            action_func (callable): Koşul sağlandığında çalışacak fonksiyon (state, devices -> dict)
            priority (int): Kural önceliği (yüksek değer daha yüksek öncelik)
            description (str): Kural açıklaması
        """
        rule = {
            'name': name,
            'condition': condition_func,
            'action': action_func,
            'priority': priority,
            'description': description or name,
            'enabled': True
        }
        
        self.rules.append(rule)
        self.rules.sort(key=lambda x: x['priority'], reverse=True)
        
        return rule
    
    def disable_rule(self, rule_name):
        """
        Belirtilen kuralı devre dışı bırakır
        
        Args:
            rule_name (str): Devre dışı bırakılacak kuralın adı
            
        Returns:
            bool: İşlem başarılıysa True
        """
        for rule in self.rules:
            if rule['name'] == rule_name:
                rule['enabled'] = False
                return True
        
        return False
    
    def enable_rule(self, rule_name):
        """
        Belirtilen kuralı etkinleştirir
        
        Args:
            rule_name (str): Etkinleştirilecek kuralın adı
            
        Returns:
            bool: İşlem başarılıysa True
        """
        for rule in self.rules:
            if rule['name'] == rule_name:
                rule['enabled'] = True
                return True
        
        return False
    
    def evaluate_rules(self, current_state, device_states, ml_predictions=None):
        """
        Mevcut durum için tüm kuralları değerlendirir ve cihaz durumlarını günceller
        
        Args:
            current_state (dict): Mevcut sensör ve çevre durumu
            device_states (dict): Mevcut cihaz durumları
            ml_predictions (dict): ML modelinden gelen tahminler (opsiyonel)
            
        Returns:
            dict: Güncellenmiş cihaz durumları
        """
        # Cihaz durumlarının bir kopyasını oluştur
        updated_states = device_states.copy()
        
        # Ensure ml_confidence_threshold is defined (fallback if __init__ wasn't updated)
        if not hasattr(self, 'ml_confidence_threshold'):
            self.ml_confidence_threshold = 0.7
        
        # Makine öğrenmesi tahminleri varsa, ML modelinden gelen önerilerini uygula
        if self.use_ml_model and ml_predictions and self.ml_model:
            
            for device_name, prediction in ml_predictions.items():
                # Cihaz zaten device_states içinde tanımlı mı kontrol et
                if device_name in updated_states:
                    # ML tahmini yeterince güvenli mi?
                    if (isinstance(prediction, dict) and 
                        'probability' in prediction and 
                        prediction['probability'] > self.ml_confidence_threshold):
                        
                        # Yeterince güvenli tahmin - yeni durumu ayarla
                        if 'state' in prediction:
                            updated_states[device_name] = prediction['state']
        
        # Kuralları öncelik sırasına göre değerlendir
        sorted_rules = sorted(self.rules, key=lambda r: r['priority'], reverse=True)
        
        for rule in sorted_rules:
            # Kuralın koşulu mevcut durumu karşılıyor mu?
            if rule['condition'](current_state):
                # Koşul karşılanıyorsa, eylemi uygula
                changes = rule['action'](current_state, updated_states)
                
                # Değişiklikler varsa uygula ve kaydet
                if changes:
                    
                    for device, state in changes.items():
                        updated_states[device] = state
                        
                        # Karar geçmişine ekle
                        self._add_decision({
                            'rule': rule['name'],
                            'device': device,
                            'action': 'Set to ' + str(state),
                            'reason': rule.get('description', 'No description')
                        })
        
        # Güncellenmiş durumları döndür
        return updated_states
    
    def record_decision(self, rule_name, description, current_state, before_state, changes, confidence):
        """
        Otomasyon kararını kayıt altına alır
        
        Args:
            rule_name (str): Kararı veren kural adı
            description (str): Kural açıklaması
            current_state (dict): Mevcut sensör ve ortam durumu
            before_state (dict): Önceki cihaz durumları
            changes (dict): Yapılan değişiklikler
            confidence (float): Karar güveni (0-1 arası)
        """
        decision = {
            'timestamp': datetime.now().isoformat(),
            'rule': rule_name,
            'description': description,
            'current_state': current_state,
            'before': before_state,
            'changes': changes,
            'confidence': confidence
        }
        
        self.decision_history.append(decision)
        
        # Tarihçeyi belirli bir boyutta tutmak için
        if len(self.decision_history) > 1000:
            self.decision_history = self.decision_history[-1000:]
    
    def export_decision_history(self, filepath=None):
        """
        Karar tarihçesini JSON dosyasına kaydeder
        
        Args:
            filepath (str): Kaydedilecek dosya yolu
            
        Returns:
            str: Kayıt edilen dosya yolu
        """
        if not filepath:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
            
            # Dizin yoksa oluştur
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            filepath = os.path.join(log_dir, f"decisions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        # JSON dosyasına kaydet
        with open(filepath, 'w') as f:
            # datetime nesneleri için özel JSON encoder kullanmamız gerekiyor
            json.dump(self.decision_history, f, indent=2, default=str)
        
        return filepath
    
    def get_decision_summary(self, limit=10):
        """
        Son kararların özetini döndürür
        
        Args:
            limit (int): Döndürülecek karar sayısı
            
        Returns:
            list: Son kararların özeti
        """
        # Son kararları al ve geri döndür
        recent_decisions = self.decision_history[-limit:] if self.decision_history else []
        
        # Kararları özet formata dönüştür
        summary = []
        for decision in recent_decisions:
            # Özet bilgiler
            summary.append({
                'timestamp': decision['timestamp'],
                'rule': decision['rule'],
                'description': decision['description'],
                'changes': decision['changes'],
                'confidence': decision['confidence']
            })
        
        return summary
    
    def _add_decision(self, decision_info):
        """
        Karar geçmişine yeni bir karar ekler
        
        Args:
            decision_info (dict): Karar bilgileri
        """
        # Add timestamp to decision
        decision_info['timestamp'] = datetime.now().isoformat()
        
        # Add to decision history
        self.decision_history.append(decision_info)
        
        # Keep decision history at reasonable size
        if len(self.decision_history) > 1000:
            self.decision_history = self.decision_history[-1000:]
        
        # Log the decision
        if 'rule' in decision_info:
            self.logger.info(f"Kural kararı: {decision_info['rule']} - {decision_info['device']} {decision_info['action']}")
        else:
            self.logger.info(f"ML kararı: {decision_info['device']} {decision_info['action']}")

# Örnek kurallar ve koşullar
def create_default_rules(rules_engine):
    """
    Kural motoruna varsayılan kuralları ekler
    
    Args:
        rules_engine (RulesEngine): Kural motoru nesnesi
    """
    # Sıcaklık kontrolü için kurallar
    def high_temp_condition(state):
        for room in config['rooms']:
            temp_key = f"{room}_Sıcaklık"
            if temp_key in state and state[temp_key] > config['automation_thresholds']['high_temp_threshold']:
                return True
        return False
    
    def turn_on_ac(state, devices):
        updated_devices = {}
        for room in config['rooms']:
            temp_key = f"{room}_Sıcaklık"
            occupancy_key = f"{room}_Doluluk"
            device_key = f"{room}_Klima"
            
            # Sıcaklık yüksek ve oda doluysa klimayı çalıştır
            if temp_key in state and state[temp_key] > config['automation_thresholds']['high_temp_threshold']:
                if occupancy_key in state and state[occupancy_key]:
                    updated_devices[device_key] = True
        
        return updated_devices
    
    rules_engine.add_rule(
        name="yuksek_sicaklik_kontrolu",
        condition_func=high_temp_condition,
        action_func=turn_on_ac,
        priority=10,
        description="Yüksek sıcaklıkta odada insanlar varsa klimayı çalıştır"
    )
    
    # Düşük sıcaklık kontrolü
    def low_temp_condition(state):
        for room in config['rooms']:
            temp_key = f"{room}_Sıcaklık"
            if temp_key in state and state[temp_key] < config['automation_thresholds']['low_temp_threshold']:
                return True
        return False
    
    def turn_off_ac(state, devices):
        updated_devices = {}
        for room in config['rooms']:
            temp_key = f"{room}_Sıcaklık"
            device_key = f"{room}_Klima"
            
            # Sıcaklık düşükse klimayı kapat
            if temp_key in state and state[temp_key] < config['automation_thresholds']['low_temp_threshold']:
                updated_devices[device_key] = False
        
        return updated_devices
    
    rules_engine.add_rule(
        name="dusuk_sicaklik_kontrolu",
        condition_func=low_temp_condition,
        action_func=turn_off_ac,
        priority=10,
        description="Düşük sıcaklıkta klimayı kapat"
    )
    
    # Işık kontrolü için kurallar
    def light_control_condition(state):
        # Gece saatleri ya da düşük ışık seviyesi ve odada hareket varsa
        current_hour = datetime.now().hour
        is_night = current_hour >= 19 or current_hour <= 7
        
        for room in config['rooms']:
            light_key = f"{room}_Işık"
            movement_key = f"{room}_Hareket"
            
            if movement_key in state and state[movement_key]:
                if is_night or (light_key in state and state[light_key] < config['automation_thresholds']['low_light_threshold']):
                    return True
        
        return False
    
    def control_lights(state, devices):
        updated_devices = {}
        current_hour = datetime.now().hour
        is_night = current_hour >= 19 or current_hour <= 7
        
        for room in config['rooms']:
            light_key = f"{room}_Işık"
            movement_key = f"{room}_Hareket"
            device_key = f"{room}_Lamba"
            
            # Gece veya düşük ışık seviyesinde hareket varsa lambayı aç
            if movement_key in state and state[movement_key]:
                if is_night or (light_key in state and state[light_key] < config['automation_thresholds']['low_light_threshold']):
                    updated_devices[device_key] = True
            # Hareket yoksa lambayı kapat
            elif movement_key in state and not state[movement_key]:
                updated_devices[device_key] = False
        
        return updated_devices
    
    rules_engine.add_rule(
        name="isik_kontrolu",
        condition_func=light_control_condition,
        action_func=control_lights,
        priority=8,
        description="Düşük ışık seviyesinde ve hareket varsa ışıkları aç"
    )
    
    # Enerji tasarrufu kuralı - Oda boşsa cihazları kapat
    def energy_save_condition(state):
        # Herhangi bir oda boşsa energy saving koşulunu kontrol et
        for room in config['rooms']:
            occupancy_key = f"{room}_Doluluk"
            if occupancy_key in state and not state[occupancy_key]:
                return True
        return False
    
    def turn_off_devices(state, devices):
        updated_devices = {}
        
        for room in config['rooms']:
            occupancy_key = f"{room}_Doluluk"
            last_movement_key = f"{room}_SonHareket_Dakika"
            
            # Oda boşsa ve son hareketten 10 dakika geçtiyse
            if (occupancy_key in state and not state[occupancy_key]) and \
               (last_movement_key not in state or state.get(last_movement_key, 0) > 10):
                
                # Lambayı kapat
                light_key = f"{room}_Lamba"
                if light_key in devices:
                    updated_devices[light_key] = False
                
                # 15 dakika geçtiyse klimayı da kapat
                if last_movement_key not in state or state.get(last_movement_key, 0) > 15:
                    ac_key = f"{room}_Klima"
                    if ac_key in devices:
                        updated_devices[ac_key] = False
        
        return updated_devices
    
    rules_engine.add_rule(
        name="enerji_tasarruf",
        condition_func=energy_save_condition,
        action_func=turn_off_devices,
        priority=5,
        description="Oda boşsa ve belirli bir süre geçtiyse enerji tasarrufu için cihazları kapat"
    )
    
    # CO2 kontrolü için kurallar
    def high_co2_condition(state):
        for room in config['rooms']:
            co2_key = f"{room}_CO2"
            if co2_key in state and state[co2_key] > config['automation_thresholds']['high_co2_threshold']:
                return True
        return False
    
    def control_ventilation(state, devices):
        updated_devices = {}
        
        for room in config['rooms']:
            co2_key = f"{room}_CO2"
            device_key = f"{room}_Havalandırma"
            
            if co2_key in state and device_key in devices:
                # CO2 seviyesi yüksekse havalandırmayı aç
                if state[co2_key] > config['automation_thresholds']['high_co2_threshold']:
                    updated_devices[device_key] = True
                # CO2 seviyesi normale döndüyse havalandırmayı kapat
                elif state[co2_key] < config['automation_thresholds']['low_co2_threshold'] and devices[device_key]:
                    updated_devices[device_key] = False
        
        return updated_devices
    
    rules_engine.add_rule(
        name="co2_kontrolu",
        condition_func=high_co2_condition,
        action_func=control_ventilation,
        priority=7,
        description="Yüksek CO2 seviyesinde havalandırmayı çalıştır"
    )
    
    # Nem kontrolü için kurallar
    def humidity_condition(state):
        for room in config['rooms']:
            humidity_key = f"{room}_Nem"
            if humidity_key in state and (state[humidity_key] > config['automation_thresholds']['high_humidity_threshold'] or state[humidity_key] < config['automation_thresholds']['low_humidity_threshold']):
                return True
        return False
    
    def control_humidity(state, devices):
        updated_devices = {}
        
        for room in config['rooms']:
            humidity_key = f"{room}_Nem"
            ventilation_key = f"{room}_Havalandırma"
            
            if humidity_key in state and ventilation_key in devices:
                # Nem yüksekse havalandırmayı aç
                if state[humidity_key] > config['automation_thresholds']['high_humidity_threshold']:
                    updated_devices[ventilation_key] = True
        
        return updated_devices
    
    rules_engine.add_rule(
        name="nem_kontrolu",
        condition_func=humidity_condition,
        action_func=control_humidity,
        priority=6,
        description="Yüksek nemde havalandırmayı çalıştır"
    )
    
    # Sabah perdeleri açma kuralı
    def morning_condition(state):
        current_hour = datetime.now().hour
        return config['automation_thresholds']['morning_start'] <= current_hour <= config['automation_thresholds']['morning_end']
    
    def open_curtains(state, devices):
        updated_devices = {}
        
        for room in config['rooms']:
            curtain_key = f"{room}_Perde"
            if curtain_key in devices:
                updated_devices[curtain_key] = True
        
        return updated_devices
    
    rules_engine.add_rule(
        name="sabah_perde_ac",
        condition_func=morning_condition,
        action_func=open_curtains,
        priority=4,
        description="Sabah saatlerinde perdeleri aç"
    )
    
    # Akşam perdeleri kapatma kuralı
    def evening_condition(state):
        current_hour = datetime.now().hour
        return config['automation_thresholds']['evening_start'] <= current_hour <= config['automation_thresholds']['evening_end']
    
    def close_curtains(state, devices):
        updated_devices = {}
        
        for room in config['rooms']:
            curtain_key = f"{room}_Perde"
            if curtain_key in devices:
                updated_devices[curtain_key] = False
        
        return updated_devices
    
    rules_engine.add_rule(
        name="aksam_perde_kapat",
        condition_func=evening_condition,
        action_func=close_curtains,
        priority=4,
        description="Akşam saatlerinde perdeleri kapat"
    )
    
    return rules_engine