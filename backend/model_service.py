import joblib
import pandas as pd
import os
import logging

class ModelService:
    def __init__(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

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
        logging.info(f"Model path: {self.model_path}")
        logging.info(f"Encoders path: {self.encoders_path}")

        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model not found at {self.model_path}")

            if not os.path.exists(self.encoders_path):
                raise FileNotFoundError(f"Encoders not found at {self.encoders_path}")

            self.model = joblib.load(self.model_path)
            self.encoders = joblib.load(self.encoders_path)

            logging.info("Model and encoders loaded successfully")

        except Exception as e:
            logging.error(f"Initialization error: {str(e)}")
            raise e


    def predict(self, input_data):
        try:
            # Create DataFrame
            df_input = pd.DataFrame([input_data])

            # Ensure all required columns exist
            for col in self.feature_cols:
                if col not in df_input.columns:
                    df_input[col] = None

            # Reorder columns
            df_input = df_input[self.feature_cols]

            # Apply encoding
            for col, le in self.encoders.items():
                if col in df_input.columns:
                    val = str(df_input[col].iloc[0])

                    if val not in le.classes_:
                        logging.warning(f"Unseen value '{val}' in column '{col}', using fallback")
                        val = le.classes_[0]

                    df_input[col] = le.transform([val])

            # Prediction
            prediction = self.model.predict(df_input)
            probability = self.model.predict_proba(df_input)

            return {
                'is_fraud': int(prediction[0]),
                'probability': float(probability[0][1])
            }

        except Exception as e:
            logging.error(f"Prediction error: {str(e)}")
            raise e


# Singleton instance
model_service = ModelService()