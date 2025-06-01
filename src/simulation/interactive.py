import threading
import time
import argparse
import os
import logging
import pandas as pd
from datetime import datetime

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
        self.logger = logging.getLogger("InteractiveSimulation")
    
    def print_help(self):
        """Kullanılabilir komutları yazdırır"""
        print("\n=== AKILLI EV SİMÜLASYONU KOMUTLARI ===")
        print("start [adım]     : Simülasyonu başlatır (opsiyonel: adım sayısı)")
        print("pause            : Simülasyonu duraklatır")
        print("resume           : Simülasyonu devam ettirir")
        print("stop             : Simülasyonu durdurur")
        print("speed [hız]      : Simülasyon hızını ayarlar (ör: 1.0, 2.0)")
        print("status           : Mevcut simülasyon durumunu gösterir")
        print("device [oda] [cihaz] [durum] : Cihaz durumunu değiştirir")
        print("                   Örnek: device Salon Lamba on")
        print("save             : Simülasyon geçmişini kaydeder")
        print("report           : Simülasyon raporu oluşturur")
        print("exit             : Programdan çıkar")
        print("help             : Bu yardım mesajını gösterir")
    
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
                    print("Program sonlandırılıyor...")
                
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
                    
                    print(f"Simülasyon başlatılıyor ({steps} adım)...")
                    self.simulator.run_in_thread(steps=steps, display=True, delay=0.5)
                
                elif command == "pause":
                    if self.simulator.running:
                        self.simulator.pause()
                        print("Simülasyon duraklatıldı")
                    else:
                        print("Simülasyon çalışmıyor")
                
                elif command == "resume":
                    if self.simulator.running and self.simulator.paused:
                        self.simulator.resume()
                        print("Simülasyon devam ediyor")
                    else:
                        print("Simülasyon duraklatılmamış veya çalışmıyor")
                
                elif command == "stop":
                    if self.simulator.running:
                        self.simulator.stop()
                        print("Simülasyon durduruldu")
                    else:
                        print("Simülasyon çalışmıyor")
                
                elif command.startswith("speed"):
                    parts = command.split()
                    if len(parts) > 1:
                        try:
                            speed = float(parts[1])
                            self.simulator.simulation_speed = speed
                            print(f"Simülasyon hızı {speed}x olarak ayarlandı")
                        except ValueError:
                            print("Geçersiz hız değeri")
                    else:
                        print(f"Mevcut simülasyon hızı: {self.simulator.simulation_speed}x")
                
                elif command == "status":
                    if self.simulator.running:
                        status = "Çalışıyor"
                        if self.simulator.paused:
                            status = "Duraklatıldı"
                        
                        print(f"Durum: {status}")
                        print(f"Adım: {self.simulator.step_count}")
                        print(f"Simülasyon zamanı: {self.simulator.simulation_time.strftime('%Y-%m-%d %H:%M')}")
                        print(f"Hız: {self.simulator.simulation_speed}x")
                        print(f"ML modeli: {'Aktif' if self.simulator.use_ml else 'Devre dışı'}")
                    else:
                        print("Simülasyon çalışmıyor")
                
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
                            print(f"{room} - {device} {'açıldı' if state else 'kapatıldı'}")
                        else:
                            print(f"Geçersiz oda adı: {room}")
                    else:
                        print("Hatalı komut. Kullanım: device [oda] [cihaz] [durum]")
                
                elif command == "save":
                    if self.simulator.history:
                        filepath = self.simulator.save_history()
                        print(f"Simülasyon geçmişi kaydedildi: {filepath}")
                    else:
                        print("Kaydedilecek simülasyon verisi yok")
                
                elif command == "report":
                    if self.simulator.history:
                        # DataFrame'e dönüştür
                        history_df = pd.DataFrame(self.simulator.history)
                        
                        # Rapor oluştur
                        print("Rapor oluşturuluyor...")
                        
                        # Görsel rapor
                        figures_dir = self.visualizer.plot_summary(history_df)
                        
                        # Etkileşimli dashboard
                        try:
                            dashboard_path = self.visualizer.create_interactive_dashboard(history_df)
                            if dashboard_path:
                                print(f"Etkileşimli dashboard oluşturuldu: {dashboard_path}")
                        except Exception as e:
                            print(f"Dashboard oluşturulurken hata: {e}")
                        
                        print(f"Grafikler şu dizine kaydedildi: {figures_dir}")
                    else:
                        print("Rapor oluşturmak için veri yok")
                
                else:
                    print(f"Bilinmeyen komut: {command}")
                    print("Yardım için 'help' yazın")
                
            except KeyboardInterrupt:
                print("\nProgram sonlandırılıyor...")
                self.running = False
                if self.simulator.running:
                    self.simulator.stop()
            
            except Exception as e:
                print(f"Hata: {e}")
    
    def start(self):
        """İnteraktif simülasyonu başlatır"""
        # Hoş geldiniz mesajı
        print("\n" + "="*60)
        print("   AKILLI EV OTOMASYON SİSTEMİ - İNTERAKTİF SİMÜLASYON")
        print("="*60)
        print(f"Odalar: {', '.join(self.rooms)}")
        print(f"Kullanıcı sayısı: {self.num_residents}")
        print(f"Makine öğrenmesi: {'Aktif' if self.use_ml else 'Devre dışı'}")
        
        # Yardım mesajı
        self.print_help()
        
        # Kullanıcı giriş döngüsünü başlat
        self.start_input_loop()

# Ana fonksiyon - CLI argümanlarını işleyerek interaktif simülasyonu başlatır
def run_interactive_simulation():
    """
    Komut satırı argümanlarını işleyerek interaktif simülasyonu başlatır
    """
    # Argümanları ayrıştır
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
    
    # Odaları ayır
    rooms = [room.strip() for room in args.rooms.split(',')]
    
    # İnteraktif simülasyon
    sim = InteractiveSimulation(
        rooms=rooms,
        num_residents=args.residents,
        time_step=args.time_step,
        use_ml=not args.no_ml
    )
    
    # Başlat
    sim.start()

if __name__ == "__main__":
    run_interactive_simulation()