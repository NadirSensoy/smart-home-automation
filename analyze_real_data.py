#!/usr/bin/env python3
"""
Gerçek simülasyon verilerini analiz eden script
"""
import pandas as pd
import numpy as np
import os

def analyze_simulation_data():
    """Gerçek simülasyon verilerini analiz et"""
    
    # Veri dosyasını oku
    df = pd.read_csv('data/simulation/simulation_history_20250624_145501.csv')
    
    print('🏠 GERÇEK SİMÜLASYON VERİ ANALİZİ')
    print('=' * 50)
    print(f'📊 Toplam kayıt sayısı: {len(df)}')
    print(f'⏱️ Simülasyon süresi: {df["step"].max()} adım')
    print(f'📁 Toplam sütun sayısı: {len(df.columns)}')
    print(f'🏠 Ev türü: 5 oda (Salon, Yatak Odası, Çocuk Odası, Mutfak, Banyo)')
    
    # Zaman aralığı
    print(f'\n📅 Zaman Aralığı:')
    print(f'   Başlangıç: {df["timestamp"].iloc[0]}')
    print(f'   Bitiş: {df["timestamp"].iloc[-1]}')
    
    # Sensör verilerinin istatistikleri
    temp_cols = [col for col in df.columns if 'Sıcaklık' in col]
    humidity_cols = [col for col in df.columns if 'Nem' in col]
    co2_cols = [col for col in df.columns if 'CO2' in col]
    
    print(f'\n🌡️ Sıcaklık Verileri ({len(temp_cols)} sensör):')
    for col in temp_cols:
        print(f'   {col}: {df[col].mean():.1f}°C (min: {df[col].min():.1f}, max: {df[col].max():.1f})')
    
    print(f'\n💧 Nem Verileri ({len(humidity_cols)} sensör):')
    for col in humidity_cols:
        print(f'   {col}: {df[col].mean():.1f}% (min: {df[col].min():.1f}, max: {df[col].max():.1f})')
    
    print(f'\n🌬️ CO2 Verileri ({len(co2_cols)} sensör):')
    for col in co2_cols:
        print(f'   {col}: {df[col].mean():.0f} ppm (min: {df[col].min():.0f}, max: {df[col].max():.0f})')
    
    # Hareket sensörleri
    motion_cols = [col for col in df.columns if 'Hareket' in col]
    print(f'\n🚶 Hareket Sensörleri ({len(motion_cols)} sensör):')
    for col in motion_cols:
        active_rate = df[col].mean() * 100
        print(f'   {col}: {active_rate:.1f}% aktif')
    
    # Cihaz kullanım oranları
    device_cols = [col for col in df.columns if col.endswith(('_Klima', '_Lamba', '_Perde', '_Havalandırma'))]
    print(f'\n⚡ Cihaz Kullanım Oranları ({len(device_cols)} cihaz):')
    total_usage = 0
    for col in device_cols:
        if col in df.columns:
            usage_rate = df[col].mean() * 100
            total_usage += usage_rate
            print(f'   {col}: {usage_rate:.1f}%')
    
    avg_usage = total_usage / len(device_cols) if device_cols else 0
    print(f'\n📊 Ortalama Cihaz Kullanımı: {avg_usage:.1f}%')
    
    # Enerji tüketimi analizi
    energy_cols = [col for col in df.columns if 'Enerji' in col and 'Toplam' not in col]
    if energy_cols:
        print(f'\n⚡ Enerji Tüketimi ({len(energy_cols)} cihaz):')
        total_energy = 0
        for col in energy_cols:
            daily_energy = df[col].sum()
            total_energy += daily_energy
            print(f'   {col}: {daily_energy:.2f} kWh/gün')
        
        print(f'\n🏠 Toplam Günlük Enerji Tüketimi: {total_energy:.2f} kWh')
        print(f'💰 Tahmini Günlük Maliyet: {total_energy * 3.5:.2f} TL')
        print(f'💰 Tahmini Aylık Maliyet: {total_energy * 3.5 * 30:.2f} TL')
    
    # Konfor skorları
    comfort_cols = [col for col in df.columns if 'Konfor' in col]
    if comfort_cols:
        print(f'\n😊 Konfor Skorları ({len(comfort_cols)} oda):')
        total_comfort = 0
        for col in comfort_cols:
            avg_comfort = df[col].mean()
            total_comfort += avg_comfort
            print(f'   {col}: {avg_comfort:.2f}/10')
        
        overall_comfort = total_comfort / len(comfort_cols) if comfort_cols else 0
        print(f'\n🏠 Genel Konfor Skoru: {overall_comfort:.2f}/10')
    
    return {
        'total_records': len(df),
        'simulation_steps': df["step"].max(),
        'columns_count': len(df.columns),
        'sensors': {
            'temperature': len(temp_cols),
            'humidity': len(humidity_cols),
            'co2': len(co2_cols),
            'motion': len(motion_cols)
        },
        'devices': len(device_cols),
        'avg_device_usage': avg_usage,
        'total_energy': total_energy if 'total_energy' in locals() else 0,
        'avg_comfort': overall_comfort if 'overall_comfort' in locals() else 0
    }

def analyze_trained_models():
    """Eğitilmiş modelleri analiz et"""
    
    models_dir = 'models/trained'
    if not os.path.exists(models_dir):
        print("❌ Eğitilmiş model klasörü bulunamadı!")
        return
    
    model_files = [f for f in os.listdir(models_dir) if f.endswith('.joblib')]
    
    print(f'\n🤖 EĞİTİLMİŞ MODELLER ANALİZİ')
    print('=' * 50)
    print(f'📊 Toplam model sayısı: {len(model_files)}')
    
    # Model türlerini grupla
    devices = {}
    for model_file in model_files:
        parts = model_file.split('_')
        if len(parts) >= 3:
            room = parts[0]
            device = parts[1]
            if room not in devices:
                devices[room] = []
            devices[room].append(device)
    
    print(f'\n🏠 Oda Bazında Model Dağılımı:')
    for room, device_list in devices.items():
        print(f'   {room}: {len(device_list)} cihaz ({", ".join(device_list)})')
    
    return {
        'total_models': len(model_files),
        'rooms': len(devices),
        'devices_per_room': {room: len(device_list) for room, device_list in devices.items()}
    }

if __name__ == "__main__":
    # Simülasyon verilerini analiz et
    sim_stats = analyze_simulation_data()
    
    # Modelleri analiz et
    model_stats = analyze_trained_models()
    
    print(f'\n📋 ÖZET İSTATİSTİKLER')
    print('=' * 50)
    print(f'📊 Veri Kayıtları: {sim_stats["total_records"]}')
    print(f'⏱️ Simülasyon Süresi: {sim_stats["simulation_steps"]} adım')
    print(f'🌡️ Toplam Sensör: {sum(sim_stats["sensors"].values())}')
    print(f'⚡ Toplam Cihaz: {sim_stats["devices"]}')
    print(f'🤖 Eğitilmiş Model: {model_stats["total_models"]}')
    print(f'💡 Ortalama Cihaz Kullanımı: {sim_stats["avg_device_usage"]:.1f}%')
    if sim_stats["total_energy"] > 0:
        print(f'⚡ Günlük Enerji Tüketimi: {sim_stats["total_energy"]:.2f} kWh')
    if sim_stats["avg_comfort"] > 0:
        print(f'😊 Ortalama Konfor: {sim_stats["avg_comfort"]:.2f}/10')
