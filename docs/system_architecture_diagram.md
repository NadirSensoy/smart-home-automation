# Sistem Mimarisi ve Akış Diyagramları

Bu doküman, Akıllı Ev Otomasyon Sistemi'nin mimari yapısını ve ana bileşenler arasındaki veri akışını görsel olarak sunmaktadır.

## Sistem Mimarisi

Aşağıdaki diyagram, sistemin genel mimarisini ve ana bileşenler arasındaki ilişkileri göstermektedir:

```
+-----------------------------------------------------+
|                                                     |
|                 AKILLI EV OTOMASYON SİSTEMİ         |
|                                                     |
+-----------------------------------------------------+
           |                  |                 |
           v                  v                 v
+------------------+ +------------------+ +------------------+
|                  | |                  | |                  |
|  Veri Yönetimi   | |  Model Yönetimi  | | Otomasyon Motoru |
|                  | |                  | |                  |
+------------------+ +------------------+ +------------------+
    |         |           |        |           |         |
    v         v           v        v           v         v
+-------+ +--------+ +--------+ +--------+ +-------+ +--------+
|       | |        | |        | |        | |       | |        |
| Sensör| |  Veri  | |   ML   | | Model  | | Kural | | Cihaz  |
| Verisi| |İşleme  | |Modelleri| |Tahminleri| |Motoru | |Kontrolü|
|       | |        | |        | |        | |       | |        |
+-------+ +--------+ +--------+ +--------+ +-------+ +--------+
```

## Veri Akışı Diyagramı

Veri akışı aşağıdaki diyagramda detaylandırılmıştır:

```
+--------+    +--------+    +-------+    +--------+
|        |    |        |    |       |    |        |
|Sensörler|--->|  Veri  |--->|  ML   |--->|Tahminler|
|        |    |İşleme  |    |Modeli |    |        |
+--------+    +--------+    +-------+    +--------+
                                            |
                                            v
+--------+    +--------+    +--------+    +--------+
|        |    |        |    |        |    |        |
|Cihazlar|<---|Kontrol |<---|  Kural |<---|Kullanıcı|
|        |    |Komutları|    |Motoru |    |Tercihleri|
+--------+    +--------+    +--------+    +--------+
```

## Veri İşleme Pipeline'ı

Veri işleme pipeline'ı aşağıdaki adımlardan oluşur:

```
+-------+    +-------+    +--------+    +--------+    +--------+
|       |    |       |    |        |    |        |    |        |
|Ham Veri|--->|Temizleme|--->|Özellik |--->|Veri Split|--->|Ölçekleme|
|       |    |       |    |Mühendisliği|    |        |    |        |
+-------+    +-------+    +--------+    +--------+    +--------+
                                                         |
                                                         v
                                                    +--------+
                                                    |        |
                                                    | Model  |
                                                    |Eğitimi |
                                                    |        |
                                                    +--------+
```

## Otomasyon Karar Süreci

Otomasyon sistemi, kararlarını aşağıdaki süreçte verir:

```
                        +-------------+
                        |             |
                        | Başlangıç   |
                        |             |
                        +------+------+
                               |
                               v
                   +-------------------------+
                   |                         |
                   | Sensör Verileri Toplama |
                   |                         |
                   +-----------+-------------+
                               |
                               v
                   +-------------------------+
                   |                         |
                   | ML Modeli Tahmin Yapma  |
                   |                         |
                   +-----------+-------------+
                               |
                               v
                   +-------------------------+
                   |                         |
                   | Kuralları Değerlendirme |
                   |                         |
                   +-----------+-------------+
                               |
                               v
              +-----------------------------+
              |                             |
              | Cihaz Durumlarını Güncelleme|
              |                             |
              +--------------+--------------+
                             |
                             v
                   +--------------------+
                   |                    |
                   | Kararı Loglama     |
                   |                    |
                   +--------------------+
```

## Bileşen Etkileşim Diyagramı

Sistemdeki ana bileşenlerin birbirleriyle etkileşimi:

```
+-------------+           +--------------+          +---------------+
|             |  veriler  |              | tahminler |               |
|  Sensörler  +---------->+ ML Modelleri +---------->+ Kural Motoru  |
|             |           |              |           |               |
+-------------+           +--------------+           +-------+-------+
                                                            |
                                                            | komutlar
                                                            v
+-------------+           +--------------+          +---------------+
|             |  geribildirim            |  durumlar|               |
| Kullanıcı   |<----------+ Raporlama    |<---------+ Cihazlar      |
|             |           |              |          |               |
+-------------+           +--------------+          +---------------+
```

## Yazılım Katmanları

Sistemin yazılım katmanları aşağıdaki gibi organize edilmiştir:

```
+---------------------------------------------------------------+
|                                                               |
|                         Uygulama Katmanı                      |
|                                                               |
+---------------------------------------------------------------+
                |                  |                |
                v                  v                v
+---------------------------+ +------------+ +------------------+
|                           | |            | |                  |
|      Veri Katmanı         | | ML Katmanı | | Otomasyon Katmanı|
|                           | |            | |                  |
+---------------------------+ +------------+ +------------------+
                |                  |                |
                v                  v                v
+---------------------------------------------------------------+
|                                                               |
|                     Altyapı Katmanı                           |
|                                                               |
+---------------------------------------------------------------+
```

## Dosya Yapısı

Projenin dosya yapısı aşağıdaki gibidir:

```
smart-home-automation/
├── app.py                    # Ana uygulama dosyası
├── setup.py                  # Kurulum dosyası
├── requirements.txt          # Bağımlılıklar
├── README.md                 # Proje bilgisi
├── src/                      # Kaynak kodları
│   ├── data_simulation/      # Veri simülasyonu
│   ├── data_processing/      # Veri işleme
│   ├── models/               # ML modelleri
│   ├── automation/           # Otomasyon sistemi
│   ├── simulation/           # Simülasyon araçları
│   └── utils/                # Yardımcı işlevler
├── data/                     # Veri dosyaları
│   ├── raw/                  # Ham veri
│   └── processed/            # İşlenmiş veri
├── models/                   # Eğitilmiş modeller
│   └── trained/              # Kaydedilmiş model dosyaları
├── reports/                  # Raporlar
├── logs/                     # Log dosyaları
└── tests/                    # Test dosyaları
```

## Ölçeklendirme ve Genişleme Planı

Sistemin ölçeklendirilmesi ve genişletilmesi aşağıdaki diyagramda gösterilmektedir:

```
                Mevcut Sistem
                      |
        +-------------+-------------+
        |                           |
+---------------+           +----------------+
|               |           |                |
|  Çoklu Ev     |           |   Web/Mobil    |
|  Desteği      |           |   Arayüz       |
|               |           |                |
+---------------+           +----------------+
        |                           |
+---------------+           +----------------+
|               |           |                |
|  Bulut        |           |   API          |
|  Entegrasyonu |           |   Servisleri   |
|               |           |                |
+---------------+           +----------------+
        |                           |
        +-------------+-------------+
                      |
             Genişletilmiş Sistem
```

Bu mimari dokümantasyon, sistem bileşenlerinin nasıl bir araya geldiğini ve çalıştığını görsel olarak açıklar. Sistemin her bir parçasının birbirleriyle nasıl etkileşim kurduğunu gösterir ve gelecekteki genişleme planlarını ortaya koyar.