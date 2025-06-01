# Configuration settings for the Smart Home Automation System

# This dictionary holds parameters for data simulation, model training, and automation rules.
config = {
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