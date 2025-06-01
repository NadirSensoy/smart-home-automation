"""
Model eğitim modülü için birim testleri
"""
import pytest
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from src.models.model_trainer import DeviceControlModel

class TestDeviceControlModel:
    """DeviceControlModel sınıfı için test sınıfı"""
    
    @pytest.fixture
    def model_data(self):
        """Model için test verisi oluşturur"""
        # Özellikler
        X = pd.DataFrame({
            'Sıcaklık': np.random.uniform(18, 30, 100),
            'Nem': np.random.uniform(30, 70, 100),
            'Doluluk': np.random.choice([True, False], 100),
            'Saat': np.random.randint(0, 24, 100),
            'Oda': np.random.choice(['Salon', 'Yatak Odası', 'Mutfak'], 100)
        })
        
        # Hedef değişken - rastgele klima durumu
        y = np.random.choice([0, 1], 100)
        
        # Önişleme pipeline'ı
        numeric_features = ['Sıcaklık', 'Nem', 'Saat']
        categorical_features = ['Doluluk', 'Oda']
        
        numeric_transformer = Pipeline(steps=[
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('onehot', OneHotEncoder(sparse_output=False, handle_unknown='ignore'))
        ])
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ])
        
        return X, y, preprocessor
    
    def test_init(self):
        """Constructor doğru çalışıyor mu?"""
        model = DeviceControlModel('Salon_Klima')
        assert model.device_name == 'Salon_Klima'
        assert model.model_type == 'random_forest'
        assert model.model is not None
        
        # Farklı model türleriyle test
        model = DeviceControlModel('Salon_Klima', model_type='decision_tree')
        assert model.model_type == 'decision_tree'
        
        # Geçersiz model türüyle test
        with pytest.raises(ValueError):
            DeviceControlModel('Salon_Klima', model_type='invalid_model')
    
    def test_build_pipeline(self, model_data):
        """build_pipeline metodu doğru çalışıyor mu?"""
        X, y, preprocessor = model_data
        model = DeviceControlModel('Salon_Klima')
        
        pipeline = model.build_pipeline(preprocessor)
        
        assert pipeline is not None
        assert hasattr(pipeline, 'fit')
        assert hasattr(pipeline, 'predict')
        
        # Pipeline yapısı doğru mu?
        assert 'preprocessor' in pipeline.named_steps
        assert 'classifier' in pipeline.named_steps
    
    def test_train_predict(self, model_data):
        """train ve predict metodları doğru çalışıyor mu?"""
        X, y, preprocessor = model_data
        model = DeviceControlModel('Salon_Klima')
        model.preprocessor = preprocessor
        
        # Eğitim
        model.train(X, y, optimize=False)
        
        # Model eğitilmiş mi?
        assert model.model is not None
        assert model.feature_names is not None
        assert model.last_training_time is not None
        
        # Tahmin
        predictions = model.predict(X)
        assert len(predictions) == len(X)
        assert set(np.unique(predictions)).issubset({0, 1})
        
        # Olasılık tahmini
        probas = model.predict_proba(X)
        assert probas.shape == (len(X), 2)
        assert (probas >= 0).all() and (probas <= 1).all()