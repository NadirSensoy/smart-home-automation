"""
Sistem bileşenleri arasındaki entegrasyonu test eden testler
"""
import pytest
import os
import pandas as pd
from datetime import datetime, timedelta

from src.data_processing.preprocessing import process_raw_data
from src.models.model_trainer import DeviceControlModel
from src.automation.rules_engine import RulesEngine
from src.automation.device_manager import DeviceManager

class TestDataToModelIntegration:
    """Veri işleme ve model entegrasyonu testi"""
    
    def test_process_data_to_model(self, test_data_path):
        """Veri işleme çıktısı ile model eğitimi entegrasyonu"""
        # Veri işleme
        try:
            X_train, X_test, y_train_dict, y_test_dict, preprocessor = process_raw_data(
                test_data_path, save_processed=False
            )
            
            assert X_train is not None
            assert X_test is not None
            assert len(y_train_dict) > 0
            assert preprocessor is not None
            
            # Cihaz için hedef var mı?
            device_name = list(y_train_dict.keys())[0]
            assert device_name in y_train_dict
            assert len(y_train_dict[device_name]) > 0
            
            # Model eğitimi
            model = DeviceControlModel(device_name, model_type='decision_tree')
            model.preprocessor = preprocessor
            model.train(X_train, y_train_dict[device_name], optimize=False)
            
            # Model eğitildi mi?
            assert model.model is not None
            
            # Tahminler
            predictions = model.predict(X_test)
            assert len(predictions) == len(X_test)
            
        except Exception as e:
            pytest.fail(f"Entegrasyon testi başarısız: {str(e)}")

class TestModelToRulesIntegration:
    """Model ve kural motoru entegrasyonu testi"""
    
    def test_model_to_rules_integration(self):
        """Model tahmini ve kural motoru entegrasyonu"""
        # Örnek durum ve cihaz durumları
        current_state = {
            'timestamp': datetime.now(),
            'Salon_Sıcaklık': 28.0,
            'Salon_Nem': 55.0,
            'Salon_CO2': 800,
            'Salon_Işık': 300,
            'Salon_Hareket': True,
            'Salon_Doluluk': True,
            'hour': 14,
            'is_weekend': 0,
            'ml_predictions': {
                'Salon_Klima': {'state': True, 'probability': 0.85}
            }
        }
        
        devices = {
            'Salon_Klima': False,
            'Salon_Lamba': True,
            'Salon_Perde': True
        }
        
        # Kural motoru oluştur
        rules_engine = RulesEngine()
        
        # ML tabanlı kural ekle
        def ml_prediction_condition(state, devices):
            ml_pred = state.get('ml_predictions', {}).get('Salon_Klima', {})
            return ml_pred.get('state', False) and ml_pred.get('probability', 0) > 0.7
        
        def ml_prediction_action(state, devices):
            devices['Salon_Klima'] = True
            return devices
        
        rules_engine.add_rule(
            'ml_prediction_rule',
            ml_prediction_condition,
            ml_prediction_action,
            priority=1,
            description='ML tahmini yüksek güvenle klima açma tavsiyesi veriyor'
        )
        
        # Kuralları değerlendir
        updated_devices = rules_engine.evaluate_rules(current_state, devices)
        
        # ML tahmini kuralı tetiklendi mi?
        assert updated_devices['Salon_Klima'] is True

class TestFullWorkflow:
    """Tam iş akışı testi - veri işleme -> model -> kural motoru -> cihaz yönetimi"""
    
    def test_end_to_end(self, test_data_path):
        """Uçtan uca iş akışı testi"""
        # 1. Veri işleme
        try:
            X_train, X_test, y_train_dict, y_test_dict, preprocessor = process_raw_data(
                test_data_path, save_processed=False
            )
            
            # Test için ilk cihazı al
            device_name = list(y_train_dict.keys())[0]
            
            # 2. Model eğitimi
            model = DeviceControlModel(device_name, model_type='decision_tree')
            model.preprocessor = preprocessor
            model.train(X_train, y_train_dict[device_name], optimize=False)
            
            # 3. Örnek durum için tahmin
            sample_state = X_test.iloc[[0]].copy()
            prediction = bool(model.predict(sample_state)[0])
            probability = float(max(model.predict_proba(sample_state)[0]))
            
            # 4. Kural motoru
            rules_engine = RulesEngine()
            
            # Temel kural ekle
            def basic_condition(state, devices):
                return state.get('ml_predictions', {}).get(device_name, {}).get('state', False)
            
            def basic_action(state, devices):
                devices[device_name] = True
                return devices
            
            rules_engine.add_rule('basic_rule', basic_condition, basic_action)
            
            # 5. Cihaz yöneticisi
            device_manager = DeviceManager()
            device_manager.set_device_state(device_name, False)  # Başlangıç durumu
            
            # 6. Tam akış
            # 6.1 Model tahmini
            current_state = {
                'timestamp': datetime.now(),
                'ml_predictions': {
                    device_name: {'state': prediction, 'probability': probability}
                }
            }
            
            # 6.2 Mevcut cihaz durumları
            current_devices = device_manager.get_all_device_states()
            
            # 6.3 Kuralları değerlendir
            updated_devices = rules_engine.evaluate_rules(current_state, current_devices)
            
            # 6.4 Cihaz durumlarını güncelle
            device_manager.update_device_states(updated_devices)
            
            # 6.5 Sonucu kontrol et
            final_state = device_manager.get_device_state(device_name)
            
            if prediction:
                assert final_state is True, "Model True tahmini yaptığında cihaz açılmalıydı"
            
            # Test başarılı
            assert True
            
        except Exception as e:
            pytest.fail(f"Uçtan uca test başarısız: {str(e)}")