"""
Pytest yapılandırma ve ortak fixture'lar için dosya
"""
import os
import sys
import pytest
import pandas as pd
from datetime import datetime, timedelta

# Ana proje dizinini Python yoluna ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def sample_data():
    """
    Test için örnek sensör verisi oluşturur
    """
    data = {
        'timestamp': [datetime.now() - timedelta(minutes=i*5) for i in range(10)],
        'Salon_Sıcaklık': [22.5 + i*0.2 for i in range(10)],
        'Salon_Nem': [45.0 + i*0.5 for i in range(10)],
        'Salon_CO2': [650 + i*5 for i in range(10)],
        'Salon_Işık': [300 + i*10 for i in range(10)],
        'Salon_Hareket': [True] * 5 + [False] * 5,
        'Salon_Doluluk': [True] * 5 + [False] * 5,
        'Salon_Klima': [False] * 4 + [True] * 6,
        'Salon_Lamba': [True] * 7 + [False] * 3
    }
    return pd.DataFrame(data)

@pytest.fixture
def test_data_path(tmp_path, sample_data):
    """
    Geçici bir dosya yolunda örnek veri CSV dosyası oluşturur
    """
    file_path = tmp_path / "test_data.csv"
    sample_data.to_csv(file_path, index=False)
    return str(file_path)

@pytest.fixture
def config():
    """
    Test için yapılandırma sözlüğü
    """
    return {
        "rooms": ["Salon", "Yatak Odası", "Mutfak", "Banyo"],
        "sensors": ["Sıcaklık", "Nem", "CO2", "Işık", "Hareket", "Doluluk"],
        "devices": ["Klima", "Lamba", "Perde", "Havalandırma"],
        "residents": 2,
        "simulation_interval": 5  # dakika
    }