import logging
import json
import os
from datetime import datetime
import pandas as pd

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
        self.rules = []
        self.use_ml_model = use_ml_model
        self.ml_model = None
        self.decision_history = []
        self.last_device_states = {}
        self.setup_logging()
    
    def setup_logging(self):
        """
        Loglama sistemini yapılandırır
        """
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        
        # Dizin yoksa oluştur
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Log dosyası adı
        log_file = os.path.join(log_dir, f"automation_{datetime.now().strftime('%Y%m%d')}.log")
        
        # Logging yapılandırması
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("RulesEngine")
        self.logger.info("Kural motoru başlatıldı")
    
    def set_ml_model(self, model):
        """
        ML modelini ayarlar
        
        Args:
            model: SmartHomeModelManager nesnesi
        """
        self.ml_model = model
        self.use_ml_model = True if model else False
        self.logger.info(f"ML modeli ayarlandı: {model is not None}")
    
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
        self.logger.info(f"Kural eklendi: {name} (öncelik: {priority})")
        
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
                self.logger.info(f"Kural devre dışı bırakıldı: {rule_name}")
                return True
        
        self.logger.warning(f"Devre dışı bırakılacak kural bulunamadı: {rule_name}")
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
                self.logger.info(f"Kural etkinleştirildi: {rule_name}")
                return True
        
        self.logger.warning(f"Etkinleştirilecek kural bulunamadı: {rule_name}")
        return False
    
    def evaluate_rules(self, current_state, devices):
        """
        Mevcut duruma göre tüm kuralları değerlendirir ve eylemleri gerçekleştirir
        
        Args:
            current_state (dict): Güncel sensör ve ortam verileri
            devices (dict): Cihaz durumları sözlüğü
            
        Returns:
            dict: Güncellenen cihaz durumları
        """
        self.logger.debug(f"Kural değerlendirme başlatıldı - Toplam {len(self.rules)} kural")
        
        updated_devices = devices.copy()
        triggered_rules = []
        
        # ML tabanlı tahminleri değerlendir
        if self.use_ml_model and self.ml_model:
            try:
                # Güncel durum verilerini DataFrame'e dönüştür
                state_df = pd.DataFrame([current_state])
                
                # ML modeli ile tahminleri al
                ml_predictions = self.ml_model.predict_device_states(state_df)
                
                # ML tahminleri hakkında log
                self.logger.info(f"ML tahmini: {ml_predictions}")
                
                # ML önerileri doğrultusunda cihazları güncelle
                for device_name, prediction in ml_predictions.items():
                    if prediction['probability'] >= 0.7:  # Güven eşiği
                        updated_devices[device_name] = prediction['state']
                        self.logger.info(f"ML önerisi: {device_name} -> {prediction['state']} ({prediction['probability']:.2f})")
                        
                        # Karar tarihçesine ekle
                        self.record_decision(
                            "ML_MODEL",
                            f"ML tahmini: {device_name}",
                            current_state,
                            {device_name: devices.get(device_name, False)},
                            {device_name: prediction['state']},
                            prediction['probability']
                        )
            
            except Exception as e:
                self.logger.error(f"ML tahminleri sırasında hata: {e}")
        
        # Kural tabanlı mantığı çalıştır
        for rule in self.rules:
            if not rule['enabled']:
                continue
                
            try:
                # Koşulu değerlendir
                if rule['condition'](current_state):
                    # Eylemi gerçekleştir
                    rule_name = rule['name']
                    before_state = updated_devices.copy()
                    
                    # Eylemi çağır ve cihaz durumlarını güncelle
                    action_result = rule['action'](current_state, updated_devices)
                    
                    # Eylem bir cihaz durumu değişikliği döndürdüyse güncelle
                    if isinstance(action_result, dict):
                        for device, state in action_result.items():
                            updated_devices[device] = state
                    
                    # Tetiklenen kuralı kaydet
                    triggered_rules.append(rule_name)
                    
                    # Değişiklikleri belirle
                    changes = {}
                    for device, state in updated_devices.items():
                        if device in before_state and before_state[device] != state:
                            changes[device] = state
                    
                    # Loglama
                    if changes:
                        self.logger.info(f"Kural tetiklendi: {rule_name} - Değişiklikler: {changes}")
                        
                        # Karar tarihçesine ekle
                        self.record_decision(
                            rule_name, 
                            rule['description'], 
                            current_state, 
                            before_state, 
                            changes, 
                            1.0  # Kural tabanlı mantık için güven değeri 1.0 olarak ayarlanır
                        )
            
            except Exception as e:
                self.logger.error(f"Kural değerlendirme hatası - {rule['name']}: {e}")
        
        if not triggered_rules:
            self.logger.debug("Hiçbir kural tetiklenmedi")
        
        # Önceki durumdan değişen cihazları belirle
        changed_devices = {}
        for device, state in updated_devices.items():
            if device not in self.last_device_states or self.last_device_states[device] != state:
                changed_devices[device] = state
        
        # Son cihaz durumlarını güncelle
        self.last_device_states = updated_devices.copy()
        
        # Değişiklikler hakkında log
        if changed_devices:
            self.logger.info(f"Cihaz durumları güncellendi: {changed_devices}")
        
        return updated_devices
    
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
        
        self.logger.info(f"Karar tarihçesi {filepath} dosyasına kaydedildi")
        
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

# Örnek kurallar ve koşullar
def create_default_rules(rules_engine):
    """
    Kural motoruna varsayılan kuralları ekler
    
    Args:
        rules_engine (RulesEngine): Kural motoru nesnesi
    """
    # Sıcaklık kontrolü için kurallar
    def high_temp_condition(state):
        for room in ['Salon', 'Yatak Odası', 'Çocuk Odası']:
            temp_key = f"{room}_Sıcaklık"
            if temp_key in state and state[temp_key] > 26:
                return True
        return False
    
    def turn_on_ac(state, devices):
        updated_devices = {}
        for room in ['Salon', 'Yatak Odası', 'Çocuk Odası']:
            temp_key = f"{room}_Sıcaklık"
            occupancy_key = f"{room}_Doluluk"
            device_key = f"{room}_Klima"
            
            # Sıcaklık yüksek ve oda doluysa klimayı çalıştır
            if temp_key in state and state[temp_key] > 26:
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
        for room in ['Salon', 'Yatak Odası', 'Çocuk Odası']:
            temp_key = f"{room}_Sıcaklık"
            if temp_key in state and state[temp_key] < 18:
                return True
        return False
    
    def turn_off_ac(state, devices):
        updated_devices = {}
        for room in ['Salon', 'Yatak Odası', 'Çocuk Odası']:
            temp_key = f"{room}_Sıcaklık"
            device_key = f"{room}_Klima"
            
            # Sıcaklık düşükse klimayı kapat
            if temp_key in state and state[temp_key] < 18:
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
        
        for room in ['Salon', 'Yatak Odası', 'Çocuk Odası', 'Mutfak', 'Banyo']:
            light_key = f"{room}_Işık"
            movement_key = f"{room}_Hareket"
            
            if movement_key in state and state[movement_key]:
                if is_night or (light_key in state and state[light_key] < 100):
                    return True
        
        return False
    
    def control_lights(state, devices):
        updated_devices = {}
        current_hour = datetime.now().hour
        is_night = current_hour >= 19 or current_hour <= 7
        
        for room in ['Salon', 'Yatak Odası', 'Çocuk Odası', 'Mutfak', 'Banyo']:
            light_key = f"{room}_Işık"
            movement_key = f"{room}_Hareket"
            device_key = f"{room}_Lamba"
            
            # Gece veya düşük ışık seviyesinde hareket varsa lambayı aç
            if movement_key in state and state[movement_key]:
                if is_night or (light_key in state and state[light_key] < 100):
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
    def energy_save_condition(state, devices):
        # Herhangi bir oda boşsa ve cihazlar açıksa
        for room in ['Salon', 'Yatak Odası', 'Çocuk Odası', 'Mutfak', 'Banyo']:
            occupancy_key = f"{room}_Doluluk"
            if occupancy_key in state and not state[occupancy_key]:
                for device in ['Lamba', 'Klima']:
                    device_key = f"{room}_{device}"
                    if device_key in devices and devices[device_key]:
                        return True
        return False
    
    def turn_off_devices(state, devices):
        updated_devices = {}
        
        for room in ['Salon', 'Yatak Odası', 'Çocuk Odası', 'Mutfak', 'Banyo']:
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
        for room in ['Salon', 'Yatak Odası', 'Çocuk Odası', 'Mutfak']:
            co2_key = f"{room}_CO2"
            if co2_key in state and state[co2_key] > 800:
                return True
        return False
    
    def control_ventilation(state, devices):
        updated_devices = {}
        
        for room in ['Salon', 'Yatak Odası', 'Çocuk Odası', 'Mutfak']:
            co2_key = f"{room}_CO2"
            device_key = f"{room}_Havalandırma"
            
            if co2_key in state and device_key in devices:
                # CO2 seviyesi yüksekse havalandırmayı aç
                if state[co2_key] > 800:
                    updated_devices[device_key] = True
                # CO2 seviyesi normale döndüyse havalandırmayı kapat
                elif state[co2_key] < 600 and devices[device_key]:
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
        for room in ['Salon', 'Yatak Odası', 'Çocuk Odası', 'Banyo', 'Mutfak']:
            humidity_key = f"{room}_Nem"
            if humidity_key in state and (state[humidity_key] > 70 or state[humidity_key] < 30):
                return True
        return False
    
    def control_humidity(state, devices):
        updated_devices = {}
        
        for room in ['Salon', 'Yatak Odası', 'Çocuk Odası', 'Mutfak', 'Banyo']:
            humidity_key = f"{room}_Nem"
            ventilation_key = f"{room}_Havalandırma"
            
            if humidity_key in state and ventilation_key in devices:
                # Nem yüksekse havalandırmayı aç
                if state[humidity_key] > 70:
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
        return 7 <= current_hour <= 9
    
    def open_curtains(state, devices):
        updated_devices = {}
        
        for room in ['Salon', 'Yatak Odası', 'Çocuk Odası']:
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
        return 19 <= current_hour <= 23
    
    def close_curtains(state, devices):
        updated_devices = {}
        
        for room in ['Salon', 'Yatak Odası', 'Çocuk Odası']:
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