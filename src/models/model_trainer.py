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
        
        # Modeli oluştur
        self._create_model()
    
    def _create_model(self):
        """Belirtilen türde model oluşturur"""
        if self.model_type == 'random_forest':
            self.model = RandomForestClassifier(random_state=self.random_state)
        elif self.model_type == 'gradient_boosting':
            self.model = GradientBoostingClassifier(random_state=self.random_state)
        elif self.model_type == 'decision_tree':
            self.model = DecisionTreeClassifier(random_state=self.random_state)
        elif self.model_type == 'logistic_regression':
            self.model = LogisticRegression(random_state=self.random_state, max_iter=1000)
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
            sklearn.pipeline.Pipeline: Önişleme ve model içeren pipeline
        """
        self.preprocessor = preprocessor
        return Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', self.model)
        ])
    
    def get_default_param_grid(self):
        """
        Model türüne göre varsayılan hiperparametre ızgarasını döndürür
        
        Returns:
            dict: Hiperparametre ızgarası
        """
        if self.model_type == 'random_forest':
            return {
                'classifier__n_estimators': [50, 100, 200],
                'classifier__max_depth': [None, 10, 20, 30],
                'classifier__min_samples_split': [2, 5, 10],
                'classifier__min_samples_leaf': [1, 2, 4]
            }
        elif self.model_type == 'gradient_boosting':
            return {
                'classifier__n_estimators': [50, 100, 200],
                'classifier__learning_rate': [0.01, 0.1, 0.2],
                'classifier__max_depth': [3, 5, 7],
                'classifier__min_samples_split': [2, 5]
            }
        elif self.model_type == 'decision_tree':
            return {
                'classifier__max_depth': [None, 10, 20, 30],
                'classifier__min_samples_split': [2, 5, 10],
                'classifier__min_samples_leaf': [1, 2, 4],
                'classifier__criterion': ['gini', 'entropy']
            }
        elif self.model_type == 'logistic_regression':
            return {
                'classifier__C': [0.01, 0.1, 1, 10, 100],
                'classifier__penalty': ['l1', 'l2'],
                'classifier__solver': ['liblinear', 'saga']
            }
        elif self.model_type == 'svm':
            return {
                'classifier__C': [0.1, 1, 10],
                'classifier__kernel': ['linear', 'rbf', 'poly'],
                'classifier__gamma': ['scale', 'auto', 0.1, 1]
            }
        elif self.model_type == 'knn':
            return {
                'classifier__n_neighbors': [3, 5, 7, 11, 15],
                'classifier__weights': ['uniform', 'distance'],
                'classifier__p': [1, 2]  # Manhattan distance (p=1) or Euclidean distance (p=2)
            }
        else:
            return {}
    
    def optimize_hyperparameters(self, pipeline, X_train, y_train, param_grid=None, cv=5, n_jobs=-1, verbose=1):
        """
        Hiperparametre optimizasyonu yapar
        
        Args:
            pipeline: Sklearn Pipeline
            X_train: Eğitim özellikleri
            y_train: Eğitim hedef değişkeni
            param_grid (dict): Hiperparametre ızgarası
            cv (int): Çapraz doğrulama katlama sayısı
            n_jobs (int): Paralel iş sayısı
            verbose (int): Ayrıntı seviyesi
            
        Returns:
            sklearn.model_selection.GridSearchCV: En iyi modeli içeren GridSearchCV nesnesi
        """
        if param_grid is None:
            param_grid = self.get_default_param_grid()
        
        print(f"{self.device_name} için hiperparametre optimizasyonu yapılıyor...")
        
        grid_search = GridSearchCV(
            pipeline, param_grid, cv=cv, scoring='accuracy',
            n_jobs=n_jobs, verbose=verbose, return_train_score=True
        )
        
        grid_search.fit(X_train, y_train)
        
        print(f"En iyi parametreler: {grid_search.best_params_}")
        print(f"En iyi çapraz doğrulama skoru: {grid_search.best_score_:.4f}")
        
        self.best_params = grid_search.best_params_
        self.model = grid_search.best_estimator_.named_steps['classifier']
        
        # Pipeline'ı güncelle
        optimized_pipeline = Pipeline([
            ('preprocessor', self.preprocessor),
            ('classifier', self.model)
        ])
        
        return optimized_pipeline
    
    def train(self, X_train, y_train, optimize=False):
        """Modeli eğitir"""
        print(f"{self.device_name} için model eğitiliyor...")
        
        try:
            # X_train DataFrame ise
            if hasattr(X_train, 'select_dtypes'):
                # Sadece sayısal sütunları al
                X_numeric = X_train.select_dtypes(include=['int64', 'float64'])
                print(f"Orijinal özellik sayısı: {X_train.shape[1]}, Sayısal özellik sayısı: {X_numeric.shape[1]}")
                
                # Sadece sayısal verilerle eğit
                self.model.fit(X_numeric, y_train)
                self.classes = self.model.classes_ if hasattr(self.model, 'classes_') else None
                self.is_trained = True
                score = self.model.score(X_numeric, y_train)
                print(f"{self.device_name} modeli eğitildi, doğruluk: {score:.4f}")
                return score
            else:
                # Daha karmaşık çözüm gerekiyor, bu basit çözümün dışında
                raise TypeError("X_train bir pandas DataFrame olmalıdır")
                
        except Exception as e:
            print(f"Eğitim hatası: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def evaluate(self, X_test, y_test):
        """Test verisi üzerinde modeli değerlendirir"""
        print(f"{self.device_name} modeli değerlendiriliyor...")
    
        # Model eğitilmiş mi kontrol et
        if not hasattr(self, 'is_trained') or not self.is_trained:
            print("Model henüz eğitilmedi!")
            return {"error": "Model not trained"}
        
        try:
            # X_test DataFrame ise, sadece sayısal sütunları al
            if hasattr(X_test, 'select_dtypes'):
                X_test_numeric = X_test.select_dtypes(include=['int64', 'float64'])
                print(f"X_test: orijinal sütun sayısı: {X_test.shape[1]}, sayısal sütun sayısı: {X_test_numeric.shape[1]}")
                X_test = X_test_numeric
        
            # Tahminleri al
            y_pred = self.model.predict(X_test)
            
            # Metrikler sözlüğünü başlat
            metrics = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred, average='weighted'),
                "recall": recall_score(y_test, y_pred, average='weighted'),
                "f1": f1_score(y_test, y_pred, average='weighted')
            }
            
            # İkili sınıflandırma için AUC hesapla (güvenli bir şekilde)
            try:
                # Eğer self.classes varsa ve uzunluğu 2 ise (ikili sınıflandırma)
                if hasattr(self, 'classes') and self.classes is not None and len(self.classes) == 2:
                    # predict_proba metodunu güvenli bir şekilde çağır
                    if hasattr(self.model, 'predict_proba'):
                        y_proba = self.model.predict_proba(X_test)[:, 1]
                        metrics["auc"] = roc_auc_score(y_test, y_proba)
            except Exception as e:
                print(f"AUC hesaplama hatası: {e}")
            
            # Metrikleri yazdır
            for metric, value in metrics.items():
                print(f"{metric.capitalize()}: {value:.4f}")
            
            self.metrics = metrics
            return metrics
        except Exception as e:
            print(f"Model değerlendirme hatası: {e}")
            # Hata durumunda da metrics nesnesini oluştur ve error bilgisini ekle
            return {
                "error": str(e),
                "accuracy": None,
                "precision": None,
                "recall": None,
                "f1": None
            }
    
    def predict(self, X):
        """
        Yeni veriler için tahmin yapar
        
        Args:
            X: Özellikler
            
        Returns:
            numpy.ndarray: Tahminler
        """
        if self.model is None or self.preprocessor is None:
            raise ValueError("Model henüz eğitilmemiş")
        
        pipeline = Pipeline([
            ('preprocessor', self.preprocessor),
            ('classifier', self.model)
        ])
        
        return pipeline.predict(X)
    
    def predict_proba(self, X):
        """
        Yeni veriler için olasılık tahminleri yapar
        
        Args:
            X: Özellikler
            
        Returns:
            numpy.ndarray: Olasılık tahminleri
        """
        if self.model is None or self.preprocessor is None:
            raise ValueError("Model henüz eğitilmemiş")
        
        pipeline = Pipeline([
            ('preprocessor', self.preprocessor),
            ('classifier', self.model)
        ])
        
        return pipeline.predict_proba(X)
    
    def plot_confusion_matrix(self, normalize=False, figsize=(8, 6), save_path=None):
        """
        Karmaşıklık matrisini görselleştirir
        
        Args:
            normalize (bool): Normalizasyon yapılıp yapılmayacağı
            figsize (tuple): Şekil boyutu
            save_path (str): Kaydedilecek dosya yolu
        """
        if 'confusion_matrix' not in self.metrics:
            raise ValueError("Önce evaluate() metodunu çağırmalısınız")
        
        cm = self.metrics['confusion_matrix']
        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        
        plt.figure(figsize=figsize)
        sns.heatmap(
            cm, annot=True, fmt='.2f' if normalize else 'd', 
            cmap='Blues', square=True,
            xticklabels=self.classes, 
            yticklabels=self.classes
        )
        plt.xlabel('Tahmin Edilen Etiket')
        plt.ylabel('Gerçek Etiket')
        plt.title(f'Karmaşıklık Matrisi - {self.device_name}')
        
        if save_path:
            plt.savefig(save_path)
            print(f"Karmaşıklık matrisi {save_path} konumuna kaydedildi")
        
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
            print(f"ROC eğrisi {save_path} konumuna kaydedildi")
        
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
        if hasattr(self.model, 'feature_importances_'):
            # Feature importances alma yöntemi (tree-based modeller için)
            importances = self.model.feature_importances_
            
            # Özellik isimleri ve önemlerini sözlükte tut
            feature_importance = {}
            
            # Hem sayısal hem kategorik özellikleri hesaba kat
            if hasattr(self.preprocessor, 'transformers_'):
                # ColumnTransformer kullanıldığı durumda
                all_features = []
                for name, transformer, features in self.preprocessor.transformers_:
                    if name != 'remainder':
                        if hasattr(transformer, 'get_feature_names_out'):
                            # OneHotEncoder gibi transformer'lar için
                            transformed_feature_names = transformer.get_feature_names_out(features)
                            all_features.extend(transformed_feature_names)
                        else:
                            # StandardScaler gibi transformer'lar için
                            all_features.extend(features)
                
                # Eğer özellik sayısı eşit değilse, basitçe orijinal özellik isimlerini kullanalım
                if len(all_features) != len(importances):
                    all_features = self.feature_names
            else:
                all_features = self.feature_names
                
            # Özellik sayısını importance uzunluğuna göre ayarla
            all_features = all_features[:len(importances)]
            
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
                print(f"Özellik önemi grafiği {save_path} konumuna kaydedildi")
            
            plt.tight_layout()
            plt.show()
        else:
            print(f"Bu model türü ({self.model_type}) özellik önemi bilgisi sağlamıyor")
    
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
        print(f"Model {model_path} konumuna kaydedildi")
        
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
        
        print(f"{model_path} konumundan {model.device_name} modeli yüklendi")
        
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
    model.preprocessor = preprocessor
    model.train(X_train, y_train, optimize=True)
    
    # Modeli değerlendir
    metrics = model.evaluate(X_test, y_test)
    
    # Görselleştirmeler
    try:
        model.plot_confusion_matrix()
        if len(model.classes) == 2:  # İkili sınıflandırma ise
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