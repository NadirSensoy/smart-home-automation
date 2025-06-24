import threading
import time
import argparse
import os
import logging
import pandas as pd
from datetime import datetime
import sys
from src.models.model_manager import SmartHomeModelManager

from src.simulation.home_simulator import SmartHomeSimulator
from src.utils.visualization import SimulationVisualizer

class InteractiveSimulation:
    """
    Kullanıcı etkileşimli akıllı ev simülasyonu.
    Terminal tabanlı komutlarla simülasyon kontrolü sağlar.
    """
    
    def __init__(self, rooms=None, num_residents=2, time_step=5, use_ml=True):
        """
        InteractiveSimulation sınıfını başlatır
        
        Args:
            rooms (list): Simüle edilecek odaların listesi
            num_residents (int): Ev sakinlerinin sayısı
            time_step (int): Simülasyon adımları arasındaki dakika farkı
            use_ml (bool): Makine öğrenmesi modeli kullanılıp kullanılmayacağı
        """
        # Simülasyon parametreleri
        self.rooms = rooms or ["Salon", "Yatak Odası", "Çocuk Odası", "Mutfak", "Banyo"]
        self.num_residents = num_residents
        self.time_step = time_step
        self.use_ml = use_ml
        
        # Simülatör oluştur
        self.simulator = SmartHomeSimulator(
            rooms=self.rooms,
            num_residents=self.num_residents,
            time_step=self.time_step,
            use_ml=self.use_ml,
            simulation_speed=1.0
        )
        
        # Görselleştirici
        self.visualizer = self.simulator.visualizer
        
        # Kullanıcı giriş iş parçacığı
        self.input_thread = None
        self.running = False
        
        # Loglama
        self.logger = logging.getLogger(__name__)
    
    def print_help(self):
        """Kullanılabilir komutları yazdırır"""
        self.logger.info("\n=== AKILLI EV SİMÜLASYONU KOMUTLARI ===")
        self.logger.info("start [adım]     : Simülasyonu başlatır (opsiyonel: adım sayısı)")
        self.logger.info("pause            : Simülasyonu duraklatır")
        self.logger.info("resume           : Simülasyonu devam ettirir")
        self.logger.info("stop             : Simülasyonu durdurur")
        self.logger.info("speed [hız]      : Simülasyon hızını ayarlar (ör: 1.0, 2.0)")
        self.logger.info("status           : Mevcut simülasyon durumunu gösterir")
        self.logger.info("device [oda] [cihaz] [durum] : Cihaz durumunu değiştirir")
        self.logger.info("                   Örnek: device Salon Lamba on")
        self.logger.info("save             : Simülasyon geçmişini kaydeder")
        self.logger.info("report           : Simülasyon raporu oluşturur")
        self.logger.info("visualize        : Güncel durumu görselleştirir (kapanana kadar bekler)")
        self.logger.info("exit             : Programdan çıkar")
        self.logger.info("help             : Bu yardım mesajını gösterir")
    
    def start_input_loop(self):
        """Kullanıcı komutlarını okur ve işler"""
        self.running = True
        
        while self.running:
            try:
                # Kullanıcı komutunu al
                command = input("\n>> ").strip().lower()
                
                # Komut işleme
                if command == "exit":
                    self.running = False
                    if self.simulator.running:
                        self.simulator.stop()
                    else:
                        # Even if simulator isn't running, make sure visualizer is properly closed
                        if hasattr(self.visualizer, 'close_matplotlib'):
                            self.visualizer.close_matplotlib()
                        elif hasattr(self.visualizer, 'close'):
                            self.visualizer.close()
                    self.logger.info("Program sonlandırılıyor...")
                
                elif command == "help":
                    self.print_help()
                
                elif command.startswith("start"):
                    # Adım sayısını al (varsa)
                    parts = command.split()
                    steps = int(parts[1]) if len(parts) > 1 else 100
                    
                    # Simülasyon zaten çalışıyorsa durdur
                    if self.simulator.running:
                        self.simulator.stop()
                        time.sleep(0.5)  # İş parçacığının sonlanmasını bekle
                    
                    self.logger.info(f"Simülasyon başlatılıyor ({steps} adım)...")
                    self.simulator.run_in_thread(steps=steps, display=True, delay=0.5)
                
                elif command == "pause":
                    if self.simulator.running:
                        self.simulator.pause()
                        self.logger.info("Simülasyon duraklatıldı")
                    else:
                        self.logger.info("Simülasyon çalışmıyor")
                
                elif command == "resume":
                    if self.simulator.running and self.simulator.paused:
                        self.simulator.resume()
                        self.logger.info("Simülasyon devam ediyor")
                    else:
                        self.logger.info("Simülasyon duraklatılmamış veya çalışmıyor")
                
                elif command == "stop":
                    if self.simulator.running:
                        self.simulator.stop()
                        self.logger.info("Simülasyon durduruldu")
                    else:
                        self.logger.info("Simülasyon çalışmıyor")
                
                elif command.startswith("speed"):
                    parts = command.split()
                    if len(parts) > 1:
                        try:
                            speed = float(parts[1])
                            self.simulator.simulation_speed = speed
                            self.logger.info(f"Simülasyon hızı {speed}x olarak ayarlandı")
                        except ValueError:
                            self.logger.warning("Geçersiz hız değeri")
                    else:
                        self.logger.info(f"Mevcut simülasyon hızı: {self.simulator.simulation_speed}x")
                
                elif command == "status":
                    if self.simulator.running:
                        status = "Çalışıyor"
                        if self.simulator.paused:
                            status = "Duraklatıldı"
                        
                        self.logger.info(f"Durum: {status}")
                        self.logger.info(f"Adım: {self.simulator.step_count}")
                        self.logger.info(f"Simülasyon zamanı: {self.simulator.simulation_time.strftime('%Y-%m-%d %H:%M')}")
                        self.logger.info(f"Hız: {self.simulator.simulation_speed}x")
                        self.logger.info(f"ML modeli: {'Aktif' if self.simulator.use_ml else 'Devre dışı'}")
                    else:
                        self.logger.info("Simülasyon çalışmıyor")
                
                elif command.startswith("device"):
                    # Cihaz kontrolü: device [oda] [cihaz] [durum]
                    parts = command.split()
                    if len(parts) >= 4:
                        room = parts[1].capitalize()
                        device = parts[2].capitalize()
                        state = parts[3].lower() in ["on", "1", "true", "açık", "aç"]
                        
                        device_key = f"{room}_{device}"
                        
                        # Cihaz durumunu güncelle
                        if room in self.rooms:
                            # Cihaz simülatöre bildir
                            self.simulator.data_generator.sensor_simulator.devices[room][device] = state
                            self.logger.info(f"{room} - {device} {'açıldı' if state else 'kapatıldı'}")
                        else:
                            self.logger.warning(f"Geçersiz oda adı: {room}")
                    else:
                        self.logger.warning("Hatalı komut. Kullanım: device [oda] [cihaz] [durum]")
                
                elif command == "save":
                    if self.simulator.history:
                        filepath = self.simulator.save_history()
                        self.logger.info(f"Simülasyon geçmişi kaydedildi: {filepath}")
                    else:
                        self.logger.info("Kaydedilecek simülasyon verisi yok")
                
                elif command == "report":
                    if self.simulator.history:
                        # DataFrame'e dönüştür
                        history_df = pd.DataFrame(self.simulator.history)
                        
                        # Rapor oluştur
                        self.logger.info("Rapor oluşturuluyor...")
                        
                        # Generate a static report instead of interactive plots
                        try:
                            # Create output directory if it doesn't exist
                            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                                  "reports", "simulation")
                            if not os.path.exists(output_dir):
                                os.makedirs(output_dir)
                                
                            # Generate timestamp
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            
                            # Save data summary
                            data_path = os.path.join(output_dir, f"simulation_data_{timestamp}.csv")
                            history_df.to_csv(data_path, index=False)
                            self.logger.info(f"Veri özeti kaydedildi: {data_path}")
                            
                            # Generate plots in separate files
                            plots_dir = os.path.join(output_dir, f"plots_{timestamp}")
                            if not os.path.exists(plots_dir):
                                os.makedirs(plots_dir)
                                
                            # Save temperature plot
                            try:
                                temp_fig = self.visualizer.plot_sensors_over_time(
                                    history_df, save=False, show=False)
                                temp_path = os.path.join(plots_dir, "temperature.png")
                                temp_fig.savefig(temp_path, dpi=300)
                                self.logger.info(f"Sıcaklık grafiği kaydedildi: {temp_path}")
                            except Exception as e:
                                self.logger.warning(f"Sıcaklık grafiği kaydedilemedi: {e}")
                                
                            # Save occupancy plot
                            try:
                                occ_fig = self.visualizer.plot_room_occupancy(
                                    history_df, save=False, show=False)
                                occ_path = os.path.join(plots_dir, "occupancy.png")
                                occ_fig.savefig(occ_path, dpi=300)
                                self.logger.info(f"Doluluk grafiği kaydedildi: {occ_path}")
                            except Exception as e:
                                self.logger.warning(f"Doluluk grafiği kaydedilemedi: {e}")
                                
                            # Save device usage plot
                            try:
                                dev_fig = self.visualizer.plot_device_usage(
                                    history_df, save=False, show=False)
                                dev_path = os.path.join(plots_dir, "device_usage.png") 
                                dev_fig.savefig(dev_path, dpi=300)
                                self.logger.info(f"Cihaz kullanım grafiği kaydedildi: {dev_path}")
                            except Exception as e:
                                self.logger.warning(f"Cihaz kullanım grafiği kaydedilemedi: {e}")
                                
                            # Create a simple HTML report that includes all plots
                            html_report_path = os.path.join(output_dir, f"simulation_report_{timestamp}.html")
                            with open(html_report_path, 'w', encoding='utf-8') as html_file:
                                html_file.write(f"""
                                <!DOCTYPE html>
                                <html>
                                <head>
                                    <title>Simulation Report {timestamp}</title>
                                    <style>
                                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                                        h1, h2 {{ color: #333; }}
                                        .plot {{ margin: 20px 0; }}
                                        img {{ max-width: 100%; border: 1px solid #ddd; }}
                                    </style>
                                </head>
                                <body>
                                    <h1>Akıllı Ev Simülasyon Raporu</h1>
                                    <p>Oluşturma zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                                    
                                    <h2>Sıcaklık Değişimi</h2>
                                    <div class="plot">
                                        <img src="plots_{timestamp}/temperature.png" alt="Sıcaklık Grafiği">
                                    </div>
                                    
                                    <h2>Oda Dolulukları</h2>
                                    <div class="plot">
                                        <img src="plots_{timestamp}/occupancy.png" alt="Doluluk Grafiği">
                                    </div>
                                    
                                    <h2>Cihaz Kullanımı</h2>
                                    <div class="plot">
                                        <img src="plots_{timestamp}/device_usage.png" alt="Cihaz Kullanım Grafiği">
                                    </div>
                                </body>
                                </html>
                                """)
                                
                            self.logger.info(f"HTML raporu oluşturuldu: {html_report_path}")
                            
                            # Try to open the HTML report
                            import platform
                            if platform.system() == 'Windows':
                                os.startfile(html_report_path)
                            else:
                                self.logger.info(f"HTML raporu görüntülemek için bu dosyayı açın: {html_report_path}")
                                
                        except Exception as e:
                            self.logger.error(f"Rapor oluşturulamadı: {e}")
                            import traceback
                            traceback.print_exc()
                    else:
                        self.logger.info("Rapor oluşturmak için veri yok")
                
                elif command == "visualize":
                    # Create a visualization of the current state that stays open
                    self.logger.info("Güncel durum görselleştiriliyor...")
                    
                    # Get the current state
                    if self.simulator.history:
                        current_state = self.simulator.history[-1]
                        
                        try:
                            # Convert state to house format
                            house_state = self._convert_state_to_house_format(current_state)
                            
                            # Create a file-based visualization that works in any thread
                            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                                   "output", "visualizations")
                            if not os.path.exists(output_dir):
                                os.makedirs(output_dir)
                            
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filepath = os.path.join(output_dir, f"house_state_{timestamp}.png")
                            
                            # Use the function that works in any thread
                            fig = self.visualizer.create_house_visualization(
                                house_state, save=True, show=False)
                            

                            if fig:
                                fig.savefig(filepath, dpi=300, bbox_inches='tight')
                                self.logger.info(f"Görselleştirme {filepath} konumuna kaydedildi.")
                                
                                # On Windows, try to open the file with the default image viewer
                                import platform
                                if platform.system() == 'Windows':
                                    os.startfile(filepath)
                                else:
                                    self.logger.info("Dosyayı manuel olarak açın.")
                        except Exception as e:
                            self.logger.error(f"Görselleştirme sırasında hata: {e}")
                    else:
                        self.logger.info("Henüz simülasyon verisi yok")
    
                else:
                    self.logger.warning(f"Bilinmeyen komut: {command}")
                    self.logger.info("Yardım için 'help' yazın")
                
            except KeyboardInterrupt:
                self.logger.info("\nProgram sonlandırılıyor...")
                self.running = False
                if self.simulator.running:
                    self.simulator.stop()
            
            except Exception as e:
                self.logger.error(f"Hata: {e}")
    
    def _convert_state_to_house_format(self, state):
        """Simülasyon durumunu ev formatına dönüştürür"""
        house_state = {"rooms": {}}
        
        # Initialize all rooms
        for room in self.rooms:
            house_state["rooms"][room] = {
                "sensors": {},
                "devices": {}
            }
        
        # Fill with data from state
        for key, value in state.items():
            if key in ['timestamp', 'step', 'simulation_time', 'step_count']:
                continue
            
            parts = key.split('_')
            if len(parts) < 2:
                continue
            
            room = parts[0]
            feature = '_'.join(parts[1:])
            
            if room in house_state["rooms"]:
                # Determine if it's a sensor or device
                if feature in ['Sıcaklık', 'Nem', 'CO2', 'Işık', 'Doluluk', 'Hareket']:
                    house_state["rooms"][room]["sensors"][feature] = value
                elif feature in ['Klima', 'Lamba', 'Perde', 'Havalandırma']:
                    house_state["rooms"][room]["devices"][feature] = value
        
        return house_state
    
    def start(self):
        """İnteraktif simülasyonu başlatır"""
        # Hoş geldiniz mesajı
        self.logger.info("\n" + "="*60)
        self.logger.info("   AKILLI EV OTOMASYON SİSTEMİ - İNTERAKTİF SİMÜLASYON")
        self.logger.info("="*60)
        self.logger.info(f"Odalar: {', '.join(self.rooms)}")
        self.logger.info(f"Kullanıcı sayısı: {self.num_residents}")
        self.logger.info(f"Makine öğrenmesi: {'Aktif' if self.use_ml else 'Devre dışı'}")
        
        # Yardım mesajı
        self.print_help()
        
        try:
            # Kullanıcı giriş döngüsünü başlat
            self.start_input_loop()
        finally:
            # Ensure resources are cleaned up even if there's an exception
            if hasattr(self, 'visualizer') and self.visualizer:
                if hasattr(self.visualizer, 'close_matplotlib'):
                    self.visualizer.close_matplotlib()
                elif hasattr(self.visualizer, 'close'):
                    self.visualizer.close()

# Ana fonksiyon - CLI argümanlarını işleyerek interaktif simülasyonu başlatır
def run_interactive_simulation(rooms=None, num_residents=3, time_step=5, use_ml=True):
    """
    Interactive simulation without parsing command line arguments
    
    Args:
        rooms (list): Rooms to simulate
        num_residents (int): Number of residents
        time_step (int): Simulation time step
        use_ml (bool): Whether to use ML model
    """
    # Set up logging
    logger = logging.getLogger("InteractiveSimulation")
    
    try:
        # Use provided arguments instead of parsing command line
        if rooms is None:
            rooms = ["Salon", "Yatak Odası", "Çocuk Odası", "Mutfak", "Banyo"]
        
        # Handle rooms if they're provided as a comma-separated string
        if isinstance(rooms, str):
            rooms = [room.strip() for room in rooms.split(',')]
            
        ml_model_path = None
        
        if use_ml:
            # Look for existing model
            model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models")
            if os.path.exists(model_dir):
                model_files = [f for f in os.listdir(model_dir) if f.startswith("model_manager_") and f.endswith(".json")]
                if model_files:
                    # Use the most recent model
                    model_files.sort(reverse=True)
                    ml_model_path = os.path.join(model_dir, model_files[0])
                    logger.info(f"Using existing model: {ml_model_path}")
        
        # İnteraktif simülasyon
        sim = InteractiveSimulation(
            rooms=rooms,
            num_residents=num_residents,
            time_step=time_step,
            use_ml=use_ml
        )
        
        # Initialize the simulator properly with ML model if available
        if use_ml and ml_model_path and os.path.exists(ml_model_path):
            try:
                sim.simulator.ml_model_manager = SmartHomeModelManager.load_manager(ml_model_path)
                logger.info("ML model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load ML model: {e}")
        elif use_ml:
            logger.info("No existing ML model found, will train a new one during simulation")
                
        # Başlat
        sim.start()
        
    except Exception as e:
        logger.error(f"Error in interactive simulation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Only parse command line arguments when running directly
    parser = argparse.ArgumentParser(description='Akıllı Ev Otomasyon Sistemi İnteraktif Simülasyon')
    parser.add_argument('--rooms', type=str, default="Salon,Yatak Odası,Çocuk Odası,Mutfak,Banyo",
                        help='Simüle edilecek odalar (virgülle ayrılmış)')
    parser.add_argument('--residents', type=int, default=3,
                        help='Ev sakinlerinin sayısı')
    parser.add_argument('--time-step', type=int, default=5,
                        help='Simülasyon adımları arasındaki dakika farkı')
    parser.add_argument('--no-ml', action='store_true',
                        help='Makine öğrenmesi modelini devre dışı bırak')
    
    args = parser.parse_args()
    
    # Call the function with parsed arguments
    run_interactive_simulation(
        rooms=args.rooms,
        num_residents=args.residents,
        time_step=args.time_step,
        use_ml=not args.no_ml
    )