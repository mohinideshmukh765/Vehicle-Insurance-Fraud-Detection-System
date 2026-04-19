import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import os

class ModelService:
    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(__file__), 'model', 'best_fraud_detection_model.pkl')
        self.data_path = os.path.join(os.path.dirname(__file__), 'data', 'fraud_oracle.csv')
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
        
        # Load Data to fit encoders (as they weren't saved in the original notebook)
        df = pd.read_csv(self.data_path)
        
        # The notebook used LabelEncoder on all object columns + 'Year'
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if 'Year' not in categorical_cols:
            categorical_cols.append('Year')
            
        for col in categorical_cols:
            le = LabelEncoder()
            le.fit(df[col].astype(str))
            self.encoders[col] = le
            
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
