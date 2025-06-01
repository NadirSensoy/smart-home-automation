from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import os

class SmartHomeDataProcessor(BaseEstimator, TransformerMixin):
    """
    Akıllı ev sensör verilerini makine öğrenmesi için hazırlayan sınıf.
    Veri temizleme, özellik çıkarımı ve dönüştürme işlemlerini gerçekleştirir.
    """
    
    def __init__(self, test_size=0.2, random_state=42):
        """SmartHomeDataProcessor sınıfını başlatır"""
        self.scaler = StandardScaler()
        # sparse=False yerine sparse_output=False kullanılmalı (güncel scikit-learn için)
        self.encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore') 
        self.numerical_features = []
        self.categorical_features = []
        self.feature_names = []
        self.target_device_columns = []
        # Eksik değişkenler eklendi
        self.test_size = test_size
        self.random_state = random_state
    
    def load_data(self, csv_path):
        """
        CSV dosyasından verileri yükler
        
        Args:
            csv_path (str): CSV dosyasının yolu
            
        Returns:
            pandas.DataFrame: Yüklenen veri çerçevesi
        """
        print(f"Veriler {csv_path} konumundan yükleniyor...")
        return pd.read_csv(csv_path)
    
    def _extract_time_features(self, df):
        """
        Zaman damgasından özellikler çıkarır: saat, dakika, gün, hafta içi/sonu
        
        Args:
            df (pandas.DataFrame): Giriş veri çerçevesi
            
        Returns:
            pandas.DataFrame: Zaman özellikleri eklenmiş veri çerçevesi
        """
        # Timestamp sütununu datetime'a dönüştür
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
        print("Veri temizleniyor...")
        
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
    
    def extract_features(self, df):
        """
        Veri setinden özellikler çıkarır ve dönüştürmeler yapar
        
        Args:
            df (pandas.DataFrame): Giriş veri çerçevesi
            
        Returns:
            pandas.DataFrame: Özellik mühendisliği uygulanmış veri çerçevesi
        """
        print("Özellikler çıkarılıyor...")
        
        # Tek bir dict oluştur, sonra DataFrame'e dönüştür
        features_dict = {}
        
        # Tüm özellikleri features_dict'e ekle
        
        # Son olarak DataFrame oluştur
        df_features = pd.DataFrame(features_dict)
        
        return df_features
    
    def prepare_target_variables(self, df):
        """
        Hedef değişkenleri hazırlar (cihaz durumları)
        
        Args:
            df (pandas.DataFrame): Giriş veri çerçevesi
            
        Returns:
            pandas.DataFrame: Hedef değişkenler eklenmiş veri çerçevesi
        """
        print("Hedef değişkenler hazırlanıyor...")
        
        # Cihaz durumu sütunlarını belirle
        self.target_device_columns = []
        for column in df.columns:
            if any(device in column for device in ['Klima', 'Lamba', 'Perde', 'Havalandırma']):
                self.target_device_columns.append(column)
        
        # Hedef sütun kontrolü ekle
        if not self.target_device_columns:
            print("UYARI: Hiçbir cihaz sütunu bulunamadı!")
            print(f"Mevcut sütunlar: {df.columns.tolist()}")
        else:
            print(f"Bulunan cihaz sütunları: {self.target_device_columns}")
        
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
        print("Makine öğrenmesi veri seti oluşturuluyor...")
        
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
        print(f"Özellik matrisi boyutu: {X.shape}")
        print(f"Hedef değişken sayısı: {len(targets)}")
        print(f"İlk birkaç satır örneği:")
        print(X.head(2))
        
        return X, targets
    
    def split_data(self, X, targets):
        """
        Veriyi eğitim ve test setlerine böler
        
        Args:
            X (pandas.DataFrame): Özellik matrisi
            targets (dict): Hedef değişkenler sözlüğü
            
        Returns:
            tuple: X_train, X_test, y_train_dict, y_test_dict
        """
        print(f"Veri {self.test_size*100}% test, {(1-self.test_size)*100}% eğitim olarak ayrılıyor...")
        
        if X.empty:
            raise ValueError(f"Özellik veri seti boş! X boyutu: {X.shape}")
        
        if not targets:
            raise ValueError("Hedef seti boş!")
        
        # Hedef sözlüklerini başlangıçta tanımla
        y_train_dict = {}  # Bu satırı ekleyin
        y_test_dict = {}   # Bu satırı ekleyin
        
        # İlk önce indeksleri ayır
        first_target = list(targets.keys())[0]
        X_indices = np.arange(len(X))
        
        # Özellik değişkenlerini her hedef için ayrı ayrı hedef değişkenleriyle ayır
        for target_name, y in targets.items():
            print(f"Hedef '{target_name}' benzersiz değerleri: {np.unique(y)}, şekil: {y.shape}")
            
            if target_name == first_target:
                # İlk hedef için indeksleri ayır
                X_train_idx, X_test_idx, y_train_first, y_test_first = train_test_split(
                    X_indices, y, test_size=self.test_size, random_state=self.random_state
                )
                
                # X'i böl
                X_train = X.iloc[X_train_idx]
                X_test = X.iloc[X_test_idx]
                
                # İlk hedefi sözlüğe ekle
                y_train_dict[first_target] = y_train_first
                y_test_dict[first_target] = y_test_first
            else:
                # Diğer hedefler için önceden ayrılmış indeksleri kullan
                y_train_dict[target_name] = y.iloc[X_train_idx]
                y_test_dict[target_name] = y.iloc[X_test_idx]
    
        return X_train, X_test, y_train_dict, y_test_dict
    
    def build_preprocessing_pipeline(self):
        """
        Veri ön işleme pipeline'ı oluşturur
        
        Returns:
            sklearn.pipeline.Pipeline: Ön işleme pipeline'ı
        """
        print("Ön işleme pipeline'ı oluşturuluyor...")
        
        # Sayısal ve kategorik özellikler için dönüştürücüler
        numerical_transformer = Pipeline(steps=[
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('onehot', OneHotEncoder(sparse=False, handle_unknown='ignore'))
        ])
        
        # ColumnTransformer ile sütun tipine göre işleme
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numerical_transformer, self.numerical_features),
                ('cat', categorical_transformer, self.categorical_features)
            ],
            remainder='passthrough'
        )
        
        return preprocessor
    
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
        
        print(f"İşlenmiş veriler {output_dir} konumuna kaydedildi.")
    
    def process_data(self, csv_path, save_processed=True, output_dir=None):
        """
        Ham veriyi işleyip ML için hazır hale getirir
        
        Args:
            csv_path (str): CSV dosyasının yolu
            save_processed (bool): İşlenmiş veriyi kaydetme durumu
            output_dir (str): İşlenmiş verinin kaydedileceği dizin
            
        Returns:
            tuple: X_train, X_test, y_train_dict, y_test_dict, preprocessor
        """
        print(f"Veriler {csv_path} konumundan yükleniyor...")
        
        # Veriyi oku - read_data yerine load_data metodunu kullanın
        df = self.load_data(csv_path)  # Bu satırı değiştirin
        print(f"Ham veri boyutu: {df.shape}")
        
        # Veriyi temizle
        df_clean = self.clean_data(df)
        print(f"Temizlenmiş veri boyutu: {df_clean.shape}")
        
        # Zaman özelliklerini çıkar
        df_features = self._extract_time_features(df_clean)
        print(f"Zaman özellikleri eklenmiş veri boyutu: {df_features.shape}")
        
        # Özel özellikler çıkar
        df_features = self.extract_custom_features(df_features)
        print(f"Özel özellikler eklenmiş veri boyutu: {df_features.shape}")
        
        # Hedef değişkenleri belirle
        df_with_targets = self.prepare_target_variables(df_features)
        print(f"Hedefler eklendikten sonra veri boyutu: {df_with_targets.shape}")
        
        # ML dataset oluştur
        X, targets = self.create_ml_dataset(df_with_targets)
        print(f"Son özellik matrisi boyutu: {X.shape}")
        
        # Eğitim ve test setlerine böl
        X_train, X_test, y_train_dict, y_test_dict = self.split_data(X, targets)
        
        # İşlenmiş veriyi kaydet
        if save_processed:
            self.save_processed_data(X_train, X_test, y_train_dict, y_test_dict, output_dir)
        
        return X_train, X_test, y_train_dict, y_test_dict, self

    def extract_custom_features(self, df):
        """
        Veri setinden özel özellikler çıkarır - daha iyi tahmin için ek özellikler oluşturur
        
        Args:
            df (pandas.DataFrame): Zaman özellikleri eklenmiş veri çerçevesi
            
        Returns:
            pandas.DataFrame: Özel özellikler eklenmiş veri çerçevesi
        """
        print("Özel özellikler çıkarılıyor...")
        
        # DataFrame'in bir kopyasını oluştur
        df_features = df.copy()
        
        # Her bir oda için özel özellikler oluştur
        rooms = set()
        for column in df.columns:
            if '_' in column:
                room = column.split('_')[0]
                if room not in ["timestamp", "hour", "minute", "day", "is", "time"]:
                    rooms.add(room)
        
        # Her oda için
        for room in rooms:
            # ----------- Hareket ve doluluk özellikleri -----------
            movement_col = f"{room}_Hareket"
            occupancy_col = f"{room}_Doluluk"
            
            if movement_col in df.columns:
                # Son 1 saatteki hareket sayısı (12 adım = 60 dakika, her 5 dakikada bir ölçüm)
                df_features[f"{room}_Hareket_Son1Saat"] = df[movement_col].rolling(window=12, min_periods=1).sum()
                
                # Son 3 saatteki hareket oranı
                df_features[f"{room}_Hareket_Oran3Saat"] = df[movement_col].rolling(window=36, min_periods=1).mean()
                
                # Son hareketin üzerinden geçen dakika sayısı
                last_movement = df_features[movement_col].copy()
                minutes_since_movement = last_movement * 0  # Başlangıç değeri
                
                # Her satır için son hareket üzerinden geçen dakika sayısını hesapla
                counter = 0
                for i in range(len(last_movement)):
                    if last_movement.iloc[i]:  # Hareket varsa
                        counter = 0
                    else:
                        counter += 5  # 5 dakikalık adımlar
                    minutes_since_movement.iloc[i] = counter
                    
                df_features[f"{room}_SonHareket_Dakika"] = minutes_since_movement
            
            if occupancy_col in df.columns:
                # Doluluk oranı (son 1 saat)
                df_features[f"{room}_Doluluk_Oran"] = df[occupancy_col].rolling(window=12, min_periods=1).mean()
            
            # ----------- Sensör değişim hızları -----------
            for sensor in ["Sıcaklık", "Nem", "CO2", "Işık"]:
                col = f"{room}_{sensor}"
                if col in df.columns:
                    # Sensör değişim hızı (önceki değere göre)
                    df_features[f"{room}_{sensor}_Değişim"] = df[col].diff()
                    
                    # Son 1 saatteki ortalama değer
                    df_features[f"{room}_{sensor}_Ort1Saat"] = df[col].rolling(window=12, min_periods=1).mean()
                    
                    # Son 1 saatteki standart sapma (değişkenlik)
                    df_features[f"{room}_{sensor}_Std1Saat"] = df[col].rolling(window=12, min_periods=1).std()
            
            # ----------- Gün içi aktivite paterni -----------
            if occupancy_col in df.columns and 'hour' in df.columns:
                # Saat bazında doluluk
                df_features[f"{room}_SabahDoluluk"] = ((df['hour'] >= 6) & (df['hour'] < 9) & df[occupancy_col]).astype(int)
                df_features[f"{room}_GündüzDoluluk"] = ((df['hour'] >= 9) & (df['hour'] < 17) & df[occupancy_col]).astype(int)
                df_features[f"{room}_AkşamDoluluk"] = ((df['hour'] >= 17) & (df['hour'] < 22) & df[occupancy_col]).astype(int)
                df_features[f"{room}_GeceDoluluk"] = (((df['hour'] >= 22) | (df['hour'] < 6)) & df[occupancy_col]).astype(int)
        
        # ----------- Tüm ev özellikleri -----------
        
        # Evdeki toplam kişi sayısı
        person_columns = [col for col in df.columns if "Kişi_" in col and "_Konum" in col]
        if person_columns:
            # Evde bulunan (None olmayan konum) kişi sayısı
            df_features["Evdeki_Kişi_Sayısı"] = df[person_columns].notnull().sum(axis=1)
        
        # Aktif oda sayısı (dolu olan)
        occupancy_columns = [col for col in df.columns if "Doluluk" in col]
        if occupancy_columns:
            df_features["Aktif_Oda_Sayısı"] = df[occupancy_columns].sum(axis=1)
        
        # Çalışan cihaz sayısı
        device_columns = []
        for device in ["Klima", "Lamba", "Perde", "Havalandırma"]:
            device_columns.extend([col for col in df.columns if col.endswith(device)])
        
        if device_columns:
            df_features["Çalışan_Cihaz_Sayısı"] = df[device_columns].sum(axis=1)
        
        # İlk ve son satırlarda NaN değerler olabilir, bunları doldur
        df_features = df_features.bfill().ffill()

        # Kalan NaN değerleri 0 ile doldur
        df_features = df_features.fillna(0)
        
        print(f"Toplam {len(df_features.columns) - len(df.columns)} yeni özellik eklendi")
        return df_features

    def fit(self, X, y=None):
        """
        Scikit-learn arayüzü: İşlemciyi veriye uygula
        
        Args:
            X: Giriş özellikleri
            y: Hedef değişken (yok sayılır)
            
        Returns:
            self: Zincirleme için kendini döndürür
        """
        if isinstance(X, pd.DataFrame):
            # Özellik sütunlarını belirle
            self.numerical_features = X.select_dtypes(include=['number']).columns.tolist()
            self.categorical_features = X.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
            
            # Cihaz durumu sütunları
            self.target_device_columns = [col for col in X.columns if any(col.endswith(f"_{device}") 
                                         for device in ["Lamba", "Klima", "Perde", "TV", "Havalandırma"])]
        
        return self

    def transform(self, X):
        """
        Scikit-learn arayüzü: Veriyi dönüştür
        
        Args:
            X: Giriş özellikleri
            
        Returns:
            Dönüştürülmüş veri
        """
        # Veri tipi kontrolü
        if isinstance(X, pd.DataFrame):
            # Özellik isimlerini kontrol et
            missing_features = [f for f in self.feature_names if f not in X.columns]
            extra_features = [f for f in X.columns if f not in self.feature_names and f != 'timestamp']
            
            if missing_features:
                # Eksik özellikleri 0 ile doldur
                for feature in missing_features:
                    X[feature] = 0
                print(f"Uyarı: Bazı özellikler eksik, 0 ile dolduruldu: {missing_features}")
            
            if extra_features and len(extra_features) < 5:  # Çok fazlaysa gösterme
                print(f"Uyarı: Bazı ekstra özellikler var: {extra_features}")
                
            # Sayısal tipteki sütunlar
            numeric_cols = X.select_dtypes(include=['int64', 'float64']).columns
            
            # Eksik değerleri doldur
            X = X.fillna(0)
            
            # Yalnızca sayısal verileri döndür
            X_numeric = X[numeric_cols]
            
            return X_numeric
        else:
            # DataFrame değilse hata ver veya dönüştür
            if hasattr(X, 'shape'):
                print(f"X şekli: {X.shape}, tipi: {type(X)}")
            return X
    
    def fit_transform(self, X, y=None):
        """
        Scikit-learn arayüzü: Uyumla ve dönüştür
        """
        return self.fit(X, y).transform(X)

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

if __name__ == "__main__":
    test_data_processing()