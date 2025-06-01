import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import os

class SensorSimulator:
    """
    Akıllı ev için sensör verilerini simüle eden sınıf.
    Sıcaklık, nem, ışık seviyesi, CO2 ve kullanıcı hareketleri gibi verileri üretir.
    """
    
    def __init__(self, rooms=None, start_time=None, time_step=5):
        """
        SensorSimulator sınıfı başlatma
        
        Args:
            rooms (list): Simüle edilecek odaların listesi
            start_time (datetime): Simülasyonun başlangıç zamanı
            time_step (int): Simülasyon adımları arasındaki dakika farkı
        """
        self.rooms = rooms or ["Salon", "Yatak Odası", "Çocuk Odası", "Mutfak", "Banyo"]
        self.start_time = start_time or datetime.now()
        self.time_step = time_step
        self.current_time = self.start_time
        
        # Cihazlar ve bunların durumları
        self.devices = {
            "Salon": {"Klima": False, "Lamba": False, "Perde": False},
            "Yatak Odası": {"Klima": False, "Lamba": False, "Perde": False},
            "Çocuk Odası": {"Klima": False, "Lamba": False, "Perde": False},
            "Mutfak": {"Lamba": False, "Havalandırma": False},
            "Banyo": {"Lamba": False, "Havalandırma": False}
        }
        
        # Her odanın başlangıç durumunu ayarla
        self.room_status = {}
        for room in self.rooms:
            self.room_status[room] = {
                "Sıcaklık": self._random_temp(),
                "Nem": self._random_humidity(),
                "Işık": self._random_light(),
                "CO2": self._random_co2(),
                "Hareket": False,
                "Doluluk": False,
                "Son_Hareket": self.start_time - timedelta(minutes=random.randint(5, 120))
            }
    
    def _random_temp(self):
        """Rastgele sıcaklık değeri üretir (°C)"""
        return round(random.uniform(18.0, 30.0), 1)
    
    def _random_humidity(self):
        """Rastgele nem değeri üretir (%)"""
        return round(random.uniform(30.0, 70.0), 1)
    
    def _random_light(self):
        """Rastgele ışık seviyesi üretir (lux)"""
        # Gün içindeki saate göre ışık seviyesini ayarla
        hour = self.current_time.hour
        if 8 <= hour <= 18:  # Gündüz
            return round(random.uniform(200, 1000), 1)
        elif 6 <= hour < 8 or 18 < hour <= 20:  # Şafak/alacakaranlık
            return round(random.uniform(50, 200), 1)
        else:  # Gece
            return round(random.uniform(0, 50), 1)
    
    def _random_co2(self):
        """Rastgele CO2 seviyesi üretir (ppm)"""
        return round(random.uniform(400, 1200), 1)
    
    def _simulate_user_movement(self):
        """Kullanıcı hareketlerini simüle eder"""
        for room in self.rooms:
            # Hareket olasılığı - odada hareket olma ihtimali
            movement_prob = 0.2
            
            # Eğer son hareketten bu yana çok zaman geçtiyse, hareket olasılığı artar
            time_since_last_movement = (self.current_time - self.room_status[room]["Son_Hareket"]).total_seconds() / 60
            if time_since_last_movement > 30:
                movement_prob += 0.2
            
            # Gün içindeki saate göre hareket olasılığını ayarla
            hour = self.current_time.hour
            if 7 <= hour <= 9:  # Sabah
                movement_prob += 0.3
            elif 17 <= hour <= 22:  # Akşam
                movement_prob += 0.4
            elif 0 <= hour <= 6:  # Gece
                movement_prob -= 0.1
            
            # Hareket simülasyonu
            if random.random() < movement_prob:
                self.room_status[room]["Hareket"] = True
                self.room_status[room]["Son_Hareket"] = self.current_time
                
                # Hareket varsa odanın dolu olma ihtimali
                if random.random() < 0.8:
                    self.room_status[room]["Doluluk"] = True
            else:
                self.room_status[room]["Hareket"] = False
                
                # Hareket yoksa, belirli bir süre sonra oda boşalabilir
                if self.room_status[room]["Doluluk"] and random.random() < 0.3:
                    self.room_status[room]["Doluluk"] = False
    
    def _update_environmental_data(self):
        """Çevresel verileri (sıcaklık, nem vb.) günceller"""
        for room in self.rooms:
            # Cihazların durumuna ve diğer faktörlere göre sensör verilerini güncelle
            
            # Sıcaklık değişimi
            temp_change = random.uniform(-0.5, 0.5)  # Doğal dalgalanma
            
            # Klima açıksa sıcaklığı ayarla
            if "Klima" in self.devices[room] and self.devices[room]["Klima"]:
                desired_temp = 23.0  # Hedef sıcaklık
                current_temp = self.room_status[room]["Sıcaklık"]
                if current_temp > desired_temp:
                    temp_change -= random.uniform(0.5, 1.0)  # Soğutma
                else:
                    temp_change += random.uniform(0.5, 1.0)  # Isıtma
            
            # Saat bazlı sıcaklık değişimi (gündüz daha sıcak, gece daha serin)
            hour = self.current_time.hour
            if 10 <= hour <= 16:  # Gün ortası
                temp_change += 0.2
            elif 0 <= hour <= 5:  # Gece
                temp_change -= 0.2
            
            # Odada insan varsa sıcaklık ve CO2 biraz artar
            if self.room_status[room]["Doluluk"]:
                temp_change += 0.1
                self.room_status[room]["CO2"] += random.uniform(10, 30)
            else:
                # Odada kimse yoksa CO2 yavaşça düşer
                if self.room_status[room]["CO2"] > 500:
                    self.room_status[room]["CO2"] -= random.uniform(5, 15)
            
            # Değerleri güncelle ve sınırlar içinde tut
            self.room_status[room]["Sıcaklık"] = max(15, min(35, self.room_status[room]["Sıcaklık"] + temp_change))
            self.room_status[room]["Nem"] = max(20, min(80, self.room_status[room]["Nem"] + random.uniform(-2, 2)))
            self.room_status[room]["Işık"] = self._random_light()  # Işık seviyesi saat bazlı güncellenir
            self.room_status[room]["CO2"] = max(400, min(2000, self.room_status[room]["CO2"]))
    
    def update_simulation(self, time_step=None):
        """
        Simülasyon durumunu günceller, sensör verilerini ve kullanıcı hareketlerini simüle eder
        
        Args:
            time_step (int): İlerletilecek dakika sayısı (None ise varsayılan kullanılır)
        
        Returns:
            dict: Güncellenen simülasyon durumu
        """
        self.current_time += timedelta(minutes=time_step or self.time_step)
        
        # Kullanıcı hareketlerini simüle et
        self._simulate_user_movement()
        
        # Çevresel verileri güncelle
        self._update_environmental_data()
        
        return self.get_current_state()
    
    def get_current_state(self):
        """
        Mevcut simülasyon durumunu döndürür
        
        Returns:
            dict: Mevcut simülasyon durumu
        """
        state = {
            "timestamp": self.current_time
        }
        
        # Her oda için durum bilgilerini ekle
        for room in self.rooms:
            for sensor, value in self.room_status[room].items():
                if sensor != "Son_Hareket":  # Dahili değişkenleri çıkarıyoruz
                    state[f"{room}_{sensor}"] = value
            
            # Cihaz durumlarını ekle
            for device, status in self.devices[room].items():
                state[f"{room}_{device}"] = status
        
        return state
    
    def generate_sensor_data(self, days=1, save_to_csv=True, csv_path=None):
        """
        Belirli bir süre için sensör verilerini simüle ederek bir DataFrame ve opsiyonel olarak CSV dosyası üretir
        
        Args:
            days (int): Simüle edilecek gün sayısı
            save_to_csv (bool): Verileri CSV'ye kaydetme durumu
            csv_path (str): Kaydedilecek CSV dosyasının yolu
            
        Returns:
            pandas.DataFrame: Simüle edilen sensör verileri
        """
        # Başlangıç zamanını ayarla
        self.current_time = self.start_time
        
        # Simülasyon için adım sayısını hesapla
        steps = int((days * 24 * 60) / self.time_step)
        
        all_states = []
        
        # Her adım için simülasyonu güncelle
        for _ in range(steps):
            state = self.update_simulation()
            all_states.append(state)
        
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
                
                csv_path = os.path.join(directory, f"sensor_data_{self.start_time.strftime('%Y%m%d_%H%M')}.csv")
            
            df.to_csv(csv_path, index=False)
            print(f"Sensör verileri {csv_path} konumuna kaydedildi.")
        
        return df

# Test işlevi
def test_sensor_simulator():
    """SensorSimulator'ü test eder ve örnek veri üretir"""
    # Simülatörü başlat
    simulator = SensorSimulator()
    
    # 2 günlük veri üret ve CSV'ye kaydet
    data = simulator.generate_sensor_data(days=2)
    
    print(f"Üretilen veri boyutu: {data.shape}")
    print("\nÖrnek Veri (ilk 5 satır):")
    print(data.head())
    
    return data

if __name__ == "__main__":
    test_sensor_simulator()