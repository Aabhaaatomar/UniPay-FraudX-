import pickle
import numpy as np
import os

class FraudDetector:
    def __init__(self, model_path='models/fraud_model.pkl'):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                artifacts = pickle.load(f)
                # Handle both updated combined dictionary structure and older raw pkl formats
                if isinstance(artifacts, dict):
                    self.model = artifacts.get('model')
                    self.scaler = artifacts.get('scaler')
                else:
                    self.model = artifacts
        else:
            print(f"⚠️ Warning: Model file not found at {self.model_path}. Please run model.py first.")

    def predict_transaction(self, amount, old_bal_org, new_bal_org, old_bal_dest, new_bal_dest):
        if self.model is None:
            return "Model Error", 0.0
        
        # Structure the input vector
        input_data = np.array([[amount, old_bal_org, new_bal_org, old_bal_dest, new_bal_dest]])
        
        # Apply scaling if available
        if self.scaler:
            input_data = self.scaler.transform(input_data)
            
        # Get raw class prediction and risk percentages
        prediction = self.model.predict(input_data)[0]
        probabilities = self.model.predict_proba(input_data)[0]
        
        # Fraud probability is index 1
        fraud_probability = round(probabilities[1] * 100, 2)
        
        status = "Suspicious" if prediction == 1 or fraud_probability > 50 else "Normal"
        return status, fraud_probability