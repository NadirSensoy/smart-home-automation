# Akıllı Ev Otomasyon Sistemi

Makine öğrenmesi tabanlı akıllı ev otomasyon sistemi, ev içindeki sensör verilerini analiz ederek cihazların otomatik kontrolünü sağlar.

## Özellikler

- Sensör verilerinin gerçekçi simülasyonu
- Kullanıcı davranışlarını analiz eden makine öğrenmesi modelleri# Smart Home Automation

## Kurulum

Paket olarak geliştirici modunda kurmak için:
```bash
pip install -e .
```

## Kullanım

### Ana Uygulamayı Çalıştırma
Ana uygulamayı çalıştırmak için:
```bash
python app.py
```

### Çalıştırma Modları
Farklı modlarda çalıştırma seçenekleri:

```bash
# Sadece veri üretimi
python app.py --mode data --days 5

# Sadece model eğitimi 
python app.py --mode train --no-optimize

# Demo simülasyon modu
python app.py --mode simulate --steps 200

# İnteraktif simülasyon modu
python app.py --mode interactive

# Tüm süreçler (veri üretimi, model eğitimi, simülasyon)
python app.py --mode all
```

### Komut Satırı Parametreleri

| Parametre       | Açıklama                                            | Varsayılan Değer |
|-----------------|-----------------------------------------------------|-----------------|
| `--mode`        | Çalışma modu (data, train, simulate, interactive, all) | `all`           |
| `--days`        | Simüle edilecek gün sayısı                            | `3`             |
| `--steps`       | Simülasyon adım sayısı                               | `100`           |
| `--no-optimize` | Hiperparametre optimizasyonu yapma                  | `False`         |
| `--no-ml`       | Makine öğrenmesi modelini devre dışı bırak           | `False`         |

### İnteraktif Mod Kullanımı
İnteraktif mod başlatıldığında (`python app.py --mode interactive`), aşağıdaki komutları kullanabilirsiniz:

```
start [adım]     : Simülasyonu başlatır (opsiyonel: adım sayısı)
pause            : Simülasyonu duraklatır
resume           : Simülasyonu devam ettirir
stop             : Simülasyonu durdurur
speed [hız]      : Simülasyon hızını ayarlar (ör: 1.0, 2.0)
status           : Mevcut simülasyon durumunu gösterir
device [oda] [cihaz] [durum] : Cihaz durumunu değiştirir
                   Örnek: device Salon Lamba on
save             : Simülasyon geçmişini kaydeder
report           : Simülasyon raporu oluşturur
visualize        : Güncel durumu görselleştirir
exit             : Programdan çıkar
help             : Yardım mesajını gösterir
```

### İnteraktif Simülasyon Örnekleri

**Simülasyon Başlatma:**
```
>> start 100
```
Bu komut, 100 adımlık bir simülasyon başlatır.

**Cihaz Kontrolü:**
```
>> device Salon Lamba on
>> device Yatak Odası Klima off
```

**Raporlama:**
```
>> report
```
Bu komut, simülasyon verilerinden bir HTML raporu oluşturur ve otomatik olarak açar.

**Görselleştirme:**
```
>> visualize
```
Bu komut, evin mevcut durumunun bir görselleştirmesini oluşturur ve PNG dosyası olarak kaydeder.

## Görselleştirme ve Raporlama
Simülasyon sırasında ve sonrasında çeşitli görselleştirmeler oluşturulabilir:

*   **Gerçek Zamanlı Görselleştirme:** Simülasyon çalışırken oda sıcaklıkları, enerji kullanımı, cihaz durumları ve sensör değerleri gösterilir.

*   **Raporlar:**
    *   Sensör verileri zaman grafikleri
    *   Oda doluluk oranları
    *   Cihaz kullanım analizleri
    *   HTML özet raporları

*   **Veriler:**
    *   Simülasyon verileri CSV formatında kaydedilir
    *   Eğitilen modeller joblib formatında kaydedilir

Raporlar ve görselleştirmeler şu konumlarda bulunur:
*   `./reports/figures/`: Grafik PNG dosyaları
*   `./reports/simulation/`: HTML raporları
*   `./output/visualizations/`: Simülasyon görselleştirme dosyaları
*   `./data/simulation/`: Kaydedilen simülasyon verileri

## Proje Yapısı
```
smart-home-automation/
│
├── app.py                  # Ana uygulama dosyası
├── setup.py                # Kurulum dosyası
├── requirements.txt        # Bağımlılıklar
│
├── src/                    # Kaynak kodlar
│   ├── automation/         # Otomasyon motoru ve kurallar
│   │   └── rules_engine.py # Kural motoru
│   ├── data_processing/    # Veri işleme
│   │   └── preprocessing.py # Veri önişleme
│   ├── data_simulation/    # Veri simülasyonu
│   │   ├── data_generator.py # Ana veri üreteci
│   │   ├── sensor_simulator.py # Sensör simülasyonu
│   │   ├── user_simulator.py # Kullanıcı davranışı simülasyonu
│   │   └── weather_simulator.py # Hava durumu simülasyonu
│   ├── models/             # Makine öğrenmesi modelleri
│   │   ├── model_manager.py # Model yöneticisi
│   │   └── model_trainer.py # Model eğitimi
│   ├── simulation/         # Ev simülasyonu
│   │   ├── home_simulator.py # Ana simülasyon motoru
│   │   └── interactive.py # İnteraktif simülasyon
│   └── utils/              # Yardımcı modüller
│       ├── error_handling.py # Hata yönetimi
│       └── visualization.py # Görselleştirme araçları
│
├── logs/                   # Log dosyaları
├── data/                   # Veri dosyaları
│   ├── raw/                # Ham veri
│   ├── processed/          # İşlenmiş veri
│   └── simulation/         # Simülasyon sonuçları
├── models/                 # Eğitilmiş modeller
│   └── trained/            # Eğitilmiş cihaz modelleri
├── output/                 # Çıktı dosyaları
│   └── visualizations/     # Görselleştirmeler
└── reports/                # Raporlar
    ├── figures/            # Grafik çıktıları
    └── simulation/         # Simülasyon raporları
```

## Sorun Giderme

### Yaygın Sorunlar ve Çözümleri

*   **Matplotlib Hataları:**
    *   **Hata:** `main thread is not in main loop`
    *   **Çözüm:** Non-interaktif modda görselleştirme kaydetme kullanılmaktadır. `visualize` komutu otomatik olarak PNG dosyası oluşturur.

*   **ML Model Eğitimi Sorunları:**
    *   **Hata:** Yetersiz veri nedeniyle model eğitimi başarısız
    *   **Çözüm:** Daha fazla veri üretmek için `--days` parametresini artırın.

*   **Simülasyon Performans Sorunları:**
    *   **Hata:** Simülasyon yavaş çalışıyor
    *   **Çözüm:** `speed` komutunu kullanarak simülasyon hızını artırın veya daha az adım çalıştırın.

### Grafik Penceresi Yanıt Vermiyor
Grafik pencereleri kapanmak yerine yanıt vermiyor veya çöküyorsa, şu adımları deneyin:

*   `visualize` yerine `report` komutunu kullanın (kayıt dosyalarına erişim sağlar)
*   Programdan çıkıp yeniden başlatın
*   `--no-ml` parametresi ile başlatın

## Lisans
Bu proje MIT lisansı altında lisanslanmıştır.

## İletişim
Sorunlar ve özellik istekleri için lütfen GitHub üzerinden issue açın.
- Kural tabanlı ve yapay zeka destekli otomasyon sistemleri
- İnteraktif ve görsel simülasyon araçları
- Detaylı raporlama ve veri görselleştirme
- Multi-thread desteği ve thread-safe görselleştirme
- Çoklu oda ve cihaz yönetimi

## Kurulum

### Gereksinimler

- Python 3.8+
- numpy
- pandas
- matplotlib
- scikit-learn
- seaborn

### Bağımlılıkları Yükleme

```bash
pip install -r requirements.txt
```

Ya da paket olarak geliştirici modunda kurmak için:

```bash
pip install -e .
```

## Kullanım

### Ana Uygulamayı Çalıştırma

Ana uygulamayı çalıştırmak için:

```bash
python app.py
```

### Çalıştırma Modları

Farklı modlarda çalıştırma seçenekleri:

```bash
# Sadece veri üretimi
python app.py --mode data --days 5

# Sadece model eğitimi 
python app.py --mode train --no-optimize

# Demo simülasyon modu
python app.py --mode simulate --steps 200

# İnteraktif simülasyon modu
python app.py --mode interactive

# Tüm süreçler (veri üretimi, model eğitimi, simülasyon)
python app.py --mode all
```

### Komut Satırı Parametreleri

| Parametre | Açıklama | Varsayılan Değer |
|-----------|------------|-----------------|
| `--mode` | Çalışma modu (data, train, simulate, interactive, all) | all |
| `--days` | Simüle edilecek gün sayısı | 3 |
| `--steps` | Simülasyon adım sayısı | 100 |
| `--no-optimize` | Hiperparametre optimizasyonu yapma | False |
| `--no-ml` | Makine öğrenmesi modelini devre dışı bırak | False |

### İnteraktif Mod Kullanımı

İnteraktif mod başlatıldığında (`python app.py --mode interactive`), aşağıdaki komutları kullanabilirsiniz:

- `start`: Simülasyonu başlatır.
- `stop`: Simülasyonu durdurur.
- `step`: Bir adım simülasyon yapar.
- `set <parametre> <değer>`: Parametre ayarlamak için kullanılır.
- `get <parametre>`: Mevcut parametre değerini görüntüler.
- `exit`: İnteraktif moddan çıkış yapar.

## Proje Yapısı

```
smart-home-automation/
│
├── app.py                  # Ana uygulama dosyası
├── setup.py                # Kurulum dosyası
├── requirements.txt        # Bağımlılıklar
│
├── src/                    # Kaynak kodlar
│   ├── automation/         # Otomasyon motoru
│   ├── data_processing/    # Veri işleme
│   ├── data_simulation/    # Veri simülasyonu
│   ├── models/             # Makine öğrenmesi modelleri
│   ├── simulation/         # Ev simülasyonu
│   └── utils/              # Yardımcı modüller
│
├── tests/                  # Birim ve entegrasyon testleri
│
├── docs/                   # Dokümantasyon
│
└── data/                   # Veri dosyaları
    ├── raw/                # Ham veri
    └── processed/          # İşlenmiş veri
```

## Testler

Tüm testleri çalıştırmak için:

```bash
python -m pytest tests/
```

Kod kapsamı raporu için:

```bash
python -m pytest tests/ --cov=src/
```

## Lisans

Bu proje [MIT](LICENSE) lisansı altında lisanslanmıştır.