# Sensörler ve Cihazlar

Bu dokümanda, Akıllı Ev Otomasyon Sistemi'nde kullanılan tüm sensörlerin ve kontrol edilen cihazların teknik özellikleri, veri formatları ve çalışma prensipleri detaylı olarak açıklanmaktadır.

## Sensörler

### 1. Sıcaklık Sensörü

**Özellikler:**
- **Ölçüm Aralığı:** -40°C ile +80°C
- **Doğruluk:** ±0.5°C
- **Çözünürlük:** 0.1°C
- **Örnekleme Hızı:** 5 dakika
- **Veri Formatı:** Celsius derecesi (°C)

**Veri Yorumlama:**
- **Düşük (<18°C):** Oda ısıtılmalı
- **Normal (18°C-24°C):** Konforlu sıcaklık
- **Yüksek (>24°C):** Oda soğutulmalı

### 2. Nem Sensörü

**Özellikler:**
- **Ölçüm Aralığı:** %0 ile %100 RH
- **Doğruluk:** ±3% RH
- **Çözünürlük:** %1 RH
- **Örnekleme Hızı:** 5 dakika
- **Veri Formatı:** Bağıl nem yüzdesi (%)

**Veri Yorumlama:**
- **Düşük (<30%):** Çok kuru, nemlendirme gerekli
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