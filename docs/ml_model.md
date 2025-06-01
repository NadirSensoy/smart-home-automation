# Makine Öğrenmesi Modeli

Bu doküman, Akıllı Ev Otomasyon Sistemi'nde kullanılan makine öğrenmesi modellerinin teknik detaylarını, eğitim süreçlerini ve performans metriklerini açıklamaktadır.

## Model Genel Bakış

Akıllı ev sistemimiz, kullanıcı davranışlarını öğrenerek cihazların ne zaman açılıp kapanması gerektiğini tahmin eden çeşitli makine öğrenmesi modelleri kullanmaktadır. Her cihaz için ayrı bir model eğitilir ve her model, sensör verilerine, saate, güne ve kullanıcı etkileşimlerine dayalı olarak tahminler yapar.

## Model Mimarisi

### DeviceControlModel Sınıfı

Her cihaz için bir `DeviceControlModel` örneği oluşturulur. Bu sınıf, çeşitli model tiplerini destekler:

- **Random Forest Sınıflandırıcı**
- **Gradient Boosting Sınıflandırıcı**
- **Karar Ağacı**
- **Lojistik Regresyon**
- **Destek Vektör Makinesi (SVM)**
- **K-En Yakın Komşuluk (KNN)**

## Veri Özellikleri

Modelin eğitimi için kullanılan özellikler şunlardır:

### Sensör Verileri
- Sıcaklık (°C)
- Nem (%)
- CO2 seviyesi (ppm)
- Işık seviyesi (lux)
- Hareket algılama (boolean)
- Oda doluluk durumu (boolean)

### Zaman Özellikleri
- Saat (0-23)
- Dakika (0-59)
- Haftanın günü (0-6)
- Hafta içi/sonu (0/1)
- Zaman dilimi (Sabah, Gündüz, Akşam, Gece)

### Türetilmiş Özellikler
- Son 1 saatteki hareket sayısı
- Oda doluluk oranı (son 1 saat)
- Son hareketten bu yana geçen süre (dakika)
- Sensör değerlerinin değişim oranları

## Eğitim Süreci

1. **Veri Toplama:** Sensör verileri ve cihaz durumları, 5'er dakikalık aralıklarla toplanır
2. **Veri Ön İşleme:** Ham veriler temizlenir, eksik değerler doldurulur ve kategorik veriler kodlanır
3. **Özellik Mühendisliği:** Zaman tabanlı ve sensör tabanlı yeni özellikler türetilir
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