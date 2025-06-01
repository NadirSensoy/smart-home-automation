import unittest
from src.models.energy_prediction import EnergyPredictionModel
from src.data_processing.preprocessing import preprocess_data

class TestEnergyPredictionModel(unittest.TestCase):
    def setUp(self):
        # Sample data for testing
        self.raw_data = {
            'temperature': [22, 23, 21, 20, 19],
            'humidity': [30, 35, 32, 31, 29],
            'light': [200, 180, 220, 210, 190],
            'device_state': [1, 0, 1, 0, 1]  # 1 for ON, 0 for OFF
        }
        self.processed_data = preprocess_data(self.raw_data)

        # Initialize the model
        self.model = EnergyPredictionModel()

    def test_model_training(self):
        # Test if the model can be trained
        self.model.train(self.processed_data)
        self.assertTrue(self.model.is_trained)

    def test_model_prediction(self):
        # Test if the model can make predictions
        predictions = self.model.predict(self.processed_data)
        self.assertEqual(len(predictions), len(self.processed_data))

    def test_model_evaluation(self):
        # Test model evaluation metrics
        self.model.train(self.processed_data)
        metrics = self.model.evaluate(self.processed_data)
        self.assertIn('accuracy', metrics)
        self.assertIn('f1_score', metrics)

if __name__ == '__main__':
    unittest.main()