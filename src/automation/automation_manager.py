import os
import time
import threading
import logging
from datetime import datetime, timedelta
import json

from src.automation.rules_engine import RulesEngine, create_default_rules
from src.automation.device_manager import DeviceManager
from src.automation.scheduler import Scheduler

class AutomationManager:
    """
    Akıllı ev otomasyon sisteminin ana kontrol sınıfı.
    RulesEngine, DeviceManager ve Scheduler bileşenlerini entegre eder.
    """
    
    def __init__(self, ml_model=None):
        """
        AutomationManager sınıfını başlatır
        
        Args:
            ml_model: Opsiyonel makine öğrenmesi modeli
        """
        # Loglama
        self.setup_logging()
        self.logger.info("AutomationManager başlatılıyor...")
        
        # Cihaz yöneticisi
        self.device_manager = DeviceManager()
        
        # Kural motoru
        self.rules_engine = RulesEngine(use_ml_model=ml_model is not None)
        
        # ML modeli varsa ayarla
        if ml_model:
            self.rules_engine.set_ml_model(ml_model)
        
        # Varsayılan kuralları ekle
        create_default_rules(self.rules_engine)
        
        # Zamanlayıcı
        self.scheduler = Scheduler(interval=10)  # Her 10 saniyede bir kontrol et
        
        # Simülasyon durumu
        self.simulation_running = False
        self.simulation_thread = None
        self.simulation_interval = 5  # Simülasyon adımları arası saniye
        self.current_state = {}
        
        self.logger.info("AutomationManager başlatıldı")
    
    def setup_logging(self):
        """
        Loglama sistemini yapılandırır
        """
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        
        # Dizin yoksa oluştur
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Log dosyası adı
        log_file = os.path.join(log_dir, f"automation_manager_{datetime.now().strftime('%Y%m%d')}.log")
        
        # Logger oluştur
        self.logger = logging.getLogger("AutomationManager")
        
        # Eğer handler yoksa ekle
        if not self.logger.handlers:
            file_handler = logging.FileHandler(log_file)
            console_handler = logging.StreamHandler()
            
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            self.logger.setLevel(logging.INFO)
    
    def process_sensor_data(self, sensor_data):
        """
        Sensör verilerini işler ve gerekli otomasyon kurallarını uygular
        
        Args:
            sensor_data (dict): Sensör okumalarını içeren sözlük
            
        Returns:
            dict: Güncellenen cihaz durumları
        """
        self.logger.info("Sensör verileri işleniyor...")
        
        # Mevcut durumu güncelle
        self.current_state = sensor_data
        
        # Mevcut cihaz durumlarını al
        device_states = self.device_manager.get_all_device_states()
        
        # Kuralları değerlendir
        updated_devices = self.rules_engine.evaluate_rules(sensor_data, device_states)
        
        # Cihaz durumlarını güncelle
        if updated_devices:
            self.device_manager.update_device_states(updated_devices, source="automation")
            self.logger.info(f"Cihaz durumları güncellendi: {updated_devices}")
        
        return updated_devices
    
    def schedule_task(self, task_func, run_at):
        """
        Gelecekte çalışacak bir görev planlar
        
        Args:
            task_func (callable): Çalıştırılacak fonksiyon
            run_at (datetime): Görevin çalıştırılacağı zaman
        """
        self.scheduler.add_task(task_func, run_at)
        self.logger.info(f"Görev planlandı: {task_func.__name__} - {run_at}")
    
    def schedule_routine_tasks(self):
        """
        Günlük rutin görevleri planlar
        """
        today = datetime.now().date()
        
        # Sabah rutini
        morning_time = datetime.combine(today, datetime.strptime("07:00", "%H:%M").time())
        if morning_time > datetime.now():
            self.schedule_task(self.morning_routine, morning_time)
        
        # Akşam rutini
        evening_time = datetime.combine(today, datetime.strptime("19:30", "%H:%M").time())
        if evening_time > datetime.now():
            self.schedule_task(self.evening_routine, evening_time)
        
        # Gece rutini
        night_time = datetime.combine(today, datetime.strptime("23:00", "%H:%M").time())
        if night_time > datetime.now():
            self.schedule_task(self.night_routine, night_time)
        
        # Yarının rutinleri
        tomorrow = today + timedelta(days=1)
        morning_time_tomorrow = datetime.combine(tomorrow, datetime.strptime("07:00", "%H:%M").time())
        self.schedule_task(self.morning_routine, morning_time_tomorrow)
        
        self.logger.info("Günlük rutin görevler planlandı")
    
    def morning_routine(self):
        """Sabah rutini - Perdeleri aç, ışıkları kontrol et"""
        self.logger.info("Sabah rutini çalıştırılıyor...")
        
        updates = {}
        # Perdeleri aç
        for room in ["Salon", "Yatak Odası", "Çocuk Odası"]:
            updates[f"{room}_Perde"] = True
        
        # Cihaz durumlarını güncelle
        self.device_manager.update_device_states(updates, source="scheduled_routine")
        
        # Bir sonraki gün için yeniden planla
        next_run = datetime.now() + timedelta(days=1)
        self.schedule_task(self.morning_routine, next_run)
    
    def evening_routine(self):
        """Akşam rutini - Işıkları ve sıcaklığı ayarla"""
        self.logger.info("Akşam rutini çalıştırılıyor...")
        
        updates = {}
        # Salon ve yatak odası ışıklarını aç
        updates["Salon_Lamba"] = True
        updates["Yatak Odası_Lamba"] = True
        
        # Perdeleri kapat
        for room in ["Salon", "Yatak Odası", "Çocuk Odası"]:
            updates[f"{room}_Perde"] = False
        
        # Cihaz durumlarını güncelle
        self.device_manager.update_device_states(updates, source="scheduled_routine")
        
        # Bir sonraki gün için yeniden planla
        next_run = datetime.now() + timedelta(days=1)
        self.schedule_task(self.evening_routine, next_run)
    
    def night_routine(self):
        """Gece rutini - Işıkları kapat, sıcaklığı ayarla"""
        self.logger.info("Gece rutini çalıştırılıyor...")
        
        updates = {}
        # Gerekli olmayan ışıkları kapat
        for room in ["Salon", "Mutfak", "Çocuk Odası"]:
            updates[f"{room}_Lamba"] = False
        
        # Cihaz durumlarını güncelle
        self.device_manager.update_device_states(updates, source="scheduled_routine")
        
        # Bir sonraki gün için yeniden planla
        next_run = datetime.now() + timedelta(days=1)
        self.schedule_task(self.night_routine, next_run)
    
    def manual_device_control(self, room, device, state):
        """
        Manuel olarak bir cihazı kontrol eder
        
        Args:
            room (str): Oda adı
            device (str): Cihaz adı
            state (bool): İstenen durum
            
        Returns:
            bool: İşlem başarılıysa True
        """
        result = self.device_manager.set_device_state(room, device, state, source="manual")
        self.logger.info(f"Manuel kontrol: {room}_{device} -> {state} (Başarı: {result})")
        return result
    
    def start_automation(self):
        """
        Otomasyon sistemini başlatır
        """
        self.logger.info("Otomasyon sistemi başlatılıyor...")
        
        # Zamanlanmış görevleri başlat
        self.scheduler.start()
        
        # Rutin görevleri planla
        self.schedule_routine_tasks()
        
        self.logger.info("Otomasyon sistemi başlatıldı")
    
    def stop_automation(self):
        """
        Otomasyon sistemini durdurur
        """
        self.logger.info("Otomasyon sistemi durduruluyor...")
        
        # Zamanlanmış görevleri durdur
        self.scheduler.stop()
        
        # Simülasyon çalışıyorsa durdur
        self.stop_simulation()
        
        self.logger.info("Otomasyon sistemi durduruldu")
    
    def start_simulation(self, initial_state=None, interval=5):
        """
        Otomasyon sistemi simülasyonunu başlatır
        
        Args:
            initial_state (dict): Başlangıç durumu
            interval (int): Simülasyon adımları arasındaki saniye
        """
        if self.simulation_running:
            self.logger.warning("Simülasyon zaten çalışıyor")
            return False
        
        self.logger.info("Simülasyon başlatılıyor...")
        self.simulation_running = True
        self.simulation_interval = interval
        
        # Başlangıç durumunu ayarla
        if initial_state:
            self.current_state = initial_state
        
        # Simülasyon thread'ini başlat
        self.simulation_thread = threading.Thread(target=self._run_simulation)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
        
        self.logger.info("Simülasyon başlatıldı")
        return True
    
    def _run_simulation(self):
        """
        Simülasyon ana döngüsü
        """
        while self.simulation_running:
            # Mevcut durumu güncelle (gerçek sistemde sensör verisi alınır)
            # Bu örnekte mevcut durumu değiştirmiyoruz, dışarıdan güncellenmesi bekleniyor
            
            # Mevcut duruma göre cihazları güncelle
            self.process_sensor_data(self.current_state)
            
            # Belirlenen süre kadar bekle
            time.sleep(self.simulation_interval)
    
    def stop_simulation(self):
        """
        Otomasyon sistemi simülasyonunu durdurur
        """
        if not self.simulation_running:
            return
        
        self.logger.info("Simülasyon durduruluyor...")
        self.simulation_running = False
        
        # Thread'in durmasını bekle
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=2)
        
        self.logger.info("Simülasyon durduruldu")
    
    def update_simulation_state(self, new_state):
        """
        Simülasyon durumunu günceller
        
        Args:
            new_state (dict): Yeni sensör ve ortam durumu
        """
        # Mevcut durumu güncelle
        self.current_state.update(new_state)
        self.logger.debug("Simülasyon durumu güncellendi")
    
    def generate_system_report(self, filepath=None):
        """
        Sistem durumu ve konfigürasyonu için rapor oluşturur
        
        Args:
            filepath (str): Kaydedilecek dosya yolu
            
        Returns:
            str: Rapor dosyasının tam yolu
        """
        if not filepath:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
            
            # Dizin yoksa oluştur
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            filepath = os.path.join(log_dir, f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        # Rapor verisi
        report = {
            'timestamp': datetime.now().isoformat(),
            'device_states': self.device_manager.get_all_device_states(),
            'room_summary': self.device_manager.get_summary_by_room(),
            'rules': [{'name': r['name'], 'description': r['description'], 'enabled': r['enabled']} for r in self.rules_engine.rules],
            'current_state': self.current_state,
            'scheduler_status': {
                'running': self.scheduler.running,
                'tasks': len(self.scheduler.tasks)
            },
            'simulation_status': {
                'running': self.simulation_running
            }
        }
        
        # JSON dosyasına kaydet
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.logger.info(f"Sistem raporu {filepath} dosyasına kaydedildi")
        
        return filepath
    
    def export_all_history(self, directory=None):
        """
        Tüm geçmiş ve log verilerini dışa aktarır
        
        Args:
            directory (str): Kaydedilecek dizin
        """
        if not directory:
            directory = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs", "export")
            
        # Dizin yoksa oluştur
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Cihaz geçmişini dışa aktar
        device_history_file = os.path.join(directory, f"device_history_{timestamp}.json")
        self.device_manager.export_device_history(device_history_file)
        
        # Karar geçmişini dışa aktar
        decision_history_file = os.path.join(directory, f"decision_history_{timestamp}.json")
        self.rules_engine.export_decision_history(decision_history_file)
        
        # Sistem raporu oluştur
        system_report_file = os.path.join(directory, f"system_report_{timestamp}.json")
        self.generate_system_report(system_report_file)
        
        self.logger.info(f"Tüm veriler {directory} dizinine aktarıldı")

# Test fonksiyonu
def test_automation_manager():
    """
    AutomationManager test fonksiyonu
    """
    # AutomationManager oluştur
    manager = AutomationManager()
    
    print("\nOtomasyon sistemi başlatılıyor...")
    manager.start_automation()
    
    # Örnek sensör verisi oluştur
    example_data = {
        "Salon_Sıcaklık": 27.5,
        "Salon_Nem": 55,
        "Salon_Işık": 80,
        "Salon_CO2": 600,
        "Salon_Hareket": True,
        "Salon_Doluluk": True,
        
        "Yatak Odası_Sıcaklık": 23.0,
        "Yatak Odası_Nem": 50,
        "Yatak Odası_Işık": 20,
        "Yatak Odası_CO2": 500,
        "Yatak Odası_Hareket": False,
        "Yatak Odası_Doluluk": False,
        
        "Çocuk Odası_Sıcaklık": 25.0,
        "Çocuk Odası_Nem": 45,
        "Çocuk Odası_Işık": 10,
        "Çocuk Odası_CO2": 550,
        "Çocuk Odası_Hareket": True,
        "Çocuk Odası_Doluluk": True,
        
        "timestamp": datetime.now().isoformat()
    }
    
    # Simülasyon başlat
    print("\nSimülasyon başlatılıyor...")
    manager.start_simulation(example_data)
    
    # Birkaç saniye bekle
    time.sleep(3)
    
    # Yeni sensör verisi gönder
    print("\nYeni sensör verisi gönderiliyor...")
    example_data["Salon_Sıcaklık"] = 29.0  # Sıcak bir oda - klima çalışmalı
    example_data["Salon_CO2"] = 900  # Yüksek CO2 - havalandırma çalışmalı
    example_data["Yatak Odası_Hareket"] = True  # Hareket başladı
    example_data["timestamp"] = datetime.now().isoformat()
    
    manager.update_simulation_state(example_data)
    
    # Birkaç saniye bekle
    time.sleep(3)
    
    # Manuel kontrol örneği
    print("\nManuel cihaz kontrolü yapılıyor...")
    manager.manual_device_control("Salon", "Lamba", False)
    
    # Birkaç saniye bekle
    time.sleep(3)
    
    # Cihaz durumlarını kontrol et
    print("\nGüncel Cihaz Durumları:")
    device_states = manager.device_manager.get_all_device_states()
    for device, state in sorted(device_states.items()):
        print(f"{device}: {'Açık' if state else 'Kapalı'}")
    
    # Sistem raporu oluştur
    print("\nSistem raporu oluşturuluyor...")
    report_path = manager.generate_system_report()
    print(f"Rapor dosyası: {report_path}")
    
    # Simülasyonu ve otomasyonu durdur
    print("\nSimülasyon ve otomasyon durduruluyor...")
    manager.stop_simulation()
    manager.stop_automation()
    
    return manager

if __name__ == "__main__":
    test_automation_manager()