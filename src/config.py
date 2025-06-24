# Configuration settings for the Smart Home Automation System

# This dictionary holds parameters for data simulation, model training, and automation rules.
config = {
    "rooms": ["Salon", "Yatak Odası", "Çocuk Odası", "Mutfak", "Banyo"],
    "devices_per_room": ["Klima", "Lamba", "Perde", "Havalandırma"],
    "sensor_types": ["Sıcaklık", "Nem", "CO2", "Işık", "Doluluk", "Hareket"],
    "automation_thresholds": {
        "high_temp_threshold": 26,
        "low_temp_threshold": 18,
        "low_light_threshold": 100,
        "high_co2_threshold": 800,
        "low_co2_threshold": 600,
        "high_humidity_threshold": 70,
        "low_humidity_threshold": 30,
        "empty_room_device_off_delay_min": 15,
        "empty_room_ac_off_delay_min": 30,
        "morning_start": 6,   # Morning period start (6 AM)
        "morning_end": 10,    # Morning period end (10 AM)
        "evening_start": 18,  # Evening period start (6 PM)
        "evening_end": 23     # Evening period end (11 PM)
    },
    "manual_operation_prob": {
        "Klima": 0.2,
        "Lamba": 0.7,
        "Perde": 0.4,
        "Havalandırma": 0.3
    },
    "data_simulation": {
        "num_rooms": 5,  # Number of rooms to simulate
        "num_devices_per_room": 3,  # Number of devices in each room
        "simulation_duration": 24,  # Duration of the simulation in hours
        "sampling_rate": 1,  # Sampling rate in minutes
    },
    "model_training": {
        "test_size": 0.2,  # Proportion of the dataset to include in the test split
        "random_state": 42,  # Random seed for reproducibility
        "n_estimators": 100,  # Number of trees in the random forest model
        "max_depth": None,  # Maximum depth of the tree
    },
    "automation_rules": {
        "temperature_threshold": 22,  # Temperature threshold for HVAC control
        "humidity_threshold": 60,  # Humidity threshold for dehumidifiers
        "light_threshold": 300,  # Light threshold for smart lighting
    },
    "visualization": {
        "plot_size": (10, 6),  # Default size for plots
        "color_palette": "viridis",  # Color palette for visualizations
    }
}