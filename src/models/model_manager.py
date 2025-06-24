import os
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import json
import warnings
import logging

from src.models.model_trainer import DeviceControlModel
from src.data_processing.preprocessing import process_raw_data

class SmartHomeModelManager:
    """
    Akıllı ev sistemi için tüm cihazların makine öğrenmesi modellerini yöneten sınıf.
    Model eğitimi, değerlendirme ve tahmin işlemlerini koordine eder.
    """
    
    def __init__(self):
        """SmartHomeModelManager sınıfını başlatır"""
        self.models = {}  # device_name -> DeviceControlModel
        self.preprocessor = None
        self.performance_summary = {}
        self.performance_data = []  # Initialize performance_data as an empty list
        self.logger = logging.getLogger(__name__)
    
    def train_models_for_all_devices(self, csv_path, model_type='random_forest', optimize=False):
        """Tüm cihazlar için ML modelleri eğitiyor"""
        self.logger.info(f"Tüm cihazlar için {model_type} modelleri eğitiliyor...")
        # Load the raw DataFrame
        df_raw = pd.read_csv(csv_path)
        # Get train/test splits and targets from process_raw_data
        df_train, df_test, y_train_dict, y_test_dict, preprocessor = process_raw_data(
            csv_path, save_processed=True
        )
        self.preprocessor = preprocessor
        # Get the indices of the train/test splits
        train_indices = df_train.index
        test_indices = df_test.index
        # Use these indices to select from the raw DataFrame
        X_train_raw = df_raw.loc[train_indices]
        X_test_raw = df_raw.loc[test_indices]
        # Modelleri eğit ve değerlendir
        for device_name, y_train in y_train_dict.items():
            model = DeviceControlModel(device_name, model_type)
            # Do NOT pass preprocessor=preprocessor; let the model fit its own on the raw train split
            print("DEBUG: Columns passed to train:", X_train_raw.columns.tolist())
            model.train(X_train_raw, y_train, optimize=optimize)
            metrics = model.evaluate(X_test_raw, y_test_dict[device_name])
            # Değerlendirme başarısız olsa bile devam et
            # metrics sözlüğünde 'accuracy' anahtarı varsa kullan
            if metrics and 'accuracy' in metrics:
                performance_data = {
                    'device_name': device_name,
                    'model_type': model_type,
                    'accuracy': metrics['accuracy'],
                    'precision': metrics.get('precision', None),
                    'recall': metrics.get('recall', None),
                    'f1': metrics.get('f1', None),
                    'auc': metrics.get('auc', None),
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                self.performance_data.append(performance_data)
                # Store metrics in performance_summary for reporting
                self.performance_summary[device_name] = {
                    'accuracy': metrics['accuracy'],
                    'precision': metrics.get('precision', 0),
                    'recall': metrics.get('recall', 0),
                    'f1': metrics.get('f1', 0),
                    'auc': metrics.get('auc', 0)
                }
            else:
                # Değerlendirme başarısız olduysa basit bir kayıt ekle
                performance_data = {
                    'device_name': device_name,
                    'model_type': model_type,
                    'error': metrics.get('error', 'Unknown error'),
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                self.performance_data.append(performance_data)            # Modeli kaydet
            try:
                model.save_model()
            except Exception as e:
                self.logger.error(f"Model kaydetme hatası: {e}")
            # Add model to self.models before deleting the local variable
            self.models[device_name] = model
    
    def predict_device_states(self, X):
        """Predict device states using the pipeline for all models."""
        predictions = {}
        for device_name, model in self.models.items():
            try:
                pred = model.predict(X)
                # Handle both 1D and 2D prediction arrays
                if hasattr(pred, 'shape') and len(pred.shape) > 0:
                    prediction_value = pred[0] if pred.shape[0] > 0 else False
                else:
                    prediction_value = pred
                
                # Get prediction probabilities
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(X)
                    # Handle probability array shape
                    if hasattr(proba, 'shape') and len(proba.shape) == 2:
                        prob = proba[0, 1] if proba.shape[1] > 1 else proba[0, 0]
                    elif hasattr(proba, 'shape') and len(proba.shape) == 1:
                        prob = proba[0] if proba.shape[0] > 0 else 0.0
                    else:
                        prob = float(proba) if proba is not None else 0.0
                else:
                    prob = 1.0 if prediction_value else 0.0
                    
                predictions[device_name] = {
                    'state': bool(prediction_value),
                    'probability': float(prob),
                    'source': 'pipeline'
                }
            except Exception as e:
                self.logger.error(f"Error predicting for {device_name}: {str(e)}")
                predictions[device_name] = {
                    'state': False,
                    'probability': 0.0,
                    'error': str(e),
                    'source': 'default'
                }
        return predictions
    
    def save_manager(self, directory=None):
        """
        Model yöneticisini kaydeder
        
        Args:
            directory (str): Kaydedilecek dizin
            
        Returns:
            str: Model yöneticisi dosyasının tam yolu
        """
        if directory is None:
            directory = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models")
        
        # Dizin yoksa oluştur
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Dosya adı
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        manager_filename = f"model_manager_{timestamp}.json"
        manager_path = os.path.join(directory, manager_filename)
        
        # Kaydedilecek model bilgileri
        models_info = {}
        for device_name, model in self.models.items():
            # Her model için dosya yolu
            model_path = model.save_model(os.path.join(directory, "trained"))
            
            models_info[device_name] = {
                'model_path': model_path,
                'model_type': model.model_type,
                'accuracy': model.metrics.get('accuracy', 0),
                'last_training_time': model.last_training_time.isoformat() if model.last_training_time else None
            }
        
        # Yönetici bilgilerini kaydet
        manager_info = {
            'models': models_info,
            'performance_summary': self.performance_summary,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(manager_path, 'w') as f:
            json.dump(manager_info, f, indent=4)
        
        self.logger.info(f"Model yöneticisi {manager_path} konumuna kaydedildi")
        
        return manager_path
    
    @classmethod
    def load_manager(cls, manager_path):
        """
        Kaydedilmiş model yöneticisini yükler
        
        Args:
            manager_path (str): Model yöneticisi dosya yolu
            
        Returns:
            SmartHomeModelManager: Yüklenmiş model yöneticisi
        """
        # JSON dosyasını yükle
        with open(manager_path, 'r') as f:
            manager_info = json.load(f)
        
        # Yeni model yöneticisi oluştur
        manager = cls()
        
        # Performans özetini yükle
        manager.performance_summary = manager_info['performance_summary']
        
        # Her cihaz için modeli yükle
        for device_name, model_info in manager_info['models'].items():
            model_path = model_info['model_path']
            if os.path.exists(model_path):
                model = DeviceControlModel.load_model(model_path)
                manager.models[device_name] = model
            else:
                manager.logger.warning(f"Uyarı: {model_path} konumunda model bulunamadı, {device_name} için model yüklenemedi.")
        
        manager.logger.info(f"{manager_path} konumundan model yöneticisi yüklendi - {len(manager.models)} model içeriyor")
        
        return manager
    
    def generate_performance_report(self, output_dir=None, include_plots=True):
        """
        Modellerin performans raporunu oluşturur
        
        Args:
            output_dir (str): Çıktı dizini
            include_plots (bool): Grafiklerin dahil edilip edilmeyeceği
            
        Returns:
            str: Rapor dosyasının tam yolu
        """
        if not self.models:
            raise ValueError("Henüz hiçbir model eğitilmemiş")
        
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports")
        
        # Dizin yoksa oluştur
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Rapor dosyası
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"performance_report_{timestamp}.md"
        report_path = os.path.join(output_dir, report_filename)
        
        # Rapor başlığı
        report = [
            "# Akıllı Ev Otomasyon Sistemi - Model Performans Raporu",
            f"*Oluşturulma Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            "## Genel Bakış",
            "",
            f"- Toplam Model Sayısı: {len(self.models)}",
            f"- Model Türleri: {set([model.model_type for model in self.models.values()])}",
            "",
            "## Model Performans Özeti",
            "",
            "| Cihaz | Doğruluk | Kesinlik | Duyarlılık | F1 Skoru | AUC (ikili) |",
            "|-------|----------|----------|------------|----------|-------------|"
        ]
        
        # Her cihaz için performans özeti
        for device_name, metrics in self.performance_summary.items():
            auc = f"{metrics.get('auc', '-'):.4f}" if 'auc' in metrics else '-'
            report.append(
                f"| {device_name} | {metrics['accuracy']:.4f} | {metrics['precision']:.4f} | "
                f"{metrics['recall']:.4f} | {metrics['f1']:.4f} | {auc} |"
            )
        
        report.append("")
        
        # Model detayları
        report.append("## Model Detayları")
        report.append("")
        
        for device_name, model in self.models.items():
            report.append(f"### {device_name}")
            report.append("")
            report.append(f"- Model Türü: {model.model_type}")
            report.append(f"- Eğitim Tarihi: {model.last_training_time.strftime('%Y-%m-%d %H:%M:%S') if model.last_training_time else 'Bilinmiyor'}")
            
            if model.best_params:
                report.append("- En İyi Parametreler:")
                for param, value in model.best_params.items():
                    report.append(f"  - {param}: {value}")
            
            report.append("")
            
            # Karmaşıklık matrisi ve diğer grafikler
            if include_plots:
                # Görsel dizini
                plots_dir = os.path.join(output_dir, "plots")
                if not os.path.exists(plots_dir):
                    os.makedirs(plots_dir)
                
                # Karmaşıklık matrisi
                cm_path = os.path.join(plots_dir, f"{device_name}_confusion_matrix.png")
                try:
                    model.plot_confusion_matrix(save_path=cm_path)
                    report.append(f"![{device_name} Karmaşıklık Matrisi](plots/{os.path.basename(cm_path)})")
                    report.append("")
                except Exception as e:
                    report.append(f"*Karmaşıklık matrisi oluşturulamadı: {e}*")
                    report.append("")
                
                # İkili sınıflandırma ise ROC eğrisi
                if len(model.classes) == 2 and 'roc' in model.metrics:
                    roc_path = os.path.join(plots_dir, f"{device_name}_roc_curve.png")
                    try:
                        model.plot_roc_curve(save_path=roc_path)
                        report.append(f"![{device_name} ROC Eğrisi](plots/{os.path.basename(roc_path)})")
                        report.append("")
                    except Exception as e:
                        report.append(f"*ROC eğrisi oluşturulamadı: {e}*")
                        report.append("")
                
                # Özellik önemi
                if hasattr(model.model, 'feature_importances_'):
                    fi_path = os.path.join(plots_dir, f"{device_name}_feature_importance.png")
                    try:
                        model.plot_feature_importance(save_path=fi_path)
                        report.append(f"![{device_name} Özellik Önemi](plots/{os.path.basename(fi_path)})")
                        report.append("")
                    except Exception as e:
                        report.append(f"*Özellik önemi grafiği oluşturulamadı: {e}*")
                        report.append("")
            
            report.append("---")
            report.append("")
        
        # Raporu dosyaya yaz
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        self.logger.info(f"Performans raporu {report_path} konumuna kaydedildi")
        
        return report_path

    def get_expected_feature_names(self):
        """
        Get the feature names expected by the models
        
        Returns:
            list: List of feature names or None if not available
        """
        if not self.models:
            self.logger.warning("No models available to extract feature names")
            return None
        
        # Try to get feature names from any model
        for device_name, model in self.models.items():
            if hasattr(model, 'model'):
                # Check for feature_names_in_ attribute directly
                if hasattr(model.model, 'feature_names_in_'):
                    return model.model.feature_names_in_.tolist()
                
                # Check for feature_names in pipeline steps
                if hasattr(model.model, 'steps'):
                    for step_name, step in model.model.steps:
                        if hasattr(step, 'feature_names_in_'):
                            return step.feature_names_in_.tolist()
                        if hasattr(step, 'get_feature_names_out'):
                            try:
                                return step.get_feature_names_out().tolist()
                            except:
                                pass
            
            # Try checking model.preprocessor if available
            if hasattr(model, 'preprocessor') and model.preprocessor:
                if hasattr(model.preprocessor, 'feature_names_'):
                    return model.preprocessor.feature_names_
        
        self.logger.warning("Could not extract feature names from any model")
        return None

# Modelleri test etmek ve performans raporu oluşturmak için fonksiyon
def test_model_manager():
    """
    Model yöneticisini test eder
    """
    import os
    
    # Örnek veri dosyasını bul
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    data_dir = os.path.join(base_dir, "data", "raw")
    
    # İlk CSV dosyasını al
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    if not csv_files:
        print("Test için CSV dosyası bulunamadı!")
        return
    
    csv_path = os.path.join(data_dir, csv_files[0])
    
    # Model yöneticisini oluştur ve modelleri eğit
    manager = SmartHomeModelManager()
    manager.train_models_for_all_devices(csv_path, model_type='random_forest', optimize=True)
    
    # Performans raporu oluştur
    report_path = manager.generate_performance_report()
    
    # Model yöneticisini kaydet
    manager_path = manager.save_manager()
    
    # Model yöneticisini yükle ve test et
    loaded_manager = SmartHomeModelManager.load_manager(manager_path)
    
    # Örneki tahmin testi
    # Veri işleme
    X_train, X_test, y_train_dict, y_test_dict, _ = process_raw_data(csv_path, save_processed=False)
    
    # İlk satırı tahmin için kullan
    sample_features = X_test.iloc[[0]]
    predictions = loaded_manager.predict_device_states(sample_features)
    
    print("\nCihaz Durumu Tahminleri:")
    for device, prediction in predictions.items():
        print(f"{device}: {prediction['state']} (güven: {prediction['probability']:.4f})")
    
    return loaded_manager

if __name__ == "__main__":
    test_model_manager()