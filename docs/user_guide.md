# Akıllı Ev Otomasyon Sistemi Kullanım Rehberi

Bu rehber, Akıllı Ev Otomasyon Sistemi'nin nasıl kullanılacağını adım adım açıklar.

## Kurulum

Projeyi çalıştırmadan önce bağımlılıkları yüklemeniz gerekir:

```bash
pip install -r requirements.txt
```

Ya da paket olarak yüklemek için:

```bash
pip install -e .
```

## Temel Kullanım

Akıllı Ev Otomasyon Sistemi'ni temel olarak dört farklı modda çalıştırabilirsiniz:

1. **Veri Üretimi Modu**: Sensör ve cihaz verileri simülasyonu
2. **Model Eğitimi Modu**: ML modellerinin eğitilmesi
3. **Simülasyon Modu**: Akıllı ev simülasyonu
4. **İnteraktif Mod**: Kullanıcı etkileşimli simülasyon

### 1. Temel Çalıştırma

Tüm adımları otomatik çalıştırmak için:

```bash
python app.py
```

Bu komut sırayla veri üretimi, model eğitimi ve simülasyonu çalıştırır.

### 2. Veri Üretimi

Sadece veri üretmek için:

```bash
python app.py --mode data --days 5
```

Bu komut 5 günlük sensör ve cihaz verisi üretir ve `data/raw/` dizinine kaydeder.

### 3. Model Eğitimi

Sadece modelleri eğitmek için:

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
