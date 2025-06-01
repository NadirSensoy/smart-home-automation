"""
Veri ve simülasyon görselleştirme yardımcıları
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from datetime import datetime, timedelta
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.animation as animation
from matplotlib.ticker import MaxNLocator
from sklearn.metrics import confusion_matrix, roc_curve, auc

class SimulationVisualizer:
    """
    Akıllı ev simülasyonunu görselleştirmek için kullanılan sınıf
    """
    
    def __init__(self, figsize=(16, 12), style="whitegrid", palette="viridis"):
        """
        Görselleştirici sınıfı başlatır
        
        Args:
            figsize (tuple): Grafik boyutu (genişlik, yükseklik)
            style (str): Seaborn stil teması
            palette (str): Renk paleti
        """
        self.figsize = figsize
        self.style = style
        self.palette = palette
        
        # Stil ayarları
        sns.set_style(style)
        sns.set_palette(palette)
        plt.rcParams['figure.figsize'] = figsize
        
        # Çıktı dizini
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports", "figures")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def plot_sensors_over_time(self, data, room=None, save=False, show=True):
        """
        Sensör verilerinin zaman içindeki değişimini görselleştirir
        
        Args:
            data (pandas.DataFrame): Sensör verilerini içeren DataFrame
            room (str): Gösterilecek oda (None ise tüm odalar)
            save (bool): Dosyaya kaydetme durumu
            show (bool): Ekranda gösterme durumu
            
        Returns:
            matplotlib.figure.Figure: Oluşturulan grafik figürü
        """
        # Veri kontrolü
        if not isinstance(data, pd.DataFrame):
            raise TypeError("data parametresi bir pandas DataFrame olmalıdır")
        
        if 'timestamp' not in data.columns:
            raise ValueError("DataFrame'de 'timestamp' sütunu bulunamadı")
            
        # Timestamp sütununu datetime'a dönüştür
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        
        # Sensör sütunlarını belirle
        sensor_types = ['Sıcaklık', 'Nem', 'CO2', 'Işık']
        
        # Oda filtresi
        if room:
            sensor_columns = [col for col in data.columns if room in col and any(sensor in col for sensor in sensor_types)]
        else:
            sensor_columns = [col for col in data.columns if any(sensor in col for sensor in sensor_types)]
        
        # Veri var mı kontrol et
        if not sensor_columns:
            raise ValueError(f"Belirtilen kriterlere uygun sensör verisi bulunamadı")
        
        # Sensör tiplerini grupla
        grouped_sensors = {}
        for sensor_type in sensor_types:
            cols = [col for col in sensor_columns if sensor_type in col]
            if cols:
                grouped_sensors[sensor_type] = cols
        
        # Grafik sayısı
        num_plots = len(grouped_sensors)
        if num_plots == 0:
            raise ValueError("Gösterilecek sensör verisi bulunamadı")
        
        # Grafikleri oluştur
        fig, axes = plt.subplots(num_plots, 1, figsize=self.figsize, sharex=True)
        
        # Tek sensör türü varsa axes'i listeye dönüştür
        if num_plots == 1:
            axes = [axes]
        
        # Her sensör tipi için grafik çiz
        for i, (sensor_type, columns) in enumerate(grouped_sensors.items()):
            ax = axes[i]
            
            # Her oda için çizgi çiz
            for col in columns:
                room_name = col.split('_')[0]
                ax.plot(data['timestamp'], data[col], label=f"{room_name}", linewidth=2)
            
            # Grafik güzelleştirmeleri
            ax.set_ylabel(sensor_type)
            ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1))
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Y ekseni sınırlarını ayarla
            if sensor_type == 'Sıcaklık':
                ax.set_ylim(15, 35)  # 15-35°C
            elif sensor_type == 'Nem':
                ax.set_ylim(20, 80)  # %20-80
            elif sensor_type == 'CO2':
                ax.set_ylim(300, 1500)  # 300-1500 ppm
        
        # X ekseni ayarları (en alttaki grafik için)
        axes[-1].set_xlabel("Zaman")
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        # Dosyaya kaydet
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            room_str = f"_{room}" if room else ""
            filename = f"sensors_over_time{room_str}_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Grafik kaydedildi: {filepath}")
        
        # Ekranda göster
        if show:
            plt.show()
        
        return fig
    
    def plot_room_occupancy(self, data, room=None, save=False, show=True):
        """
        Oda kullanım durumunu görselleştirir
        
        Args:
            data (pandas.DataFrame): Sensör verilerini içeren DataFrame
            room (str): Gösterilecek oda (None ise tüm odalar)
            save (bool): Dosyaya kaydetme durumu
            show (bool): Ekranda gösterme durumu
            
        Returns:
            matplotlib.figure.Figure: Oluşturulan grafik figürü
        """
        # Veri kontrolü
        if not isinstance(data, pd.DataFrame):
            raise TypeError("data parametresi bir pandas DataFrame olmalıdır")
        
        if 'timestamp' not in data.columns:
            raise ValueError("DataFrame'de 'timestamp' sütunu bulunamadı")
            
        # Timestamp sütununu datetime'a dönüştür
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        
        # Doluluk sütunlarını belirle
        if room:
            occupancy_columns = [col for col in data.columns if room in col and 'Doluluk' in col]
        else:
            occupancy_columns = [col for col in data.columns if 'Doluluk' in col]
        
        # Veri var mı kontrol et
        if not occupancy_columns:
            raise ValueError(f"Belirtilen kriterlere uygun doluluk verisi bulunamadı")
        
        # Grafik oluştur
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Her oda için çubuk çiz
        room_names = [col.split('_')[0] for col in occupancy_columns]
        
        # Zaman aralıklarını belirle
        time_periods = []
        current_time = data['timestamp'].min()
        while current_time <= data['timestamp'].max():
            time_periods.append(current_time)
            current_time += timedelta(hours=1)
        
        # Her oda için doluluk oranını hesapla
        occupancy_data = {}
        for i, col in enumerate(occupancy_columns):
            room_name = room_names[i]
            occupancy_data[room_name] = []
            
            for j in range(len(time_periods) - 1):
                start_time = time_periods[j]
                end_time = time_periods[j + 1]
                
                # Verilen zaman aralığındaki doluluk oranı
                mask = (data['timestamp'] >= start_time) & (data['timestamp'] < end_time)
                occupancy_ratio = data.loc[mask, col].mean() if mask.any() else 0
                occupancy_data[room_name].append(occupancy_ratio)
        
        # Verileri çizdir
        bar_width = 0.8 / len(occupancy_columns)
        for i, room_name in enumerate(occupancy_data.keys()):
            x = np.arange(len(time_periods) - 1) + i * bar_width
            ax.bar(x, occupancy_data[room_name], width=bar_width, label=room_name, alpha=0.7)
        
        # Grafik güzelleştirmeleri
        ax.set_ylabel('Doluluk Oranı')
        ax.set_xlabel('Saat Aralığı')
        ax.set_title('Oda Doluluk Oranları (Saatlik)')
        ax.set_xticks(np.arange(len(time_periods) - 1) + 0.4)
        ax.set_xticklabels([f"{t.strftime('%H:00')}" for t in time_periods[:-1]], rotation=45)
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7, axis='y')
        
        plt.tight_layout()
        
        # Dosyaya kaydet
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            room_str = f"_{room}" if room else ""
            filename = f"room_occupancy{room_str}_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Grafik kaydedildi: {filepath}")
        
        # Ekranda göster
        if show:
            plt.show()
        
        return fig
    
    def plot_device_usage(self, data, device_type=None, room=None, save=False, show=True):
        """
        Cihaz kullanım durumlarını görselleştirir
        
        Args:
            data (pandas.DataFrame): Cihaz verilerini içeren DataFrame
            device_type (str): Gösterilecek cihaz tipi (None ise tüm cihazlar)
            room (str): Gösterilecek oda (None ise tüm odalar)
            save (bool): Dosyaya kaydetme durumu
            show (bool): Ekranda gösterme durumu
            
        Returns:
            matplotlib.figure.Figure: Oluşturulan grafik figürü
        """
        # Veri kontrolü
        if not isinstance(data, pd.DataFrame):
            raise TypeError("data parametresi bir pandas DataFrame olmalıdır")
        
        if 'timestamp' not in data.columns:
            raise ValueError("DataFrame'de 'timestamp' sütunu bulunamadı")
            
        # Timestamp sütununu datetime'a dönüştür
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        
        # Cihaz sütunlarını belirle
        device_types = ['Klima', 'Lamba', 'Perde', 'Havalandırma']
        
        if device_type:
            if device_type not in device_types:
                raise ValueError(f"Geçersiz cihaz tipi. Desteklenen tipler: {device_types}")
            device_types = [device_type]
        
        if room:
            device_columns = [col for col in data.columns if room in col and any(device in col for device in device_types)]
        else:
            device_columns = [col for col in data.columns if any(device in col for device in device_types)]
        
        # Veri var mı kontrol et
        if not device_columns:
            raise ValueError(f"Belirtilen kriterlere uygun cihaz verisi bulunamadı")
        
        # Grafik oluştur
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Her cihaz için çizgi çiz
        for col in device_columns:
            parts = col.split('_')
            room_name = parts[0]
            device_name = parts[1]
            ax.step(data['timestamp'], data[col], where='post', label=f"{room_name} {device_name}", linewidth=2)
        
        # Grafik güzelleştirmeleri
        ax.set_ylabel('Durum (Açık/Kapalı)')
        ax.set_xlabel('Zaman')
        ax.set_title('Cihaz Kullanım Durumları')
        ax.set_yticks([0, 1])
        ax.set_yticklabels(['Kapalı', 'Açık'])
        ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.xticks(rotation=45)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        # Dosyaya kaydet
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            room_str = f"_{room}" if room else ""
            device_str = f"_{device_type}" if device_type else ""
            filename = f"device_usage{room_str}{device_str}_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Grafik kaydedildi: {filepath}")
        
        # Ekranda göster
        if show:
            plt.show()
        
        return fig
    
    def create_heatmap_visualization(self, data, target_column, feature_columns=None, save=False, show=True):
        """
        Özelliklerin hedef değişken üzerindeki etkisini gösteren heatmap oluşturur
        
        Args:
            data (pandas.DataFrame): Veri seti
            target_column (str): Hedef değişken sütunu
            feature_columns (list): Gösterilecek özellik sütunları (None ise otomatik seçilir)
            save (bool): Dosyaya kaydetme durumu
            show (bool): Ekranda gösterme durumu
            
        Returns:
            matplotlib.figure.Figure: Oluşturulan grafik figürü
        """
        # Veri kontrolü
        if not isinstance(data, pd.DataFrame):
            raise TypeError("data parametresi bir pandas DataFrame olmalıdır")
        
        if target_column not in data.columns:
            raise ValueError(f"Hedef sütun '{target_column}' veri setinde bulunamadı")
            
        # Özellik sütunlarını belirle
        if feature_columns is None:
            # Sayısal sütunları seç
            numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns
            # Kategorik sütunları kodla
            categorical_cols = data.select_dtypes(include=['object', 'category', 'bool']).columns
            
            # timestamp ve hedef sütunu hariç tüm sütunları al
            feature_columns = [col for col in numeric_cols if col != target_column and 'timestamp' not in col]
            
            # En fazla 10 özellik göster
            if len(feature_columns) > 10:
                feature_columns = feature_columns[:10]
        
        # Korelasyon matrisini hesapla
        corr_data = data[feature_columns + [target_column]].copy()
        
        # Kategorik değişkenleri sayısala dönüştür
        for col in corr_data.columns:
            if corr_data[col].dtype == 'bool':
                corr_data[col] = corr_data[col].astype(int)
        
        corr = corr_data.corr()
        
        # Grafik oluştur
        plt.figure(figsize=self.figsize)
        
        # Heatmap oluştur
        mask = np.zeros_like(corr)
        mask[np.triu_indices_from(mask)] = True
        
        # Özel renk paleti
        cmap = sns.diverging_palette(220, 10, as_cmap=True)
        
        # Heatmap çiz
        heatmap = sns.heatmap(corr, mask=mask, cmap=cmap, vmax=1, vmin=-1, center=0,
                square=True, linewidths=.5, annot=True, fmt=".2f", cbar_kws={"shrink": .5})
        
        plt.title('Özellikler ve Hedef Değişken Korelasyon Matrisi')
        
        # Dosyaya kaydet
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_str = target_column.replace(' ', '_').replace(',', '')
            filename = f"correlation_heatmap_{target_str}_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Grafik kaydedildi: {filepath}")
        
        # Ekranda göster
        if show:
            plt.show()
        
        return plt.gcf()
    
    def plot_model_performance(self, y_true, y_pred, y_prob=None, model_name="Model", save=False, show=True):
        """
        Model performansını görselleştirir (karmaşıklık matrisi ve ROC eğrisi)
        
        Args:
            y_true (array-like): Gerçek etiketler
            y_pred (array-like): Tahmin edilen etiketler
            y_prob (array-like): Tahmin olasılıkları (ROC eğrisi için)
            model_name (str): Model adı
            save (bool): Dosyaya kaydetme durumu
            show (bool): Ekranda gösterme durumu
            
        Returns:
            matplotlib.figure.Figure: Oluşturulan grafik figürü
        """
        # Konfüzyon matrisi
        cm = confusion_matrix(y_true, y_pred)
        
        # İki grafik oluştur (konfüzyon matrisi ve ROC eğrisi)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.figsize)
        
        # Konfüzyon matrisi
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax1)
        ax1.set_title(f'{model_name} Konfüzyon Matrisi')
        ax1.set_xlabel('Tahmin Edilen Etiket')
        ax1.set_ylabel('Gerçek Etiket')
        
        # ROC eğrisi (eğer olasılık değerleri verilmişse)
        if y_prob is not None:
            fpr, tpr, _ = roc_curve(y_true, y_prob)
            roc_auc = auc(fpr, tpr)
            
            ax2.plot(fpr, tpr, lw=2, label=f'ROC eğrisi (AUC = {roc_auc:.2f})')
            ax2.plot([0, 1], [0, 1], 'k--', lw=2)
            ax2.set_xlim([0.0, 1.0])
            ax2.set_ylim([0.0, 1.05])
            ax2.set_xlabel('Yanlış Pozitif Oranı')
            ax2.set_ylabel('Doğru Pozitif Oranı')
            ax2.set_title(f'{model_name} ROC Eğrisi')
            ax2.legend(loc="lower right")
        else:
            # ROC eğrisi çizilemiyorsa, doğruluk metriğini göster
            accuracy = np.sum(y_true == y_pred) / len(y_true)
            ax2.text(0.5, 0.5, f"Doğruluk: {accuracy:.2f}", horizontalalignment='center',
                    verticalalignment='center', transform=ax2.transAxes, fontsize=20)
            ax2.set_title(f'{model_name} Doğruluk')
            ax2.axis('off')
        
        plt.tight_layout()
        
        # Dosyaya kaydet
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_name_clean = model_name.replace(' ', '_').replace(',', '')
            filename = f"model_performance_{model_name_clean}_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Grafik kaydedildi: {filepath}")
        
        # Ekranda göster
        if show:
            plt.show()
        
        return fig
    
    def create_house_visualization(self, home_state, save=False, show=True):
        """
        Ev durumunun görsel temsilini oluşturur
        
        Args:
            home_state (dict): Ev durumu (odalar, sensörler, cihazlar)
            save (bool): Dosyaya kaydetme durumu
            show (bool): Ekranda gösterme durumu
            
        Returns:
            matplotlib.figure.Figure: Oluşturulan grafik figürü
        """
        # Ev durum kontrolü
        if not isinstance(home_state, dict) or 'rooms' not in home_state:
            raise ValueError("home_state geçerli bir ev durumu sözlüğü olmalıdır")
        
        rooms = home_state['rooms']
        
        # Oda sayısına göre ızgara boyutunu belirle
        n_rooms = len(rooms)
        ncols = min(3, n_rooms)
        nrows = (n_rooms + ncols - 1) // ncols  # Yukarı yuvarlama
        
        # Grafik oluştur
        fig, axes = plt.subplots(nrows, ncols, figsize=self.figsize)
        
        # Tek oda için axes'i düzelt
        if n_rooms == 1:
            axes = np.array([axes])
        
        # axes'i düzleştir
        axes = axes.flatten()
        
        # Her oda için bir panel
        for i, room_name in enumerate(rooms):
            ax = axes[i]
            
            # Oda durumu
            room_data = rooms[room_name]
            
            # Oda arkaplanı
            ax.set_facecolor("#f8f9fa")
            
            # Sensör değerlerini yazdır
            sensors = room_data.get('sensors', {})
            sensor_text = '\n'.join([
                f"Sıcaklık: {sensors.get('Sıcaklık', 'N/A')}°C",
                f"Nem: {sensors.get('Nem', 'N/A')}%",
                f"CO2: {sensors.get('CO2', 'N/A')} ppm",
                f"Işık: {sensors.get('Işık', 'N/A')} lux",
                f"Doluluk: {'Evet' if sensors.get('Doluluk', False) else 'Hayır'}",
                f"Hareket: {'Var' if sensors.get('Hareket', False) else 'Yok'}"
            ])
            
            # Cihaz durumları
            devices = room_data.get('devices', {})
            device_icons = {
                'Klima': '❄️' if devices.get('Klima', False) else '⚪',
                'Lamba': '💡' if devices.get('Lamba', False) else '⚪',
                'Perde': '🪟' if devices.get('Perde', False) else '⚪',
                'Havalandırma': '🌀' if devices.get('Havalandırma', False) else '⚪'
            }
            
            device_text = ' '.join([
                f"{icon} {name}"
                for name, icon in device_icons.items()
            ])
            
            # Doluluk durumuna göre kişi ikonu
            people_icons = ''
            if 'people' in room_data:
                for person_idx, person_name in room_data['people'].items():
                    people_icons += f"👤 {person_name}\n"
            
            # Metni odanın içine yerleştir
            ax.text(0.05, 0.95, room_name, transform=ax.transAxes, 
                   fontsize=14, fontweight='bold', va='top')
            
            ax.text(0.05, 0.85, sensor_text, transform=ax.transAxes, 
                   fontsize=10, va='top')
            
            ax.text(0.05, 0.3, device_text, transform=ax.transAxes, 
                   fontsize=12, va='top')
            
            if people_icons:
                ax.text(0.05, 0.15, people_icons, transform=ax.transAxes, 
                       fontsize=12, va='top')
            
            # Odanın sınırlarını çiz
            ax.spines['top'].set_visible(True)
            ax.spines['right'].set_visible(True)
            ax.spines['bottom'].set_visible(True)
            ax.spines['left'].set_visible(True)
            
            # Eksen etiketlerini kaldır
            ax.set_xticks([])
            ax.set_yticks([])
        
        # Artık odalar için boş grafikleri kaldır
        for i in range(n_rooms, len(axes)):
            fig.delaxes(axes[i])
        
        plt.tight_layout()
        
        # Dosyaya kaydet
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"house_visualization_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Grafik kaydedildi: {filepath}")
        
        # Ekranda göster
        if show:
            plt.show()
        
        return fig
    
    def create_animated_simulation(self, simulation_data, interval=200, save=False, show=True):
        """
        Simülasyon verilerinden animasyon oluşturur
        
        Args:
            simulation_data (list): Zaman içindeki simülasyon durumlarını içeren liste
            interval (int): Animasyon karesi arasındaki milisaniye cinsinden süre
            save (bool): Dosyaya kaydetme durumu
            show (bool): Ekranda gösterme durumu
            
        Returns:
            matplotlib.animation.Animation: Oluşturulan animasyon
        """
        if not simulation_data:
            raise ValueError("simulation_data boş olamaz")
        
        # İlk durum üzerinden oda sayısını ve adlarını al
        first_state = simulation_data[0]
        rooms = list(first_state['rooms'].keys())
        n_rooms = len(rooms)
        
        # Izgara boyutunu belirle
        ncols = min(3, n_rooms)
        nrows = (n_rooms + ncols - 1) // ncols
        
        # Grafik oluştur
        fig, axes = plt.subplots(nrows, ncols, figsize=self.figsize)
        
        # Tek oda için axes'i düzelt
        if n_rooms == 1:
            axes = np.array([axes])
        
        # axes'i düzleştir
        axes = axes.flatten()
        
        # Artık odalar için boş grafikleri kaldır
        for i in range(n_rooms, len(axes)):
            fig.delaxes(axes[i])
        
        # Animasyon başlığı
        fig.suptitle(f"Simülasyon: Adım 0 / {len(simulation_data)-1}", fontsize=16)
        
        def update(frame):
            """Her animasyon karesi için güncelleme fonksiyonu"""
            state = simulation_data[frame]
            
            # Başlık güncelleme
            timestamp = state.get('timestamp', '')
            timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S") if isinstance(timestamp, datetime) else str(timestamp)
            fig.suptitle(f"Simülasyon: Adım {frame} / {len(simulation_data)-1}\nZaman: {timestamp_str}", fontsize=16)
            
            # Her oda için panel güncelle
            for i, room_name in enumerate(rooms):
                ax = axes[i]
                ax.clear()
                
                # Oda durumu
                if room_name in state['rooms']:
                    room_data = state['rooms'][room_name]
                else:
                    continue
                
                # Oda arkaplanı
                ax.set_facecolor("#f8f9fa")
                
                # Sensör değerlerini yazdır
                sensors = room_data.get('sensors', {})
                sensor_text = '\n'.join([
                    f"Sıcaklık: {sensors.get('Sıcaklık', 'N/A')}°C",
                    f"Nem: {sensors.get('Nem', 'N/A')}%",
                    f"CO2: {sensors.get('CO2', 'N/A')} ppm",
                    f"Işık: {sensors.get('Işık', 'N/A')} lux",
                    f"Doluluk: {'Evet' if sensors.get('Doluluk', False) else 'Hayır'}",
                    f"Hareket: {'Var' if sensors.get('Hareket', False) else 'Yok'}"
                ])
                
                # Cihaz durumları
                devices = room_data.get('devices', {})
                device_icons = {
                    'Klima': '❄️' if devices.get('Klima', False) else '⚪',
                    'Lamba': '💡' if devices.get('Lamba', False) else '⚪',
                    'Perde': '🪟' if devices.get('Perde', False) else '⚪',
                    'Havalandırma': '🌀' if devices.get('Havalandırma', False) else '⚪'
                }
                
                device_text = ' '.join([
                    f"{icon} {name}"
                    for name, icon in device_icons.items()
                ])
                
                # Doluluk durumuna göre kişi ikonu
                people_icons = ''
                if 'people' in room_data:
                    for person_idx, person_name in room_data['people'].items():
                        people_icons += f"👤 {person_name}\n"
                
                # Metni odanın içine yerleştir
                ax.text(0.05, 0.95, room_name, transform=ax.transAxes, 
                       fontsize=14, fontweight='bold', va='top')
            
                ax.text(0.05, 0.85, sensor_text, transform=ax.transAxes, 
                       fontsize=10, va='top')
                
                ax.text(0.05, 0.3, device_text, transform=ax.transAxes, 
                       fontsize=12, va='top')
                
                if people_icons:
                    ax.text(0.05, 0.15, people_icons, transform=ax.transAxes, 
                           fontsize=12, va='top')
                
                # Odanın sınırlarını çiz
                ax.spines['top'].set_visible(True)
                ax.spines['right'].set_visible(True)
                ax.spines['bottom'].set_visible(True)
                ax.spines['left'].set_visible(True)
                
                # Eksen etiketlerini kaldır
                ax.set_xticks([])
                ax.set_yticks([])
        
        # Animasyonu oluştur
        ani = animation.FuncAnimation(fig, update, frames=len(simulation_data), 
                                    interval=interval, blit=False)
        
        plt.tight_layout()
        
        # Dosyaya kaydet
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simulation_animation_{timestamp}.mp4"
            filepath = os.path.join(self.output_dir, filename)
            # FFmpeg gerektirir!
            ani.save(filepath, writer='ffmpeg', fps=5, dpi=200)
            print(f"Animasyon kaydedildi: {filepath}")
        
        # Ekranda göster
        if show:
            plt.show()
        
        return ani