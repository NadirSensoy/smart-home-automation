# home_simulator.py

import time
import threading
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import logging

# İç modülleri içe aktarma
from src.data_simulation.data_generator import HomeDataGenerator
from src.automation.rules_engine import RulesEngine
from src.models.model_manager import SmartHomeModelManager
from src.utils.visualization import SimulationVisualizer

class SmartHomeSimulator:
    """
    Akıllı ev sistemi simülatörü. 
    Gerçek zamanlı sensör verileri, kullanıcı hareketleri ve cihaz durumları simüle eder.
    Otomasyon kurallarını ve ML modellerini entegre ederek bir prototip sunar.
    """
    
    def __init__(self, rooms=None, num_residents=2, time_step=5, 
                 use_ml=True, ml_model_path=None, simulation_speed=1.0):
        """
        SmartHomeSimulator sınıfını başlatır
        
        Args:
            rooms (list): Simüle edilecek odaların listesi
            num_residents (int): Ev sakinlerinin sayısı
            time_step (int): Simülasyon adımları arasındaki dakika farkı (sanal zaman)
            use_ml (bool): Makine öğrenmesi modeli kullanılıp kullanılmayacağı
            ml_model_path (str): ML model yöneticisinin dosya yolu (None ise yeni model eğitilir)
            simulation_speed (float): Simülasyon hızı çarpanı (1.0 = gerçek zamanla aynı)
        """
        # Simülasyon parametreleri
        self.rooms = rooms or ["Salon", "Yatak Odası", "Çocuk Odası", "Mutfak", "Banyo"]
        self.num_residents = num_residents
        self.time_step = time_step
        self.use_ml = use_ml
        self.simulation_speed = simulation_speed
        self.simulation_time = datetime.now()
        
        # Durum değişkenleri
        self.running = False
        self.paused = False
        self.step_count = 0
        
        # Veri üreteci başlat
        self.data_generator = HomeDataGenerator(
            start_time=self.simulation_time,
            rooms=self.rooms,
            num_residents=num_residents,
            time_step=time_step
        )
        
        # Kural motoru başlat
        self.rules_engine = RulesEngine(use_ml_model=use_ml)
        
        # ML modelini yükle veya başlat
        self.ml_model_manager = None
        if use_ml:
            if ml_model_path and os.path.exists(ml_model_path):
                self.ml_model_manager = SmartHomeModelManager.load_manager(ml_model_path)
            # Model yoksa, simülasyon başlangıcında veri üretip model eğitilecektir.
        
        # Veri kayıtları
        self.history = []
        self.decision_history = []
        
        # Görselleştirme
        self.visualizer = SimulationVisualizer()
        
        # Loglama
        self._setup_logging()
    
    def _setup_logging(self):
        """Simülasyon için log yapılandırması yapar"""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file = os.path.join(log_dir, f"simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        # Logger yapılandırması
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("SmartHomeSimulator")
        self.logger.info("Simülasyon başlatıldı")
    
    def train_ml_model(self, days=3):
        """
        Simülasyon için bir ML modeli eğitir
        
        Args:
            days (int): Eğitim için simüle edilecek gün sayısı
        """
        if not self.use_ml:
            self.logger.info("ML modeli devre dışı, eğitim atlanıyor")
            return
            
        self.logger.info(f"Makine öğrenmesi modeli için {days} günlük veri üretiliyor")
        
        # Veri üret
        dataset = self.data_generator.generate_dataset(days=days)
        
        # CSV'ye kaydet
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "raw")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        csv_path = os.path.join(data_dir, f"training_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv")
        dataset.to_csv(csv_path, index=False)
        
        # Model yöneticisi oluştur ve eğit
        self.ml_model_manager = SmartHomeModelManager()
        self.ml_model_manager.train_models_for_all_devices(csv_path, model_type='random_forest', optimize=True)
        
        # Modeli kural motoruna ekle
        self.rules_engine.set_ml_model(self.ml_model_manager)
        
        self.logger.info("ML modeli eğitimi tamamlandı")
    
    def setup_default_rules(self):
        """Kural motoruna varsayılan kuralları ekler"""
        self.logger.info("Varsayılan kurallar ayarlanıyor")
        
        # Sıcaklık kontrolü
        def high_temp_condition(state):
            for room in self.rooms:
                if f"{room}_Sıcaklık" in state and state[f"{room}_Sıcaklık"] > 26:
                    return True
            return False
        
        def turn_on_ac(state, devices):
            changes = {}
            for room in self.rooms:
                if f"{room}_Sıcaklık" in state and state[f"{room}_Sıcaklık"] > 26:
                    if f"{room}_Klima" in devices:
                        changes[f"{room}_Klima"] = True
            return changes
        
        self.rules_engine.add_rule(
            name="Yüksek Sıcaklık - Klima Aç", 
            condition_func=high_temp_condition,
            action_func=turn_on_ac,
            priority=2,
            description="Oda sıcaklığı 26°C üzerinde ise klimayı aç"
        )
        
        # Boş oda kontrolü
        def empty_room_condition(state):
            for room in self.rooms:
                if f"{room}_Doluluk" in state and state[f"{room}_Doluluk"] == False:
                    return True
            return False
        
        def turn_off_lights_empty_room(state, devices):
            changes = {}
            for room in self.rooms:
                if f"{room}_Doluluk" in state and state[f"{room}_Doluluk"] == False:
                    # Oda boşsa ve lamba açıksa
                    if f"{room}_Lamba" in devices and devices[f"{room}_Lamba"]:
                        changes[f"{room}_Lamba"] = False
            return changes
        
        self.rules_engine.add_rule(
            name="Boş Oda - Lamba Kapat", 
            condition_func=empty_room_condition,
            action_func=turn_off_lights_empty_room,
            priority=1,
            description="Oda boş ise ışıkları kapat"
        )
        
        # Gece modu
        def night_time_condition(state):
            hour = self.simulation_time.hour
            return 22 <= hour or hour <= 6
        
        def night_mode_devices(state, devices):
            changes = {}
            for room in self.rooms:
                # Yatak odasında düşük ışık
                if room == "Yatak Odası" and f"{room}_Doluluk" in state and state[f"{room}_Doluluk"]:
                    changes[f"{room}_Lamba"] = True
                # Diğer odalarda ışıkları kapat
                elif f"{room}_Lamba" in devices and devices[f"{room}_Lamba"]:
                    if f"{room}_Doluluk" in state and state[f"{room}_Doluluk"] == False:
                        changes[f"{room}_Lamba"] = False
                # Perdeleri kapat
                if f"{room}_Perde" in devices:
                    changes[f"{room}_Perde"] = False
            return changes
        
        self.rules_engine.add_rule(
            name="Gece Modu", 
            condition_func=night_time_condition,
            action_func=night_mode_devices,
            priority=3,
            description="Gece saatlerinde (22:00-06:00) perdeleri kapat, boş odalarda ışıkları kapat"
        )
        
        # Sabah rutini
        def morning_time_condition(state):
            hour = self.simulation_time.hour
            return 7 <= hour <= 9
        
        def morning_routine_devices(state, devices):
            changes = {}
            for room in self.rooms:
                # Perdeleri aç
                if f"{room}_Perde" in devices:
                    changes[f"{room}_Perde"] = True
            return changes
        
        self.rules_engine.add_rule(
            name="Sabah Rutini", 
            condition_func=morning_time_condition,
            action_func=morning_routine_devices,
            priority=2,
            description="Sabah saatlerinde (07:00-09:00) perdeleri aç"
        )
    
    def step(self):
        """
        Simülasyonu bir adım ilerletir
        
        Returns:
            dict: Mevcut simülasyon durumu
        """
        # Simülasyon zamanını ilerlet
        self.simulation_time += timedelta(minutes=self.time_step)
        self.step_count += 1
        
        # Simüle edilmiş veriyi güncelle
        current_state = self.data_generator.update_simulation()
        
        # Mevcut cihaz durumlarını al
        device_states = {}
        for room in self.rooms:
            for device_type in ["Klima", "Lamba", "Perde", "Havalandırma"]:
                device_key = f"{room}_{device_type}"
                if device_key in current_state:
                    device_states[device_key] = current_state[device_key]
        
        # ML tahminleri var mı kontrol et
        ml_predictions = {}
        if self.use_ml and self.ml_model_manager:
            try:
                # Create a more complete feature set for prediction
                input_data = self._prepare_prediction_input(current_state)
                
                # Generate all the derived features used during training
                derived_features = self._generate_derived_features(input_data)
                
                # Combine original and derived features
                combined_data = pd.concat([input_data, derived_features], axis=1)
                
                # Try feature bypass with the enhanced feature set
                try:
                    ml_predictions = self.ml_model_manager.predict_with_feature_bypass(combined_data)
                    self.logger.info("Successfully made predictions with feature bypass")
                except Exception as e:
                    self.logger.error(f"Feature bypass failed: {e}")
                    ml_predictions = self._get_default_prediction()
                    
                # Log predictions
                self.logger.info(f"ML predictions: {ml_predictions}")
            except Exception as e:
                self.logger.error(f"Error in ML prediction process: {e}")
                ml_predictions = self._get_default_prediction()
        
        # Now evaluate rules with ML predictions - wrapped in try-except to handle missing attributes
        try:
            updated_devices = self.rules_engine.evaluate_rules(current_state, device_states, ml_predictions)
        except AttributeError as attr_err:
            if 'ml_confidence_threshold' in str(attr_err):
                # Add missing attribute dynamically if it's the issue
                self.logger.warning("Adding missing ml_confidence_threshold to RulesEngine")
                self.rules_engine.ml_confidence_threshold = 0.7
                # Try again
                updated_devices = self.rules_engine.evaluate_rules(current_state, device_states, ml_predictions)
            else:
                raise  # Re-raise if it's a different attribute error
        
        # Cihaz durumlarını güncelle
        for device_name, new_state in updated_devices.items():
            if device_name in current_state:
                current_state[device_name] = new_state
        
        # Geçmiş veriye ekle
        state_record = current_state.copy()
        state_record['step'] = self.step_count
        state_record['ml_predictions'] = str(ml_predictions)
        self.history.append(state_record)
        
        return current_state
    
    def run_simulation(self, steps=100, display=True, delay=1.0):
        """
        Simülasyonu belirtilen adım sayısı kadar çalıştırır
        
        Args:
            steps (int): Çalıştırılacak simülasyon adımı sayısı
            display (bool): Görselleştirme yapılıp yapılmayacağı
            delay (float): Adımlar arasındaki gecikme süresi (saniye)
        """
        self.running = True
        self.paused = False
        
        if not self.ml_model_manager and self.use_ml:
            self.logger.info("ML modeli bulunamadı, eğitiliyor...")
            self.train_ml_model(days=3)
        
        # Varsayılan kuralları ayarla
        self.setup_default_rules()
        
        self.logger.info(f"Simülasyon başlatılıyor: {steps} adım, görüntüleme: {display}")
        
        for i in range(steps):
            if not self.running:
                break
                
            if self.paused:
                time.sleep(0.1)  # Duraklama sırasında CPU kullanımını azaltma
                continue
            try:
                # Simülasyon adımı
                current_state = self.step()
                
                # Güncel durumu görselleştir
                if display:
                    # Fix: update_display doesn't accept step parameter
                    # Add simulation_time as part of current_state instead
                    display_data = current_state.copy() if isinstance(current_state, dict) else {}
                    display_data['simulation_time'] = self.simulation_time
                    display_data['step_count'] = self.step_count
                    
                    self.visualizer.update_display(display_data)
                
                # Simülasyon adımları arasında gecikme
                adjusted_delay = delay / self.simulation_speed
                time.sleep(adjusted_delay)
                
            except Exception as e:
                self.logger.error(f"Simülasyon adımında hata: {e}")
        
        self.logger.info(f"Simülasyon tamamlandı: {self.step_count} adım")
        self.running = False
    
    def run_in_thread(self, steps=100, display=True, delay=1.0):
        """
        Simülasyonu ayrı bir iş parçacığında başlatır
        
        Args:
            steps (int): Çalıştırılacak simülasyon adımı sayısı
            display (bool): Görselleştirme yapılıp yapılmayacağı
            delay (float): Adımlar arasındaki gecikme süresi (saniye)
        """
        threading.Thread(
            target=self.run_simulation,
            args=(steps, display, delay)
        ).start()
    
    def pause(self):
        """Simülasyonu duraklatır"""
        self.paused = True
        self.logger.info("Simülasyon duraklatıldı")
    
    def resume(self):
        """Duraklatılmış simülasyonu devam ettirir"""
        self.paused = False
        self.logger.info("Simülasyon devam ediyor")
    
    def stop(self):
        """Simülasyonu durdurur"""
        self.running = False
        # Clean up matplotlib resources to prevent threading errors
        if hasattr(self, 'visualizer') and self.visualizer:
            if hasattr(self.visualizer, 'close_matplotlib'):
                self.visualizer.close_matplotlib()
            elif hasattr(self.visualizer, 'close'):
                self.visualizer.close()
    
        self.logger.info("Simülasyon durduruldu")
    
    def save_history(self, output_dir=None):
        """
        Simülasyon geçmişini CSV dosyasına kaydeder
        
        Args:
            output_dir (str): Çıktı dizini
        """
        if not self.history:
            self.logger.warning("Kaydedilecek simülasyon verisi yok")
            return None
        
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "simulation")
        
        # Dizin yoksa oluştur
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # DataFrame oluştur
        history_df = pd.DataFrame(self.history)
        
        # Dosya adı
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"simulation_history_{timestamp}.csv"
        csv_path = os.path.join(output_dir, csv_filename)
        
        # CSV'ye kaydet
        history_df.to_csv(csv_path, index=False)
        self.logger.info(f"Simülasyon geçmişi {csv_path} konumuna kaydedildi")
        
        # Karar geçmişini de kaydet
        if self.decision_history:
            decision_df = pd.DataFrame(self.decision_history)
            decision_path = os.path.join(output_dir, f"decision_history_{timestamp}.csv")
            decision_df.to_csv(decision_path, index=False)
            self.logger.info(f"Karar geçmişi {decision_path} konumuna kaydedildi")
        
        return csv_path

    def _get_model_expected_features(self):
        """Get the feature names that the model was trained on"""
        try:
            # First try to get feature names directly from the first model's preprocessing
            if hasattr(self.ml_model_manager, 'device_models') and self.ml_model_manager.device_models:
                # Get the first device model key
                first_model_key = list(self.ml_model_manager.device_models.keys())[0]
                model = self.ml_model_manager.device_models[first_model_key]
                
                # Try to extract feature names from the model directly
                feature_names = None
                
                # Try for scikit-learn pipeline
                if hasattr(model, 'named_steps'):
                    for step_name, step in model.named_steps.items():
                        if hasattr(step, 'feature_names_in_'):
                            feature_names = step.feature_names_in_
                            self.logger.info(f"Found feature names in pipeline step {step_name}")
                            break
                        if hasattr(step, 'get_feature_names_out'):
                            try:
                                feature_names = step.get_feature_names_out()
                                self.logger.info(f"Retrieved feature names with get_feature_names_out() from {step_name}")
                                break
                            except:
                                pass
                
                # Try for direct model attributes
                if feature_names is None and hasattr(model, 'feature_names_in_'):
                    feature_names = model.feature_names_in_
                    self.logger.info("Found feature_names_in_ directly in model")
                
                if feature_names is not None:
                    self.logger.info(f"Found {len(feature_names)} feature names from model")
                    return feature_names
                
            # If no feature names found in model, create them based on error messages
            self.logger.warning("Creating features based on training data patterns")
            
            # Creating a comprehensive list of potential features based on the training data
            base_features = []
            derived_features = []
            
            # Base features for each room
            for room in self.rooms:
                base_features.extend([
                    f"{room}_Sıcaklık", f"{room}_Nem", f"{room}_CO2", 
                    f"{room}_Işık", f"{room}_Doluluk", f"{room}_Hareket"
                ])
            
            # Resident location features
            for i in range(1, self.num_residents + 1):
                base_features.append(f"Kişi_{i}_Konum")
            
            # Device state features for each room
            for room in self.rooms:
                for device in ["Klima", "Lamba", "Perde", "Havalandırma"]:
                    base_features.append(f"{room}_{device}")
            
            # Time features
            base_features.extend(["hour", "day", "month", "dayofweek", "is_weekend"])
            
            # These are the derived features mentioned in the error messages
            for room in self.rooms:
                for sensor in ["Sıcaklık", "Nem", "CO2", "Işık"]:
                    derived_features.extend([
                        f"{room}_{sensor}_Ort1Saat",
                        f"{room}_{sensor}_Std1Saat", 
                        f"{room}_{sensor}_Değişim"
                    ])
                
                derived_features.extend([
                    f"{room}_SabahDoluluk",
                    f"{room}_GündüzDoluluk",
                    f"{room}_AkşamDoluluk", 
                    f"{room}_GeceDoluluk"
                ])
            
            derived_features.extend([
                "Evdeki_Kişi_Sayısı", 
                "Aktif_Oda_Sayısı", 
                "Çalışan_Cihaz_Sayısı"
            ])
            
            # Combine all features
            expected_features = base_features + derived_features
            self.logger.info(f"Created {len(expected_features)} expected features")
            
            return expected_features
        
        except Exception as e:
            self.logger.error(f"Error in _get_model_expected_features: {str(e)}")
            return None
    
    def _generate_derived_features(self, input_df):
        """Generate all derived features needed for prediction"""
        try:
            # Create new DataFrame for derived features
            df = input_df.copy()
            result_df = pd.DataFrame(index=df.index)
            
            # Ensure we have time features
            if 'timestamp' in df.columns:
                time_col = pd.to_datetime(df['timestamp'])
                result_df['hour'] = time_col.dt.hour
                result_df['day'] = time_col.dt.day
                result_df['month'] = time_col.dt.month
                result_df['dayofweek'] = time_col.dt.dayofweek
                result_df['is_weekend'] = (time_col.dt.dayofweek >= 5).astype(int)
            else:
                # Use current time if timestamp not available
                now = datetime.now()
                result_df['hour'] = now.hour
                result_df['day'] = now.day
                result_df['month'] = now.month
                result_df['dayofweek'] = now.weekday()
                result_df['is_weekend'] = int(now.weekday() >= 5)
            
            # Set up tracking for device and room features
            device_cols = []
            occupied_room_count = 0
            
            # Generate room-specific features
            for room in self.rooms:
                occupancy_col = f"{room}_Doluluk"
                
                # Time-based occupancy features if room occupancy is available
                if occupancy_col in df.columns:
                    is_occupied = df[occupancy_col].iloc[0] if not df.empty else False
                    occupied_room_count += int(is_occupied)
                    
                    # Generate time-of-day occupancy flags
                    result_df[f"{room}_SabahDoluluk"] = int(
                        (6 <= result_df['hour'].iloc[0] < 9) and is_occupied)
                        
                    result_df[f"{room}_GündüzDoluluk"] = int(
                        (9 <= result_df['hour'].iloc[0] < 17) and is_occupied)
                        
                    result_df[f"{room}_AkşamDoluluk"] = int(
                        (17 <= result_df['hour'].iloc[0] < 22) and is_occupied)
                        
                    result_df[f"{room}_GeceDoluluk"] = int(
                        ((result_df['hour'].iloc[0] >= 22) or 
                         (result_df['hour'].iloc[0] < 6)) 
                        and is_occupied)
                else:
                    # Default values if occupancy not available
                    result_df[f"{room}_SabahDoluluk"] = 0
                    result_df[f"{room}_GündüzDoluluk"] = 0
                    result_df[f"{room}_AkşamDoluluk"] = 0
                    result_df[f"{room}_GeceDoluluk"] = 0
                
                # Generate sensor statistics
                for sensor in ["Sıcaklık", "Nem", "CO2", "Işık"]:
                    sensor_col = f"{room}_{sensor}"
                    if sensor_col in df.columns:
                        sensor_val = df[sensor_col].iloc[0] if not df.empty else 0
                        
                        # Without historical data, use current value for mean
                        result_df[f"{room}_{sensor}_Ort1Saat"] = sensor_val
                        
                        # Set std and change to 0 (no historical data)
                        result_df[f"{room}_{sensor}_Std1Saat"] = 0
                        result_df[f"{room}_{sensor}_Değişim"] = 0
                    else:
                        # Default values if sensor not available
                        result_df[f"{room}_{sensor}_Ort1Saat"] = 0
                        result_df[f"{room}_{sensor}_Std1Saat"] = 0
                        result_df[f"{room}_{sensor}_Değişim"] = 0
                
                # Track active devices
                for device_type in ["Klima", "Lamba", "Perde", "Havalandırma"]:
                    device_col = f"{room}_{device_type}"
                    if device_col in df.columns:
                        device_cols.append(device_col)
            
            # Generate home-wide statistics
            result_df["Evdeki_Kişi_Sayısı"] = self.num_residents  # Default to all residents
            result_df["Aktif_Oda_Sayısı"] = occupied_room_count
            
            # Calculate active device count
            device_count = 0
            for col in device_cols:
                if col in df.columns:
                    device_count += int(df[col].iloc[0]) if not df.empty else 0
                    
            result_df["Çalışan_Cihaz_Sayısı"] = device_count
            
            return result_df
            
        except Exception as e:
            self.logger.error(f"Error generating derived features: {str(e)}")
            return pd.DataFrame(index=input_df.index)
    
    def _align_features(self, input_df, expected_features):
        """
        Create a DataFrame with exactly the features the model expects
        
        Args:
            input_df: Input DataFrame with current state
            expected_features: List of features expected by the model
        
        Returns:
            DataFrame with aligned features
        """
        if expected_features is None:
            self.logger.warning("No expected features provided")
            return input_df
            
        try:
            # Create an empty result DataFrame with same index
            result_df = pd.DataFrame(index=input_df.index)
            
            # Generate all derived features
            derived_df = self._generate_derived_features(input_df)
            
            # Copy over exact columns from input dataframe
            common_features = set(input_df.columns) & set(expected_features)
            for col in common_features:
                result_df[col] = input_df[col]
                
            # Copy columns from derived features if available
            derived_common = set(derived_df.columns) & set(expected_features)
            for col in derived_common:
                if col not in result_df.columns:  # Don't overwrite existing
                    result_df[col] = derived_df[col]
                
            # Set any remaining missing columns to 0
            missing_cols = set(expected_features) - set(result_df.columns)
            for col in missing_cols:
                result_df[col] = 0
                
            # Ensure all expected columns are present
            missing_after = set(expected_features) - set(result_df.columns)
            if missing_after:
                self.logger.warning(f"Still missing {len(missing_after)} features after alignment!")
                
            # Log feature counts
            self.logger.info(f"Input features: {len(input_df.columns)}, " + 
                            f"Derived: {len(derived_df.columns)}, " + 
                            f"Result: {len(result_df.columns)}, " + 
                            f"Expected: {len(expected_features)}")
                
            # Make sure DataFrame has columns in the expected order
            return result_df[expected_features]
            
        except Exception as e:
            self.logger.error(f"Error in feature alignment: {str(e)}", exc_info=True)
            # Return a DataFrame with zeros for all expected features
            return pd.DataFrame(0, index=input_df.index, columns=expected_features)
    
    def predict_next_state(self, current_state):
        """Make predictions using the ML model with proper feature handling"""
        if not self.ml_model_manager:
            self.logger.warning("ML model manager not available for predictions")
            return self._get_default_prediction()
        
        try:
            # Create a DataFrame from the current state
            input_data = self._prepare_prediction_input(current_state)
            
            # First try the direct feature bypass method
            if hasattr(self.ml_model_manager, 'predict_with_feature_bypass'):
                try:
                    predictions = self.ml_model_manager.predict_with_feature_bypass(input_data)
                    self.logger.info("Successfully made predictions using feature bypass")
                    return predictions
                except Exception as bypass_error:
                    self.logger.error(f"Feature bypass prediction failed: {str(bypass_error)}")
                    # Continue to standard approach if this fails
            
            # Standard approach with feature alignment
            # Get the expected feature names from the model
            expected_features = self._get_model_expected_features()
            
            if expected_features is not None:
                self.logger.info(f"Got expected features: {len(expected_features)} features")
                
                # Generate all derived features needed
                derived_features = self._generate_derived_features(input_data)
                
                # Create a new dataframe with all needed features
                aligned_data = pd.DataFrame(index=input_data.index)
                
                # First, copy over any direct matches from input data
                for col in expected_features:
                    if col in input_data.columns:
                        aligned_data[col] = input_data[col]
                    elif col in derived_features.columns:
                        # Then get any derived features
                        aligned_data[col] = derived_features[col]
                    else:
                        # Default for any remaining
                        aligned_data[col] = 0
                        
                # Ensure the column order matches exactly
                final_input = aligned_data[expected_features]
                
                self.logger.debug(f"Final input shape: {final_input.shape}, expected features: {len(expected_features)}")
                
                try:
                    # Try the standard prediction
                    predictions = self.ml_model_manager.predict_device_states(final_input)
                    self.logger.info("Successfully made predictions using aligned features")
                    return predictions
                except Exception as e1:
                    self.logger.error(f"Standard prediction failed: {str(e1)}")
                    
                    try:
                        # Try with robust prediction
                        return self._make_robust_prediction(final_input)
                    except Exception as e2:
                        self.logger.error(f"Robust prediction failed: {str(e2)}")
                        return self._get_default_prediction()
            else:
                self.logger.warning("Could not determine expected features, using default prediction")
                return self._get_default_prediction()
                
        except Exception as e:
            self.logger.error(f"Error during prediction process: {str(e)}")
            return self._get_default_prediction()
    
    def _prepare_prediction_input(self, current_state):
        """Prepare the input data for prediction, ensuring all necessary features are present"""
        try:
            # Start with the current state as a DataFrame
            if isinstance(current_state, dict):
                input_data = pd.DataFrame([current_state])
            else:
                input_data = current_state.copy()
            
            # Ensure we have at least the base columns for each room
            for room in self.rooms:
                for sensor in ["Sıcaklık", "Nem", "CO2", "Işık", "Doluluk", "Hareket"]:
                    col_name = f"{room}_{sensor}"
                    if col_name not in input_data.columns:
                        input_data[col_name] = 0
                
                for device in ["Klima", "Lamba", "Perde", "Havalandırma"]:
                    col_name = f"{room}_{device}"
                    if col_name not in input_data.columns:
                        input_data[col_name] = False
            
            # Add time features if not present
            if "hour" not in input_data:
                current_time = datetime.now()
                input_data["hour"] = current_time.hour
                input_data["day"] = current_time.day
                input_data["month"] = current_time.month
                input_data["dayofweek"] = current_time.weekday()
                input_data["is_weekend"] = 1 if current_time.weekday() >= 5 else 0
            
            return input_data
            
        except Exception as e:
            self.logger.error(f"Error preparing prediction input: {str(e)}")
            return pd.DataFrame([current_state]) if isinstance(current_state, dict) else current_state.copy()
    
    def _get_default_prediction(self):
        """Return a default prediction when ML fails"""
        default_predictions = {}
        
        # Set all devices to off by default
        for room in self.rooms:
            for device_type in ["Klima", "Lamba", "Perde", "Havalandırma"]:
                device_key = f"{room}_{device_type}"
                default_predictions[device_key] = {
                    "state": False,
                    "probability": 0.0,
                    "source": "default"
                }
        
        self.logger.warning("Using default predictions (all devices off)")
        return default_predictions
    
    def _make_robust_prediction(self, final_input):
        """Attempt predictions with additional error handling and fallbacks"""
        if not self.ml_model_manager:
            return self._get_default_prediction()
        
        try:
            # Try to get predictions from model manager
            predictions = self.ml_model_manager.predict_device_states(final_input)
            
            # Validate predictions
            if not predictions:
                return self._get_default_prediction()
                
            return predictions
        except Exception as e:
            self.logger.error(f"Robust prediction failed: {str(e)}")
            return self._get_default_prediction()
        

# Simülatör sınıfını test etmek için yardımcı fonksiyon
def run_simulation_demo(steps=50, rooms=None, display=True):
    """
    Simülasyon demosunu çalıştırır
    
    Args:
        steps (int): Simülasyon adım sayısı
        rooms (list): Simüle edilecek odalar
        display (bool): Görsel çıktı olup olmayacağı
        
    Returns:
        SmartHomeSimulator: Çalıştırılan simülatör
    """
    # Varsayılan odalar
    if rooms is None:
        rooms = ["Salon", "Yatak Odası", "Çocuk Odası", "Mutfak", "Banyo"]
    
    # Simülatörü oluştur
    simulator = SmartHomeSimulator(
        rooms=rooms,
        num_residents=3,
        time_step=5,  # 5 dakikalık adımlar
        use_ml=True,
        simulation_speed=2.0  # 2x hızlı simülasyon
    )
    
    # Simülasyonu başlat
    simulator.run_simulation(steps=steps, display=display, delay=0.5)
    
    # Geçmişi kaydet
    simulator.save_history()
    
    return simulator

if __name__ == "__main__":
    run_simulation_demo(steps=100)