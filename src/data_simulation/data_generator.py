import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os
import random

from src.data_simulation.sensor_simulator import SensorSimulator
from src.data_simulation.user_simulator import UserSimulator

class HomeDataGenerator:
    """
    Akıllı ev için kapsamlı veri seti üreten sınıf.
    Sensör verileri ve kullanıcı davranışlarını entegre ederek gerçekçi bir veri seti oluşturur.
    """
    
    def __init__(self, start_time=None, rooms=None, num_residents=2, time_step=5):
        """
        HomeDataGenerator sınıfını başlatır
        
        Args:
            start_time (datetime): Simülasyonun başlangıç zamanı
            rooms (list): Simüle edilecek odaların listesi
            num_residents (int): Ev sakinlerinin sayısı
            time_step (int): Simülasyon adımları arasındaki dakika farkı
        """
        self.start_time = start_time or datetime.now()
        self.rooms = rooms or ["Salon", "Yatak Odası", "Çocuk Odası", "Mutfak", "Banyo"]
        self.time_step = time_step
        self.current_time = self.start_time
        
        # Simülatörleri başlat
        self.sensor_simulator = SensorSimulator(rooms=self.rooms, start_time=self.start_time, time_step=self.time_step)
        self.user_simulator = UserSimulator(num_residents=num_residents, rooms=self.rooms)
        
        # Cihazların manuel kullanım olasılıkları (kullanıcı tarafından açma/kapama)
        self.manual_operation_prob = {
            "Klima": 0.2,
            "Lamba": 0.7,
            "Perde": 0.4,
            "Havalandırma": 0.3
        }
    
    def _update_devices_by_user_behavior(self, user_locations):
        """
        Kullanıcı davranışlarına göre cihazları günceller
        
        Args:
            user_locations (dict): Kullanıcı konumları
        """
        # Hangi odalarda insan var?
        occupied_rooms = []
        for location in user_locations.values():
            if location in self.rooms:
                occupied_rooms.append(location)
        
        # Cihaz durumlarını güncelle
        for room in self.rooms:
            is_occupied = room in occupied_rooms
            devices = self.sensor_simulator.devices[room]
            
            for device in devices:
                # Kullanıcının cihazı manuel olarak kontrol etme olasılığı
                if is_occupied and random.random() < self.manual_operation_prob.get(device, 0.5):
                    if device == "Lamba":
                        # Oda doluysa ve saat akşamsa lambayı açma olasılığı yüksek
                        if 18 <= self.current_time.hour <= 23 or 0 <= self.current_time.hour <= 6:
                            devices[device] = random.random() < 0.9  # %90 açık
                        else:
                            devices[device] = random.random() < 0.3  # %30 açık
                    
                    elif device == "Klima":
                        # Sıcaklık yüksekse klimayı açma olasılığı yüksek
                        temp = self.sensor_simulator.room_status[room]["Sıcaklık"]
                        if temp > 26:
                            devices[device] = random.random() < 0.8  # %80 açık
                        elif temp < 20:
                            devices[device] = random.random() < 0.2  # %20 açık
                        else:
                            devices[device] = random.random() < 0.4  # %40 açık
                    
                    elif device == "Perde":
                        # Sabah saatlerinde perdeyi açma olasılığı yüksek
                        if 7 <= self.current_time.hour <= 10:
                            devices[device] = random.random() < 0.9  # %90 açık
                        # Akşam saatlerinde perdeyi kapatma olasılığı yüksek
                        elif 19 <= self.current_time.hour <= 23:
                            devices[device] = random.random() < 0.2  # %20 açık
                        else:
                            devices[device] = random.random() < 0.5  # %50 açık
                    
                    elif device == "Havalandırma":
                        # CO2 seviyesi yüksekse havalandırmayı açma olasılığı yüksek
                        co2 = self.sensor_simulator.room_status[room]["CO2"]
                        if co2 > 800:
                            devices[device] = random.random() < 0.7  # %70 açık
                        else:
                            devices[device] = random.random() < 0.3  # %30 açık
            
            # Oda boşsa ve belirli bir süre geçtiyse, cihazları otomatik olarak kapat (enerji tasarrufu)
            if not is_occupied:
                # Son hareket zamanından bu yana geçen süre (dakika)
                time_since_last_movement = (self.current_time - self.sensor_simulator.room_status[room]["Son_Hareket"]).total_seconds() / 60
                
                if time_since_last_movement > 15:  # 15 dakikadan fazla süre geçtiyse
                    # Lambaları %90 olasılıkla kapat
                    if "Lamba" in devices and devices["Lamba"] and random.random() < 0.9:
                        devices["Lamba"] = False
                
                if time_since_last_movement > 30:  # 30 dakikadan fazla süre geçtiyse
                    # Klimayı %70 olasılıkla kapat
                    if "Klima" in devices and devices["Klima"] and random.random() < 0.7:
                        devices["Klima"] = False
                    
                    # Havalandırmayı %80 olasılıkla kapat
                    if "Havalandırma" in devices and devices["Havalandırma"] and random.random() < 0.8:
                        devices["Havalandırma"] = False
    
    def update_simulation(self):
        """
        Simülasyonu bir adım ilerletir
        
        Returns:
            dict: Güncellenmiş simülasyon durumu
        """
        # Simülasyon zamanını güncelle
        self.current_time += timedelta(minutes=self.time_step)
        
        # Kullanıcı konumlarını güncelle
        user_locations = self.user_simulator.update_locations(self.current_time)
        
        # Kullanıcı davranışlarına göre cihazları güncelle
        self._update_devices_by_user_behavior(user_locations)
        
        # Sensör verilerini güncelle
        self.sensor_simulator.current_time = self.current_time
        sensor_state = self.sensor_simulator.update_simulation(self.time_step)
        
        # Oda doluluklarını kullanıcı konumlarına göre güncelle
        room_occupancy = self.user_simulator.get_room_occupancy()
        for room in self.rooms:
            self.sensor_simulator.room_status[room]["Doluluk"] = room_occupancy[room]
        
        # Güncellenmiş tam durumu al
        full_state = self.get_current_state()
        
        return full_state
    
    def get_current_state(self):
        """
        Mevcut simülasyon durumunu döndürür
        
        Returns:
            dict: Mevcut simülasyon durumu
        """
        state = {
            "timestamp": self.current_time
        }
        
        # Sensör durumlarını al
        sensor_state = self.sensor_simulator.get_current_state()
        for key, value in sensor_state.items():
            if key != "timestamp":  # timestamp zaten eklendi
                state[key] = value
        
        # Kullanıcı konumlarını ekle
        user_locations = self.user_simulator.resident_locations
        for user, location in user_locations.items():
            state[f"{user}_Konum"] = location
        
        return state
    
    def generate_dataset(self, days=1, save_to_csv=True, csv_path=None):
        """
        Belirli bir süre için veri seti üretir
        
        Args:
            days (int): Simüle edilecek gün sayısı
            save_to_csv (bool): Verileri CSV'ye kaydetme durumu
            csv_path (str): Kaydedilecek CSV dosyasının yolu
            
        Returns:
            pandas.DataFrame: Üretilen veri seti
        """
        # Başlangıç zamanını ayarla
        self.current_time = self.start_time
        
        # Simülasyon için adım sayısını hesapla
        steps = int((days * 24 * 60) / self.time_step)
        
        all_states = []
        
        print(f"{days} gün için veri üretiliyor ({steps} adım)...")
        
        # Her adım için simülasyonu güncelle
        for i in range(steps):
            state = self.update_simulation()
            all_states.append(state)
            
            # İlerleme göster
            if (i + 1) % 100 == 0 or i == steps - 1:
                print(f"İlerleme: {i + 1}/{steps} adım ({((i + 1) / steps * 100):.1f}%)")
        
        # DataFrame oluştur
        df = pd.DataFrame(all_states)
        
        # CSV'ye kaydet
        if save_to_csv:
            if csv_path is None:
                # Varsayılan dosya yolu
                directory = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "raw")
                
                # Dizin yoksa oluştur
                if not os.path.exists(directory):
                    os.makedirs(directory)
                
                csv_path = os.path.join(directory, f"home_data_{self.start_time.strftime('%Y%m%d_%H%M')}.csv")
            
            df.to_csv(csv_path, index=False)
            print(f"Veri seti {csv_path} konumuna kaydedildi.")
        
        return df

# Ana işlev
def generate_sample_dataset(days=3, rooms=None, num_residents=3):
    """
    Örnek bir veri seti oluşturur ve CSV olarak kaydeder
    
    Args:
        days (int): Simüle edilecek gün sayısı
        rooms (list): Simüle edilecek odaların listesi
        num_residents (int): Simüle edilecek ev sakini sayısı
        
    Returns:
        pandas.DataFrame: Üretilen veri seti
    """
    # Varsayılan odaları ayarla
    if rooms is None:
        rooms = ["Salon", "Yatak Odası", "Çocuk Odası", "Mutfak", "Banyo"]
    
    # Simülasyon başlangıç zamanını ayarla (bugün sabah 8:00)
    start_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    
    # Veri üreticiyi başlat
    generator = HomeDataGenerator(
        start_time=start_time,
        rooms=rooms,
        num_residents=num_residents
    )
    
    # Veri setini üret
    dataset = generator.generate_dataset(days=days)
    
    print(f"\nVeri seti boyutu: {dataset.shape}")
    print(f"Veri seti örneği (ilk 5 satır):")
    print(dataset.head())
    
    return dataset

if __name__ == "__main__":
    # Örnek veri seti oluştur
    generate_sample_dataset(days=3)