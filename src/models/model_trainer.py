import os
import numpy as np
import pandas as pd
import joblib
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report, roc_curve, auc
)
import logging

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_curve, auc
)
from sklearn.pipeline import Pipeline
from src.data_processing.preprocessing import SmartHomeDataProcessor

class DeviceControlModel:
    """
    Akıllı ev cihazlarının durumunu (açık/kapalı) tahmin eden makine öğrenmesi modeli.
    Farklı model türleri ve hiperparametre optimizasyonu imkanı sunar.
    """
    
    def __init__(self, device_name, model_type='random_forest'):
        """
        DeviceControlModel sınıfını başlatır
        
        Args:
            device_name (str): Cihaz adı (ör: "Salon_Klima")
            model_type (str): Kullanılacak model türü ('random_forest', 'gradient_boosting', 
                            'decision_tree', 'logistic_regression', 'svm', 'knn')
        """
        self.device_name = device_name
        self.model_type = model_type
        self.model = None
        self.preprocessor = None
        self.feature_names = None
        self.classes = None
        self.last_training_time = None
        self.best_params = None
        self.metrics = {}
        self.random_state = 42  # Rastgelelik için sabit bir değer
        self.logger = logging.getLogger(__name__)
          # Modeli oluştur
        self._create_model()
    
    def _create_model(self):
        """Belirtilen türde model oluşturur - PERFORMANS OPTIMIZASYONU"""
        if self.model_type == 'random_forest':
            # n_estimators'ı 100'den 50'ye düşürdük
            self.model = RandomForestClassifier(n_estimators=50, random_state=self.random_state)
        elif self.model_type == 'gradient_boosting':
            # n_estimators'ı 100'den 50'ye düşürdük
            self.model = GradientBoostingClassifier(n_estimators=50, random_state=self.random_state)
        elif self.model_type == 'decision_tree':
            self.model = DecisionTreeClassifier(random_state=self.random_state)
        elif self.model_type == 'logistic_regression':
            # max_iter'i 1000'den 500'e düşürdük
            self.model = LogisticRegression(random_state=self.random_state, max_iter=500)
        elif self.model_type == 'svm':
            self.model = SVC(probability=True, random_state=self.random_state)
        elif self.model_type == 'knn':
            self.model = KNeighborsClassifier()
        else:
            raise ValueError(f"Desteklenmeyen model türü: {self.model_type}")
    
    def build_pipeline(self, preprocessor):
        """
        Önişleme ve model adımlarından oluşan bir pipeline oluşturur
        
        Args:
            preprocessor: Sklearn preprocessing pipeline
            
        Returns:
            sklearn.pipeline.Pipeline: Önişleme ve model içeren pipeline        """
        self.preprocessor = preprocessor
        return Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', self.model)
        ])
    
    def get_default_param_grid(self):
        """
        Model türüne göre varsayılan hiperparametre ızgarasını döndürür
        PERFORMANS OPTIMIZASYONU: Daha az parametre kombinasyonu
        
        Returns:
            dict: Hiperparametre ızgarası
        """
        if self.model_type == 'random_forest':
            return {
                'classifier__n_estimators': [50, 100],  # Azaltıldı: 3→2
                'classifier__max_depth': [None, 10, 20],  # Azaltıldı: 4→3
                'classifier__min_samples_split': [2, 5],  # Azaltıldı: 3→2
            }
        elif self.model_type == 'gradient_boosting':
            return {
                'classifier__n_estimators': [50, 100],  # Azaltıldı: 3→2
                'classifier__learning_rate': [0.1, 0.2],  # Azaltıldı: 3→2
                'classifier__max_depth': [3, 5],  # Azaltıldı: 3→2
            }
        elif self.model_type == 'decision_tree':
            return {
                'classifier__max_depth': [10, 20],  # Azaltıldı: 4→2
                'classifier__min_samples_split': [2, 5],  # Azaltıldı: 3→2
                'classifier__criterion': ['gini']  # Azaltıldı: 2→1
            }
        elif self.model_type == 'logistic_regression':
            return {                'classifier__C': [0.1, 1, 10],  # Azaltıldı: 5→3
                'classifier__penalty': ['l2'],  # Azaltıldı: 2→1
                'classifier__solver': ['liblinear']  # Azaltıldı: 2→1
            }
        elif self.model_type == 'svm':
            return {
                'classifier__C': [1, 10],  # Azaltıldı: 3→2
                'classifier__kernel': ['linear', 'rbf'],  # Azaltıldı: 3→2
            }
        elif self.model_type == 'knn':
            return {
                'classifier__n_neighbors': [3, 5, 7],  # Azaltıldı: 5→3
                'classifier__weights': ['uniform']  # Azaltıldı: 2→1
            }
        else:
            return {}
    
    def optimize_hyperparameters(self, pipeline, X_train, y_train, param_grid=None, cv=3, n_jobs=2, verbose=0):
        """
        Hiperparametre optimizasyonu yapar - PERFORMANS OPTIMIZASYONU
        
        Args:
            pipeline: Sklearn Pipeline
            X_train: Eğitim özellikleri
            y_train: Eğitim hedef değişkeni
            param_grid (dict): Hiperparametre ızgarası
            cv (int): Çapraz doğrulama katlama sayısı (varsayılan: 3, eskiden 5)
            n_jobs (int): Paralel iş sayısı (varsayılan: 2, eskiden -1)
            verbose (int): Ayrıntı seviyesi (varsayılan: 0, eskiden 1)
            
        Returns:
            sklearn.model_selection.GridSearchCV: En iyi modeli içeren GridSearchCV nesnesi
        """
        if param_grid is None:
            param_grid = self.get_default_param_grid()
        
        self.logger.info(f"{self.device_name} için hiperparametre optimizasyonu yapılıyor...")
        
        grid_search = GridSearchCV(
            pipeline, param_grid, cv=cv, scoring='accuracy',
            n_jobs=n_jobs, verbose=verbose, return_train_score=True
        )
        
        grid_search.fit(X_train, y_train)
        
        self.logger.info(f"En iyi parametreler: {grid_search.best_params_}")
        self.logger.info(f"En iyi çapraz doğrulama skoru: {grid_search.best_score_:.4f}")
        
        self.best_params = grid_search.best_params_
        self.model = grid_search.best_estimator_.named_steps['classifier']
          # Pipeline'ı güncelle
        optimized_pipeline = Pipeline([
            ('preprocessor', self.preprocessor),
            ('classifier', self.model)
        ])
        
        return optimized_pipeline
    
    def train(self, X_train, y_train, preprocessor=None, optimize=False):
        print("\n==================== START TRAIN ====================\n")
        self.logger.info(f"{self.device_name} için model eğitiliyor...")        # Drop target column from features if present
        if self.device_name in X_train.columns:
            self.logger.warning(f"Target column {self.device_name} found in features. Dropping it.")
            X_train = X_train.drop(columns=[self.device_name])
        
        print("==== X_train columns before pipeline fit ====")
        print(X_train.columns.tolist())
        print("==== X_train dtypes before pipeline fit ====")
        print(X_train.dtypes)
        print("==== X_train shape before pipeline fit ====")
        print(X_train.shape)
        
        if preprocessor is None:
            preprocessor = SmartHomeDataProcessor()
            preprocessor.fit(X_train)
        self.preprocessor = preprocessor
        self.pipeline = Pipeline([
            ('preprocessor', self.preprocessor),
            ('classifier', self.model)
        ])
        
        print("\n==== BEFORE PIPELINE FIT ====")
        try:
            if optimize:
                param_grid = self.get_default_param_grid()
                # PERFORMANS OPTIMIZASYONU: cv=3, n_jobs=2, verbose=0
                grid_search = GridSearchCV(self.pipeline, param_grid, cv=3, n_jobs=2, verbose=0)
                grid_search.fit(X_train, y_train)
                self.pipeline = grid_search.best_estimator_
                self.best_params = grid_search.best_params_
                self.logger.info(f"En iyi parametreler: {self.best_params}")
            else:
                self.pipeline.fit(X_train, y_train)
            print("\n==== AFTER PIPELINE FIT ====")
        except Exception as e:
            print("\n==== ERROR DURING PIPELINE FIT ====")
            print(e)
            raise
        self.classes = self.pipeline.named_steps['classifier'].classes_ if hasattr(self.pipeline.named_steps['classifier'], 'classes_') else None
        self.is_trained = True
        score = self.pipeline.score(X_train, y_train)
        self.logger.info(f"{self.device_name} modeli eğitildi, doğruluk: {score:.4f}")
        print("\n==================== END TRAIN ====================\n")
        return score
        
    def evaluate(self, X_test, y_test):
        """Test verisi üzerinde modeli değerlendirir"""
        self.logger.info(f"{self.device_name} modeli değerlendiriliyor...")
    
        # Model eğitilmiş mi kontrol et
        if not hasattr(self, 'is_trained') or not self.is_trained:
            self.logger.warning("Model henüz eğitilmedi!")
            return {"error": "Model not trained"}
        
        try:
            # X_test raw data ise, preprocessing pipeline'ından geçir
            if hasattr(X_test, 'columns') and 'timestamp' in X_test.columns:
                self.logger.info(f"X_test: raw data detected, applying preprocessing pipeline")
                # Drop target column from features if present
                if self.device_name in X_test.columns:
                    self.logger.warning(f"Target column {self.device_name} found in test features. Dropping it.")
                    X_test = X_test.drop(columns=[self.device_name])
                # Pipeline predict kullanarak otomatik preprocessing yap
                y_pred = self.pipeline.predict(X_test)
            else:
                # Eğer X_test zaten işlenmiş veri ise
                self.logger.info(f"X_test: processed data detected")
                # Pipeline predict kullan - bu işlenmiş veriyi bekliyor
                y_pred = self.pipeline.predict(X_test)
            
            # Metrikler sözlüğünü başlat
            metrics = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred, average='weighted'),
                "recall": recall_score(y_test, y_pred, average='weighted'),
                "f1": f1_score(y_test, y_pred, average='weighted'),
                "confusion_matrix": confusion_matrix(y_test, y_pred)
            }
            
            # İkili sınıflandırma için AUC hesapla (güvenli bir şekilde)
            try:
                # Eğer self.classes varsa ve uzunluğu 2 ise (ikili sınıflandırma)
                if self.classes is not None and len(self.classes) == 2:
                    # predict_proba metodunu güvenli bir şekilde çağır
                    if hasattr(self.pipeline.named_steps['classifier'], 'predict_proba'):
                        y_proba = self.pipeline.predict_proba(X_test)[:, 1]
                        metrics["auc"] = roc_auc_score(y_test, y_proba)
            except Exception as e:
                self.logger.error(f"AUC hesaplama hatası: {e}")
            
            # Metrikleri yazdır
            for metric, value in metrics.items():
                if metric != "confusion_matrix":
                    self.logger.info(f"{metric.capitalize()}: {value:.4f}")
            
            self.metrics = metrics
            return metrics
        except Exception as e:
            self.logger.error(f"Model değerlendirme hatası: {e}")
            # Hata durumunda da metrics nesnesini oluştur ve error bilgisini ekle
            return {
                "error": str(e),
                "accuracy": None,
                "precision": None,
                "recall": None,
                "f1": None
            }
    
    def predict(self, X):
        if not hasattr(self, 'pipeline') or self.pipeline is None:
            raise ValueError("Model pipeline henüz eğitilmemiş.")
        return self.pipeline.predict(X)
    
    def predict_proba(self, X):
        if not hasattr(self, 'pipeline') or self.pipeline is None:
            raise ValueError("Model pipeline henüz eğitilmemiş.")
        classifier = self.pipeline.named_steps['classifier']
        if hasattr(classifier, 'predict_proba'):
            return self.pipeline.predict_proba(X)
        else:
            raise AttributeError(f"Model {self.model_type} predict_proba metodunu desteklemiyor.")
    
    def plot_confusion_matrix(self, normalize=False, figsize=(8, 6), save_path=None):
        """
        Karmaşıklık matrisini görselleştirir
        
        Args:
            normalize (bool): Normalizasyon yapılıp yapılmayacağı
            figsize (tuple): Şekil boyutu
            save_path (str): Kaydedilecek dosya yolu
        """
        if 'confusion_matrix' not in self.metrics or self.metrics['confusion_matrix'] is None:
            raise ValueError("Önce evaluate() metodunu çağırmalısınız")
        
        cm = self.metrics['confusion_matrix']
        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        
        plt.figure(figsize=figsize)
        xticklabels = self.classes if self.classes is not None else 'auto'
        yticklabels = self.classes if self.classes is not None else 'auto'
        sns.heatmap(
            cm, annot=True, fmt='.2f' if normalize else 'd', 
            cmap='Blues', square=True,
            xticklabels=xticklabels, 
            yticklabels=yticklabels
        )
        plt.xlabel('Tahmin Edilen Etiket')
        plt.ylabel('Gerçek Etiket')
        plt.title(f'Karmaşıklık Matrisi - {self.device_name}')
        
        if save_path:
            plt.savefig(save_path)
            self.logger.info(f"Karmaşıklık matrisi {save_path} konumuna kaydedildi")
        
        plt.tight_layout()
        plt.show()
    
    def plot_roc_curve(self, figsize=(8, 6), save_path=None):
        """
        ROC eğrisini görselleştirir (ikili sınıflandırma için)
        
        Args:
            figsize (tuple): Şekil boyutu
            save_path (str): Kaydedilecek dosya yolu
        """
        if 'roc' not in self.metrics or 'auc' not in self.metrics:
            raise ValueError("İkili sınıflandırma modeli değil veya henüz evaluate() metodu çağrılmamış")
        
        fpr = self.metrics['roc']['fpr']
        tpr = self.metrics['roc']['tpr']
        roc_auc = self.metrics['auc']
        
        plt.figure(figsize=figsize)
        plt.plot(fpr, tpr, color='darkorange', lw=2, 
                 label=f'ROC curve (area = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'Receiver Operating Characteristic - {self.device_name}')
        plt.legend(loc="lower right")
        
        if save_path:
            plt.savefig(save_path)
            self.logger.info(f"ROC eğrisi {save_path} konumuna kaydedildi")
        
        plt.tight_layout()
        plt.show()
    
    def plot_feature_importance(self, top_n=20, figsize=(10, 8), save_path=None):
        """
        Özellik önemini görselleştirir
        
        Args:
            top_n (int): Gösterilecek en önemli özellik sayısı
            figsize (tuple): Şekil boyutu
            save_path (str): Kaydedilecek dosya yolu
        """
        if hasattr(self.pipeline.named_steps['classifier'], 'feature_importances_'):
            # Feature importances alma yöntemi (tree-based modeller için)
            importances = self.pipeline.named_steps['classifier'].feature_importances_
            
            # Özellik isimleri ve önemlerini sözlükte tut
            feature_importance = {}
            
            # Her zaman self.feature_names kullan
            all_features = self.feature_names
            
            # Özellik sayısını importance uzunluğuna göre ayarla
            if all_features is not None and importances is not None:
                all_features = all_features[:len(importances)]
            else:
                all_features = []
            
            # Özellik-önem eşleştirmesi
            feature_importance = dict(zip(all_features, importances))
            
            # Önem değerine göre sırala
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            top_features = sorted_features[:top_n]
            
            # Görselleştirme
            features, importance = zip(*top_features)
            
            plt.figure(figsize=figsize)
            plt.barh(range(len(features)), importance, align='center')
            plt.yticks(range(len(features)), features)
            plt.xlabel('Önem')
            plt.ylabel('Özellik')
            plt.title(f'En Önemli {top_n} Özellik - {self.device_name}')
            
            if save_path:
                plt.savefig(save_path)
                self.logger.info(f"Özellik önemi grafiği {save_path} konumuna kaydedildi")
            
            plt.tight_layout()
            plt.show()
        else:
            self.logger.warning(f"Bu model türü ({self.model_type}) özellik önemi bilgisi sağlamıyor")
    
    def save_model(self, directory=None):
        """
        Eğitilmiş modeli kaydeder
        
        Args:
            directory (str): Kaydedilecek dizin
            
        Returns:
            str: Model dosyasının tam yolu
        """
        if self.model is None:
            raise ValueError("Model henüz eğitilmemiş")
            
        if directory is None:
            directory = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models", "trained")
        
        # Dizin yoksa oluştur
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Model dosya adı
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"{self.device_name}_{self.model_type}_{timestamp}.joblib"
        model_path = os.path.join(directory, model_filename)
        
        # Model nesnesi
        model_data = {
            'device_name': self.device_name,
            'model_type': self.model_type,
            'model': self.model,
            'preprocessor': self.preprocessor,
            'feature_names': self.feature_names,
            'classes': self.classes,
            'last_training_time': self.last_training_time,
            'best_params': self.best_params,
            'metrics': self.metrics
        }
        
        # Modeli kaydet
        joblib.dump(model_data, model_path)
        self.logger.info(f"Model {model_path} konumuna kaydedildi")
        
        return model_path
    
    @classmethod
    def load_model(cls, model_path):
        """
        Kaydedilmiş modeli yükler
        
        Args:
            model_path (str): Model dosya yolu
            
        Returns:
            DeviceControlModel: Yüklenmiş model
        """
        # Modeli yükle
        model_data = joblib.load(model_path)
        
        # Yeni model nesnesi oluştur
        model = cls(model_data['device_name'], model_data['model_type'])
          # Model verilerini yükle
        model.model = model_data['model']
        model.preprocessor = model_data['preprocessor']
        model.feature_names = model_data['feature_names']
        model.classes = model_data['classes']
        model.last_training_time = model_data['last_training_time']
        model.best_params = model_data['best_params']
        model.metrics = model_data['metrics']
        
        # Pipeline'ı yeniden oluştur
        if model.preprocessor is not None and model.model is not None:
            model.pipeline = Pipeline([
                ('preprocessor', model.preprocessor),
                ('classifier', model.model)
            ])
            model.is_trained = True
        else:
            model.logger.warning("Pipeline oluşturulamadı: preprocessor veya model eksik")
        
        model.logger.info(f"{model_path} konumundan {model.device_name} modeli yüklendi")
        
        return model

# Modeli test etmek için fonksiyon
def test_model_training():
    """
    Örnek veri seti ile modeli test eder
    """
    from src.data_processing.preprocessing import process_raw_data
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
    
    # Veri işleme
    X_train, X_test, y_train_dict, y_test_dict, preprocessor = process_raw_data(
        csv_path, save_processed=True
    )
    
    # Hedef cihazı seç
    device_name = list(y_train_dict.keys())[0]
    y_train = y_train_dict[device_name]
    y_test = y_test_dict[device_name]
    
    # Modeli oluştur ve eğit
    model = DeviceControlModel(device_name, model_type='random_forest')
    model.train(X_train, y_train, preprocessor=preprocessor, optimize=True)
    
    # Modeli değerlendir
    metrics = model.evaluate(X_test, y_test)
    
    # Görselleştirmeler
    try:
        model.plot_confusion_matrix()
        if model.classes is not None and len(model.classes) == 2:  # İkili sınıflandırma ise
            model.plot_roc_curve()
        model.plot_feature_importance()
    except Exception as e:
        print(f"Görselleştirme sırasında hata: {e}")
    
    # Modeli kaydet
    model_path = model.save_model()
    
    # Modeli yükle ve test et
    loaded_model = DeviceControlModel.load_model(model_path)
    loaded_predictions = loaded_model.predict(X_test)
    loaded_accuracy = accuracy_score(y_test, loaded_predictions)
    print(f"Yüklenmiş model doğruluğu: {loaded_accuracy:.4f}")
    
    return model

# Pipeline oluşturma örneği:

def create_model_pipeline(self, model_type='random_forest'):
    """Model ve önişleme adımlarını içeren bir pipeline oluştur"""
    
    if model_type == 'random_forest':
        model = RandomForestClassifier(n_estimators=100, random_state=self.random_state)
    elif model_type == 'gradient_boosting':
        model = GradientBoostingClassifier(random_state=self.random_state)
    else:
        model = RandomForestClassifier(n_estimators=100, random_state=self.random_state)
    
    # Bu şekilde pipeline oluştur:
    pipeline = Pipeline([
        ('preprocessor', self.preprocessor),  # Artık fit/transform metodları var
        ('classifier', model)
    ])
    
    return pipeline

def create_pipeline(self, X_train):
    """
    Eğitim için ML pipeline oluşturur.
    
    Args:
        X_train: Eğitim verileri
        
    Returns:
        Pipeline: Scikit-learn pipeline
    """
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import StandardScaler, OneHotEncoder
    from sklearn.pipeline import Pipeline
    import pandas as pd
    import numpy as np
    
    # Veri tipi kontrolü
    if not isinstance(X_train, pd.DataFrame):
        # DataFrame değilse numpy array'e çevir ve sonra DataFrame'e dönüştür
        if isinstance(X_train, np.ndarray):
            X_train = pd.DataFrame(X_train)
        else:
            raise ValueError("X_train bir pandas DataFrame veya numpy array olmalıdır")
    
    # Sütun tiplerini belirle
    num_features = X_train.select_dtypes(include=['int64', 'float64']).columns.tolist()
    cat_features = X_train.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    
    # Dönüştürücü listesi
    transformers = []
    
    # Sayısal özellikler için StandardScaler
    if num_features:
        transformers.append(('num', StandardScaler(), num_features))
    
    # Kategorik özellikler için OneHotEncoder
    if cat_features:
        transformers.append(('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_features))
    
    # Özellik dönüştürücüleri olmadan temel pipeline
    if not transformers:
        return Pipeline([('classifier', self.model)])
    
    # Column Transformer oluştur
    preprocessor = ColumnTransformer(
        transformers=transformers,
        remainder='drop'  # Kategorik ve sayısal olmayan sütunları at
    )
    
    # Pipeline oluştur
    return Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', self.model)
    ])

if __name__ == "__main__":
    test_model_training()