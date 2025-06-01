# Akıllı Ev Otomasyon Sistemi

## Proje Özeti

Akıllı Ev Otomasyon Sistemi, ev içerisindeki sensör verilerini analiz ederek ve kullanıcı alışkanlıklarını öğrenerek çeşitli ev cihazlarını otomatik olarak kontrol eden bir sistemdir. Makine öğrenmesi algoritmalarını kullanarak kullanıcı tercihlerini öğrenir ve enerji tasarrufu sağlarken maksimum konfor sunar.

## Sistem Mimarisi

![Sistem Mimarisi](images/system_architecture.png)

Sistem temel olarak şu bileşenlerden oluşur:

1. **Veri Toplama Modülü:** Sensörlerden gelen verileri toplar ve işler
2. **Veri İşleme Pipeline'ı:** Ham verileri makine öğrenimi için hazırlar
3. **Makine Öğrenmesi Modülleri:** Kullanıcı davranışlarını öğrenir ve tahmin eder
4. **Otomasyon Motoru:** Kuralları ve ML tahminlerini kullanarak cihazları kontrol eder
5. **Simülasyon Araçları:** Sistemin test edilmesi için sanal bir ortam sağlar

## Teknoloji Yığını

- **Programlama Dili:** Python 3.8+
- **Veri İşleme:** Pandas, NumPy
- **Makine Öğrenmesi:** Scikit-learn
- **Görselleştirme:** Matplotlib, Seaborn
- **Entegrasyon:** RESTful API (opsiyonel uygulama için)

## Daha Detaylı Dokümantasyon

- [Sistem Gereksinimleri](system_requirements.md)
- [Kurulum ve Yapılandırma](installation.md)
- [Sensörler ve Cihazlar](sensors_and_devices.md)
- [Veri Yapıları](data_structures.md)
- [Makine Öğrenmesi Modeli](ml_model.md)
- [Otomasyon Kuralları](automation_rules.md)
- [Kullanım Kılavuzu](user_guide.md)
- [Test Sonuçları](test_results.md)

## İletişim

Projenin geliştirilmesi veya katkıda bulunmak için:

- **Geliştirici:** [Ad Soyad]
- **E-posta:** [e-posta adresi]