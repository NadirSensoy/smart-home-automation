from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import os
import sklearn
from packaging import version
import inspect
import logging

class SmartHomeDataProcessor(BaseEstimator, TransformerMixin):
    """
    Akıllı ev sensör verilerini makine öğrenmesi için hazırlayan sklearn uyumlu transformer.
    Tüm özellik çıkarımı ve dönüştürme işlemlerini burada yapar.
    """
    def __init__(self, test_size=0.2, random_state=42):
        self.test_size = test_size
        self.random_state = random_state
        self.numerical_features = []
        self.categorical_features = []
        self.target_device_columns = []
        self.feature_names = []
        self.preprocessor = None
        self.logger = logging.getLogger(__name__)
        # Store all expected device columns detected during fit
        self.all_device_columns = []

    def _ensure_all_device_columns(self, X):
        """
        Ensures all expected device state columns are present in the DataFrame.
        Adds missing columns with default values (False for boolean device states).
        
        Args:
            X (pandas.DataFrame): Input DataFrame
            
        Returns:
            pandas.DataFrame: DataFrame with all expected device columns
        """
        if not self.all_device_columns:
            # If no device columns stored yet, detect them from current DataFrame
            device_columns = []
            for column in X.columns:
                if any(device in column for device in ['Klima', 'Lamba', 'Perde', 'Havalandırma']):
                    device_columns.append(column)
            self.all_device_columns = device_columns
            
        # Ensure all expected device columns are present
        X_copy = X.copy()
        missing_columns = set(self.all_device_columns) - set(X_copy.columns)
        
        if missing_columns:
            self.logger.info(f"Adding {len(missing_columns)} missing device columns: {list(missing_columns)}")
            for col in missing_columns:
                # Add missing device state columns with default value False
                X_copy[col] = False
                
        return X_copy

    def fit(self, X, y=None):
        print("DEBUG: Columns at start of fit:", X.columns.tolist())
        # Check for 'timestamp' at the very start
        if 'timestamp' not in X.columns:
            raise ValueError("Input DataFrame must contain a 'timestamp' column for time feature extraction.")
        # Extract time features if 'timestamp' exists
        X = self._extract_time_features(X)
        X = X.drop(columns=['timestamp'])
        # Detect and store all device columns seen during fit
        self.prepare_target_variables(X)
        self.all_device_columns = list(self.target_device_columns)
        # Ensure all device columns are present
        X = self._ensure_all_device_columns(X)
        # Automatically detect all object/category columns as categorical features
        self.categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()
        # Remove target columns from categorical features if present
        for target in self.target_device_columns:
            if target in self.categorical_features:
                self.categorical_features.remove(target)
        # Remove target columns from X before fitting transformer
        for target in self.target_device_columns:
            if target in X.columns:
                X = X.drop(columns=[target])
        print("==== CATEGORICAL FEATURES DETECTED ====")
        print(self.categorical_features)
        # Print all object columns, their unique values, and dtypes
        obj_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
        print("==== OBJECT COLUMNS AND UNIQUES ====")
        for col in obj_cols:
            print(f"Column: {col}, dtype: {X[col].dtype}, uniques: {X[col].unique()[:10]}")
        # Build and fit the ColumnTransformer
        self.column_transformer = ColumnTransformer(
            transformers=[
                ('cat', OneHotEncoder(handle_unknown='ignore'), self.categorical_features)
            ],
            remainder='passthrough'
        )
        self.column_transformer.fit(X)
        print("==== COLUMN TRANSFORMER CONFIGURATION ====")
        print(self.column_transformer)
        X = self.extract_custom_features(X)
        X = remove_duplicate_columns(X)
        self._get_feature_columns(X)
        self.preprocessor = self.build_preprocessing_pipeline()
        self.preprocessor.fit(X)
        return self

    def transform(self, X):
        # Extract time features if 'timestamp' exists
        if 'timestamp' in X.columns:
            X = self._extract_time_features(X)
            X = X.drop(columns=['timestamp'])
        # Ensure all device columns are present
        X = self._ensure_all_device_columns(X)
        # Remove target columns if present
        for target in self.target_device_columns:
            if target in X.columns:
                X = X.drop(columns=[target])
        # Apply the fitted ColumnTransformer
        X_transformed = self.column_transformer.transform(X)
        return X_transformed

    def fit_transform(self, X, y=None):
        return self.fit(X, y).transform(X)

    def process_data_for_prediction(self, X):
        # For prediction: expects a DataFrame with raw features
        return self.transform(X)

    def build_preprocessing_pipeline(self):
        numerical_transformer = Pipeline(steps=[
            ('scaler', StandardScaler())
        ])
        # Robust OneHotEncoder initialization for all sklearn versions
        if 'sparse_output' in inspect.signature(OneHotEncoder).parameters:
            encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        else:
            encoder = OneHotEncoder(handle_unknown='ignore')
        categorical_transformer = Pipeline(steps=[
            ('onehot', encoder)
        ])
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numerical_transformer, self.numerical_features),
                ('cat', categorical_transformer, self.categorical_features)
            ],
            remainder='drop'
        )
        return preprocessor

    def load_data(self, csv_path):
        """
        CSV dosyasından verileri yükler
        
        Args:
            csv_path (str): CSV dosyasının yolu
            
        Returns:
            pandas.DataFrame: Yüklenen veri çerçevesi
        """
        self.logger.info(f"Veriler {csv_path} konumundan yükleniyor...")
        return pd.read_csv(csv_path)
    
    def _extract_time_features(self, df):
        """
        Zaman damgasından özellikler çıkarır: saat, dakika, gün, hafta içi/sonu
        
        Args:
            df (pandas.DataFrame): Giriş veri çerçevesi
            
        Returns:
            pandas.DataFrame: Zaman özellikleri eklenmiş veri çerçevesi
        """
        if 'timestamp' not in df.columns:
            return df
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Zaman özelliklerini çıkar
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
        
        # Gün içindeki zaman dilimini kategorik özellik olarak ekle
        conditions = [
            (df['hour'] >= 5) & (df['hour'] < 9),
            (df['hour'] >= 9) & (df['hour'] < 17),
            (df['hour'] >= 17) & (df['hour'] < 22),
            (df['hour'] >= 22) | (df['hour'] < 5)
        ]
        time_periods = ['Sabah', 'Gündüz', 'Akşam', 'Gece']
        df['time_period'] = np.select(conditions, time_periods, default='Diğer')
        
        return df
    
    def clean_data(self, df):
        """
        Verideki eksik değerleri doldurur ve veri temizliği yapar
        
        Args:
            df (pandas.DataFrame): Ham veri çerçevesi
            
        Returns:
            pandas.DataFrame: Temizlenmiş veri çerçevesi
        """
        self.logger.info("Veri temizleniyor...")
        
        # Orijinal verilerin bir kopyasını oluştur
        df_clean = df.copy()
        
        # Eksik değerleri doldur
        for column in df_clean.columns:
            # Sayısal değerler için
            if df_clean[column].dtype in ['float64', 'int64'] and df_clean[column].isna().any():
                # `inplace=True` kullanmak yerine değer atama kullan
                df_clean[column] = df_clean[column].fillna(df_clean[column].mean())
                
            # Boolean veya kategorik değerler için
            elif df_clean[column].dtype in ['object', 'bool', 'category'] and df_clean[column].isna().any():
                # `inplace=True` kullanmak yerine değer atama kullan
                df_clean[column] = df_clean[column].fillna(df_clean[column].mode()[0])
        
        # Gereksiz sütunları kaldır (örneğin tüm değerleri eksik olan)
        df_clean = df_clean.dropna(axis=1, how='all')
        
        # Satır sayısını kontrol et
        if df_clean.empty:
            raise ValueError("Temizlemeden sonra veri seti boş!")
            
        return df_clean
    
    def extract_custom_features(self, df):
        """
        Veri setinden özel özellikler çıkarır - daha iyi tahmin için ek özellikler oluşturur
        
        Args:
            df (pandas.DataFrame): Zaman özellikleri eklenmiş veri çerçevesi
            
        Returns:
            pandas.DataFrame: Özel özellikler eklenmiş veri çerçevesi
        """
        self.logger.info("Özel özellikler çıkarılıyor...")
        
        # Create a copy of the DataFrame to work with
        df_input = df.copy()
        
        # Instead of adding columns one by one, collect all features in a dictionary
        new_features = {}
        
        # Identify all rooms
        rooms = set()
        for column in df.columns:
            if '_' in column:
                room = column.split('_')[0]
                if room not in ["timestamp", "hour", "minute", "day", "is", "time"]:
                    rooms.add(room)
        
        # Calculate features for each room
        for room in rooms:
            # ----------- Hareket ve doluluk özellikleri -----------
            movement_col = f"{room}_Hareket"
            occupancy_col = f"{room}_Doluluk"
            
            if movement_col in df.columns:
                # Son 1 saatteki hareket sayısı (12 adım = 60 dakika, her 5 dakikada bir ölçüm)
                new_features[f"{room}_Hareket_Son1Saat"] = df[movement_col].rolling(window=12, min_periods=1).sum().values
                
                # Son 3 saatteki hareket oranı
                new_features[f"{room}_Hareket_Oran3Saat"] = df[movement_col].rolling(window=36, min_periods=1).mean().values
                
                # Son hareketin üzerinden geçen dakika sayısı (vectorized)
                # Find the last index where movement was True
                last_true = df[movement_col].eq(True).cumsum()
                last_true_idx = df[movement_col][df[movement_col]].index
                last_seen = df[movement_col].eq(True).cumsum().replace(0, np.nan)
                last_seen_idx = last_seen.where(df[movement_col]).ffill().fillna(0)
                # Calculate the time since last movement in steps, then multiply to minutes
                idx = np.arange(len(df))
                last_true_idx = np.where(df[movement_col])[0]
                last_seen_idx = np.maximum.accumulate(np.where(df[movement_col], idx, -1))
                minutes_since_movement = (idx - last_seen_idx) * 5
                new_features[f"{room}_SonHareket_Dakika"] = minutes_since_movement
            
            if occupancy_col in df.columns:
                # Doluluk oranı (son 1 saat)
                new_features[f"{room}_Doluluk_Oran"] = df[occupancy_col].rolling(window=12, min_periods=1).mean().values
            
            # ----------- Sensör değişim hızları -----------
            for sensor in ["Sıcaklık", "Nem", "CO2", "Işık"]:
                col = f"{room}_{sensor}"
                if col in df.columns:
                    # Sensör değişim hızı (önceki değere göre)
                    new_features[f"{room}_{sensor}_Değişim"] = df[col].diff().values
                    
                    # Son 1 saatteki ortalama değer ve standart sapma
                    new_features[f"{room}_{sensor}_Ort1Saat"] = df[col].rolling(window=12, min_periods=1).mean().values
                    new_features[f"{room}_{sensor}_Std1Saat"] = df[col].rolling(window=12, min_periods=1).std().values
            
            # ----------- Gün içi aktivite paterni -----------
            if occupancy_col in df.columns and 'hour' in df.columns:
                # Combine all these calculations for better performance
                new_features[f"{room}_SabahDoluluk"] = ((df['hour'] >= 6) & (df['hour'] < 9) & df[occupancy_col]).astype(int).values
                new_features[f"{room}_GündüzDoluluk"] = ((df['hour'] >= 9) & (df['hour'] < 17) & df[occupancy_col]).astype(int).values
                new_features[f"{room}_AkşamDoluluk"] = ((df['hour'] >= 17) & (df['hour'] < 22) & df[occupancy_col]).astype(int).values
                new_features[f"{room}_GeceDoluluk"] = (((df['hour'] >= 22) | (df['hour'] < 6)) & df[occupancy_col]).astype(int).values
        
        # ----------- Tüm ev özellikleri -----------
        
        # Evdeki toplam kişi sayısı
        person_columns = [col for col in df.columns if "Kişi_" in col and "_Konum" in col]
        if person_columns:
            # Evde bulunan (None olmayan konum) kişi sayısı
            new_features["Evdeki_Kişi_Sayısı"] = df[person_columns].notnull().sum(axis=1).values
        
        # Aktif oda sayısı (dolu olan)
        occupancy_columns = [col for col in df.columns if "Doluluk" in col]
        if occupancy_columns:
            new_features["Aktif_Oda_Sayısı"] = df[occupancy_columns].sum(axis=1).values
        
        # Çalışan cihaz sayısı
        device_columns = []
        for device in ["Klima", "Lamba", "Perde", "Havalandırma"]:
            device_columns.extend([col for col in df.columns if col.endswith(device)])
        
        if device_columns:
            new_features["Çalışan_Cihaz_Sayısı"] = df[device_columns].sum(axis=1).values
        
        # Create a DataFrame with all the new features at once
        features_df = pd.DataFrame(new_features, index=df.index)
        
        # Combine original DataFrame and new features
        result = pd.concat([df, features_df], axis=1)
        
        # Fill any NaN values
        result = result.bfill().ffill().fillna(0)
        
        self.logger.info(f"Toplam {len(features_df.columns)} yeni özellik eklendi")
        return result
    
    def prepare_target_variables(self, df):
        """
        Hedef değişkenleri hazırlar (cihaz durumları)
        
        Args:
            df (pandas.DataFrame): Giriş veri çerçevesi
            
        Returns:
            pandas.DataFrame: Hedef değişkenler eklenmiş veri çerçevesi
        """
        self.logger.info("Hedef değişkenler hazırlanıyor...")
        
        # Cihaz durumu sütunlarını belirle
        self.target_device_columns = []
        for column in df.columns:
            if any(device in column for device in ['Klima', 'Lamba', 'Perde', 'Havalandırma']):
                self.target_device_columns.append(column)
        
        # Hedef sütun kontrolü ekle
        if not self.target_device_columns:
            self.logger.warning("UYARI: Hiçbir cihaz sütunu bulunamadı!")
            self.logger.warning(f"Mevcut sütunlar: {df.columns.tolist()}")
        else:
            self.logger.info(f"Bulunan cihaz sütunları: {self.target_device_columns}")
        
        return df
    
    def _get_feature_columns(self, df):
        """
        Özellik sütunlarını ve türlerini belirler
        
        Args:
            df (pandas.DataFrame): Giriş veri çerçevesi
        """
        # Hedef değişken olmayan tüm sütunlar
        excluded_cols = self.target_device_columns + ['timestamp']
        
        # Sayısal ve kategorik özellikleri ayır
        self.numerical_features = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        self.categorical_features = df.select_dtypes(include=['object', 'bool']).columns.tolist()
        
        # Hedef değişkenleri ve timestamp'i çıkar
        self.numerical_features = [col for col in self.numerical_features if col not in excluded_cols]
        self.categorical_features = [col for col in self.categorical_features if col not in excluded_cols]
    
    def create_ml_dataset(self, df):
        """
        Makine öğrenmesi için veri seti oluşturur
        
        Args:
            df (pandas.DataFrame): İşlenmiş veri çerçevesi
            
        Returns:
            tuple: X (özellikler), targets (hedef sözlüğü)
        """
        self.logger.info("Makine öğrenmesi veri seti oluşturuluyor...")
        
        # Özellik sütunlarını belirle - timestamp ve cihaz durumları hariç
        feature_cols = [col for col in df.columns if col not in self.target_device_columns and col != 'timestamp']
        
        # Eğer feature_cols boşsa hata ver
        if not feature_cols:
            raise ValueError("Özellik sütunları bulunamadı!")
        
        # X (özellikler) ve targets (hedefler) oluştur
        X = df[feature_cols].copy()  # copy() ile yeni bir kopya oluştur
        
        # Özellik adlarını kaydet
        self.feature_names = feature_cols
        
        # X boşsa hata ver
        if X.empty:
            raise ValueError("Özellik matrisi boş!")
        
        # Hedef değişkenler
        targets = {}
        for col in self.target_device_columns:
            # Kategorik değerlere dönüştür (boolean -> int)
            if df[col].dtype == bool:
                targets[col] = df[col].astype(int)
            else:
                targets[col] = df[col]
        
        # Hedefler boşsa hata ver
        if not targets:
            raise ValueError("Hedef değişkenler bulunamadı!")
        
        # Ek bilgileri yazdır
        self.logger.info(f"Özellik matrisi boyutu: {X.shape}")
        self.logger.info(f"Hedef değişken sayısı: {len(targets)}")
        self.logger.info(f"İlk birkaç satır örneği:")
        self.logger.info(X.head(2))
        
        return X, targets
    
    def split_data(self, df, targets):
        """
        Veriyi eğitim ve test setlerine böler (raw DataFrame ile)
        Args:
            df (pandas.DataFrame): Ham veri çerçevesi (tüm sütunlar dahil)
            targets (dict): Hedef değişkenler sözlüğü
        Returns:
            tuple: df_train, df_test, y_train_dict, y_test_dict
        """
        self.logger.info(f"Veri {self.test_size*100}% test, {(1-self.test_size)*100}% eğitim olarak ayrılıyor...")
        if df.empty:
            raise ValueError(f"Veri seti boş! df boyutu: {df.shape}")
        if not targets:
            raise ValueError("Hedef seti boş!")
        y_train_dict = {}
        y_test_dict = {}
        first_target = list(targets.keys())[0]
        X_indices = np.arange(len(df))
        for target_name, y in targets.items():
            self.logger.info(f"Hedef '{target_name}' benzersiz değerleri: {np.unique(y)}, şekil: {y.shape}")
            if target_name == first_target:
                X_train_idx, X_test_idx, y_train_first, y_test_first = train_test_split(
                    X_indices, y, test_size=self.test_size, random_state=self.random_state
                )
                df_train = df.iloc[X_train_idx]
                df_test = df.iloc[X_test_idx]
                y_train_dict[first_target] = y_train_first
                y_test_dict[first_target] = y_test_first
            else:
                y_train_dict[target_name] = y.iloc[X_train_idx]
                y_test_dict[target_name] = y.iloc[X_test_idx]
        return df_train, df_test, y_train_dict, y_test_dict
    
    def save_processed_data(self, X_train, X_test, y_train_dict, y_test_dict, output_dir=None):
        """
        İşlenmiş verileri kaydeder
        
        Args:
            X_train, X_test: Eğitim ve test özellikleri
            y_train_dict, y_test_dict: Eğitim ve test hedef değişkenleri
            output_dir (str): Çıktı dizini
        """
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "processed")
        
        # Dizin yoksa oluştur
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Özellikleri kaydet
        X_train.to_csv(os.path.join(output_dir, "X_train.csv"), index=False)
        X_test.to_csv(os.path.join(output_dir, "X_test.csv"), index=False)
        
        # Hedef değişkenleri kaydet
        for target_name in y_train_dict:
            y_train_dict[target_name].to_csv(os.path.join(output_dir, f"y_train_{target_name}.csv"), index=False)
            y_test_dict[target_name].to_csv(os.path.join(output_dir, f"y_test_{target_name}.csv"), index=False)
        
        self.logger.info(f"İşlenmiş veriler {output_dir} konumuna kaydedildi.")
    
    def process_data(self, csv_path, save_processed=True, output_dir=None):
        self.logger.info(f"Veriler {csv_path} konumundan yükleniyor...")
        df = self.load_data(csv_path)
        self.logger.info(f"Ham veri boyutu: {df.shape}")
        df_clean = self.clean_data(df)
        self.logger.info(f"Temizlenmiş veri boyutu: {df_clean.shape}")
        df_features = self._extract_time_features(df_clean)
        self.logger.info(f"Zaman özellikleri eklenmiş veri boyutu: {df_features.shape}")
        df_features = self.extract_custom_features(df_features)
        self.logger.info(f"Özel özellikler eklenmiş veri boyutu: {df_features.shape}")
        df_with_targets = self.prepare_target_variables(df_features)
        self.logger.info(f"Hedefler eklendikten sonra veri boyutu: {df_with_targets.shape}")
        X, targets = self.create_ml_dataset(df_with_targets)
        self.logger.info(f"Son özellik matrisi boyutu: {X.shape}")
        # Split the raw DataFrame (with all columns)
        df_train, df_test, y_train_dict, y_test_dict = self.split_data(df_with_targets, targets)
        if save_processed:
            self.save_processed_data(df_train, df_test, y_train_dict, y_test_dict, output_dir)
        return df_train, df_test, y_train_dict, y_test_dict, self

# __init__.py dosyasına eklemek için temel fonksiyonlar
def process_raw_data(csv_path, save_processed=True, output_dir=None):
    """
    Ham veri dosyasını işleyerek makine öğrenmesi için hazır hale getirir
    
    Args:
        csv_path (str): Ham veri CSV dosya yolu
        save_processed (bool): İşlenmiş verilerin kaydedilip kaydedilmeyeceği
        output_dir (str): İşlenmiş verilerin kaydedileceği dizin
        
    Returns:
        tuple: X_train, X_test, y_train_dict, y_test_dict, preprocessor
    """
    processor = SmartHomeDataProcessor()
    return processor.process_data(csv_path, save_processed, output_dir)

# Test işlevi
def test_data_processing():
    """SmartHomeDataProcessor'ı test eder"""
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
    processor = SmartHomeDataProcessor()
    X_train, X_test, y_train_dict, y_test_dict, preprocessor = processor.process_data(
        csv_path, save_processed=True
    )
    
    print("\nEğitim seti boyutu:", X_train.shape)
    print("Test seti boyutu:", X_test.shape)
    print("Hedef değişkenler:", list(y_train_dict.keys()))
    print("\nSayısal özellikler:", processor.numerical_features)
    print("\nKategorik özellikler:", processor.categorical_features)

def remove_duplicate_columns(df):
    duplicates = df.columns[df.columns.duplicated()].unique()
    if len(duplicates) > 0:
        print(f"Warning: Duplicate columns found and removed: {list(duplicates)}")
    return df.loc[:, ~df.columns.duplicated()]

if __name__ == "__main__":
    test_data_processing()