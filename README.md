# Akıllı Ev Otomasyon Sistemi

Makine öğrenmesi tabanlı akıllı ev otomasyon sistemi, ev içindeki sensör verilerini analiz ederek cihazların otomatik kontrolünü sağlar.

## Özellikler

- Sensör verilerinin gerçekçi simülasyonu
- Kullanıcı davranışlarının analizi ve öğrenilmesi
- Enerji tüketiminin tahmin edilmesi ve optimize edilmesi
- Kural tabanlı ve makine öğrenmesi tabanlı otomasyon
- Görsel simülasyon ve raporlama araçları

## Kurulum

Gerekli bağımlılıkları yüklemek için:

```bash
pip install -r requirements.txt
```

Ya da paket olarak kurmak için:

```bash
pip install -e .
```

## Kullanım

Ana uygulamayı çalıştırmak için:

```bash
python app.py
```

Farklı modlarda çalıştırmak için:

```bash
# Sadece veri üretimi
python app.py --mode data --days 5

# Sadece model eğitimi
python app.py --mode train --no-optimize

# Sadece simülasyon
python app.py --mode simulate --steps 200

# İnteraktif simülasyon
python app.py --mode interactive
```

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