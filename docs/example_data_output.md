# Örnek Veri ve Sistem Çıktıları

Bu doküman, Akıllı Ev Otomasyon Sistemi'nin çalışmasını daha iyi anlamak için örnek veri setleri ve sistem tarafından üretilen çıktıları göstermektedir.

## 1. Sensör Veri Örnekleri

### Ham Sensör Verisi

Aşağıda, sistemin işlediği ham sensör verilerinden bir örnek bulunmaktadır:

```csv
timestamp,Salon_Sıcaklık,Salon_Nem,Salon_CO2,Salon_Işık,Salon_Hareket,Salon_Doluluk,Yatak Odası_Sıcaklık,Yatak Odası_Nem,Yatak Odası_CO2,Yatak Odası_Işık,Yatak Odası_Hareket,Yatak Odası_Doluluk,Mutfak_Sıcaklık,Mutfak_Nem,Mutfak_CO2,Mutfak_Işık,Mutfak_Hareket,Mutfak_Doluluk,Banyo_Sıcaklık,Banyo_Nem,Banyo_CO2,Banyo_Işık,Banyo_Hareket,Banyo_Doluluk,Salon_Klima,Salon_Lamba,Salon_Perde,Salon_Havalandırma,Yatak Odası_Klima,Yatak Odası_Lamba,Yatak Odası_Perde,Yatak Odası_Havalandırma,Mutfak_Klima,Mutfak_Lamba,Mutfak_Perde,Mutfak_Havalandırma,Banyo_Klima,Banyo_Lamba,Banyo_Perde,Banyo_Havalandırma,Kişi_1_Konum,Kişi_2_Konum,Kişi_3_Konum
2025-05-27 08:05:00,22.5,45.2,650,320,True,True,23.1,50.3,520,15,False,False,21.8,52.1,580,250,False,False,22.7,65.8,510,10,False,False,False,True,True,False,False,False,False,False,False,False,True,False,False,False,False,False,Salon,None,None
2025-05-27 08:10:00,22.7,45.5,655,350,True,True,23.0,50.1,525,18,False,False,21.9,51.8,585,280,True,True,22.6,66.0,515,12,False,False,False,True,True,False,False,False,False,False,False,True,True,False,False,False,False,False,Salon,Mutfak,None
2025-05-27 08:15:00,22.9,46.0,660,380,True,True,22.9,49.8,530,20,False,False,22.1,51.5,595,300,True,True,22.5,65.5,520,15,False,False,False,True,True,False,False,False,False,False,False,True,True,False,False,False,False,False,Salon,Mutfak,None
```

### İşlenmiş Sensör Verisi

Ham veri işlendikten sonra, özellik mühendisliği uygulanarak aşağıdaki gibi genişletilmiş bir veri seti elde edilir:

```csv
timestamp,Salon_Sıcaklık,Salon_Nem,Salon_CO2,Salon_Işık,Salon_Hareket,Salon_Doluluk,hour,minute,day_of_week,is_weekend,time_period,Salon_Hareket_Son1Saat,Salon_Doluluk_Oran,Salon_SonHareket_Dakika,Salon_Sıcaklık_Değişim,Salon_Nem_Değişim,Salon_CO2_Değişim,Salon_Işık_Değişim,Salon_Klima
2025-05-27 08:05:00,22.5,45.2,650,320,True,True,8,5,1,0,Sabah,10,0.83,0,0.0,0.0,0.0,0.0,False
2025-05-27 08:10:00,22.7,45.5,655,350,True,True,8,10,1,0,Sabah,11,0.92,0,0.2,0.3,5.0,30.0,False
2025-05-27 08:15:00,22.9,46.0,660,380,True,True,8,15,1,0,Sabah,12,1.00,0,0.2,0.5,5.0,30.0,False
```

## 2. ML Model Girdileri ve Çıktıları

### Model Girdi Örneği

Makine öğrenmesi modeline verilen girdi örneği:

```python
{
    'hour': 8,
    'minute': 15,
    'day_of_week': 1,
    'is_weekend': 0,
    'time_period': 'Sabah',
    'Salon_Sıcaklık': 22.9,
    'Salon_Nem': 46.0,
    'Salon_CO2': 660,
    'Salon_Işık': 380,
    'Salon_Hareket': True,
    'Salon_Doluluk': True,
    'Salon_Hareket_Son1Saat': 12,
    'Salon_Doluluk_Oran': 1.0,
    'Salon_SonHareket_Dakika': 0,
    'Salon_Sıcaklık_Değişim': 0.2,
    'Salon_Nem_Değişim': 0.5,
    'Salon_CO2_Değişim': 5.0,
    'Salon_Işık_Değişim': 30.0
}
```

### Model Tahmin Çıktısı

Modelin, Salon_Klima için verdiği tahmin çıktısı:

```python
{
    'state': False,  # Klima kapalı kalmalı
    'probability': 0.95  # %95 güven düzeyi
}
```

## 3. Kural Motoru Kararı Örneği

### Durum Bilgisi

Kural motoru değerlendirmesi için durum bilgisi:

```python
{
    'room': 'Salon',
    'timestamp': datetime(2025, 5, 27, 14, 30, 0),
    'Salon_Sıcaklık': 27.5,
    'Salon_Nem': 55.2,
    'Salon_CO2': 750,
    'Salon_Işık': 450,
    'Salon_Hareket': True,
    'Salon_Doluluk': True,
    'hour': 14,
    'minute': 30,
    'day_of_week': 1,
    'is_weekend': 0,
    'time_period': 'Gündüz',
    'ml_predictions': {
        'Salon_Klima': {'state': True, 'probability': 0.88}
    }
}
```

### Cihaz Durumları (Öncesi)

```python
{
    'Salon_Klima': False,
    'Salon_Lamba': False,
    'Salon_Perde': True,
    'Salon_Havalandırma': False
}
```

### Kural Değerlendirmesi

```
Kural "high_temp_cooling" değerlendiriliyor:
- Koşul: Salon_Sıcaklık > 26.0
- Değer: 27.5
- Sonuç: True (Koşul sağlandı)
- Eylem: Salon_Klima = True

Kural "ml_predictions" değerlendiriliyor:
- Koşul: prediction_confidence > 0.7
- Değer: 0.88
- Sonuç: True (Koşul sağlandı)
- Eylem: Salon_Klima = True
```

### Cihaz Durumları (Sonrası)

```python
{
    'Salon_Klima': True,  # Değişti
    'Salon_Lamba': False,
    'Salon_Perde': True,
    'Salon_Havalandırma': False
}
```

### Karar Logu

```json
{
  "timestamp": "2025-05-27 14:30:00",
  "rule_name": "high_temp_cooling",
  "description": "Sıcaklık 26°C'yi geçtiğinde klimayı aç",
  "room": "Salon",
  "conditions": {
    "Salon_Sıcaklık": 27.5,
    "Salon_Doluluk": true
  },
  "before_state": {
    "Salon_Klima": false
  },
  "changes": {
    "Salon_Klima": true
  },
  "confidence": 1.0,
  "triggered_by": "rule_engine"
}
```

## 4. Model Performans Raporu

### Doğruluk Metrikleri

```
Model: Salon_Klima (Random Forest)
===================================
Doğruluk (Accuracy): 0.9356
Kesinlik (Precision): 0.9112
Duyarlılık (Recall): 0.9478
F1 Skoru: 0.9291
AUC: 0.9725
```

### Karmaşıklık Matrisi

```
[[324  18]
 [ 25 233]]
```

### Özellik Önemi Grafiği

En önemli 10 özellik:

```
1. hour: 0.3245
2. Salon_Sıcaklık: 0.2876
3. Salon_Doluluk: 0.1567
4. day_of_week: 0.0932
5. time_period_Gündüz: 0.0456
6. Salon_Doluluk_Oran: 0.0345
7. is_weekend: 0.0298
8. Salon_Sıcaklık_Değişim: 0.0187
9. Salon_Hareket_Son1Saat: 0.0132
10. Salon_CO2: 0.0098
```

## 5. Simülasyon Çıktısı

### Simülasyon Adımı Örneği

```
Simülasyon Adımı: 45
Zaman: 2025-05-27 10:20:00

Sensör Değerleri:
----------------
Salon:
- Sıcaklık: 24.8°C
- Nem: 47.5%
- CO2: 720 ppm
- Işık: 480 lux
- Hareket: Var
- Doluluk: Dolu

Yatak Odası:
- Sıcaklık: 23.2°C
- Nem: 51.0%
- CO2: 550 ppm
- Işık: 120 lux
- Hareket: Yok
- Doluluk: Boş

Cihaz Durumları:
---------------
Salon:
- Klima: Kapalı
- Lamba: Kapalı
- Perde: Açık
- Havalandırma: Kapalı

Yatak Odası:
- Klima: Kapalı
- Lamba: Kapalı
- Perde: Açık
- Havalandırma: Kapalı

Ev Sakinleri:
------------
- Kişi 1: Salon
- Kişi 2: Dışarıda
- Kişi 3: Dışarıda

ML Tahminleri ve Kararlar:
------------------------
Salon_Klima: Kapalı kalmalı (Güven: %92)
Salon_Lamba: Kapalı kalmalı (Güven: %88)
Salon_Perde: Açık kalmalı (Güven: %95)

Tetiklenen Kural:
---------------
Kural: morning_routine
Açıklama: Sabah rutini: perdeleri aç, gerekirse ısıtmayı aç
```

## 6. Enerji Tasarrufu Raporu

```
7 Günlük Enerji Kullanım Özeti:
==============================
Toplam Enerji Tüketimi:
- Otomasyonlu: 24.6 kWh
- Manuel (Tahmini): 38.2 kWh
- Tasarruf: 13.6 kWh (%35.6)

Cihaz Bazında Tasarruf:
---------------------
- Klimalar: 8.2 kWh (%47.1)
- Lambalar: 4.1 kWh (%34.2)
- Havalandırma: 1.3 kWh (%21.7)
```

## 7. Kullanıcı Davranış Analizi

```
Kullanıcı Tercih Analizi:
=======================
- En çok kullanılan oda: Salon (günde ort. 5.2 saat)
- En çok açılan cihaz: Salon_Lamba (günde ort. 6.1 saat)
- En aktif zaman dilimi: Akşam (17:00-22:00)
- En sık manuel müdahale: Salon_Klima (haftada 4 kez)

Haftalık Alışkanlık Paterni:
--------------------------
- Sabah (06:00-09:00): Mutfak aktivitesi yüksek
- Gündüz (09:00-17:00): Ev genellikle boş
- Akşam (17:00-22:00): Salon kullanımı yoğun
- Gece (22:00-06:00): Yatak odası aktivitesi
```

Bu örnekler, Akıllı Ev Otomasyon Sistemi'nin nasıl çalıştığını ve farklı modüllerin nasıl etk# filepath: c:\Users\ndr20\Desktop\b.tasarım\smart-home-automation\docs\example_data_output.md
# Örnek Veri ve Sistem Çıktıları

Bu doküman, Akıllı Ev Otomasyon Sistemi'nin çalışmasını daha iyi anlamak için örnek veri setleri ve sistem tarafından üretilen çıktıları göstermektedir.

## 1. Sensör Veri Örnekleri

### Ham Sensör Verisi

Aşağıda, sistemin işlediği ham sensör verilerinden bir örnek bulunmaktadır:

```csv
timestamp,Salon_Sıcaklık,Salon_Nem,Salon_CO2,Salon_Işık,Salon_Hareket,Salon_Doluluk,Yatak Odası_Sıcaklık,Yatak Odası_Nem,Yatak Odası_CO2,Yatak Odası_Işık,Yatak Odası_Hareket,Yatak Odası_Doluluk,Mutfak_Sıcaklık,Mutfak_Nem,Mutfak_CO2,Mutfak_Işık,Mutfak_Hareket,Mutfak_Doluluk,Banyo_Sıcaklık,Banyo_Nem,Banyo_CO2,Banyo_Işık,Banyo_Hareket,Banyo_Doluluk,Salon_Klima,Salon_Lamba,Salon_Perde,Salon_Havalandırma,Yatak Odası_Klima,Yatak Odası_Lamba,Yatak Odası_Perde,Yatak Odası_Havalandırma,Mutfak_Klima,Mutfak_Lamba,Mutfak_Perde,Mutfak_Havalandırma,Banyo_Klima,Banyo_Lamba,Banyo_Perde,Banyo_Havalandırma,Kişi_1_Konum,Kişi_2_Konum,Kişi_3_Konum
2025-05-27 08:05:00,22.5,45.2,650,320,True,True,23.1,50.3,520,15,False,False,21.8,52.1,580,250,False,False,22.7,65.8,510,10,False,False,False,True,True,False,False,False,False,False,False,False,True,False,False,False,False,False,Salon,None,None
2025-05-27 08:10:00,22.7,45.5,655,350,True,True,23.0,50.1,525,18,False,False,21.9,51.8,585,280,True,True,22.6,66.0,515,12,False,False,False,True,True,False,False,False,False,False,False,True,True,False,False,False,False,False,Salon,Mutfak,None
2025-05-27 08:15:00,22.9,46.0,660,380,True,True,22.9,49.8,530,20,False,False,22.1,51.5,595,300,True,True,22.5,65.5,520,15,False,False,False,True,True,False,False,False,False,False,False,True,True,False,False,False,False,False,Salon,Mutfak,None
```

### İşlenmiş Sensör Verisi

Ham veri işlendikten sonra, özellik mühendisliği uygulanarak aşağıdaki gibi genişletilmiş bir veri seti elde edilir:

```csv
timestamp,Salon_Sıcaklık,Salon_Nem,Salon_CO2,Salon_Işık,Salon_Hareket,Salon_Doluluk,hour,minute,day_of_week,is_weekend,time_period,Salon_Hareket_Son1Saat,Salon_Doluluk_Oran,Salon_SonHareket_Dakika,Salon_Sıcaklık_Değişim,Salon_Nem_Değişim,Salon_CO2_Değişim,Salon_Işık_Değişim,Salon_Klima
2025-05-27 08:05:00,22.5,45.2,650,320,True,True,8,5,1,0,Sabah,10,0.83,0,0.0,0.0,0.0,0.0,False
2025-05-27 08:10:00,22.7,45.5,655,350,True,True,8,10,1,0,Sabah,11,0.92,0,0.2,0.3,5.0,30.0,False
2025-05-27 08:15:00,22.9,46.0,660,380,True,True,8,15,1,0,Sabah,12,1.00,0,0.2,0.5,5.0,30.0,False
```

## 2. ML Model Girdileri ve Çıktıları

### Model Girdi Örneği

Makine öğrenmesi modeline verilen girdi örneği:

```python
{
    'hour': 8,
    'minute': 15,
    'day_of_week': 1,
    'is_weekend': 0,
    'time_period': 'Sabah',
    'Salon_Sıcaklık': 22.9,
    'Salon_Nem': 46.0,
    'Salon_CO2': 660,
    'Salon_Işık': 380,
    'Salon_Hareket': True,
    'Salon_Doluluk': True,
    'Salon_Hareket_Son1Saat': 12,
    'Salon_Doluluk_Oran': 1.0,
    'Salon_SonHareket_Dakika': 0,
    'Salon_Sıcaklık_Değişim': 0.2,
    'Salon_Nem_Değişim': 0.5,
    'Salon_CO2_Değişim': 5.0,
    'Salon_Işık_Değişim': 30.0
}
```

### Model Tahmin Çıktısı

Modelin, Salon_Klima için verdiği tahmin çıktısı:

```python
{
    'state': False,  # Klima kapalı kalmalı
    'probability': 0.95  # %95 güven düzeyi
}
```

## 3. Kural Motoru Kararı Örneği

### Durum Bilgisi

Kural motoru değerlendirmesi için durum bilgisi:

```python
{
    'room': 'Salon',
    'timestamp': datetime(2025, 5, 27, 14, 30, 0),
    'Salon_Sıcaklık': 27.5,
    'Salon_Nem': 55.2,
    'Salon_CO2': 750,
    'Salon_Işık': 450,
    'Salon_Hareket': True,
    'Salon_Doluluk': True,
    'hour': 14,
    'minute': 30,
    'day_of_week': 1,
    'is_weekend': 0,
    'time_period': 'Gündüz',
    'ml_predictions': {
        'Salon_Klima': {'state': True, 'probability': 0.88}
    }
}
```

### Cihaz Durumları (Öncesi)

```python
{
    'Salon_Klima': False,
    'Salon_Lamba': False,
    'Salon_Perde': True,
    'Salon_Havalandırma': False
}
```

### Kural Değerlendirmesi

```
Kural "high_temp_cooling" değerlendiriliyor:
- Koşul: Salon_Sıcaklık > 26.0
- Değer: 27.5
- Sonuç: True (Koşul sağlandı)
- Eylem: Salon_Klima = True

Kural "ml_predictions" değerlendiriliyor:
- Koşul: prediction_confidence > 0.7
- Değer: 0.88
- Sonuç: True (Koşul sağlandı)
- Eylem: Salon_Klima = True
```

### Cihaz Durumları (Sonrası)

```python
{
    'Salon_Klima': True,  # Değişti
    'Salon_Lamba': False,
    'Salon_Perde': True,
    'Salon_Havalandırma': False
}
```

### Karar Logu

```json
{
  "timestamp": "2025-05-27 14:30:00",
  "rule_name": "high_temp_cooling",
  "description": "Sıcaklık 26°C'yi geçtiğinde klimayı aç",
  "room": "Salon",
  "conditions": {
    "Salon_Sıcaklık": 27.5,
    "Salon_Doluluk": true
  },
  "before_state": {
    "Salon_Klima": false
  },
  "changes": {
    "Salon_Klima": true
  },
  "confidence": 1.0,
  "triggered_by": "rule_engine"
}
```

## 4. Model Performans Raporu

### Doğruluk Metrikleri

```
Model: Salon_Klima (Random Forest)
===================================
Doğruluk (Accuracy): 0.9356
Kesinlik (Precision): 0.9112
Duyarlılık (Recall): 0.9478
F1 Skoru: 0.9291
AUC: 0.9725
```

### Karmaşıklık Matrisi

```
[[324  18]
 [ 25 233]]
```

### Özellik Önemi Grafiği

En önemli 10 özellik:

```
1. hour: 0.3245
2. Salon_Sıcaklık: 0.2876
3. Salon_Doluluk: 0.1567
4. day_of_week: 0.0932
5. time_period_Gündüz: 0.0456
6. Salon_Doluluk_Oran: 0.0345
7. is_weekend: 0.0298
8. Salon_Sıcaklık_Değişim: 0.0187
9. Salon_Hareket_Son1Saat: 0.0132
10. Salon_CO2: 0.0098
```

## 5. Simülasyon Çıktısı

### Simülasyon Adımı Örneği

```
Simülasyon Adımı: 45
Zaman: 2025-05-27 10:20:00

Sensör Değerleri:
----------------
Salon:
- Sıcaklık: 24.8°C
- Nem: 47.5%
- CO2: 720 ppm
- Işık: 480 lux
- Hareket: Var
- Doluluk: Dolu

Yatak Odası:
- Sıcaklık: 23.2°C
- Nem: 51.0%
- CO2: 550 ppm
- Işık: 120 lux
- Hareket: Yok
- Doluluk: Boş

Cihaz Durumları:
---------------
Salon:
- Klima: Kapalı
- Lamba: Kapalı
- Perde: Açık
- Havalandırma: Kapalı

Yatak Odası:
- Klima: Kapalı
- Lamba: Kapalı
- Perde: Açık
- Havalandırma: Kapalı

Ev Sakinleri:
------------
- Kişi 1: Salon
- Kişi 2: Dışarıda
- Kişi 3: Dışarıda

ML Tahminleri ve Kararlar:
------------------------
Salon_Klima: Kapalı kalmalı (Güven: %92)
Salon_Lamba: Kapalı kalmalı (Güven: %88)
Salon_Perde: Açık kalmalı (Güven: %95)

Tetiklenen Kural:
---------------
Kural: morning_routine
Açıklama: Sabah rutini: perdeleri aç, gerekirse ısıtmayı aç
```

## 6. Enerji Tasarrufu Raporu

```
7 Günlük Enerji Kullanım Özeti:
==============================
Toplam Enerji Tüketimi:
- Otomasyonlu: 24.6 kWh
- Manuel (Tahmini): 38.2 kWh
- Tasarruf: 13.6 kWh (%35.6)

Cihaz Bazında Tasarruf:
---------------------
- Klimalar: 8.2 kWh (%47.1)
- Lambalar: 4.1 kWh (%34.2)
- Havalandırma: 1.3 kWh (%21.7)
```

## 7. Kullanıcı Davranış Analizi

```
Kullanıcı Tercih Analizi:
=======================
- En çok kullanılan oda: Salon (günde ort. 5.2 saat)
- En çok açılan cihaz: Salon_Lamba (günde ort. 6.1 saat)
- En aktif zaman dilimi: Akşam (17:00-22:00)
- En sık manuel müdahale: Salon_Klima (haftada 4 kez)

Haftalık Alışkanlık Paterni:
--------------------------
- Sabah (06:00-09:00): Mutfak aktivitesi yüksek
- Gündüz (09:00-17:00): Ev genellikle boş
- Akşam (17:00-22:00): Salon kullanımı yoğun
- Gece (22:00-06:00): Yatak odası aktivitesi
```

Bu örnekler, Akıllı Ev Otomasyon Sistemi'nin nasıl çalıştığını ve farklı modüllerin nasıl etk