from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import pandas as pd

class EnergyPredictionModel:
    def __init__(self):
        # Initialize the model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)

    def load_data(self, filepath):
        # Load the dataset from a CSV file
        data = pd.read_csv(filepath)
        return data

    def preprocess_data(self, data):
        # Preprocess the data for training
        # Here we assume 'target' is the column we want to predict
        X = data.drop(columns=['target'])
        y = data['target']
        return X, y

    def train(self, X, y):
        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train the model
        self.model.fit(X_train, y_train)
        
        # Evaluate the model
        predictions = self.model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        print(f'Mean Squared Error: {mse}')

    def predict(self, new_data):
        # Predict the energy consumption based on new data
        return self.model.predict(new_data)

# Example usage:
# if __name__ == "__main__":
#     model = EnergyPredictionModel()
#     data = model.load_data('path_to_processed_data.csv')
#     X, y = model.preprocess_data(data)
#     model.train(X, y)
#     new_data = pd.DataFrame(...)  # Replace with actual new data
#     predictions = model.predict(new_data)
#     print(predictions)