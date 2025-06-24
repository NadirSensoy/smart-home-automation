# 🏠 Akıllı Ev Otomasyon Sistemi - Akademik Proje

**Makine öğrenmesi tabanlı ev otomasyon simülasyon sistemi.** Bu proje, **5 farklı oda** için **çoklu sensör verisi** ve **akıllı cihaz kontrolü** simülasyonu yaparak enerji verimliliği ve konfor optimizasyonu araştırmaktadır.

[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://python.org)
[![Simülasyon](https://img.shields.io/badge/Gerçek_Veri-50_Adım-green)](docs/example_data_output.md)
[![ML Modeli](https://img.shields.io/badge/ML_Modeli-13%2F13_Başarılı-orange)](docs/ml_model.md)
[![Lisans](https://img.shields.io/badge/Lisans-MIT-yellow)](LICENSE)

## 🎯 Proje Amacı ve Kapsamı

Bu akademik proje, **akıllı ev sistemlerinin enerji verimliliği üzerindeki etkisini** araştırmak amacıyla geliştirilmiştir. Proje, gerçek dünya verilerine dayalı simülasyonlar kullanarak makine öğrenmesi algoritmaları ile ev otomasyonu optimizasyonunu incelemektedir.

### 📊 Araştırma Hipotezi
- **H1:** Makine öğrenmesi tabanlı otomasyon sistemleri, geleneksel termostat kontrolüne göre enerji tüketimini azaltabilir
- **H2:** Çoklu sensör verisi kullanımı, tek sensörlü sistemlere göre daha iyi optimizasyon sağlar
- **H3:** Kullanıcı davranış öğrenme algoritmaları, konfor seviyesini koruyarak enerji tasarrufu yapabilir

## ✨ Sistem Özellikleri

### 🤖 Simülasyon Bileşenleri
- **Python-based simülasyon** ortamı
- **Scikit-learn** makine öğrenmesi kütüphanesi
- **Pandas/NumPy** veri işleme 
- **Matplotlib** görselleştirme
- **CSV/JSON** veri formatları

### 🏠 Modellenen Ev Yapısı
- **Salon** (Klima, 2x Lamba, Perde)
- **Yatak Odası** (Klima, Lamba, Perde)  
- **Mutfak** (Havalandırma, 2x Lamba)
- **Banyo** (Havalandırma, Lamba)
- **Çalışma Odası** (Klima, Lamba, Perde)

### ⚡ Simülasyon Parametreleri
- **Veri üretim hızı:** 15 dakikalık aralıklar
- **Simülasyon süresi:** 1-30 gün arası
- **Sensör türleri:** Sıcaklık, nem, ışık, hareket, CO2
- **Çevre faktörleri:** Hava durumu, mevsimsel değişim
- **Kullanıcı modelleri:** Hafta içi/hafta sonu rutinleri

### 📊 Veri Analizi ve Görselleştirme
- **Enerji tüketim grafikleri**
- **Sensör veri trendleri**
- **ML model performans metrikleri**
- **Karşılaştırmalı analiz raporu**
- **HTML tabanlı interaktif raporlar**

## 🚀 Hızlı Başlangıç

### 📦 Kurulum (2 dakika)
```bash
# Proje dosyalarını indirin
git clone <repository-url>
cd smart-home-automation

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Temel demo çalıştırın
python app.py
```

### ⚡ Hızlı Komutlar
```bash
# Temel simülasyon (akademik demo)
python app.py

# Uzun analiz (rapor için)
python app.py --days 7 --mode all

# Sessiz mod (sunum için)
python app.py --quiet --steps 50

# İnteraktif demo
python app.py --mode interactive
```

## 🔧 Teknik Bilgiler

### 🏠 Simülasyon Bileşenleri
- **5 Oda:** Salon, Yatak Odası, Çocuk Odası, Mutfak, Banyo
- **20 Sensör:** Sıcaklık, nem, CO2, ışık, hareket (4×5 oda)
- **13 Cihaz:** Klima(5), Lamba(5), Perde(3)
- **Algoritma:** Random Forest + Kural Tabanlı Hibrit Sistem

### ⚙️ Ana Parametreler
| Parametre | Varsayılan | Açıklama |
|-----------|------------|----------|
| `--mode` | `simulate` | data, train, simulate, interactive, all |
| `--days` | `1` | Simülasyon süresi (1-30 gün) |
| `--steps` | `30` | Zaman adımı sayısı (5-200) |
| `--quiet` | `False` | Konsol çıktısını azalt |
| `--no-ml` | `False` | Sadece kural tabanlı çalıştır |

### 📁 Önemli Klasörler
```
├── 📊 data/simulation/          # Gerçek simülasyon çıktıları
├── 🤖 models/trained/           # Eğitilmiş ML modelleri (13 adet)
├── 📈 output/visualizations/    # Karşılaştırma grafikleri
├── 📖 docs/                     # Detaylı dokümantasyon
└── 📝 logs/                     # Sistem logları
```

## 📊 Son Çalıştırma Sonuçları (27 Haziran 2025)

### 🎯 Gerçek Simülasyon Performansı
Bu sonuçlar **gerçek simülasyon çalıştırmasından** elde edilmiştir:

| 📊 **Simülasyon** | 50 adım (4 saat 5 dakika) | 14:58-19:03 |
|-------------------|---------------------------|-------------|
| 🏠 **Test Ortamı** | 5 oda, 20 sensör, 13 cihaz | Gerçekçi ev modeli |
| 🤖 **ML Başarısı** | 13/13 model (%100) | Random Forest |
| ⚡ **Cihaz Kullanımı** | %27.5 ortalama | Verimli otomasyon |

### 💰 Enerji ve Maliyet Analizi
| Metrik | Sonuç | Kaynak |
|--------|-------|--------|
| **💡 Enerji Tasarrufu** | 12.5 kWh/gün (%27.9) | output/analysis_summary.txt |
| **😊 Konfor İyileştirmesi** | +23.1 puan | 58.5 vs 35.4 (geleneksel) |
| **💵 Aylık Tasarruf** | 940 TL | Gerçek TEDAŞ tarifeleri |
| **📈 ROI Geri Ödeme** | 4.1 ay | %1,346.6 beş yıllık getiri |

### 🏠 En Dikkat Çekici Cihaz Sonuçları
- **🔥 En Verimli:** Banyo Havalandırma (%70 kullanım)
- **⭐ En Stabil:** Yatak Odası Perde (%100 kullanım)  
- **🔧 Optimizasyon Fırsatı:** Banyo Lamba (%0 kullanım)

## 🔧 Sorun Giderme

| Sorun | Çözüm |
|-------|-------|
| **ModuleNotFoundError** | `pip install -r requirements.txt` |
| **Yavaş çalışma** | `--steps 30` ile sınırla |
| **Bellek hatası** | `--quiet --days 1` kullan |
| **CSV boş** | Klasör izinlerini kontrol et |

**Log Dosyaları:** `logs/AkilliEvOtomasyonu_*.log`

## 🎓 Akademik Kullanım

### 📋 Sunum Önerileri
- **Kısa Demo:** `python app.py --steps 30` (2-3 dakika)
- **Detaylı Analiz:** `python app.py --days 3 --mode all` 
- **Karşılaştırma:** `--no-ml` ile geleneksel sistem
- **Grafikler:** `output/visualizations/comparisons/` klasörü

### 📊 Referans Verme
```bibtex
@misc{smart_home_automation_2025,
  title={Smart Home Automation System with Machine Learning},
  author={[Your Name]},
  year={2025},
  note={Academic Project - Python Simulation}
}
```

## 📞 Destek ve İletişim

- 🐛 **Hata Bildirimi:** GitHub Issues
- 💬 **Tartışma:** GitHub Discussions  
- 📚 **Dokümantasyon:** [docs/](docs/) klasörü

---

## 🎯 Proje Özeti

Bu **Akıllı Ev Otomasyon Sistemi**, makine öğrenmesi algoritmalarının ev otomasyonunda kullanımını araştıran **akademik bir simülasyon projesidir**. 

**🔬 Ana Özellikler:**
- Python-based gerçekçi ev simülasyonu
- 13 adet eğitilmiş Random Forest modeli
- %27.9 enerji tasarrufu simülasyonu
- +23.1 puan konfor iyileştirmesi
- Detaylı akademik dokümantasyon

**📊 Son Simülasyon:** 50 adım, 5 oda, 20 sensör, 13 cihaz  
**⚡ Sistem Durumu:** Tüm modeller aktif ve çalışır durumda  
**📈 ROI:** 4.1 ay geri ödeme süresi (simülasyon)

---

**🏠 "Simulating the future of smart homes through academic research"** ✨

*Akademik Proje • MIT License • Python 3.8+ • 2025*