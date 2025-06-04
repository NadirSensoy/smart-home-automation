import os
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import json
import warnings

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
    
    def train_models_for_all_devices(self, csv_path, model_type='random_forest', optimize=False):
        """Tüm cihazlar için ML modelleri eğitiyor"""
        print(f"Tüm cihazlar için {model_type} modelleri eğitiliyor...")
        
        # Veriyi işle
        X_train, X_test, y_train_dict, y_test_dict, preprocessor = process_raw_data(
            csv_path, save_processed=True
        )
        
        self.preprocessor = preprocessor
        
        # Modelleri eğit ve değerlendir
        for device_name, y_train in y_train_dict.items():
            model = DeviceControlModel(device_name, model_type)
            model.preprocessor = preprocessor
            model.train(X_train, y_train_dict[device_name], optimize=optimize)
            
            # Model değerlendirmesi
            metrics = model.evaluate(X_test, y_test_dict[device_name])
            
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
                self.performance_data.append(performance_data)
            
            # Modeli kaydet
            try:
                model.save_model()
            except Exception as e:
                print(f"Model kaydetme hatası: {e}")
            
            # Add model to self.models before deleting the local variable
            self.models[device_name] = model
    
    def predict_device_states(self, features_df):
        """
        Verilen özelliklere göre tüm cihazların durumlarını tahmin eder
        
        Args:
            features_df (pandas.DataFrame): Özellik değerleri
            
        Returns:
            dict: Cihaz adı -> tahmin edilen durum
        """
        if not self.models:
            raise ValueError("Henüz hiçbir model eğitilmemiş")
        
        predictions = {}
        
        for device_name, model in self.models.items():
            try:
                # First try to match the expected feature names
                model_features = None
                
                # Get expected feature names from the model
                if hasattr(model.model, 'feature_names_in_'):
                    model_features = model.model.feature_names_in_
                
                # If we have model features, try to align the input
                if model_features is not None and len(model_features) > 0:
                    # Create aligned input with zeros for missing features
                    aligned_input = pd.DataFrame(index=features_df.index)
                    
                    # For each expected feature
                    for feature in model_features:
                        if feature in features_df.columns:
                            aligned_input[feature] = features_df[feature]
                        else:
                            # Print information about missing features to help debug
                            print(f"Feature '{feature}' not found in input, using default value 0")
                            aligned_input[feature] = 0
                    
                    # Check if we've accounted for all expected features
                    missing_features = set(model_features) - set(aligned_input.columns)
                    if missing_features:
                        print(f"Warning: Still missing features after alignment: {missing_features}")
                    
                    # Use the aligned input
                    pred = model.predict(aligned_input)
                    pred_proba = model.predict_proba(aligned_input)
                    
                    print(f"Successfully used aligned features for {device_name}")
                else:
                    # Fallback - try using numpy array to bypass feature name checks
                    print(f"No feature names found for {device_name}, attempting direct prediction")
                    
                    # Convert to numpy array to bypass feature name checking
                    X_values = features_df.values
                    pred = model.model.predict(X_values)
                    pred_proba = model.model.predict_proba(X_values)
                
                # Get the first row predictions
                prediction = pred[0]
                probability = np.max(pred_proba[0])
                
                predictions[device_name] = {
                    'state': bool(prediction),
                    'probability': float(probability),
                    'source': 'aligned_features'
                }
                
                print(f"Successfully predicted {device_name}")
                
            except Exception as e:
                print(f"{device_name} için tahmin yapılırken hata oluştu: {e}")
                
                # Try direct approach with model.model as a last resort
                try:
                    if hasattr(model, 'model'):
                        raw_model = model.model
                        if hasattr(raw_model, 'predict'):
                            # Get raw predictions - use numpy array to bypass feature checks
                            raw_pred = raw_model.predict(features_df.values)
                            
                            # Set prediction using raw result
                            state = bool(raw_pred[0])
                            predictions[device_name] = {
                                'state': state,
                                'probability': 1.0 if state else 0.0,
                                'method': 'raw_predict'
                            }
                            print(f"Successfully predicted {device_name} using raw model")
                            continue
                except Exception as inner_error:
                    print(f"Raw prediction failed for {device_name}: {inner_error}")
                
                # Default fallback
                predictions[device_name] = {
                    'state': False,
                    'probability': 0.0,
                    'error': str(e)
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
        
        print(f"Model yöneticisi {manager_path} konumuna kaydedildi")
        
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
                print(f"Uyarı: {model_path} konumunda model bulunamadı, {device_name} için model yüklenemedi.")
        
        print(f"{manager_path} konumundan model yöneticisi yüklendi - {len(manager.models)} model içeriyor")
        
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
        
        print(f"Performans raporu {report_path} konumuna kaydedildi")
        
        return report_path

    def predict_with_feature_bypass(self, X):
        """
        Make predictions while bypassing feature name checks
        
        Args:
            X (pandas.DataFrame): Input features
        
        Returns:
            dict: Predictions for each device
        """
        predictions = {}
        
        # Handle timestamp columns before conversion to numpy array
        if isinstance(X, pd.DataFrame):
            # Convert timestamp columns to numeric features
            for col in X.columns:
                if pd.api.types.is_datetime64_dtype(X[col]) or isinstance(X[col].iloc[0], pd.Timestamp):
                    # Extract useful numeric features from timestamp
                    X[f"{col}_hour"] = X[col].dt.hour
                    X[f"{col}_dayofweek"] = X[col].dt.dayofweek
                    X[f"{col}_day"] = X[col].dt.day
                    X[f"{col}_month"] = X[col].dt.month
                    # Drop original timestamp column
                    X = X.drop(columns=[col])
        
        # Ensure all data is numeric
        if isinstance(X, pd.DataFrame):
            for col in X.columns:
                if not pd.api.types.is_numeric_dtype(X[col]):
                    try:
                        X[col] = pd.to_numeric(X[col], errors='coerce')
                    except:
                        # If conversion fails, replace with zeros
                        X[col] = 0
            
            # Convert to numpy array after cleaning
            X_values = X.values
        else:
            X_values = X
            
        # Predict for each device model
        for device_name, model in self.models.items():
            try:
                # We need to handle the feature count mismatch more directly
                if hasattr(model.model, 'n_features_in_'):
                    expected_feature_count = model.model.n_features_in_
                    
                    # Create a correctly sized input array
                    if X_values.shape[1] != expected_feature_count:
                        # Generate dummy data with the correct shape
                        dummy_data = np.zeros((1, expected_feature_count))
                        
                        # Copy available features into the dummy data
                        features_to_use = min(X_values.shape[1], expected_feature_count)
                        try:
                            dummy_data[0, :features_to_use] = X_values[0, :features_to_use]
                        except (ValueError, TypeError) as e:
                            # Handle any type conversion errors
                            print(f"Error copying features for {device_name}: {e}")
                            # Use zeros as a fallback
                        
                        # Make prediction with properly sized data
                        try:
                            with warnings.catch_warnings():
                                warnings.filterwarnings("ignore", category=UserWarning)
                                
                                if hasattr(model.model, 'predict_proba'):
                                    proba = model.model.predict_proba(dummy_data)
                                    if proba.shape[1] > 1:  # Binary classification
                                        prob = proba[0, 1]  # Probability of class 1
                                    else:
                                        prob = proba[0, 0]
                                    
                                    state = bool(prob > 0.5)
                                    predictions[device_name] = {
                                        'state': state,
                                        'probability': float(prob),
                                        'source': 'feature_padded'
                                    }
                                else:
                                    pred = model.model.predict(dummy_data)[0]
                                    predictions[device_name] = {
                                        'state': bool(pred),
                                        'probability': 1.0 if pred else 0.0,
                                        'source': 'feature_padded'
                                    }
                        except Exception as predict_err:
                            print(f"Error predicting with padded features for {device_name}: {predict_err}")
                            predictions[device_name] = {
                                'state': False,
                                'probability': 0.0,
                                'error': str(predict_err),
                                'source': 'default'
                            }
                    else:
                        # Input already has the right feature count
                        if hasattr(model.model, 'predict_proba'):
                            proba = model.model.predict_proba(X_values)
                            if proba.shape[1] > 1:
                                prob = proba[0, 1]
                            else:
                                prob = proba[0, 0]
                        
                            state = bool(prob > 0.5)
                            predictions[device_name] = {
                                'state': state,
                                'probability': float(prob),
                                'source': 'direct'
                            }
                        else:
                            pred = model.model.predict(X_values)[0]
                            predictions[device_name] = {
                                'state': bool(pred),
                                'probability': 1.0 if pred else 0.0,
                                'source': 'direct'
                            }
                else:
                    # Model doesn't have n_features_in_ attribute
                    # Make a direct prediction and hope for the best
                    if hasattr(model.model, 'predict_proba'):
                        proba = model.model.predict_proba(X_values)
                        prob = proba[0, 1] if proba.shape[1] > 1 else proba[0, 0]
                        state = bool(prob > 0.5)
                        predictions[device_name] = {
                            'state': state,
                            'probability': float(prob),
                            'source': 'direct'
                        }
                    else:
                        pred = model.model.predict(X_values)[0]
                        predictions[device_name] = {
                            'state': bool(pred),
                            'probability': 1.0 if pred else 0.0,
                            'source': 'direct'
                        }
                
            except Exception as e:
                # Log error and provide default prediction
                print(f"Error predicting for {device_name}: {str(e)}")
                predictions[device_name] = {
                    'state': False,
                    'probability': 0.0,
                    'error': str(e),
                    'source': 'default'
                }
                
        return predictions

    def get_expected_feature_names(self):
        """
        Get the feature names expected by the models
        
        Returns:
            list: List of feature names or None if not available
        """
        if not self.models:
            print("No models available to extract feature names")
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
        
        print("Could not extract feature names from any model")
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