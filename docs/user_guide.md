# 🏠 Akıllı Ev Otomasyon Sistemi - Detaylı Kullanım Rehberi

Bu kapsamlı rehber, Akıllı Ev Otomasyon Sistemi'nin tüm özelliklerini kullanmanız için gereken bilgileri içerir.

## 🚀 Hızlı Başlangıç

### Kurulum
```bash
# Projeyi klonlayın
git clone <repository-url>
cd smart-home-automation

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Geliştirici modunda kurun
pip install -e .
```

### İlk Çalıştırma
```bash
# En basit kullanım - 30 adımlık hızlı demo
python app.py

# Sistemin banner'ını görmek için
python app.py --help
```

## 🎯 Çalıştırma Modları

### 1. 🔄 Simülasyon Modu (Varsayılan)
En yaygın kullanım - akıllı ev simülasyonu çalıştırır.

```bash
# Temel simülasyon (30 adım)
python app.py

# Özelleştirilmiş simülasyon
python app.py --mode simulate --steps 50 --residents 3

# Sadece belirli odalar
python app.py --rooms "Salon" "Yatak Odası" --steps 40
```

**Ne yapar:**
- Mevcut ML modellerini kullanır
- Gerçek zamanlı simülasyon çalıştırır
- Karşılaştırmalı görselleştirmeler oluşturur
- Enerji tasarrufu analizleri yapar

### 2. 🎮 İnteraktif Mod
Canlı, etkileşimli simülasyon ortamı.

```bash
# İnteraktif simülasyon başlat
python app.py --mode interactive

# Daha uzun süre için
python app.py --mode interactive --steps 100
```

**Özellikler:**
- Gerçek zamanlı grafik güncellemeleri
- Manuel cihaz kontrolü
- Sensör verisi izleme
- HTML rapor üretimi
- Adım adım simülasyon kontrolü

### 3. 🎯 Model Eğitimi Modu
ML modellerini eğitir veya yeniden eğitir.

```bash
# Hızlı eğitim
python app.py --mode train

# Optimizasyonlu eğitim (uzun sürer ama daha iyi sonuç)
python app.py --mode train --optimize

# Belirli veri ile eğitim
python app.py --mode train --days 7 --optimize
```

**Çıktılar:**
- `models/trained/` klasöründe .joblib dosyaları
- `models/model_manager_*.json` durum dosyası
- `reports/performance_report_*.md` performans raporu

### 4. 📊 Veri Üretimi Modu
Simülasyon verisi oluşturur.

```bash
# 1 günlük veri (varsayılan)
python app.py --mode data

# 7 günlük veri
python app.py --mode data --days 7

# 3 kişilik aile için 3 günlük veri
python app.py --mode data --days 3 --residents 3
```

**Çıktılar:**
- `data/raw/generated_data_*.csv` dosyası
- 288+ kayıt, 47+ sütun (gün sayısına göre)

### 5. 🚀 Tam Süreç Modu
Veri üretimi + Model eğitimi + Simülasyon

```bash
# Standart tam süreç
python app.py --mode all

# Optimizasyonlu tam süreç (önerilen)
python app.py --mode all --days 3 --optimize

# Haftalık analiz
python app.py --mode all --days 7 --optimize --residents 3
```

## ⚙️ Parametre Rehberi

### 🎯 --mode (Çalıştırma Modu)
| Değer | Açıklama | Süre | Kullanım |
|-------|----------|------|----------|
| `simulate` | Hızlı simülasyon | 30s-2dk | Günlük test |
| `interactive` | Etkileşimli | Değişken | Analiz/demo |
| `train` | Model eğitimi | 1-10dk | Model güncelleme |
| `data` | Veri üretimi | 10s-1dk | Veri hazırlama |
| `all` | Tam süreç | 2-15dk | Kapsamlı analiz |

### 📅 --days (Gün Sayısı)
| Değer | Veri Boyutu | Önerilen Kullanım |
|-------|-------------|-------------------|
| `1` | ~288 kayıt | Hızlı test |
| `3` | ~864 kayıt | Standart analiz |
| `7` | ~2016 kayıt | Haftalık pattern |
| `14` | ~4032 kayıt | İki haftalık analiz |
| `30` | ~8640 kayıt | Aylık analiz (uzun sürer) |

### ⚡ --steps (Simülasyon Adımı)
| Değer | Süre | Önerilen Kullanım |
|-------|------|-------------------|
| `10-20` | 15-30s | Hızlı test |
| `30-50` | 45s-1.5dk | Standart demo |
| `50-100` | 1.5-3dk | Detaylı analiz |
| `100+` | 3dk+ | Uzun vadeli trend |

### 👥 --residents (Ev Sakini)
| Değer | Etki | Gerçeklik |
|-------|------|-----------|
| `1` | Minimal aktivite | Bekar |
| `2` | Dengeli kullanım | Çift |
| `3` | Artırılmış aktivite | Küçük aile |
| `4-5` | Yoğun kullanım | Büyük aile |

### 🏠 --rooms (Oda Seçimi)
```bash
# Tüm odalar (varsayılan)
python app.py

# Sadece yaşam alanları
python app.py --rooms "Salon" "Mutfak"

# Sadece yatak odaları
python app.py --rooms "Yatak Odası" "Çocuk Odası"

# Tek oda test
python app.py --rooms "Salon"
```

### 🔧 Diğer Parametreler
```bash
# Sessiz mod (script için)
python app.py --quiet

# ML olmadan (sadece kurallar)
python app.py --no-ml

# Hiperparametre optimizasyonu
python app.py --optimize

# Yardım
python app.py --help
```

## 📊 Çıktıları Anlama

### 📈 Görselleştirmeler
Simülasyon sonrası otomatik olarak 5 grafik oluşturulur:

1. **energy_comparison.png**
   - Geleneksel vs Akıllı sistem enerji kullanımı
   - Cihaz bazında tasarruf yüzdeleri
   - Aylık TL tasarruf hesabı

2. **comfort_comparison.png**
   - Radar grafik: 5 konfor metriği
   - Akıllı vs geleneksel sistem skorları
   - Genel konfor iyileştirme puanı

3. **device_usage_analysis.png**
   - 4 alt grafik: Saatlik kullanım patternleri
   - Oda bazında cihaz aktivitesi
   - Enerji tüketim trendi

4. **learning_improvement.png**
   - 30 günlük öğrenme eğrisi
   - Performans artış grafiği
   - Hedef vs gerçek başarı

5. **roi_analysis.png**
   - 5 yıllık maliyet-tasarruf analizi
   - Başabaş noktası hesaplaması
   - Yatırım getirisi (ROI) %'si

### 📋 Raporlar
- **performance_report_*.md**: ML model performansları
- **analysis_summary.txt**: Özet analiz sonuçları
- **simulation_report_*.html**: Detaylı HTML raporu (interactive mod)

### 📁 Dosya Yapısı
```
output/
└── visualizations/
    └── comparisons/
        ├── energy_comparison.png
        ├── comfort_comparison.png
        ├── device_usage_analysis.png
        ├── learning_improvement.png
        ├── roi_analysis.png
        └── analysis_summary.txt
```

## 🔧 İleri Düzey Kullanım

### Konfigürasyon Düzenleme
`src/config.py` dosyasını düzenleyerek sistemi özelleştirebilirsiniz:

```python
# Sensör eşikleri
"automation_thresholds": {
    "high_temp_threshold": 26,  # Klima açılma sıcaklığı
    "low_light_threshold": 100, # Lamba açılma ışık seviyesi
    "high_co2_threshold": 800,  # Havalandırma eşiği
}

# ML model parametreleri
"model_training": {
    "n_estimators": 50,  # Random Forest ağaç sayısı
    "test_size": 0.2,    # Test veri oranı
}
```

### Performans Optimizasyonu
```bash
# Hızlı test için
python app.py --steps 20 --quiet

# Bellek tasarrufu için
python app.py --days 1 --steps 30

# En iyi kalite için
python app.py --mode all --days 7 --optimize
```

### Batch İşleme
```bash
# Birden fazla konfigürasyon testi
for days in 1 3 7; do
    python app.py --mode all --days $days --quiet
done

# Farklı aile büyüklükleri
for residents in 1 2 3 4; do
    python app.py --residents $residents --quiet
done
```

## 🐛 Sorun Giderme

### Yaygın Hatalar

1. **"Parametre Hatası"**
   ```bash
   # Çözüm: Geçerli aralıkları kontrol et
   python app.py --help
   ```

2. **"Bellek Yetersiz"**
   ```bash
   # Çözüm: Parametre değerlerini düşür
   python app.py --days 1 --steps 20
   ```

3. **"ML Model Bulunamadı"**
   ```bash
   # Çözüm: Önce model eğit
   python app.py --mode train
   ```

4. **"Grafik Açılmıyor"**
   - Tarayıcı izinlerini kontrol et
   - `output/visualizations/` klasörünü manuel aç

### Log İnceleme
```bash
# En son log dosyasını görüntüle
ls -la logs/ | tail -1

# Hata detayları için
grep "ERROR" logs/AkilliEvOtomasyonu_*.log
```

### Performans İzleme
```bash
# Sistem kaynak kullanımı
python app.py --quiet --mode simulate --steps 50

# Zaman ölçümü
time python app.py --mode all --days 3
```

## 🎯 Kullanım Senaryoları

### 1. 👨‍💻 Geliştirici Testi
```bash
# Hızlı kod değişikliği testi
python app.py --steps 10 --quiet

# Yeni özellik testi
python app.py --mode simulate --steps 30
```

### 2. 📊 Araştırma/Analiz
```bash
# Detaylı veri analizi
python app.py --mode all --days 7 --optimize

# Performans karşılaştırması
python app.py --mode simulate --steps 100
```

### 3. 🎥 Demo/Sunum
```bash
# Canlı demo
python app.py --mode interactive --steps 50

# Otomatik sunum
python app.py --mode all --days 3
```

### 4. 🔬 Akademik Çalışma
```bash
# Büyük veri seti
python app.py --mode data --days 30

# Kapsamlı model analizi
python app.py --mode train --optimize
```

### 5. 🏠 Ev Sahibi Simülasyonu
```bash
# Gerçek ev benzetimi
python app.py --residents 4 --days 7 --optimize

# Enerji tasarrufu hesaplama
python app.py --mode all --days 30
```

## 📱 Gelecek Özellikler

### Planlanmış Geliştirmeler
- 📱 Web arayüzü
- 🌐 REST API
- 📧 E-posta raporları
- 📱 Mobil uygulama
- 🔗 Gerçek IoT entegrasyonu
- ☁️ Bulut depolama
- 🤖 Ses kontrolü (Alexa/Google)

Bu rehber sürekli güncellenmektedir. Yeni özellikler ve güncellemeler için düzenli olarak kontrol edin.

```bash
python app.py --mode train
```

Hiperparametre optimizasyonu olmadan eğitmek için:

```bash
python app.py --mode train --no-optimize
```

### 4. Simülasyon Çalıştırma

Akıllı ev simülasyonunu çalıştırmak için:

```bash
python app.py --mode simulate --steps 200
```

Bu komut 200 adımlık bir simülasyon çalıştırır (her adım 5 dakikalık gerçek zamanı temsil eder).

### 5. İnteraktif Simülasyon

İnteraktif modu çalıştırmak için:

```bash
python app.py --mode interactive
```

Bu mod, simülasyonu görsel arayüzle izlemenize ve cihazları manuel kontrol etmenize olanak tanır.

## İleri Düzey Kullanım

### Parametreler

Uygulamayı çalıştırırken kullanabileceğiniz parametreler:

- `--mode`: Çalıştırma modu (`data`, `train`, `simulate`, `interactive`, `all`)
- `--days`: Simüle edilecek gün sayısı
- `--steps`: Simülasyon adım sayısı
- `--no-optimize`: Hiperparametre optimizasyonunu devre dışı bırakır
- `--no-ml`: ML modeli kullanımını devre dışı bırakır

Örneğin:

```bash
python app.py --mode simulate --steps 300 --no-ml
```

Bu komut, ML modellerini kullanmadan 300 adımlık bir simülasyon çalıştırır.

## Çıktılar ve Raporlar

### Veri Dosyaları

- Ham veriler: `data/raw/` dizininde CSV formatında
- İşlenmiş veriler: `data/processed/` dizininde

### Modeller

- Eğitilmiş modeller: `models/trained/` dizininde
- Model yöneticisi: `models/` dizininde JSON formatında

### Raporlar

- Performans raporları: `reports/` dizininde
- Görselleştirmeler: `reports/figures/` dizininde

### Loglar

- Uygulama logları: `logs/` dizininde

## Sonuçları İnceleme

Simülasyon sonuçlarını ve model performans raporlarını incelemek için:

1. `reports/` dizinindeki performans raporlarına bakın
2. ML model performans grafiklerini `reports/figures/` dizininde bulabilirsiniz
3. Simülasyon geçmişi `data/simulation/` dizininde kaydedilir

## Özel Kurallar Tanımlama

Sistem, kural tabanlı otomasyon motorunu kullanır. Özel kurallar tanımlamak için `src/automation/rules_engine.py` dosyasındaki `create_default_rules` fonksiyonuna benzer şekilde kurallar ekleyebilirsiniz.

Örnek bir kural:

```python
def my_condition(state):
    # Kural için koşul tanımı
    return state['Salon_Sıcaklık'] > 25 and state['Salon_Doluluk']

def my_action(state, devices):
    # Kural tetiklendiğinde yapılacak eylem
    return {'Salon_Klima': True}

rules_engine.add_rule(
    name="kendi_kurali",
    condition_func=my_condition,
    action_func=my_action,
    priority=5,
    description="Salon sıcaklığı 25°C üzerinde ve oda doluysa klimayı aç"
)
```

## Sorun Giderme

### Yaygın Hatalar

1. **"No module named 'src'"**: Terminali projenin ana dizininden çalıştırdığınızdan emin olun
2. **ML modeli hatası**: Önce veri üretimi ve model eğitimi adımlarını tamamlayın
3. **Görselleştirme hataları**: Matplotlib ve Seaborn bağımlılıklarını kontrol edin

### Log Dosyaları

Hata ayıklama için log dosyalarını kontrol edin:

```
logs/app_[tarih].log
logs/simulation_[tarih].log
logs/automation_[tarih].log
```

## Örnek İş Akışı

Tipik bir iş akışı şu şekildedir:

1. Veri üretimi: `python app.py --mode data --days 7`
2. Model eğitimi: `python app.py --mode train`
3. Eğitilmiş modelle simülasyon: `python app.py --mode simulate --steps 500`
4. Sonuçları inceleme: `reports/` ve `logs/` dizinlerindeki dosyaları inceleme

## Kaynaklar ve İleri Okuma

Sistemin daha detaylı belgelerine ulaşmak için:

- [ML Model Dokümanı](ml_model.md)
- [Sensörler ve Cihazlar](sensors_and_devices.md)
- [Otomasyon Kuralları](automation_rules.md)
- [Sistem Mimarisi](system_architecture_diagram.md)
