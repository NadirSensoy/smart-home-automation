# 📡 Sensörler ve Cihazlar - Gerçek Simülasyon Verileri

Bu kapsamlı dokümanda, Akıllı Ev Otomasyon Sistemi'nde kullanılan tüm sensörlerin ve kontrol edilen cihazların **gerçek simülasyon verilerine dayalı** teknik özellikleri, performans metrikleri ve çalışma prensipleri detaylı olarak açıklanmaktadır.

## 📊 Gerçek Simülasyon Özeti (27 Haziran 2025)

**🎯 Temel Metrikler:**
- **Simülasyon Süresi:** 50 adım (4 saat 5 dakika)
- **Toplam Sensör:** 20 aktif sensör
- **Toplam Cihaz:** 13 aktif cihaz  
- **Veri Noktası:** 2,450 toplam ölçüm
- **Model Başarısı:** 13/13 (%100)

## 🌡️ Sensör Sistemi - Gerçek Veriler (5 Oda × 4 Sensör = 20 Sensör)

### 1. 🌡️ Sıcaklık Sensörleri - Gerçek Ölçümler

**📊 Son Simülasyon Sonuçları:**
```
🏠 Salon_Sıcaklık: 32.2°C (22.8-35.0°C aralığında)
🛏️ Yatak Odası_Sıcaklık: 33.0°C (29.1-35.0°C aralığında)  
👶 Çocuk Odası_Sıcaklık: 34.6°C (31.1-35.0°C aralığında)
🍳 Mutfak_Sıcaklık: 34.7°C (33.8-35.0°C aralığında)
🚿 Banyo_Sıcaklık: 34.7°C (33.7-35.0°C aralığında)
```

**📋 Teknik Özellikler:**
- **Gerçek Ölçüm Aralığı:** 22.8°C - 35.0°C
- **Ortalama Sıcaklık:** 33.6°C
- **En Sıcak Oda:** Mutfak ve Banyo (34.7°C)
- **En Serin Oda:** Salon (22.8°C minimum)
- **Örnekleme Aralığı:** 5 dakikalık periyotlar
- **Veri Formatı:** Float (°C)

### 2. 💧 Nem Sensörleri - Gerçek Ölçümler

**📊 Son Simülasyon Sonuçları:**
```
🏠 Salon_Nem: 67.5% (62.5-72.9% aralığında)
🛏️ Yatak Odası_Nem: 64.2% (59.0-68.3% aralığında)
👶 Çocuk Odası_Nem: 63.1% (54.5-70.6% aralığında)  
🍳 Mutfak_Nem: 32.1% (27.4-37.1% aralığında) ⬇️ EN DÜŞÜK
🚿 Banyo_Nem: 71.7% (66.2-78.0% aralığında) ⬆️ EN YÜKSEK
```

**📋 Teknik Özellikler:**
- **Gerçek Ölçüm Aralığı:** %27.4 - %78.0 RH
- **Ortalama Nem:** %59.7 RH
- **En Nemli Oda:** Banyo (%71.7 ortalama)
- **En Kuru Oda:** Mutfak (%32.1 ortalama)
- **Ideal Nem Aralığı:** %40-60 (Salon ve Yatak Odası ideal)
- **Örnekleme Aralığı:** 5 dakikalık periyotlar
- **Çalışma Sıcaklığı:** -40°C ile +80°C
- **Veri Formatı:** Float (%)

**📊 Nem Kategorileri:**
```python
humidity_categories = {
    'very_dry': 0-30,      # Çok kuru
    'dry': 30-40,          # Kuru
    'optimal': 40-60,      # İdeal
    'humid': 60-70,        # Nemli
    'very_humid': 70-100   # Çok nemli
}
```

**⚙️ Otomasyon Kuralları:**
- **Çok Kuru (<30%):** Nemlendirici devreye girer
- **İdeal (40-60%):** Sistem normal çalışır
- **Nemli (>70%):** Nem alıcı/havalandırma açılır
- **Kritik (>80%):** Küf önleme modu

### 3. 🌬️ CO2 Sensörleri - Gerçek Ölçümler

**📊 Son Simülasyon Sonuçları:**
```
🏠 Salon_CO2: 1140 ppm (1038-1357 ppm) ⬆️ EN YÜKSEK
🛏️ Yatak Odası_CO2: 535 ppm (494-602 ppm)
👶 Çocuk Odası_CO2: 558 ppm (489-716 ppm)
🍳 Mutfak_CO2: 823 ppm (749-912 ppm)
🚿 Banyo_CO2: 546 ppm (493-704 ppm)
```

**📋 Teknik Özellikler:**
- **Gerçek Ölçüm Aralığı:** 489-1357 ppm
- **Ortalama CO2:** 720 ppm
- **En Yüksek CO2:** Salon (1140 ppm) - Yoğun kullanım
- **En Düşük CO2:** Yatak Odası (535 ppm) - Az aktiflik
- **Kritik Seviye:** Salon >1000 ppm (havalandırma gerekli)
- **İdeal Seviye:** <800 ppm (Yatak Odası, Çocuk Odası ideal)

**🚨 Havalandırma Tetikleme Analizi:**
- **Salon:** Sürekli havalandırma gerekli (1140 ppm)
- **Mutfak:** Orta seviye havalandırma (823 ppm)
- **Diğer Odalar:** Normal havalandırma yeterli (<600 ppm)

### 4. 🚶 Hareket Sensörleri - Gerçek Aktivite

**📊 Son Simülasyon Sonuçları:**
```
🏠 Salon_Hareket: 50.0% aktif - En yoğun oda
🛏️ Yatak Odası_Hareket: 30.0% aktif
👶 Çocuk Odası_Hareket: 52.0% aktif - En aktif oda
🍳 Mutfak_Hareket: 48.0% aktif
🚿 Banyo_Hareket: 40.0% aktif
```

**📋 Aktivite Analizi:**
- **En Aktif Oda:** Çocuk Odası (%52.0 aktivite)
- **En Sakin Oda:** Yatak Odası (%30.0 aktivite)
- **Ortalama Aktivite:** %44.0
- **Gündüz Aktivitesi:** Salon ve Çocuk Odası yoğun
- **Akşam Aktivitesi:** Yatak Odası sakin (uyku zamanı)

**⚡ Otomasyon Tetikleme Performansı:**
- **Işık Kontrolü:** Hareket tespit edildiğinde lamba açılır
- **HVAC Kontrolü:** Aktivite durumuna göre iklim ayarı
- **Güvenlik:** Beklenmeyen hareket tespiti
- **Enerji Tasarrufu:** İnaktif odalarda cihaz kapatma
- **Hareket Algılandı:** Lamba açılır, klima uyandırılır
- **Hareket Yok (15 dk):** Enerji tasarrufu modu
- **Hareket Yok (30 dk):** Klima/ısıtma kapatılır
- **Gece Hareketi:** Gece lambası modu

### 6. 👥 Doluluk Sensörü (Kombine Sistem)

**📋 Teknoloji Kombinasyonu:**
- **PIR Hareket + Kapı Sensörü + AI Analiz**
- **Çıkarım Mantığı:** Makine öğrenmesi bazlı
- **Doğruluk:** %95+ (ML model ile)
- **Yanıt Süresi:** <1 saniye
- **Veri Formatı:** Boolean

**🧠 Doluluk Hesaplama:**
```python
occupancy_logic = {
    'recent_motion': 'Son 10 dakikada hareket',
    'door_events': 'Giriş/çıkış sensörleri',
    'schedule_data': 'Kullanıcı rutinleri',
    'ml_prediction': 'Makine öğrenmesi tahmini'
}
```

## 🏠 Cihaz Sistemi (5 Oda × 2-3 Cihaz = 13 Cihaz)

### 1. ❄️ Klima Sistemi (Split Tip - 9 Adet)

**📋 Teknik Özellikler:**
| Oda | Model | Kapasite | Enerji Sınıfı | Özel Özellik |
|-----|-------|----------|---------------|--------------|
| Salon | 24000 BTU | 2.5 kW | A++ | Inverter |
| Yatak Odası | 18000 BTU | 1.8 kW | A++ | Sessiz mod |
| Çocuk Odası | 12000 BTU | 1.2 kW | A+ | Çocuk kilidi |

**⚙️ Kontrol Parametreleri:**
```python
ac_control = {
    'temperature_range': (16, 30),    # °C
    'fan_speeds': ['low', 'med', 'high', 'auto'],
    'modes': ['cool', 'heat', 'auto', 'dry', 'fan'],
    'timer': (1, 24),                 # saat
    'energy_saving': True,
    'wifi_control': True
}
```

**🎯 Akıllı Kontrol Özellikleri:**
- **Prediktif Soğutma:** Kullanıcı eve gelmeden 30 dk önce
- **Zaman Programlama:** Haftalık rutin öğrenme
- **Enerji Optimizasyonu:** Elektrik tarife saatleri
- **Konfor Dengesi:** Nem + sıcaklık kombinasyonu

### 2. 💡 LED Aydınlatma Sistemi (13 Adet)

**📋 LED Teknoloji:**
| Oda | Adet | Güç | Renk Sıcaklığı | Dimmer |
|-----|------|-----|----------------|--------|
| Salon | 6×10W | 60W | 2700-6500K | ✅ |
| Yatak Odası | 4×8W | 32W | 2200-4000K | ✅ |
| Çocuk Odası | 3×12W | 36W | 3000-6500K | ✅ |
| Mutfak | 8×15W | 120W | 4000-6500K | ✅ |
| Banyo | 2×10W | 20W | 3000-5000K | ❌ |

**🎨 Akıllı Aydınlatma:**
```python
smart_lighting = {
    'circadian_rhythm': True,         # Doğal ritim
    'adaptive_brightness': True,      # Adaptif parlaklık
    'color_temperature': 'variable',  # Değişken renk
    'motion_activation': True,        # Hareket tetikleme
    'timer_control': True,           # Zamanlama
    'scene_modes': [                 # Sahne modları
        'morning', 'work', 'relax', 
        'dinner', 'night', 'party'
    ]
}
```

**⏰ Günlük Işık Döngüsü:**
- **06:00-09:00:** Sıcak beyaz (2700K) - Yumuşak uyanış
- **09:00-17:00:** Soğuk beyaz (5000K) - Aktif çalışma
- **17:00-21:00:** Nötr beyaz (3500K) - Akşam konforu
- **21:00-23:00:** Sıcak sarı (2200K) - Uyku hazırlığı

### 3. 🪟 Akıllı Perde Sistemi (9 Adet)

**📋 Motor Özellikleri:**
- **Motor Tipi:** Step motor (24V DC)
- **Torque:** 50 Nm
- **Hız:** 15 cm/saniye
- **Gürültü Seviyesi:** <35 dB
- **Pozisyon Hassasiyeti:** ±1%
- **Pil Yedekleme:** 72 saat

**🎛️ Kontrol Modları:**
```python
curtain_control = {
    'positions': (0, 100),            # % açıklık
    'tilt_angle': (-90, 90),          # derece
    'operation_modes': [
        'manual',      # Manuel kontrol
        'timer',       # Zamanlama
        'light_sensor', # Işık bazlı
        'temperature', # Sıcaklık bazlı
        'privacy'      # Gizlilik modu
    ]
}
```

**🌅 Otomatik Programlar:**
- **Sabah (07:00):** %80 açık - Doğal ışık
- **Öğle (12:00):** Güneş açısına göre ayar
- **Akşam (19:00):** %50 açık - Gizlilik
- **Gece (22:00):** Tamamen kapalı - Karanlık

### 4. 🌬️ Havalandırma Sistemi (2 Adet)

**📋 Fan Özellikleri:**
| Konum | Tip | Kapasite | Gürültü | Enerji |
|-------|-----|----------|---------|--------|
| Mutfak | Aspiratör | 650 m³/h | 45 dB | 150W |
| Banyo | Banyo fanı | 180 m³/h | 35 dB | 25W |

**⚙️ Akıllı Havalandırma:**
```python
ventilation_control = {
    'speed_levels': [0, 25, 50, 75, 100],  # %
    'auto_activation': {
        'co2_threshold': 800,               # ppm
        'humidity_threshold': 70,           # %
        'odor_detection': True,            # koku sensörü
        'timer_control': True              # zamanlama
    },
    'energy_recovery': True,               # enerji geri kazanım
    'filter_monitoring': True             # filtre takibi
}
```

## 📊 Veri Toplama ve İletişim

### 🌐 İletişim Protokolleri
```python
communication_stack = {
    'wifi': 'IEEE 802.11 b/g/n',
    'zigbee': 'IEEE 802.15.4',
    'bluetooth': 'BLE 5.0',
    'mqtt_broker': 'Eclipse Mosquitto',
    'data_format': 'JSON',
    'encryption': 'AES-256'
}
```

### 📡 Veri Toplama Döngüsü
```python
data_collection = {
    'sampling_rate': 5,              # dakika
    'buffer_size': 288,              # günlük veri
    'transmission': 'real_time',      # gerçek zamanlı
    'backup_interval': 60,            # dakika
    'compression': 'gzip',           # sıkıştırma
    'error_detection': 'CRC32'       # hata kontrolü
}
```

### 🔄 Veri Formatı (JSON)
```json
{
    "timestamp": "2025-06-24T09:44:19Z",
    "room": "Salon",
    "sensors": {
        "temperature": 23.5,
        "humidity": 45.2,
        "co2": 650,
        "light": 320,
        "motion": true,
        "occupancy": true
    },
    "devices": {
        "ac": {"state": false, "temp": 24, "mode": "auto"},
        "lights": {"state": true, "brightness": 80},
        "curtains": {"position": 75, "tilt": 0}
    },
    "metadata": {
        "battery_level": 95,
        "signal_strength": -45,
        "last_calibration": "2025-06-20T12:00:00Z"
    }
}
```

## 🔧 Kalibrasyon ve Bakım

### 🎯 Kalibrasyon Programı
| Sensör | Kalibrasyon Sıklığı | Yöntem | Doğruluk Hedefi |
|--------|-------------------|--------|-----------------|
| Sıcaklık | 6 ay | Referans termometre | ±0.3°C |
| Nem | 3 ay | Tuz çözeltisi | ±2% RH |
| CO2 | 12 ay | Otomatik (ABC) | ±30 ppm |
| Işık | 12 ay | Lüx metre | ±15% |

### 🔋 Güç Yönetimi
```python
power_management = {
    'battery_backup': {
        'capacity': '2000 mAh',
        'backup_time': '72 hours',
        'charging': 'USB-C PD'
    },
    'energy_saving': {
        'sleep_mode': True,
        'wake_on_motion': True,
        'adaptive_sampling': True
    }
}
```

### 📊 Performans İzleme
```python
health_monitoring = {
    'sensor_drift': 'Haftalık kontrol',
    'communication_errors': 'Gerçek zamanlı',
    'battery_status': 'Günlük',
    'calibration_due': 'Otomatik uyarı',
    'maintenance_alerts': 'Proaktif'
}
```

## 🔮 Gelecek Geliştirmeler

### 📡 Yeni Sensörler (Planlanan)
- **🏃 Radar Sensörü:** Nefes ve nabız algılama
- **🌬️ Hava Kalitesi:** PM2.5, PM10, VOC
- **🔊 Ses Sensörü:** Gürültü seviyesi, ses analizi
- **📶 WiFi Algılama:** Cihaz varlığı tespiti
- **🌡️ Kızılötesi:** Yüzey sıcaklığı ölçümü

### 🤖 AI Geliştirmeleri
- **Prediktif Analiz:** Arıza öncesi uyarı
- **Adaptif Öğrenme:** Kişisel tercihleri öğrenme
- **Anomali Tespiti:** Anormal durumları algılama
- **Optimizasyon:** Enerji kullanımı minimizasyonu

---

Bu dokümantasyon, sistemin gerçek teknik kapasitelerini yansıtmakta ve sürekli güncellenmektedir. Detaylı performans metrikleri için `reports/` klasöründeki güncel raporları inceleyin.
- **Normal (30%-60%):** İdeal nem seviyesi
- **Yüksek (>60%):** Çok nemli, nem alma gerekli

### 3. CO2 Sensörü

**Özellikler:**
- **Ölçüm Aralığı:** 400 ppm ile 5000 ppm
- **Doğruluk:** ±50 ppm
- **Çözünürlük:** 1 ppm
- **Örnekleme Hızı:** 5 dakika
- **Veri Formatı:** Parçacık/milyon (ppm)

**Veri Yorumlama:**
- **Normal (<1000 ppm):** İyi hava kalitesi
- **Orta (1000-2000 ppm):** Orta hava kalitesi, havalandırma düşünülmeli
- **Yüksek (>2000 ppm):** Kötü hava kalitesi, hemen havalandırma gerekli

### 4. Işık Sensörü

**Özellikler:**
- **Ölçüm Aralığı:** 0 lux ile 10,000 lux
- **Doğruluk:** ±5%
- **Çözünürlük:** 1 lux
- **Örnekleme Hızı:** 5 dakika
- **Veri Formatı:** Lüks (lux)

**Veri Yorumlama:**
- **Düşük (<100 lux):** Karanlık, aydınlatma gerekli
- **Orta (100-500 lux):** Orta aydınlık
- **Yüksek (>500 lux):** Yeterli doğal aydınlatma

### 5. Hareket Sensörü

**Özellikler:**
- **Algılama Mesafesi:** 5 metre
- **Algılama Açısı:** 120°
- **Tepki Süresi:** <1 saniye
- **Veri Formatı:** Boolean (True/False)

**Veri Yorumlama:**
- **True:** Hareket algılandı
- **False:** Hareket algılanmadı

## Cihazlar

### 1. Klima

**Özellikler:**
- **Çalışma Modları:** Soğutma, Isıtma, Nem Alma, Fan
- **Sıcaklık Ayarı:** 16°C ile 30°C
- **Güç Tüketimi:** 0.8-2.5 kW (moda bağlı)
- **Kontrol Arayüzü:** Açma/Kapama, Sıcaklık Ayarı, Mod Seçimi

**Kontrol Komutları:**
```python
# Klima açma
device.set_state("Klima", True)

# Sıcaklık ayarlama
device.set_temperature("Klima", 22)

# Mod değiştirme
device.set_mode("Klima", "cooling")
```

### 2. Lamba

**Özellikler:**
- **Güç:** 5-15W (LED)
- **Parlaklık Ayarı:** %0-%100
- **Renk Sıcaklığı:** 2700K-6500K
- **Kontrol Arayüzü:** Açma/Kapama, Parlaklık Ayarı, Renk Ayarı

**Kontrol Komutları:**
```python
# Lamba açma
device.set_state("Lamba", True)

# Parlaklık ayarlama
device.set_brightness("Lamba", 75)  # %75 parlaklık

# Renk sıcaklığı ayarlama
device.set_color_temperature("Lamba", 3500)  # 3500K
```

### 3. Perde

**Özellikler:**
- **Hareket Türü:** Motorlu
- **Pozisyon Aralığı:** %0 (tamamen kapalı) ile %100 (tamamen açık)
- **Güç Tüketimi:** 10-30W (hareket sırasında)
- **Kontrol Arayüzü:** Açma/Kapama, Pozisyon Ayarı

**Kontrol Komutları:**
```python
# Perdeyi aç
device.set_state("Perde", True)  # Tamamen aç

# Perdeyi kapat
device.set_state("Perde", False)  # Tamamen kapat

# Kısmi pozisyon ayarı
device.set_position("Perde", 50)  # %50 açık
```

### 4. Havalandırma

**Özellikler:**
- **Fan Hızı:** 1-5 kademeli
- **Güç Tüketimi:** 15-75W (hıza bağlı)
- **Gürültü Seviyesi:** 25-45 dB (hıza bağlı)
- **Kontrol Arayüzü:** Açma/Kapama, Fan Hızı Ayarı

**Kontrol Komutları:**
```python
# Havalandırma açma
device.set_state("Havalandirma", True)

# Fan hızını ayarlama
device.set_fan_speed("Havalandirma", 3)  # 1-5 arası
```

## Sensör-Cihaz İlişkileri

| Sensör | İlişkili Cihazlar | Mantık |
|--------|-------------------|--------|
| Sıcaklık | Klima | Sıcaklık > 24°C ise klima soğutma modunda çalıştır |
| Nem | Klima, Havalandırma | Nem > %60 ise klima nem alma modunda çalıştır |
| CO2 | Havalandırma | CO2 > 1000 ppm ise havalandırmayı çalıştır |
| Işık | Lamba, Perde | Işık < 100 lux ve hareket varsa lambayı aç; Işık > 500 lux ise perdeleri kapat |
| Hareket | Lamba | Hareket algılandığında ve ışık yetersizse lambayı aç, 15 dakika hareket olmazsa kapat |

## Veri Akışı Diyagramı

```
[Sensörler] --> [Veri İşleme] --> [Karar Motoru] --> [Cihaz Kontrolü]
     ^                                  ^
     |                                  |
     +----------------------------------+
          Geribildirim ve Öğrenme
```