"""
Veri işleme modülü için birim testleri
"""
import pytest
import pandas as pd
import numpy as np
from src.data_processing.preprocessing import SmartHomeDataProcessor

class TestSmartHomeDataProcessor:
    """SmartHomeDataProcessor sınıfı için test sınıfı"""
    
    def test_init(self):
        """Constructor doğru çalışıyor mu?"""
        processor = SmartHomeDataProcessor()
        assert processor is not None
        # OneHotEncoder ve StandardScaler başlatılmış mı?
        assert processor.encoder is not None
        assert processor.scaler is not None
    
    def test_clean_data(self, sample_data):
        """clean_data metodu doğru çalışıyor mu?"""
        processor = SmartHomeDataProcessor()
        
        # Eksik değerler ekle
        data_with_missing = sample_data.copy()
        data_with_missing.loc[0, 'Salon_Sıcaklık'] = np.nan
        data_with_missing.loc[1, 'Salon_Nem'] = np.nan
        data_with_missing.loc[2, 'Salon_Hareket'] = np.nan
        
        cleaned_data = processor.clean_data(data_with_missing)
        
        # Tüm eksik değerler doldurulmuş mu?
        assert not cleaned_data.isna().any().any()
        
        # Sayısal alanlar ortalama ile doldurulmuş mu?
        assert cleaned_data.loc[0, 'Salon_Sıcaklık'] == pytest.approx(np.mean(data_with_missing['Salon_Sıcaklık'].dropna()))
        
        # Kategorik alanlar mod ile doldurulmuş mu?
        assert isinstance(cleaned_data.loc[2, 'Salon_Hareket'], (bool, np.bool_))
    
    def test_extract_datetime_features(self, sample_data):
        """extract_datetime_features metodu doğru çalışıyor mu?"""
        processor = SmartHomeDataProcessor()
        
        # Timestamp sütununu datetime'a dönüştür
        sample_data['timestamp'] = pd.to_datetime(sample_data['timestamp'])
        
        data_with_features = processor._extract_time_features(sample_data)
        
        # Yeni özellikler eklenmiş mi?
        assert 'hour' in data_with_features.columns
        assert 'day_of_week' in data_with_features.columns
        assert 'is_weekend' in data_with_features.columns
        assert 'time_period' in data_with_features.columns
        
        # Değerler doğru hesaplanmış mı?
        first_row = data_with_features.iloc[0]
        first_date = sample_data['timestamp'].iloc[0]
        
        assert first_row['hour'] == first_date.hour
        assert first_row['day_of_week'] == first_date.dayofweek
        assert first_row['is_weekend'] == (1 if first_date.dayofweek >= 5 else 0)
        
        # time_period doğru hesaplanmış mı?
        hour = first_date.hour
        if 5 <= hour < 9:
            expected_period = 'Sabah'
        elif 9 <= hour < 17:
            expected_period = 'Gündüz'
        elif 17 <= hour < 22:
            expected_period = 'Akşam'
        else:
            expected_period = 'Gece'
            
        assert first_row['time_period'] == expected_period

    def test_prepare_target_variables(self, sample_data):
        """prepare_target_variables metodu doğru çalışıyor mu?"""
        processor = SmartHomeDataProcessor()
        
        processed_data = processor.prepare_target_variables(sample_data)
        
        # Hedef cihaz sütunları tespit edilmiş mi?
        assert 'Salon_Klima' in processor.target_device_columns
        assert 'Salon_Lamba' in processor.target_device_columns