import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import os

class ModelService:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        self.model_path = os.path.join(base_dir, 'model', 'best_fraud_detection_model.pkl')
        self.encoders_path = os.path.join(base_dir, 'model', 'encoders.pkl')
        self.model = None
        self.encoders = {}
        self.feature_cols = [
            'Make', 'AccidentArea', 'Sex', 'MaritalStatus', 'Fault', 
            'VehicleCategory', 'VehiclePrice', 'Year', 'DriverRating', 
            'Days_Policy_Accident', 'Days_Policy_Claim', 'PastNumberOfClaims', 
            'AgeOfVehicle', 'AgeOfPolicyHolder', 'PoliceReportFiled', 
            'WitnessPresent', 'AgentType', 'NumberOfSuppliments', 
            'AddressChange_Claim', 'NumberOfCars', 'BasePolicy'
        ]
        self._initialize()

    def _initialize(self):
        # Load Model
        self.model = joblib.load(self.model_path)
        
        # Load Encoders
        self.encoders = joblib.load(self.encoders_path)
            
    def predict(self, input_data):
        """
        input_data: dict containing the 21 features
        """
        # Convert dict to DataFrame with correct column order
        df_input = pd.DataFrame([input_data])
        df_input = df_input[self.feature_cols]
        
        # Apply Label Encoding
        for col, le in self.encoders.items():
            if col in df_input.columns:
                # Handle unseen values by mapping to the first class if not found (basic fallback)
                # Ideally, we should handle this more robustly
                val = str(df_input[col].iloc[0])
                if val not in le.classes_:
                    print(f"Warning: Unseen value '{val}' for column '{col}'. Falling back to default.")
                    df_input[col] = le.transform([le.classes_[0]])[0]
                else:
                    df_input[col] = le.transform([val])[0]
        
        # Predict
        prediction = self.model.predict(df_input)
        probability = self.model.predict_proba(df_input)
        
        return {
            'is_fraud': int(prediction[0]),
            'probability': float(probability[0][1]) # Always return the probability of class 1 (Fraud)
        }

# Singleton instance
model_service = ModelService()
