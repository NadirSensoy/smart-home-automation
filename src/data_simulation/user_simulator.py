import random
from datetime import datetime, timedelta

class UserSimulator:
    """
    Ev sakinlerinin davranışlarını simüle eden sınıf.
    Günlük rutinler, ev içi hareketler ve cihaz kullanımlarını simüle eder.
    """
    
    def __init__(self, num_residents=2, rooms=None):
        """
        UserSimulator sınıfını başlatır
        
        Args:
            num_residents (int): Ev sakinlerinin sayısı
            rooms (list): Simüle edilecek odaların listesi
        """
        self.num_residents = num_residents
        self.rooms = rooms or ["Salon", "Yatak Odası", "Çocuk Odası", "Mutfak", "Banyo"]
        
        # Ev sakinlerinin şu andaki konumları
        self.resident_locations = {}
        for i in range(num_residents):
            # Başlangıçta herkesi rastgele bir odaya yerleştir
            self.resident_locations[f"Kişi_{i+1}"] = random.choice(self.rooms)
        
        # Günlük rutinler (saat:dakika formatında)
        self.daily_routines = {
            # Hafta içi rutinleri
            "Weekday": {
                "Kişi_1": {
                    "07:00": "Yatak Odası",  # Uyanma
                    "07:15": "Banyo",        # Duş/hazırlık
                    "07:45": "Mutfak",       # Kahvaltı
                    "08:30": None,           # Evden çıkış (işe gidiş)
                    "18:00": "Salon",        # Eve dönüş
                    "19:30": "Mutfak",       # Akşam yemeği
                    "20:30": "Salon",        # TV/dinlenme
                    "23:00": "Yatak Odası"   # Uyku
                },
                "Kişi_2": {
                    "06:30": "Yatak Odası",
                    "06:45": "Banyo",
                    "07:15": "Mutfak",
                    "08:00": None,
                    "17:30": "Salon",
                    "19:30": "Mutfak",
                    "20:30": "Salon",
                    "22:30": "Yatak Odası"
                }
            },
            # Hafta sonu rutinleri
            "Weekend": {
                "Kişi_1": {
                    "09:00": "Yatak Odası",
                    "09:30": "Banyo",
                    "10:00": "Mutfak",
                    "11:00": "Salon",
                    "13:30": "Mutfak",
                    "14:30": "Salon",
                    "19:00": "Mutfak",
                    "20:00": "Salon",
                    "23:30": "Yatak Odası"
                },
                "Kişi_2": {
                    "08:30": "Yatak Odası",
                    "09:00": "Banyo",
                    "09:30": "Mutfak",
                    "10:30": "Salon",
                    "13:30": "Mutfak",
                    "14:30": "Çocuk Odası",
                    "17:00": "Salon",
                    "19:00": "Mutfak",
                    "20:00": "Salon",
                    "23:00": "Yatak Odası"
                }
            }
        }
        
        # Rastgele hareketler için son hareket zamanları
        self.last_random_move = {resident: datetime.now() for resident in self.resident_locations}
    
    def _is_weekend(self, date):
        """Verilen tarihin hafta sonu olup olmadığını kontrol eder"""
        return date.weekday() >= 5  # 5 = Cumartesi, 6 = Pazar
    
    def _get_routine_type(self, date):
        """Tarih için rutin tipini döndürür (Weekday/Weekend)"""
        return "Weekend" if self._is_weekend(date) else "Weekday"
    
    def _get_scheduled_location(self, resident, current_time):
        """
        Belirli bir zaman için kullanıcının planlanan konumunu döndürür
        
        Args:
            resident (str): Kullanıcı adı
            current_time (datetime): Mevcut zaman
            
        Returns:
            str: Planlanan konum (oda adı) veya None (ev dışında)
        """
        routine_type = self._get_routine_type(current_time)
        
        # Kullanıcı için rutin yoksa None döndür
        if resident not in self.daily_routines[routine_type]:
            return None
            
        routine = self.daily_routines[routine_type][resident]
        current_time_str = current_time.strftime("%H:%M")
        
        # Planlanan saatleri kontrol et ve şu anki zamandan önceki en son planlanan konumu bul
        scheduled_times = sorted(routine.keys())
        scheduled_location = None
        
        for time_str in scheduled_times:
            if time_str <= current_time_str:
                scheduled_location = routine[time_str]
            else:
                break
                
        return scheduled_location
    
    def _should_make_random_move(self, resident, current_time):
        """
        Kullanıcının rastgele hareket etmesi gerekip gerekmediğini belirler
        
        Args:
            resident (str): Kullanıcı adı
            current_time (datetime): Mevcut zaman
            
        Returns:
            bool: Rastgele hareket yapılması gerekiyorsa True
        """
        # Son rastgele hareketten bu yana geçen süre (dakika)
        time_since_last_move = (current_time - self.last_random_move[resident]).total_seconds() / 60
        
        # Ortalama olarak her 30 dakikada bir rastgele hareket etme olasılığı
        probability = min(1.0, time_since_last_move / 30)
        
        return random.random() < probability
    
    def update_locations(self, current_time):
        """
        Belirtilen zamana göre kullanıcı konumlarını günceller
        
        Args:
            current_time (datetime): Güncellenecek zaman
            
        Returns:
            dict: Kullanıcı konumları (kullanıcı adı -> oda adı)
        """
        for resident in self.resident_locations:
            # Planlanan konumu al
            scheduled_location = self._get_scheduled_location(resident, current_time)
            
            # Kullanıcı evde değilse (None), konumunu güncelle
            if scheduled_location is None:
                self.resident_locations[resident] = None
                continue
                
            # Kullanıcı planlanan bir aktivitede mi yoksa rastgele hareket mi etmeli?
            if self._should_make_random_move(resident, current_time):
                # Rastgele hareket - evdeki bir odaya git
                self.resident_locations[resident] = random.choice(self.rooms)
                self.last_random_move[resident] = current_time
            else:
                # Planlanan lokasyona git
                self.resident_locations[resident] = scheduled_location
        
        return self.resident_locations
    
    def get_room_occupancy(self):
        """
        Her odanın doluluk durumunu hesaplar
        
        Returns:
            dict: Oda adı -> doluluk durumu (Boolean)
        """
        occupancy = {room: False for room in self.rooms}
        
        for location in self.resident_locations.values():
            if location in occupancy:
                occupancy[location] = True
                
        return occupancy

# Test işlevi
def test_user_simulator():
    """UserSimulator'ü test eder"""
    # Simülatörü başlat
    simulator = UserSimulator(num_residents=3)
    
    # Günün farklı saatlerinde konum güncellemesi yap
    test_times = [
        datetime.now().replace(hour=7, minute=30),
        datetime.now().replace(hour=12, minute=0),
        datetime.now().replace(hour=18, minute=30),
        datetime.now().replace(hour=22, minute=0)
    ]
    
    for time in test_times:
        locations = simulator.update_locations(time)
        occupancy = simulator.get_room_occupancy()
        
        print(f"\nZaman: {time.strftime('%H:%M')}")
        print(f"Kullanıcı Konumları: {locations}")
        print(f"Oda Dolulukları: {occupancy}")

if __name__ == "__main__":
    test_user_simulator()