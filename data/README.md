# 📊 Veri Klasörü

Bu klasör, Akıllı Ev Otomasyon Sistemi'nin veri dosyalarını içerir.

## 📁 Klasör Yapısı

- **`raw/`** - Ham sensör verileri ve sistem tarafından toplanan orijinal veriler
- **`processed/`** - İşlenmiş, temizlenmiş ve özellik mühendisliği uygulanmış veriler  
- **`simulation/`** - Simülasyon çalıştırması sonucu oluşturulan geçmiş verileri

## 🔄 Veri Akışı

```
Ham Veriler (raw/) → İşleme → İşlenmiş Veriler (processed/) → ML Modeli → Sonuçlar
```

## 📝 Not

Bu klasörler sistem çalıştırıldıkça otomatik olarak doldurulacaktır. Manuel olarak dosya eklemeniz gerekmez.
