# home_simulator.py

import time
import threading
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import logging

# İç modülleri içe aktarma
from src.data_simulation.data_generator import HomeDataGenerator
from src.automation.rules_engine import RulesEngine
from src.models.model_manager import SmartHomeModelManager
from src.utils.visualization import SimulationVisualizer

class SmartHomeSimulator:
    """
    Akıllı ev sistemi simülatörü. 
    Gerçek zamanlı sensör verileri, kullanıcı hareketleri ve cihaz durumları simüle eder.
    Otomasyon kurallarını ve ML modellerini entegre ederek bir prototip sunar.
    """
    
    def __init__(self, rooms=None, num_residents=2, time_step=5, 
                 use_ml=True, ml_model_path=None, simulation_speed=1.0):
        """
        SmartHomeSimulator sınıfını başlatır
        
        Args:
            rooms (list): Simüle edilecek odaların listesi
            num_residents (int): Ev sakinlerinin sayısı
            time_step (int): Simülasyon adımları arasındaki dakika farkı (sanal zaman)
            use_ml (bool): Makine öğrenmesi modeli kullanılıp kullanılmayacağı
            ml_model_path (str): ML model yöneticisinin dosya yolu (None ise yeni model eğitilir)
            simulation_speed (float): Simülasyon hızı çarpanı (1.0 = gerçek zamanla aynı)
        """
        # Simülasyon parametreleri
        self.rooms = rooms or ["Salon", "Yatak Odası", "Çocuk Odası", "Mutfak", "Banyo"]
        self.num_residents = num_residents
        self.time_step = time_step
        self.use_ml = use_ml
        self.simulation_speed = simulation_speed
        self.simulation_time = datetime.now()
        
        # Durum değişkenleri
        self.running = False
        self.paused = False
        self.step_count = 0
        
        # Veri üreteci başlat
        self.data_generator = HomeDataGenerator(
            start_time=self.simulation_time,
            rooms=self.rooms,
            num_residents=num_residents,
            time_step=time_step
        )
        
        # Kural motoru başlat
        self.rules_engine = RulesEngine(use_ml_model=use_ml)
        
        # ML modelini yükle veya başlat
        self.ml_model_manager = None
        if use_ml:
            if ml_model_path and os.path.exists(ml_model_path):
                self.ml_model_manager = SmartHomeModelManager.load_manager(ml_model_path)
            # Model yoksa, simülasyon başlangıcında veri üretip model eğitilecektir.
        
        # Veri kayıtları
        self.history = []
        self.decision_history = []
        
        # Görselleştirme
        self.visualizer = SimulationVisualizer()
        
        # Loglama
        self._setup_logging()
    
    def _setup_logging(self):
        """Simülasyon için log yapılandırması yapar"""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file = os.path.join(log_dir, f"simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        # Logger yapılandırması
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("SmartHomeSimulator")
        self.logger.info("Simülasyon başlatıldı")
    
    def train_ml_model(self, days=3):
        """
        Simülasyon için bir ML modeli eğitir
        
        Args:
            days (int): Eğitim için simüle edilecek gün sayısı
        """
        if not self.use_ml:
            self.logger.info("ML modeli devre dışı, eğitim atlanıyor")
            return
            
        self.logger.info(f"Makine öğrenmesi modeli için {days} günlük veri üretiliyor")
        
        # Veri üret
        dataset = self.data_generator.generate_dataset(days=days)
        
        # CSV'ye kaydet
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "raw")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        csv_path = os.path.join(data_dir, f"training_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv")
        dataset.to_csv(csv_path, index=False)
        
        # Model yöneticisi oluştur ve eğit
        self.ml_model_manager = SmartHomeModelManager()
        self.ml_model_manager.train_models_for_all_devices(csv_path, model_type='random_forest', optimize=True)
        
        # Modeli kural motoruna ekle
        self.rules_engine.set_ml_model(self.ml_model_manager)
        
        self.logger.info("ML modeli eğitimi tamamlandı")
    
    def setup_default_rules(self):
        """Kural motoruna varsayılan kuralları ekler"""
        self.logger.info("Varsayılan kurallar ayarlanıyor")
        
        # Sıcaklık kontrolü
        def high_temp_condition(state):
            for room in self.rooms:
                if f"{room}_Sıcaklık" in state and state[f"{room}_Sıcaklık"] > 26:
                    return True
            return False
        
        def turn_on_ac(state, devices):
            changes = {}
            for room in self.rooms:
                if f"{room}_Sıcaklık" in state and state[f"{room}_Sıcaklık"] > 26:
                    if f"{room}_Klima" in devices:
                        changes[f"{room}_Klima"] = True
            return changes
        
        self.rules_engine.add_rule(
            name="Yüksek Sıcaklık - Klima Aç", 
            condition_func=high_temp_condition,
            action_func=turn_on_ac,
            priority=2,
            description="Oda sıcaklığı 26°C üzerinde ise klimayı aç"
        )
        
        # Boş oda kontrolü
        def empty_room_condition(state):
            for room in self.rooms:
                if f"{room}_Doluluk" in state and state[f"{room}_Doluluk"] == False:
                    return True
            return False
        
        def turn_off_lights_empty_room(state, devices):
            changes = {}
            for room in self.rooms:
                if f"{room}_Doluluk" in state and state[f"{room}_Doluluk"] == False:
                    # Oda boşsa ve lamba açıksa
                    if f"{room}_Lamba" in devices and devices[f"{room}_Lamba"]:
                        changes[f"{room}_Lamba"] = False
            return changes
        
        self.rules_engine.add_rule(
            name="Boş Oda - Lamba Kapat", 
            condition_func=empty_room_condition,
            action_func=turn_off_lights_empty_room,
            priority=1,
            description="Oda boş ise ışıkları kapat"
        )
        
        # Gece modu
        def night_time_condition(state):
            hour = self.simulation_time.hour
            return 22 <= hour or hour <= 6
        
        def night_mode_devices(state, devices):
            changes = {}
            for room in self.rooms:
                # Yatak odasında düşük ışık
                if room == "Yatak Odası" and f"{room}_Doluluk" in state and state[f"{room}_Doluluk"]:
                    changes[f"{room}_Lamba"] = True
                # Diğer odalarda ışıkları kapat
                elif f"{room}_Lamba" in devices and devices[f"{room}_Lamba"]:
                    if f"{room}_Doluluk" in state and state[f"{room}_Doluluk"] == False:
                        changes[f"{room}_Lamba"] = False
                # Perdeleri kapat
                if f"{room}_Perde" in devices:
                    changes[f"{room}_Perde"] = False
            return changes
        
        self.rules_engine.add_rule(
            name="Gece Modu", 
            condition_func=night_time_condition,
            action_func=night_mode_devices,
            priority=3,
            description="Gece saatlerinde (22:00-06:00) perdeleri kapat, boş odalarda ışıkları kapat"
        )
        
        # Sabah rutini
        def morning_time_condition(state):
            hour = self.simulation_time.hour
            return 7 <= hour <= 9
        
        def morning_routine_devices(state, devices):
            changes = {}
            for room in self.rooms:
                # Perdeleri aç
                if f"{room}_Perde" in devices:
                    changes[f"{room}_Perde"] = True
            return changes
        
        self.rules_engine.add_rule(
            name="Sabah Rutini", 
            condition_func=morning_time_condition,
            action_func=morning_routine_devices,
            priority=2,
            description="Sabah saatlerinde (07:00-09:00) perdeleri aç"
        )
    
    def step(self):
        """
        Simülasyonu bir adım ilerletir
        
        Returns:
            dict: Mevcut simülasyon durumu
        """
        # Simülasyon zamanını ilerlet
        self.simulation_time += timedelta(minutes=self.time_step)
        self.step_count += 1
        
        # Simüle edilmiş veriyi güncelle
        current_state = self.data_generator.update_simulation()
        
        # Mevcut cihaz durumlarını al
        device_states = {}
        for room in self.rooms:
            for device_type in ["Klima", "Lamba", "Perde", "Havalandırma"]:
                device_key = f"{room}_{device_type}"
                if device_key in current_state:
                    device_states[device_key] = current_state[device_key]
        
        # Kuralları değerlendir ve cihaz durumlarını güncelle
        updated_devices = self.rules_engine.evaluate_rules(current_state, device_states)
        
        # Kural motorundan dönen karar bilgileri için geçici bir değer oluştur
        decision_info = self.rules_engine.decision_history[-10:] if self.rules_engine.decision_history else []
        
        # Cihaz durumlarını güncelle
        for device_name, new_state in updated_devices.items():
            if device_name in current_state:
                current_state[device_name] = new_state
        
        # ML tahminleri var mı kontrol et
        ml_predictions = {}
        if self.use_ml and self.ml_model_manager:
            try:
                # Veri çerçevesi oluştur (sadece ilgili özellikler)
                features_df = pd.DataFrame([current_state])
                
                # Makine öğrenmesi tahminlerini al
                ml_predictions = self.ml_model_manager.predict_device_states(features_df)
                
                # Loga yazdır
                self.logger.info(f"ML tahminleri: {ml_predictions}")
            except Exception as e:
                self.logger.error(f"ML tahmin hatası: {e}")
        
        # Geçmiş veriye ekle
        state_record = current_state.copy()
        state_record['step'] = self.step_count
        state_record['ml_predictions'] = str(ml_predictions)  # JSON dönüştürme gerekebilir
        self.history.append(state_record)
        
        return current_state
    
    def run_simulation(self, steps=100, display=True, delay=1.0):
        """
        Simülasyonu belirtilen adım sayısı kadar çalıştırır
        
        Args:
            steps (int): Çalıştırılacak simülasyon adımı sayısı
            display (bool): Görselleştirme yapılıp yapılmayacağı
            delay (float): Adımlar arasındaki gecikme süresi (saniye)
        """
        self.running = True
        self.paused = False
        
        if not self.ml_model_manager and self.use_ml:
            self.logger.info("ML modeli bulunamadı, eğitiliyor...")
            self.train_ml_model(days=3)
        
        # Varsayılan kuralları ayarla
        self.setup_default_rules()
        
        self.logger.info(f"Simülasyon başlatılıyor: {steps} adım, görüntüleme: {display}")
        
        for i in range(steps):
            if not self.running:
                break
                
            if self.paused:
                time.sleep(0.1)  # Duraklama sırasında CPU kullanımını azaltma
                continue
            try:
                # Simülasyon adımı
                current_state = self.step()
                
                # Güncel durumu görselleştir
                if display:
                    self.visualizer.update_display(
                        current_state, 
                        step=self.step_count, 
                        simulation_time=self.simulation_time
                    )
                
                # Simülasyon adımları arasında gecikme
                adjusted_delay = delay / self.simulation_speed
                time.sleep(adjusted_delay)
                
            except Exception as e:
                self.logger.error(f"Simülasyon adımında hata: {e}")
        
        self.logger.info(f"Simülasyon tamamlandı: {self.step_count} adım")
        self.running = False
    
    def run_in_thread(self, steps=100, display=True, delay=1.0):
        """
        Simülasyonu ayrı bir iş parçacığında başlatır
        
        Args:
            steps (int): Çalıştırılacak simülasyon adımı sayısı
            display (bool): Görselleştirme yapılıp yapılmayacağı
            delay (float): Adımlar arasındaki gecikme süresi (saniye)
        """
        threading.Thread(
            target=self.run_simulation,
            args=(steps, display, delay)
        ).start()
    
    def pause(self):
        """Simülasyonu duraklatır"""
        self.paused = True
        self.logger.info("Simülasyon duraklatıldı")
    
    def resume(self):
        """Duraklatılmış simülasyonu devam ettirir"""
        self.paused = False
        self.logger.info("Simülasyon devam ediyor")
    
    def stop(self):
        """Simülasyonu durdurur"""
        self.running = False
        self.logger.info("Simülasyon durduruldu")
    
    def save_history(self, output_dir=None):
        """
        Simülasyon geçmişini CSV dosyasına kaydeder
        
        Args:
            output_dir (str): Çıktı dizini
        """
        if not self.history:
            self.logger.warning("Kaydedilecek simülasyon verisi yok")
            return None
        
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "simulation")
        
        # Dizin yoksa oluştur
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # DataFrame oluştur
        history_df = pd.DataFrame(self.history)
        
        # Dosya adı
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"simulation_history_{timestamp}.csv"
        csv_path = os.path.join(output_dir, csv_filename)
        
        # CSV'ye kaydet
        history_df.to_csv(csv_path, index=False)
        self.logger.info(f"Simülasyon geçmişi {csv_path} konumuna kaydedildi")
        
        # Karar geçmişini de kaydet
        if self.decision_history:
            decision_df = pd.DataFrame(self.decision_history)
            decision_path = os.path.join(output_dir, f"decision_history_{timestamp}.csv")
            decision_df.to_csv(decision_path, index=False)
            self.logger.info(f"Karar geçmişi {decision_path} konumuna kaydedildi")
        
        return csv_path

# Simülatör sınıfını test etmek için yardımcı fonksiyon
def run_simulation_demo(steps=50, rooms=None, display=True):
    """
    Simülasyon demosunu çalıştırır
    
    Args:
        steps (int): Simülasyon adım sayısı
        rooms (list): Simüle edilecek odalar
        display (bool): Görsel çıktı olup olmayacağı
        
    Returns:
        SmartHomeSimulator: Çalıştırılan simülatör
    """
    # Varsayılan odalar
    if rooms is None:
        rooms = ["Salon", "Yatak Odası", "Çocuk Odası", "Mutfak", "Banyo"]
    
    # Simülatörü oluştur
    simulator = SmartHomeSimulator(
        rooms=rooms,
        num_residents=3,
        time_step=5,  # 5 dakikalık adımlar
        use_ml=True,
        simulation_speed=2.0  # 2x hızlı simülasyon
    )
    
    # Simülasyonu başlat
    simulator.run_simulation(steps=steps, display=display, delay=0.5)
    
    # Geçmişi kaydet
    simulator.save_history()
    
    return simulator

if __name__ == "__main__":
    run_simulation_demo(steps=100)