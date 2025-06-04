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
import logging
import threading
import matplotlib
import tempfile
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

# Use Agg backend if running in a non-main thread
if threading.current_thread() is not threading.main_thread():
    plt.switch_backend('Agg')

# Set custom fonts for emoji support
try:
    # Try to use a font that supports emoji characters
    font_paths = matplotlib.font_manager.findSystemFonts(fontpaths=None)
    emoji_fonts = [f for f in font_paths if any(name in f.lower() for name in 
                  ['segoe ui emoji', 'symbola', 'noto', 'emoji', 'segoeui'])]
    
    if emoji_fonts:
        # Use the first found emoji-supporting font
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = [os.path.basename(emoji_fonts[0])]
    else:
        # If no emoji font found, use default and replace emoji with text
        plt.rcParams['font.family'] = 'sans-serif'
except Exception as e:
    logging.getLogger("SimulationVisualizer").warning(f"Error setting emoji fonts: {e}")

class SimulationVisualizer:
    """
    Akıllı ev simülasyonunu görselleştirmek için kullanılan sınıf
    """
    
    def __init__(self, figsize=(16, 12), style="whitegrid", palette="viridis", display_mode='inline'):
        """
        Görselleştirici sınıfı başlatır
        
        Args:
            figsize (tuple): Grafik boyutu (genişlik, yükseklik)
            style (str): Seaborn stil teması
            palette (str): Renk paleti
            display_mode (str): Görüntüleme modu ('inline', 'window', veya 'none')
        """
        self.figsize = figsize
        self.style = style
        self.palette = palette
        self.display_mode = display_mode
        self.data_history = []
        self.figure = None
        self.axes = None
        self.logger = logging.getLogger("SimulationVisualizer")
        
        # Stil ayarları
        sns.set_style(style)
        sns.set_palette(palette)
        plt.rcParams['figure.figsize'] = figsize
        
        # Çıktı dizini
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports", "figures")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def initialize_display(self):
        """Görselleştirme için Matplotlib figürünü hazırla"""
        if self.display_mode == 'none':
            return
        
        # Check if we're in the main thread
        if threading.current_thread() is not threading.main_thread():
            self.logger.warning("Starting visualization in non-main thread - using non-interactive mode")
            plt.ioff()  # Turn off interactive mode for non-main threads
            self.display_mode = 'save-only'  # Switch to save-only mode
        else:
            plt.ion()  # Etkileşimli mod
        
        # Ana figürü oluştur
        self.figure, self.axes = plt.subplots(2, 2, figsize=(14, 10))
        self.figure.tight_layout(pad=4.0)
        self.figure.suptitle('Akıllı Ev Simülasyonu', fontsize=16)
        
        # Alt grafik başlıklarını belirle
        self.axes[0, 0].set_title('Oda Sıcaklıkları')
        self.axes[0, 1].set_title('Enerji Kullanımı')
        self.axes[1, 0].set_title('Cihaz Aktivitesi')
        self.axes[1, 1].set_title('Sensör Değerleri')
        
        plt.subplots_adjust(hspace=0.3)
    
    def update_display(self, simulation_data):
        """
        Görselleştirmeyi son verilerle güncelle
        
        Args:
            simulation_data (dict): Güncel simülasyon verileri
        """
        # Veriyi geçmişe ekle
        self.data_history.append(simulation_data)
        
        # Görüntüleme devre dışıysa geri dön
        if self.display_mode == 'none':
            return
            
        # Display yoksa başlat
        if self.figure is None or (hasattr(self.figure, 'number') and not plt.fignum_exists(self.figure.number)):
            self.initialize_display()
            
        try:
            # Veriyi çıkar ve görselleştir
            self._extract_and_visualize_data(simulation_data)
            
            # Figürü güncelle
            if self.figure and hasattr(self.figure.canvas, 'draw') and self.display_mode != 'save-only':
                # Only try to draw if we're in the main thread or using a thread-safe backend
                self.figure.canvas.draw()
                self.figure.canvas.flush_events()
            elif self.display_mode == 'save-only':
                # For non-main threads, save the figure instead of displaying it
                self.save_visualization()
                
        except Exception as e:
            self.logger.error(f"Görselleştirme hatası: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def _extract_and_visualize_data(self, data):
        """Simülasyon verisinden ilgili verileri çıkar ve görselleştir"""
        # Check if axes is properly initialized and data is not empty
        if (self.axes is None) or (not hasattr(self.axes, 'shape')) or (len(data) == 0):
            return
        
        try:
            # Tüm grafikleri temizle
            for ax_row in self.axes:
                for ax in ax_row:
                    ax.clear()
            
            # Başlıkları yeniden belirle
            self.axes[0, 0].set_title('Oda Sıcaklıkları')
            self.axes[0, 1].set_title('Enerji Kullanımı')
            self.axes[1, 0].set_title('Cihaz Aktivitesi')
            self.axes[1, 1].set_title('Sensör Değerleri')
            
            # Simülasyon zamanını ayarla
            simulation_time = data.get('simulation_time', datetime.now())
            step_count = data.get('step_count', 0)
            
            # Sıcaklık verilerini görselleştir
            self._visualize_temperatures(self.axes[0, 0], data)
            
            # Enerji kullanımını görselleştir
            self._visualize_energy_usage(self.axes[0, 1], data)
            
            # Cihaz aktivitelerini görselleştir
            self._visualize_device_states(self.axes[1, 0], data)
            
            # Sensör değerlerini görselleştir
            self._visualize_sensor_values(self.axes[1, 1], data)
            
            # Simülasyon zamanı ve adımı ekle
            self.figure.suptitle(f'Akıllı Ev Simülasyonu - Zaman: {simulation_time.strftime("%H:%M:%S")} - Adım: {step_count}', fontsize=16)
            
            # Layout'u düzenle
            self.figure.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        except Exception as e:
            self.logger.error(f"Görselleştirme hatası: {e}")
    
    def _visualize_temperatures(self, ax, data):
        """Oda sıcaklıklarını görselleştir"""
        # Veri hazırla
        rooms = []
        temperatures = []
        
        for key, value in data.items():
            if key.endswith('_Sıcaklık'):
                room = key.split('_')[0]
                rooms.append(room)
                temperatures.append(value)
                
        if not rooms:  # Veri yoksa
            ax.text(0.5, 0.5, 'Sıcaklık verisi yok', ha='center', va='center')
            return
            
        # Çubuk grafiği oluştur
        ax.bar(rooms, temperatures, color='orange')
        ax.set_ylabel('Sıcaklık (°C)')
        ax.set_ylim(15, 30)  # Sıcaklık aralığını ayarla
        
        # Değerleri çubukların üzerine ekle
        for i, temp in enumerate(temperatures):
            ax.text(i, temp + 0.5, f'{temp}°C', ha='center')
            
    def _visualize_energy_usage(self, ax, data):
        """Enerji kullanımını görselleştir"""
        # Geçmiş verileri kullan (en fazla son 50 adım)
        history_length = min(len(self.data_history), 50)
        
        if history_length < 2:  # Yeterli veri yoksa
            ax.text(0.5, 0.5, 'Enerji kullanım verisi yok', ha='center', va='center')
            return
        
        # Veri hazırla
        steps = list(range(history_length))
        energy_values = []
        
        for i in range(history_length):
            history_data = self.data_history[-history_length + i]
            # Aktif cihazları say
            active_devices = sum(1 for k, v in history_data.items() if 
                                k.endswith(('_Klima', '_Lamba', '_Havalandırma')) and v is True)
            energy_values.append(active_devices * 0.5)  # Basit enerji hesabı
            
        # Çizgi grafiği oluştur
        ax.plot(steps, energy_values, marker='o', color='red')
        ax.set_ylabel('Enerji Kullanımı (kW)')
        ax.set_xlabel('Simülasyon Adımları')
        ax.grid(True, linestyle='--', alpha=0.7)
        
    def _visualize_device_states(self, ax, data):
        """Cihaz durumlarını görselleştir"""
        # Veri hazırla
        device_types = ['Klima', 'Lamba', 'Perde', 'Havalandırma']
        active_counts = {device: 0 for device in device_types}
        total_counts = {device: 0 for device in device_types}
        
        for key, value in data.items():
            for device_type in device_types:
                if key.endswith(f'_{device_type}'):
                    total_counts[device_type] += 1
                    # Use safe boolean check to avoid ambiguity errors
                    if self._safe_bool_check(value):
                        active_counts[device_type] += 1
        
        if sum(total_counts.values()) == 0:  # Veri yoksa
            ax.text(0.5, 0.5, 'Cihaz durumu verisi yok', ha='center', va='center')
            return
        
        # Yüzdeleri hesapla
        percentages = []
        labels = []
        
        for device_type in device_types:
            if total_counts[device_type] > 0:
                percentage = (active_counts[device_type] / total_counts[device_type]) * 100
                percentages.append(percentage)
                labels.append(f'{device_type} ({active_counts[device_type]}/{total_counts[device_type]})')
        
        # Yatay çubuk grafik oluştur
        ax.barh(labels, percentages, color=['blue', 'yellow', 'green', 'purple'])
        ax.set_xlim(0, 100)
        ax.set_xlabel('Aktif Cihaz Yüzdesi')
        
        # Değerleri çubukların üzerine ekle
        for i, percentage in enumerate(percentages):
            ax.text(percentage + 2, i, f'%{percentage:.1f}', va='center')
            
    def _visualize_sensor_values(self, ax, data):
        """Sensör değerlerini görselleştir"""
        try:
            # Veri hazırla
            sensor_types = ['Sıcaklık', 'Nem', 'Işık', 'Hareket']
            sensor_data = {}
            
            for sensor_type in sensor_types:
                values = []
                rooms = []
                
                for key, value in data.items():
                    if key.endswith(f'_{sensor_type}'):
                        try:
                            # Safely convert to numeric if needed - handle arrays appropriately
                            if isinstance(value, (list, np.ndarray, pd.Series)):
                                numeric_value = float(np.mean(value))  # Take mean for arrays
                            elif value is None:
                                numeric_value = 0
                            elif pd.isna(value):
                                numeric_value = 0
                            else:
                                numeric_value = float(value)
                            
                            rooms.append(key.split('_')[0])
                            values.append(numeric_value)
                        except (TypeError, ValueError):
                            # Skip non-numeric values
                            pass
                        
                if values:  # Sensör verisi varsa ekle
                    sensor_data[sensor_type] = {'rooms': rooms, 'values': values}
            
            if not sensor_data:  # Hiç sensör verisi yoksa
                ax.text(0.5, 0.5, 'Sensör verisi yok', ha='center', va='center')
                return
                
            # Sensör türü seç (ilk bulunan)
            selected_sensor = list(sensor_data.keys())[0]
            selected_data = sensor_data[selected_sensor]
            
            # Pasta grafik oluştur
            ax.pie(selected_data['values'], labels=selected_data['rooms'], autopct='%1.1f%%',
                   shadow=True, startangle=90)
            ax.axis('equal')  # Daire şeklinde olması için
            ax.set_title(f'Oda {selected_sensor} Değerleri')
        
        except Exception as e:
            self.logger.error(f"Sensör visualizasyonu hatası: {e}")
            ax.text(0.5, 0.5, 'Sensör görselleştirme hatası', ha='center', va='center')
    
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
            plt.show(block=True)  # Set block=True to wait until figure is closed
        
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
            plt.show(block=True)  # Set block=True to wait until figure is closed
        
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
            plt.show(block=True)  # Set block=True to wait until figure is closed
        
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
            plt.show(block=True)  # Set block=True to wait until figure is closed
        
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
            plt.show(block=True)  # Set block=True to wait until figure is closed
        
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
        
        # Thread-safe way to create figure
        is_main_thread = threading.current_thread() is threading.main_thread()
        
        try:
            # Grafik oluştur
            if is_main_thread:
                fig, axes = plt.subplots(nrows, ncols, figsize=self.figsize)
            else:
                # Use a non-interactive backend for non-main thread
                fig = Figure(figsize=self.figsize)
                canvas = FigureCanvasAgg(fig)
                if nrows == 1 and ncols == 1:
                    axes = np.array([fig.add_subplot(1, 1, 1)])
                else:
                    axes = np.array([fig.add_subplot(nrows, ncols, i+1) for i in range(nrows*ncols)])
                    axes = axes.reshape(nrows, ncols) if nrows > 1 and ncols > 1 else axes
            
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
                
                # Cihaz durumları (use text instead of emoji for better compatibility)
                devices = room_data.get('devices', {})
                device_icons = {
                    'Klima': '[AC]' if devices.get('Klima', False) else '[ ]',
                    'Lamba': '[Lamp]' if devices.get('Lamba', False) else '[ ]',
                    'Perde': '[Curtain]' if devices.get('Perde', False) else '[ ]',
                    'Havalandırma': '[Fan]' if devices.get('Havalandırma', False) else '[ ]'
                }
                
                device_text = ' '.join([
                    f"{icon} {name}"
                    for name, icon in device_icons.items()
                ])
                
                # Doluluk durumuna göre kişi ikonu
                people_icons = ''
                if 'people' in room_data:
                    for person_idx, person_name in room_data['people'].items():
                        people_icons += f"[Person] {person_name}\n"
                
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
                if is_main_thread:
                    fig.delaxes(axes[i])
                else:
                    axes[i].set_visible(False)
            
            if is_main_thread:
                plt.tight_layout()
            else:
                fig.tight_layout()
            
            # Dosyaya kaydet
            if save:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"house_visualization_{timestamp}.png"
                filepath = os.path.join(self.output_dir, filename)
                
                if is_main_thread:
                    plt.savefig(filepath, dpi=300, bbox_inches='tight')
                else:
                    fig.savefig(filepath, dpi=300, bbox_inches='tight')
                print(f"Grafik kaydedildi: {filepath}")
            
            # Handle different thread scenarios for visualization
            if show:
                if is_main_thread:
                    plt.show(block=True)  # Wait until closed in main thread
                else:
                    # Create a temporary file to show in browser/image viewer in non-main thread
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        temp_filename = tmp.name
                        fig.savefig(temp_filename, dpi=300, bbox_inches='tight')
                        print(f"Görselleştirme {temp_filename} konumuna kaydedildi. "
                              f"Bu dosyayı inceledikten sonra enter tuşuna basarak devam edin.")
                        input("Devam etmek için enter tuşuna basın...")
            
            return fig
        
        except Exception as e:
            self.logger.error(f"House visualization error: {e}", exc_info=True)
            if save:
                # Try to save error information
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                error_path = os.path.join(self.output_dir, f"visualization_error_{timestamp}.txt")
                with open(error_path, 'w') as f:
                    f.write(f"Error: {str(e)}")
                print(f"Hata bilgisi {error_path} konumuna kaydedildi.")
            return None

    def save_visualization(self, output_path=None):
        """Mevcut görselleştirmeyi dosyaya kaydet"""
        if not self.figure:
            self.logger.warning("Kaydedilecek görselleştirme yok")
            return
        
        if output_path is None:
            # Varsayılan yol
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                               "output", "visualizations")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            output_path = os.path.join(output_dir, 
                         f"simulation_vis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    
        try:
            self.figure.savefig(output_path, dpi=150, bbox_inches='tight')
            self.logger.info(f"Görselleştirme kaydedildi: {output_path}")
        except Exception as e:
            self.logger.error(f"Görselleştirme kaydedilemedi: {e}")

    def close(self):
        """Görselleştirmeyi kapat"""
        if self.figure:
            plt.close(self.figure)
            self.figure = None
            self.axes = None    

    def _safe_bool_check(self, value):
        """Safely convert potentially problematic values to boolean"""
        if value is None:
            return False
    
        if isinstance(value, (list, np.ndarray, pd.Series)):
            # Use any() for arrays or lists
            try:
                # For numpy arrays, use np.any
                if isinstance(value, np.ndarray):
                    return bool(np.any(value))
                # For pandas Series, use any()  
                elif isinstance(value, pd.Series):
                    return bool(value.any())
                # For lists, convert to numpy array then check
                else:
                    return bool(np.any(np.array(value, dtype=bool)))
            except:
                # If conversion fails, default to False
                return False
            
        if isinstance(value, str):
            # Handle string representations of boolean values
            return value.lower() in ('true', 't', 'yes', 'y', '1')
        
        if pd.isna(value):
            return False
        
        # Try standard boolean conversion
        try:
            return bool(value)
        except:
            return False
    
    # Add close_matplotlib method to properly clean up resources
    def close_matplotlib(self):
        """Properly close all matplotlib resources to avoid thread errors"""
        try:
            # Safe cleanup without relying on main thread
            if hasattr(plt, '_pylab_helpers'):
                # Only close our figures, not any others that might be open
                if hasattr(self, 'figure') and self.figure is not None:
                    try:
                        plt.close(self.figure)
                    except:
                        pass
                    self.figure = None
                    self.axes = None
                    
            # For safety, close all figures in less aggressive way
            for i in range(10):  # Close up to 10 figures (reasonable upper limit)
                try:
                    plt.close(i)
                except:
                    pass
                    
        except Exception as e:
            self.logger.error(f"Error closing matplotlib resources: {e}")