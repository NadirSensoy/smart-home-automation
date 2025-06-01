# Weather Simulator for Smart Home Automation

import random
import pandas as pd
from datetime import datetime, timedelta

class WeatherSimulator:
    def __init__(self, start_date, end_date):
        """
        Initializes the WeatherSimulator with a date range.

        Parameters:
        start_date (str): The start date for the simulation in 'YYYY-MM-DD' format.
        end_date (str): The end date for the simulation in 'YYYY-MM-DD' format.
        """
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        self.weather_data = []

    def generate_weather_data(self):
        """
        Generates simulated weather data for each day in the specified date range.
        The data includes temperature, humidity, and weather conditions.
        """
        current_date = self.start_date
        while current_date <= self.end_date:
            temperature = self.simulate_temperature()
            humidity = self.simulate_humidity()
            condition = self.simulate_weather_condition()
            self.weather_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'temperature': temperature,
                'humidity': humidity,
                'condition': condition
            })
            current_date += timedelta(days=1)

    def simulate_temperature(self):
        """
        Simulates a temperature value between 15 and 35 degrees Celsius.

        Returns:
        float: Simulated temperature.
        """
        return round(random.uniform(15.0, 35.0), 2)

    def simulate_humidity(self):
        """
        Simulates a humidity value between 30 and 90 percent.

        Returns:
        float: Simulated humidity.
        """
        return round(random.uniform(30.0, 90.0), 2)

    def simulate_weather_condition(self):
        """
        Randomly selects a weather condition from a predefined list.

        Returns:
        str: Simulated weather condition.
        """
        conditions = ['Sunny', 'Cloudy', 'Rainy', 'Stormy', 'Snowy']
        return random.choice(conditions)

    def save_to_csv(self, filename):
        """
        Saves the generated weather data to a CSV file.

        Parameters:
        filename (str): The name of the file to save the data.
        """
        df = pd.DataFrame(self.weather_data)
        df.to_csv(filename, index=False)

# Example usage:
if __name__ == "__main__":
    simulator = WeatherSimulator(start_date='2023-01-01', end_date='2023-01-10')
    simulator.generate_weather_data()
    simulator.save_to_csv('../data/raw/simulated_weather_data.csv')  # Adjust path as necessary