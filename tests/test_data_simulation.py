import unittest
from src.data_simulation.sensor_simulator import generate_sensor_data
from src.data_simulation.weather_simulator import generate_weather_data

class TestDataSimulation(unittest.TestCase):
    def test_generate_sensor_data(self):
        # Test the sensor data generation function
        num_samples = 100
        sensor_data = generate_sensor_data(num_samples)
        
        # Check if the generated data has the correct number of samples
        self.assertEqual(len(sensor_data), num_samples)
        
        # Check if the generated data contains expected keys
        expected_keys = ['temperature', 'humidity', 'light', 'room']
        for key in expected_keys:
            self.assertIn(key, sensor_data[0])

    def test_generate_weather_data(self):
        # Test the weather data generation function
        weather_data = generate_weather_data()
        
        # Check if the generated weather data contains expected keys
        expected_keys = ['temperature', 'humidity', 'condition']
        for key in expected_keys:
            self.assertIn(key, weather_data)

if __name__ == '__main__':
    unittest.main()