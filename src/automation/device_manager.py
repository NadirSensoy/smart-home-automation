"""
Akıllı ev cihazlarının yönetimi için sınıf
"""
from datetime import datetime
import logging
import os
import json
from src.utils.error_handling import AutomationError, error_handler

class DeviceManager:
    """
    Akıllı ev cihazlarını yöneten sınıf
    """
    def __init__(self, config_file=None):
        """
        DeviceManager sınıfını başlatır
        
        Args:
            config_file (str, optional): Cihaz yapılandırma dosyası yolu
        """
        self.logger = logging.getLogger("DeviceManager")
        
        # Cihaz durumları
        self.device_states = {}
        
        # Cihaz geçmişi
        self.device_history = {}
        
        # Yapılandırma dosyası
        if config_file:
            self.load_config(config_file)
    
    @error_handler
    def load_config(self, config_file):
        """
        Cihaz yapılandırmasını dosyadan yükler
        
        Args:
            config_file (str): Yapılandırma dosyasının yolu
        """
        try:
            if not os.path.exists(config_file):
                self.logger.warning(f"Yapılandırma dosyası bulunamadı: {config_file}")
                return
                
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Cihaz durumlarını yükle
            if 'devices' in config:
                self.device_states = config['devices']
                self.logger.info(f"Yapılandırma dosyasından {len(self.device_states)} cihaz yüklendi")
        except Exception as e:
            self.logger.error(f"Yapılandırma yüklenirken hata: {str(e)}")
            raise AutomationError(f"Yapılandırma yüklenirken hata: {str(e)}")
    
    @error_handler
    def save_config(self, config_file):
        """
        Cihaz yapılandırmasını dosyaya kaydeder
        
        Args:
            config_file (str): Yapılandırma dosyasının yolu
        """
        try:
            # Yapılandırma dizinini kontrol et
            config_dir = os.path.dirname(config_file)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
                
            config = {
                'devices': self.device_states,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
                
            self.logger.info(f"Yapılandırma dosyasına {len(self.device_states)} cihaz kaydedildi")
        except Exception as e:
            self.logger.error(f"Yapılandırma kaydedilirken hata: {str(e)}")
            raise AutomationError(f"Yapılandırma kaydedilirken hata: {str(e)}")
    
    def register_device(self, device_id, room=None, type=None, initial_state=False):
        """
        Yeni bir cihazı kaydeder
        
        Args:
            device_id (str): Cihaz kimliği (örn. "Salon_Lamba")
            room (str, optional): Cihazın bulunduğu oda
            type (str, optional): Cihaz tipi (Klima, Lamba, vb.)
            initial_state (bool, optional): Başlangıç durumu
        
        Returns:
            bool: Kayıt başarılı ise True
        """
        if device_id in self.device_states:
            self.logger.warning(f"Cihaz zaten kayıtlı: {device_id}")
            return False
            
        self.device_states[device_id] = initial_state
        self.device_history[device_id] = [
            {
                'timestamp': datetime.now().isoformat(),
                'state': initial_state,
                'trigger': 'registration'
            }
        ]
        
        self.logger.info(f"Yeni cihaz kaydedildi: {device_id}, başlangıç durumu: {initial_state}")
        return True
    
    def set_device_state(self, device_id, state, trigger='manual'):
        """
        Bir cihazın durumunu değiştirir
        
        Args:
            device_id (str): Cihaz kimliği
            state (bool): Yeni durum
            trigger (str, optional): Durum değişikliğine neden olan tetikleyici
            
        Returns:
            bool: Değişiklik başarılı ise True
        """
        # Cihaz var mı kontrol et
        if device_id not in self.device_states:
            # Cihaz yoksa otomatik kaydet
            self.register_device(device_id, initial_state=state)
            return True
            
        # Durum değişti mi kontrol et
        if self.device_states[device_id] == state:
            return False  # Durum değişmedi
        
        # Durumu güncelle
        self.device_states[device_id] = state
        
        # Geçmişe kaydet
        if device_id not in self.device_history:
            self.device_history[device_id] = []
            
        self.device_history[device_id].append({
            'timestamp': datetime.now().isoformat(),
            'state': state,
            'trigger': trigger
        })
        
        # Log
        self.logger.info(f"Cihaz durumu değişti: {device_id} = {state} (Tetikleyen: {trigger})")
        return True
    
    def get_device_state(self, device_id):
        """
        Bir cihazın mevcut durumunu döndürür
        
        Args:
            device_id (str): Cihaz kimliği
            
        Returns:
            bool: Cihaz durumu (cihaz kayıtlı değilse None)
        """
        return self.device_states.get(device_id)
    
    def get_all_device_states(self):
        """
        Tüm cihazların durumlarını döndürür
        
        Returns:
            dict: Cihaz kimliği -> durum eşlemesi
        """
        return dict(self.device_states)
    
    def get_device_history(self, device_id, limit=10):
        """
        Bir cihazın durum geçmişini döndürür
        
        Args:
            device_id (str): Cihaz kimliği
            limit (int, optional): Döndürülecek kayıt sayısı
            
        Returns:
            list: Durum değişikliği kayıtları (en yeniden en eskiye)
        """
        if device_id not in self.device_history:
            return []
            
        return self.device_history[device_id][-limit:]
    
    def update_device_states(self, device_states, trigger='automation'):
        """
        Birden çok cihazın durumunu günceller
        
        Args:
            device_states (dict): Cihaz kimliği -> durum eşlemesi
            trigger (str, optional): Durum değişikliğine neden olan tetikleyici
            
        Returns:
            list: Değişen cihazların listesi
        """
        changed_devices = []
        
        for device_id, state in device_states.items():
            if self.set_device_state(device_id, state, trigger):
                changed_devices.append(device_id)
                
        return changed_devices