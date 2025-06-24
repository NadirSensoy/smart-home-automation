# 🏠 Akıllı Ev Otomasyon Sistemi

Makine öğrenmesi destekli gelişmiş akıllı ev otomasyon sistemi. Gerçek zamanlı sensör verilerini analiz ederek ev içindeki cihazların otomatik kontrolünü sağlar, enerji tasarrufu ve konfor optimizasyonu gerçekleştirir.

## ✨ Öne Çıkan Özellikler

### 🤖 Makine Öğrenmesi & AI
- **Random Forest** tabanlı cihaz kontrol modelleri
- **13 farklı cihaz** için özelleştirilmiş ML modelleri
- **%90+** doğruluk oranı ile tahmin
- **Gerçek zamanlı öğrenme** ve adaptasyon
- **Hiperparametre optimizasyonu** desteği

### 📊 Gelişmiş Sensör Sistemi  
- **5 farklı oda** (Salon, Yatak Odası, Çocuk Odası, Mutfak, Banyo)
- **6 sensör türü** (Sıcaklık, Nem, CO2, Işık, Hareket, Doluluk)
- **Gerçekçi sensör simülasyonu** ve veri üretimi
- **Zaman bazlı pattern** analizi

### ⚡ Enerji & Konfor Optimizasyonu
- **%20-40 enerji tasarrufu** (gerçek veri bazlı)
- **Akıllı klima kontrolü** (sıcaklık optimizasyonu)
- **Adaptif aydınlatma** sistemi
- **Hava kalitesi** yönetimi
- **Kullanıcı alışkanlıkları** öğrenme

### 📈 Görselleştirme & Analiz
- **Gerçek zamanlı dashboard**
- **Karşılaştırmalı enerji analizi**
- **ROI hesaplama** (geri ödeme süresi)
- **Konfor indeksi** radar grafikleri
- **Cihaz kullanım pattern** analizi

### 🎮 İnteraktif Simülasyon
- **Canlı simülasyon** ortamı
- **Manuel cihaz kontrolü**
- **Gerçek zamanlı grafik** güncellemeleri
- **Sensör verisi** izleme
- **HTML rapor** üretimi

## 🚀 Hızlı Başlangıç

### Kurulum
```bash
# Depoyu klonlayın
git clone <repository-url>
cd smart-home-automation

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Geliştirici modunda kurun
pip install -e .
```

### İlk Çalıştırma
```bash
# Hızlı demo simülasyonu (30 adım)
python app.py

# Tam süreç (veri + eğitim + simülasyon)
python app.py --mode all --days 3 --optimize

# İnteraktif mod
python app.py --mode interactive --steps 50
```

## 📋 Kullanım Modları

### 🎯 Çalıştırma Modları
| Mod | Açıklama | Kullanım |
|-----|----------|----------|
| `simulate` | Hızlı demo simülasyonu | `python app.py --mode simulate --steps 30` |
| `interactive` | İnteraktif simülasyon | `python app.py --mode interactive` |
| `train` | Sadece model eğitimi | `python app.py --mode train --optimize` |
| `data` | Sadece veri üretimi | `python app.py --mode data --days 7` |
| `all` | Tam süreç | `python app.py --mode all --days 7 --optimize` |

### ⚙️ Parametre Seçenekleri

| Parametre | Açıklama | Varsayılan | Aralık |
|-----------|----------|------------|--------|
| `--mode` | 🎯 Çalıştırma modu | `simulate` | data, train, simulate, interactive, all |
| `--days` | 📅 Simülasyon günü | `1` | 1-30 |
| `--steps` | ⚡ Simülasyon adımı | `30` | 5-200 |
| `--optimize` | ⚙️ Hiperparametre optimizasyonu | `False` | - |
| `--no-ml` | 🔄 ML devre dışı | `False` | - |
| `--quiet` | 🔇 Sessiz mod | `False` | - |
| `--rooms` | 🏠 Odalar | Tümü | Liste |
| `--residents` | 👥 Ev sakini sayısı | `2` | 1-5 |

### 💡 Örnek Kullanımlar
```bash
# Hızlı test (30 saniye)
python app.py --mode simulate --steps 20

# Haftalık analiz (optimizasyonlu)
python app.py --mode all --days 7 --optimize

# Sadece yatak odası ve salon
python app.py --rooms "Yatak Odası" "Salon" --steps 40

# 3 kişilik aile simülasyonu
python app.py --residents 3 --days 2

# Sessiz mod (scriptler için)
python app.py --quiet --mode simulate --steps 50

# ML olmadan sadece kurallar
python app.py --no-ml --mode simulate
```

## 📊 Sistem Bileşenleri

### 🏠 Desteklenen Cihazlar
- **Klima** (Sıcaklık kontrolü, enerji verimliliği)
- **Lamba** (Akıllı aydınlatma, gece/gündüz modu)  
- **Perde** (Güneş ışığı kontrolü, gizlilik)
- **Havalandırma** (Hava kalitesi, CO2 kontrolü)

### 📡 Sensör Türleri
- **Sıcaklık:** 15-35°C (ideal: 20-24°C)
- **Nem:** 20-80% (ideal: 40-60%)
- **CO2:** 300-2000 ppm (ideal: <800 ppm)
- **Işık:** 0-1000 lux (gece/gündüz adaptasyonu)
- **Hareket:** Boolean (hareket algılama)
- **Doluluk:** Boolean (oda doluluk durumu)

### 🧠 ML Model Detayları
- **Model Türü:** Random Forest Classifier
- **Eğitim Verisi:** 288+ kayıt, 47+ özellik
- **Doğruluk:** %85-95 (cihaza göre değişir)
- **Özellikler:** Sensör verileri, zaman, kullanıcı davranışları
- **Güncelleme:** Gerçek zamanlı öğrenme

## 📈 Performans Metrikleri

### ⚡ Enerji Tasarrufu
- **Klima:** %40 tasarruf (akıllı sıcaklık kontrolü)
- **Aydınlatma:** %30 tasarruf (LED + akıllı kontrol)
- **Genel:** %20-40 toplam enerji tasarrufu
- **ROI:** 12-24 ay geri ödeme süresi

### 🎯 Konfor İyileştirmeleri
- **Sıcaklık Konforu:** %80+ ideal aralıkta
- **Hava Kalitesi:** %70+ optimal seviye
- **Aydınlatma:** %80+ uygun seviye
- **Genel Konfor:** +15-25 puan iyileşme

### ⏱️ Sistem Performansı
- **Veri Üretimi:** ~2 saniye/gün
- **Model Eğitimi:** 1-5 dakika (optimizasyona göre)
- **Simülasyon:** ~1.5 saniye/adım
- **Gerçek Zamanlı:** <100ms yanıt süresi

## 📁 Çıktı Dosyaları

### 📊 Veri Dosyaları
- `data/raw/` - Ham simülasyon verileri
- `data/processed/` - İşlenmiş eğitim verileri
- `data/simulation/` - Simülasyon geçmişi

### 🤖 Model Dosyaları  
- `models/trained/` - Eğitilmiş ML modelleri (.joblib)
- `models/model_manager_*.json` - Model yöneticisi durumu

### 📈 Raporlar & Görseller
- `reports/` - Performans raporları (.md)
- `output/visualizations/` - Karşılaştırmalı grafikler
- `logs/` - Sistem logları

### 🎨 Görselleştirmeler
1. **Enerji Karşılaştırması** - Geleneksel vs Akıllı sistem
2. **Konfor İndeksi** - Radar grafik karşılaştırması  
3. **Cihaz Kullanım Analizi** - Saatlik/oda bazlı pattern
4. **Öğrenme Trendi** - 30 günlük performans artışı
5. **ROI Analizi** - Maliyet-tasarruf hesaplama

## 🔧 Gelişmiş Özellikler

### 🎛️ Konfigürasyon
- `src/config.py` - Sistem ayarları
- Sensör eşikleri özelleştirme
- Otomasyon kuralları düzenleme
- ML model parametreleri

### 🏗️ Sistem Mimarisi
```
app.py (Ana uygulama)
├── src/data_simulation/ (Veri simülasyonu)
├── src/models/ (ML modelleri)  
├── src/automation/ (Kural motoru)
├── src/simulation/ (Simülasyon motoru)
└── src/utils/ (Yardımcı araçlar)
```

### 🔌 API & Entegrasyon
- Modüler yapı (kolay entegrasyon)
- JSON bazlı konfigürasyon
- CSV veri formatı
- HTML rapor çıktısı

## 🐛 Sorun Giderme

### ❓ Sık Karşılaşılan Sorunlar
1. **Parametre Hataları:** `--help` ile geçerli aralıkları kontrol edin
2. **Bellek Sorunu:** `--steps` sayısını azaltın (max 200)
3. **Uzun Süre:** `--optimize` kullanmayın, `--quiet` ekleyin
4. **Grafik Açılmıyor:** Tarayıcı ayarlarını kontrol edin

### 📝 Log Dosyaları
- `logs/AkilliEvOtomasyonu_*.log` - Detaylı sistem logları
- Hata mesajları ve performans bilgileri
- Sorun giderme için temel kaynak

## 🤝 Katkıda Bulunma

### 📋 Geliştirme Alanları
- Yeni sensör türleri ekleme
- Farklı ML algoritmaları test etme  
- Daha fazla cihaz türü desteği
- Mobile/web arayüz geliştirme
- Gerçek IoT cihaz entegrasyonu

### 🔄 Güncelleme Geçmişi
- **v1.3:** Güzelleştirilmiş parametreler ve banner
- **v1.2:** Gerçek veri bazlı görselleştirmeler  
- **v1.1:** ML model optimizasyonu ve hata düzeltmeleri
- **v1.0:** İlk stabil sürüm

## 📞 İletişim & Destek

- 📧 E-posta: [İletişim bilgisi]
- 🐛 Hata Bildirimi: GitHub Issues
- 📖 Dokümantasyon: `docs/` klasörü
- 💬 Tartışma: GitHub Discussions

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

---

**🏠 Akıllı Ev Otomasyon Sistemi** - Geleceğin evlerini bugünden yaşayın! 🚀
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