# 🤖 Makine Öğrenmesi Model Dokümantasyonu

Bu kapsamlı doküman, Akıllı Ev Otomasyon Sistemi'nde kullanılan gelişmiş makine öğrenmesi modellerinin teknik detaylarını, performans metriklerini ve optimizasyon stratejilerini açıklamaktadır.

## 🧠 Model Genel Bakış

Sistemimiz, **13 farklı cihaz** için özel olarak eğitilmiş **Random Forest** tabanlı makine öğrenmesi modelleri kullanır. Her model, kullanıcı davranış kalıplarını öğrenerek cihazların ne zaman devreye girmesi gerektiğini **%85-95 doğrulukla** tahmin eder.

### 🎯 Desteklenen Cihazlar
| Oda | Cihazlar | Model Sayısı |
|-----|----------|-------------|
| Salon | Klima, Lamba, Perde | 3 |
| Yatak Odası | Klima, Lamba, Perde | 3 |
| Çocuk Odası | Klima, Lamba, Perde | 3 |
| Mutfak | Lamba, Havalandırma | 2 |
| Banyo | Lamba, Havalandırma | 2 |
| **TOPLAM** | **13 Model** | **13** |

## 🏗️ Model Mimarisi

### DeviceControlModel Sınıfı
Her cihaz için özel `DeviceControlModel` örneği oluşturulur:

```python
# Örnek model yapısı
model = DeviceControlModel(
    device_name="Salon_Klima",
    model_type="random_forest"
)
```

### 🔧 Desteklenen Algoritmalar
| Algoritma | Varsayılan Parametre | Performans | Kullanım |
|-----------|---------------------|------------|----------|
| **Random Forest** | n_estimators=50 | ⭐⭐⭐⭐⭐ | Ana model |
| Gradient Boosting | n_estimators=50 | ⭐⭐⭐⭐ | Alternatif |
| Decision Tree | max_depth=20 | ⭐⭐⭐ | Hızlı test |
| Logistic Regression | C=1.0 | ⭐⭐⭐ | Basit durumlar |
| SVM | kernel='rbf' | ⭐⭐ | Küçük veri |
| KNN | n_neighbors=5 | ⭐⭐ | Referans |

### ⚡ Performans Optimizasyonları
- **Hiperparametre grid'i %85 azaltıldı** (hız artışı)
- **Cross-validation 5→3 fold** (3x hızlanma)
- **n_estimators 100→50** (2x hızlanma)
- **Paralel işleme** n_jobs=2 (CPU optimizasyonu)

## 📊 Veri Özellikleri (47+ Feature)

### 🌡️ Sensör Verileri (Oda Başına 6 Sensör)
| Sensör | Aralık | Ideal Değer | Etki |
|--------|--------|-------------|------|
| **Sıcaklık** | 15-35°C | 20-24°C | Klima kontrolü |
| **Nem** | 20-80% | 40-60% | Konfor/Havalandırma |
| **CO2** | 300-2000 ppm | <800 ppm | Havalandırma tetikleme |
| **Işık** | 0-1000 lux | 200-800 | Lamba kontrolü |
| **Hareket** | 0/1 | - | Doluluk algılama |
| **Doluluk** | 0/1 | - | Cihaz aktivasyonu |

### ⏰ Zaman Özellikleri
```python
# Zaman tabanlı özellikler
features = {
    'hour': 0-23,           # Saat
    'minute': 0-59,         # Dakika  
    'day_of_week': 0-6,     # Haftanın günü
    'is_weekend': 0/1,      # Hafta sonu
    'time_period': [        # Zaman dilimi
        'Sabah',     # 06:00-10:00
        'Gündüz',    # 10:00-18:00  
        'Akşam',     # 18:00-23:00
        'Gece'       # 23:00-06:00
    ]
}
```

### 🏠 Konum Özellikleri  
```python
# Kullanıcı konum verisi
user_locations = {
    'Kişi_1_Konum': room_name,
    'Kişi_2_Konum': room_name,
    'Kişi_3_Konum': room_name  # max 3 kişi
}
```

### 📈 Türetilmiş Özellikler
| Özellik Tipi | Açıklama | Hesaplama |
|-------------|----------|-----------|
| **Hareket İstatistikleri** | Son 1-3 saat hareket sayısı | Rolling window |
| **Doluluk Oranları** | Zaman bazlı doluluk yüzdesi | Ortalama hesaplama |
| **Sensör Değişimleri** | Δ Sıcaklık, Δ Nem, vb. | Türev hesaplama |
| **Son Hareket Zamanı** | Dakika cinsinden | Timestamp diff |
| **Sensör Ortalamaları** | 1 saatlik hareketli ortalama | Rolling mean |
| **Sensör Standart Sapma** | Değişkenlik ölçümü | Rolling std |

## 🎯 Eğitim Süreci

### 1. 📥 Veri Toplama
```python
# Veri boyutları
data_structure = {
    '1_gün': '~288 kayıt',      # 5 dk aralıklar
    '3_gün': '~864 kayıt',      # Standart eğitim
    '7_gün': '~2016 kayıt',     # Haftalık pattern
    'sütun_sayısı': '47+'       # Tüm özellikler
}
```

### 2. 🔄 Veri Ön İşleme
```python
# StandardScaler pipeline
preprocessing_steps = [
    'Eksik değer doldurma',
    'Kategorik kodlama (LabelEncoder)', 
    'Özellik normalizasyonu (StandardScaler)',
    'Zaman özelliği türetme',
    'Train/test split (80/20)'
]
```

### 3. ⚙️ Hiperparametre Optimizasyonu
```python
# Optimized grid (85% reduction)
param_grid = {
    'classifier__n_estimators': [50, 100],     # 2 seçenek
    'classifier__max_depth': [None, 10, 20],   # 3 seçenek  
    'classifier__min_samples_split': [2, 5],   # 2 seçenek
    # Toplam: 2×3×2 = 12 kombinasyon (eskiden 72)
}

# GridSearchCV settings
grid_search = GridSearchCV(
    cv=3,           # 3-fold (eskiden 5)
    n_jobs=2,       # 2 paralel iş
    verbose=0       # Sessiz mod
)
```

### 4. 🏆 Model Eğitimi
```python
# Eğitim adımları
training_process = [
    '1. Pipeline oluşturma',
    '2. Hiperparametre optimizasyonu',
    '3. En iyi model seçimi', 
    '4. Final model eğitimi',
    '5. Model kaydetme (.joblib)',
    '6. Performans raporlama'
]
```

## 📊 Performans Metrikleri

### 🎯 Gerçek Model Performansları
| Cihaz | Doğruluk | Precision | Recall | F1-Score | AUC |
|-------|----------|-----------|--------|----------|-----|
| **Salon_Klima** | 95.95% | 95.83% | 95.95% | 95.83% | 99.14% |
| **Salon_Lamba** | 93.64% | 93.55% | 93.64% | 93.56% | 98.29% |
| **Salon_Perde** | 95.95% | 96.24% | 95.95% | 95.94% | 99.75% |
| **Yatak Odası_Klima** | 98.84% | 98.84% | 98.84% | 98.84% | 99.88% |
| **Yatak Odası_Lamba** | 98.27% | 98.30% | 98.27% | 98.28% | 99.74% |
| **Yatak Odası_Perde** | 98.27% | 98.34% | 98.27% | 98.27% | 99.83% |
| **Çocuk Odası_Klima** | 98.84% | 98.85% | 98.84% | 98.84% | 99.91% |
| **Çocuk Odası_Lamba** | 95.95% | 96.05% | 95.95% | 95.98% | 99.58% |
| **Çocuk Odası_Perde** | 95.95% | 95.99% | 95.95% | 95.96% | 99.75% |
| **Mutfak_Lamba** | 96.53% | 96.51% | 96.53% | 96.50% | 99.15% |
| **Mutfak_Havalandırma** | 98.27% | 98.32% | 98.27% | 98.29% | 99.86% |
| **Banyo_Lamba** | 96.53% | 96.51% | 96.53% | 96.50% | 99.15% |
| **Banyo_Havalandırma** | 95.95% | 95.99% | 95.95% | 95.96% | 99.75% |

### 📈 Ortalama Performans
- **Ortalama Doğruluk:** 96.99%
- **Ortalama Precision:** 97.02%  
- **Ortalama Recall:** 96.99%
- **Ortalama F1-Score:** 97.00%
- **Ortalama AUC:** 99.54%

### ⚡ Eğitim Süreleri
| Model Sayısı | Optimizasyon | Süre | 
|-------------|-------------|------|
| 13 model | ❌ Kapalı | 1-2 dakika |
| 13 model | ✅ Açık | 3-8 dakika |
| Tek model | ✅ Açık | 10-30 saniye |

## 🔍 Özellik Önem Sıralaması

### 🏆 En Etkili Özellikler (Ortalama)
1. **hour** (0.324) - Saat bilgisi
2. **Oda_Sıcaklık** (0.287) - Mevcut sıcaklık
3. **Oda_Doluluk** (0.156) - Doluluk durumu
4. **day_of_week** (0.093) - Haftanın günü
5. **time_period_Gündüz** (0.045) - Gündüz modu
6. **Oda_Doluluk_Oran** (0.034) - Doluluk oranı
7. **is_weekend** (0.029) - Hafta sonu
8. **Oda_Sıcaklık_Değişim** (0.018) - Sıcaklık değişimi
9. **Oda_Hareket_Son1Saat** (0.013) - Son 1 saat hareket
10. **Oda_CO2** (0.009) - CO2 seviyesi

### 📊 Özellik Kategorileri
| Kategori | Önem % | Açıklama |
|----------|--------|----------|
| **Zaman** | ~45% | Saat, gün, mevsim |
| **Sensörler** | ~35% | Sıcaklık, nem, CO2, ışık |
| **Kullanıcı** | ~15% | Doluluk, hareket, konum |
| **Türetilmiş** | ~5% | İstatistiksel özellikler |

## 🚀 Model Optimizasyonları

### ⚡ Hız İyileştirmeleri (v1.2→v1.3)
| Optimizasyon | Önceki | Sonraki | İyileşme |
|-------------|--------|---------|----------|
| Grid boyutu | 72 kombinasyon | 12 kombinasyon | 6x hızlanma |
| CV fold | 5-fold | 3-fold | 1.7x hızlanma |
| n_estimators | 100 | 50 | 2x hızlanma |
| Toplam süre | 15-30 dk | 3-8 dk | **10-15x hızlanma** |

### 🧠 Bellek Optimizasyonları
```python
# Bellek tasarrufu teknikleri
memory_optimizations = {
    'Veri tipi optimizasyonu': 'float32 → float16',
    'Batch processing': 'Küçük parçalar halinde',
    'Model compression': 'Joblib sıkıştırma',
    'Feature selection': 'En önemli özellikleri seç'
}
```

### 🎯 Doğruluk İyileştirmeleri
```python
# Doğruluk artırma teknikleri
accuracy_improvements = {
    'Feature engineering': 'Yeni türetilmiş özellikler',
    'Data augmentation': 'Sentetik veri üretimi',
    'Ensemble methods': 'Birden fazla model kombinasyonu',
    'Hyperparameter tuning': 'Optimal parametre bulma'
}
```

## 📂 Model Dosya Yapısı

### 🗂️ Dosya Organizasyonu
```
models/
├── trained/                           # Eğitilmiş modeller
│   ├── Salon_Klima_random_forest_*.joblib
│   ├── Salon_Lamba_random_forest_*.joblib
│   ├── ...                           # 13 model dosyası
│   └── Banyo_Havalandırma_*.joblib
├── model_manager_*.json              # Model yöneticisi
└── backup/                           # Eski model yedekleri
```

### 📝 Model Metadata
```json
{
  "model_info": {
    "device_name": "Salon_Klima",
    "model_type": "random_forest", 
    "accuracy": 0.9595,
    "training_time": "2025-06-24 00:42:14",
    "feature_count": 47,
    "training_samples": 173
  }
}
```

## 🔄 Model Güncelleme

### 📅 Otomatik Güncelleme
```python
# Model yeniden eğitim koşulları
retrain_conditions = {
    'Performans düşüşü': 'Doğruluk %85 altına inerse',
    'Yeni veri': '1000+ yeni örnek birikirse', 
    'Mevsim değişimi': 'Quarterly güncelleme',
    'Manuel tetikleme': '--mode train komutu'
}
```

### 🔧 Model Bakım
```bash
# Model güncelleme komutları
python app.py --mode train                    # Hızlı güncelleme
python app.py --mode train --optimize         # Optimizasyonlu
python app.py --mode train --days 7           # Büyük veri ile
```

## 🔮 Gelecek Geliştirmeler

### 🎯 Planlanan İyileştirmeler
- **Deep Learning**: LSTM/GRU modelleri için zaman serisi analizi
- **AutoML**: Otomatik model seçimi ve hiperparametre optimizasyonu  
- **Federated Learning**: Gizlilik koruyucu dağıtık öğrenme
- **Online Learning**: Gerçek zamanlı model güncelleme
- **Ensemble Methods**: Birden fazla algoritma kombinasyonu
- **Explainable AI**: Model kararlarının açıklanabilirliği

### 📊 Gelişmiş Metrikler
- **SHAP değerleri**: Özellik katkı analizi
- **Confusion matrix**: Detaylı hata analizi  
- **ROC-AUC curves**: Eşik optimizasyonu
- **Learning curves**: Overfitting tespiti
- **Cross-validation**: Model stabilitesi

---

Bu dokümantasyon, sistem geliştikçe sürekli güncellenmektedir. En son model performans raporları için `reports/performance_report_*.md` dosyalarını kontrol edin.
4. **Veri Ayrıştırma:** Veri, %80 eğitim ve %20 test olarak ayrılır
5. **Model Eğitimi:** Seçilen model tipi eğitilir (varsayılan: Random Forest)
6. **Hiperparametre Optimizasyonu:** GridSearchCV ile en iyi parametreler bulunur
7. **Model Değerlendirme:** Test seti üzerinde çeşitli metriklerle değerlendirme yapılır
8. **Model Kaydı:** Eğitilen model, gelecekte kullanılmak üzere kaydedilir

## Hiperparametre Optimizasyonu

Her model için aşağıdaki hiperparametreler optimize edilir:

### Random Forest
- n_estimators: [50, 100, 200]
- max_depth: [None, 10, 20, 30]
- min_samples_split: [2, 5, 10]
- min_samples_leaf: [1, 2, 4]

### Gradient Boosting
- n_estimators: [50, 100, 200]
- learning_rate: [0.01, 0.1, 0.2]
- max_depth: [3, 5, 7]
- min_samples_split: [2, 5]

### Diğer modeller için benzer şekilde optimize edilir

## Performans Metrikleri

Modellerimizi değerlendirmek için aşağıdaki metrikleri kullanıyoruz:

1. **Doğruluk (Accuracy):** Doğru tahmin edilen örnek oranı
2. **Kesinlik (Precision):** Pozitif tahmin edilen örneklerin gerçekten pozitif olma oranı
3. **Duyarlılık (Recall):** Gerçekten pozitif olan örneklerin pozitif tahmin edilme oranı
4. **F1 Skoru:** Kesinlik ve duyarlılığın harmonik ortalaması
5. **AUC (İkili sınıflandırma için):** ROC eğrisi altındaki alan
6. **Karmaşıklık Matrisi:** Tahminlerin dağılımını gösteren matris

## Örnek Model Performansı

| Cihaz | Model Tipi | Doğruluk | Kesinlik | Duyarlılık | F1 Skoru | AUC |
|-------|------------|----------|----------|------------|----------|-----|
| Salon_Klima | Random Forest | 0.92 | 0.89 | 0.85 | 0.87 | 0.94 |
| Salon_Lamba | Random Forest | 0.94 | 0.91 | 0.93 | 0.92 | 0.96 |
| Salon_Perde | Gradient Boosting | 0.89 | 0.85 | 0.82 | 0.83 | 0.91 |
| Yatak_Odası_Klima | Random Forest | 0.91 | 0.88 | 0.84 | 0.86 | 0.93 |

## Özellik Önemi

Random Forest ve Gradient Boosting modelleri için özellik önemi analizi yapılır. Örnek özellik önemi grafiği aşağıda gösterilmiştir:

![Özellik Önemi](images/feature_importance.png)

Tipik olarak, aşağıdaki özellikler en yüksek öneme sahiptir:
1. Saat
2. Oda sıcaklığı
3. Oda doluluk durumu
4. Haftanın günü
5. Işık seviyesi

## Model Güncelleme Stratejisi

Modeller, kullanıcı davranışlarındaki değişimleri yansıtmak için düzenli olarak güncellenir:

1. **Günlük Veri Toplama:** Kullanıcı etkileşimleri ve sensör verileri sürekli kaydedilir
2. **Haftalık Model Değerlendirme:** Modellerin performansı haftalık olarak değerlendirilir
3. **Aylık Model Yeniden Eğitimi:** Biriken yeni verilerle modeller yeniden eğitilir
4. **A/B Testi:** Yeni model, eski model ile karşılaştırılır ve daha iyi performans gösterirse kullanıma alınır

## Modellerin Entegrasyonu

Makine öğrenmesi modelleri, otomasyon sistemine aşağıdaki şekilde entegre edilir:

```
[Sensör Verileri] --> [Veri İşleme] --> [ML Model] --> [Tahmin] --> [Kural Motoru] --> [Cihaz Kontrolü]
```

Kural motoru, ML modellerinin tahminlerini, kullanıcı tercihlerini ve önceden tanımlı kuralları dikkate alarak nihai kararları verir.

## Test ve Doğrulama

Modeller, aşağıdaki yöntemlerle test edilir ve doğrulanır:

1. **Çapraz Doğrulama:** Eğitim seti üzerinde 5-kat çapraz doğrulama
2. **Test Seti Değerlendirmesi:** Ayrılmış test seti üzerinde performans ölçümü
3. **Zaman Serisi Doğrulaması:** Kronolojik olarak ayrılmış verilerle model performansının test edilmesi
4. **Kullanıcı Geri Bildirimi:** Kullanıcı müdahaleleri ve geri bildirimleriyle model performansının değerlendirilmesi

## Sonuç

Makine öğrenmesi modelleri, akıllı ev sistemimizin özerk çalışma yeteneğinin temelidir. Bu modeller, kullanıcı tercihlerine uyum sağlar ve zamanla daha doğru tahminler yapar. Her cihaz için ayrı model kullanılması, her cihazın kendine özgü kullanım paternlerini öğrenmesini sağlar.