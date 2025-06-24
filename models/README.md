# 🤖 Modeller Klasörü

Bu klasör, eğitilmiş makine öğrenmesi modellerini içerir.

## 📁 Klasör Yapısı

- **`trained/`** - Eğitilmiş ML model dosyaları (.joblib formatında)
- **Model yönetim dosyaları** - Model metadata ve performans bilgileri

## 🎯 Model Türleri

Sistem 13 farklı cihaz için ayrı modeller eğitir:
- Salon: Klima, Lamba, Perde, Havalandırma
- Yatak Odası: Klima, Lamba, Perde, Havalandırma  
- Mutfak: Klima, Lamba, Havalandırma
- Banyo: Lamba, Havalandırma
- Çocuk Odası: Klima, Lamba, Perde

## 📝 Not

Modeller sistem tarafından otomatik olarak eğitilir ve kaydedilir. İlk çalıştırmada bu klasör boştur ve sistem çalıştıkça dolar.
