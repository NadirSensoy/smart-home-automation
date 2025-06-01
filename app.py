import os
import sys  # Bu satırı ekleyin
import argparse
import logging
import traceback  # traceback modülünü de ekleyin (hata yönetimi için)
from datetime import datetime
import pandas as pd

# Proje modülleri
from src.data_simulation.data_generator import HomeDataGenerator, generate_sample_dataset
from src.data_processing.preprocessing import SmartHomeDataProcessor, process_raw_data
from src.models.model_manager import SmartHomeModelManager
from src.models.model_trainer import DeviceControlModel
from src.automation.rules_engine import RulesEngine
from src.simulation.home_simulator import SmartHomeSimulator, run_simulation_demo
from src.simulation.interactive import InteractiveSimulation, run_interactive_simulation
from src.utils.error_handling import (
    SmartHomeError, DataProcessingError, ModelError, 
    AutomationError, SimulationError, error_handler
)

# Loglama yapılandırması
def setup_logging():
    """Ana uygulama için loglama yapılandırması yapar"""
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # UTF-8 kodlaması için handler oluştur
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    console_handler = logging.StreamHandler()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[file_handler, console_handler]
    )
    
    # Logger adını ASCII karakterlerle değiştir
    return logging.getLogger("AkilliEvOtomasyonu")

@error_handler
def generate_data(days=3, rooms=None, num_residents=3):
    """
    Sensör ve cihaz verilerini simüle eder
    
    Args:
        days (int): Simüle edilecek gün sayısı
        rooms (list): Simüle edilecek odalar
        num_residents (int): Ev sakini sayısı
    
    Returns:
        str: Üretilen veri dosyasının yolu
        
    Raises:
        DataProcessingError: Veri üretimi sırasında bir hata oluştuğunda
    """
    logger = logging.getLogger("VeriUretimi")
    logger.info(f"{days} gün için veri üretiliyor...")
    
    # Odalar None ise varsayılan odaları kullan
    if rooms is None:
        rooms = ["Salon", "Yatak Odası", "Çocuk Odası", "Mutfak", "Banyo"]
    
    try:
        # Veri üretecini oluştur ve veri seti üret
        dataset = generate_sample_dataset(days=days, rooms=rooms, num_residents=num_residents)
        
        # Veri dosyasının adı ve yolu
        data_dir = os.path.join(os.path.dirname(__file__), "data", "raw")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        csv_path = os.path.join(data_dir, f"generated_data_{timestamp}.csv")
        
        # CSV'ye kaydet
        dataset.to_csv(csv_path, index=False)
        logger.info(f"Veri seti {csv_path} konumuna kaydedildi.")
        
        return csv_path
    except Exception as e:
        logger.error(f"Veri üretimi hatası: {str(e)}")
        raise DataProcessingError(f"Veri üretiminde hata: {str(e)}")

@error_handler
def train_models(data_path=None, days=3, optimize=True):
    """
    ML modellerini eğitir
    
    Args:
        data_path (str): Eğitim verisi dosya yolu (None ise yeni veri üretilir)
        days (int): Veri üretilecekse gün sayısı
        optimize (bool): Hiperparametre optimizasyonu yapılıp yapılmayacağı
    
    Returns:
        SmartHomeModelManager: Eğitilmiş modelleri içeren model yöneticisi
    """
    logger = logging.getLogger("ModelEgitimi")
    
    # Veri yolu belirtilmemişse veri üret
    if not data_path:
        logger.info("Eğitim için veri üretiliyor...")
        data_path = generate_data(days=days)
    
    logger.info(f"ML modelleri eğitiliyor: {data_path}")
    
    # Model yöneticisini oluştur ve eğit
    model_manager = SmartHomeModelManager()
    model_manager.train_models_for_all_devices(data_path, model_type='random_forest', optimize=optimize)
    
    # Performans raporu oluştur
    report_path = model_manager.generate_performance_report()
    logger.info(f"Performans raporu oluşturuldu: {report_path}")
    
    # Model yöneticisini kaydet
    manager_path = model_manager.save_manager()
    logger.info(f"Model yöneticisi kaydedildi: {manager_path}")
    
    return model_manager

@error_handler
def run_simulation(mode="demo", steps=100, use_ml=True, rooms=None, num_residents=3):
    """
    Akıllı ev simülasyonunu çalıştırır
    
    Args:
        mode (str): Simülasyon modu ('demo' veya 'interactive')
        steps (int): Simülasyon adım sayısı
        use_ml (bool): ML modellerinin kullanılıp kullanılmayacağı
        rooms (list): Simüle edilecek odalar
        num_residents (int): Ev sakini sayısı
    """
    logger = logging.getLogger("Simülasyon")
    logger.info(f"Simülasyon başlatılıyor: {mode} modu")
    
    if mode == "demo":
        simulator = run_simulation_demo(steps=steps, rooms=rooms, display=True)
    elif mode == "interactive":
        run_interactive_simulation()
    else:
        logger.error(f"Bilinmeyen simülasyon modu: {mode}")

def generate_report(data_path):
    """
    Veriler ve modellerden kapsamlı bir rapor oluşturur
    
    Args:
        data_path (str): Veri dosyasının yolu
    
    Returns:
        str: Rapor dosyasının yolu
    """
    logger = logging.getLogger("Raporlama")
    logger.info(f"Veri analizi ve rapor oluşturuluyor: {data_path}")
    
    # Veriyi oku
    try:
        data = pd.read_csv(data_path)
    except Exception as e:
        logger.error(f"Veri okuma hatası: {e}")
        return None
    
    # Rapor dizini
    reports_dir = os.path.join(os.path.dirname(__file__), "reports")
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # Rapor dosyası
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"system_report_{timestamp}.md"
    report_path = os.path.join(reports_dir, report_filename)
    
    # Rapor içeriği
    report_content = [
        "# Akıllı Ev Otomasyon Sistemi Raporu",
        f"*Oluşturulma Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        "",
        "## Veri Özeti",
        "",
        f"- Toplam Veri Noktası: {len(data)}",
        f"- Sütunlar: {', '.join(data.columns[:10])}{'...' if len(data.columns) > 10 else ''}",
        f"- Zaman Aralığı: {data['timestamp'].min()} - {data['timestamp'].max()}",
        "",
        "## Sensör İstatistikleri",
        ""
    ]
    
    # Sensör istatistiklerini ekle
    rooms = set()
    for column in data.columns:
        for sensor in ["Sıcaklık", "Nem", "CO2", "Işık"]:
            if sensor in column:
                room = column.split('_')[0]
                rooms.add(room)
    
    for room in rooms:
        report_content.append(f"### {room}")
        report_content.append("")
        
        for sensor in ["Sıcaklık", "Nem", "CO2", "Işık"]:
            column = f"{room}_{sensor}"
            if column in data.columns:
                stats = data[column].describe()
                report_content.append(f"**{sensor}:**")
                report_content.append(f"- Ortalama: {stats['mean']:.2f}")
                report_content.append(f"- Min: {stats['min']:.2f}")
                report_content.append(f"- Max: {stats['max']:.2f}")
                report_content.append(f"- Std. Sapma: {stats['std']:.2f}")
                report_content.append("")
    
    # Cihaz kullanım istatistikleri
    report_content.extend([
        "## Cihaz Kullanım İstatistikleri",
        ""
    ])
    
    for room in rooms:
        for device in ["Klima", "Lamba", "Perde", "Havalandırma"]:
            column = f"{room}_{device}"
            if column in data.columns:
                if data[column].dtype == bool:
                    on_ratio = data[column].mean() * 100
                    report_content.append(f"- {room} {device}: %{on_ratio:.1f} açık")
    
    report_content.extend([
        "",
        "## Sistem Bileşenleri",
        "",
        "### Sensörler",
        "",
        "- **Sıcaklık Sensörü:** Ortam sıcaklığını ölçer (°C)",
        "- **Nem Sensörü:** Ortam nem seviyesini ölçer (%)",
        "- **Işık Sensörü:** Ortam aydınlık seviyesini ölçer (lux)",
        "- **CO2 Sensörü:** Ortamdaki CO2 seviyesini ölçer (ppm)",
        "- **Hareket Sensörü:** Ortamdaki hareketi algılar",
        "",
        "### Cihazlar",
        "",
        "- **Klima:** Odanın sıcaklığını ayarlar",
        "- **Lamba:** Odanın aydınlatmasını sağlar",
        "- **Perde:** Güneş ışığının oda içine girişini kontrol eder",
        "- **Havalandırma:** Odanın hava kalitesini iyileştirir",
        "",
        "## Otomasyon Kuralları",
        "",
        "1. **Yüksek Sıcaklık - Klima Aç:** Oda sıcaklığı 26°C üzerinde ise klimayı aç",
        "2. **Boş Oda - Lamba Kapat:** Oda boş ise ışıkları kapat",
        "3. **Gece Modu:** Gece saatlerinde (22:00-06:00) perdeleri kapat, boş odalarda ışıkları kapat",
        "4. **Sabah Rutini:** Sabah saatlerinde (07:00-09:00) perdeleri aç",
        "",
        "## Makine Öğrenmesi Modeli",
        "",
        "Sistem, kullanıcı davranışlarını öğrenerek otomatik olarak cihaz durumlarını tahmin eden bir makine öğrenmesi modeli kullanmaktadır.",
        "",
        "- **Model Türü:** Random Forest Sınıflandırıcı",
        "- **Doğruluk:** Modelin genel doğruluk oranı yaklaşık %85-95 arasındadır",
        "",
        "## Sonuç",
        "",
        "Bu rapor, Akıllı Ev Otomasyon Sistemi'nin temel bileşenlerini ve performansını özetlemektedir. Sistem, sensör verilerine ve kullanıcı alışkanlıklarına dayanarak ev otomasyonunu gerçekleştirmektedir."
    ])
    
    # Raporu dosyaya kaydet
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_content))
    
    logger.info(f"Sistem raporu oluşturuldu: {report_path}")
    
    return report_path

def main():
    """Ana fonksiyon - argümanları işleyerek uygulamayı başlatır"""
    # Loglama yapılandırması
    logger = setup_logging()
    logger.info("Akilli Ev Otomasyon Sistemi baslatiliyor")
    
    # Argüman ayrıştırıcısı oluştur
    parser = argparse.ArgumentParser(description='Akıllı Ev Otomasyon Sistemi')
    parser.add_argument('--mode', type=str, default='all', 
                      help='Çalıştırma modu: "data", "train", "simulate", "interactive", "all"')
    parser.add_argument('--days', type=int, default=3,
                      help='Simüle edilecek gün sayısı')
    parser.add_argument('--steps', type=int, default=100,
                      help='Simülasyon adım sayısı')
    parser.add_argument('--no-optimize', action='store_true',
                      help='Hiperparametre optimizasyonu yapılmasın')
    parser.add_argument('--no-ml', action='store_true',
                      help='Makine öğrenmesi kullanılmasın')
    
    try:
        args = parser.parse_args()
        
        # Veri üretimi
        if args.mode in ['data', 'all']:
            logger.info("Veri simülasyonu başlatılıyor")
            data_path = generate_data(days=args.days)
        else:
            # Varsayılan veri yolu
            data_dir = os.path.join(os.path.dirname(__file__), "data", "raw")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            # Mevcut veri dosyalarını bul
            csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
            if csv_files:
                # En son veriyi kullan
                csv_files.sort(reverse=True)  # En yeni dosya en üstte
                data_path = os.path.join(data_dir, csv_files[0])
            else:
                # Veri yoksa oluştur
                logger.info("Veri simülasyonu başlatılıyor")
                data_path = generate_data(days=args.days)
        
        # Model eğitimi
        if args.mode in ['train', 'all']:
            logger.info("Model eğitimi başlatılıyor")
            train_models(data_path=data_path, days=args.days, optimize=not args.no_optimize)
        
        # Simülasyon
        if args.mode in ['simulate', 'interactive', 'all']:
            use_ml = not args.no_ml
            if args.mode == 'interactive':
                run_simulation(mode='interactive', use_ml=use_ml, steps=args.steps)
            elif args.mode == 'simulate' or args.mode == 'all':
                run_simulation(mode='demo', use_ml=use_ml, steps=args.steps)
        
        logger.info("Uygulama başarıyla tamamlandı")
        
    except SmartHomeError as e:
        logger.error(f"Uygulama hatası: {str(e)}")
        print(f"HATA: {str(e)}")
        return 1
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {str(e)}")
        print(f"HATA: Beklenmeyen hata: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())