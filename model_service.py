import joblib
import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO)

class ModelService:
    def __init__(self):
        # Absolute base directory (works on Azure)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # Paths to model files
        self.model_path = os.path.join(self.base_dir, "model", "best_fraud_detection_model.pkl")
        self.encoders_path = os.path.join(self.base_dir, "model", "encoders.pkl")

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
        try:
            logging.info(f"Base directory: {self.base_dir}")
            logging.info(f"Model path: {self.model_path}")
            logging.info(f"Encoders path: {self.encoders_path}")

            # Validate files exist
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model NOT FOUND at {self.model_path}")

            if not os.path.exists(self.encoders_path):
                raise FileNotFoundError(f"Encoders NOT FOUND at {self.encoders_path}")

            # Load model
            self.model = joblib.load(self.model_path)
            self.encoders = joblib.load(self.encoders_path)

            logging.info("✅ Model and encoders loaded successfully")

        except Exception as e:
            logging.error(f"❌ Initialization failed: {str(e)}")
            raise

    def predict(self, input_data):
        try:
            # Convert to DataFrame
            df_input = pd.DataFrame([input_data])

            # Ensure all required columns exist
            for col in self.feature_cols:
                if col not in df_input.columns:
                    df_input[col] = "Unknown"

            # Reorder columns
            df_input = df_input[self.feature_cols]

            # Apply encoders safely
            for col, encoder in self.encoders.items():
                if col in df_input.columns:
                    value = str(df_input[col].iloc[0])

                    # Handle unseen values
                    if value not in encoder.classes_:
                        logging.warning(f"Unseen value '{value}' in '{col}', using default")
                        value = encoder.classes_[0]

                    df_input[col] = encoder.transform([value])

            # Prediction
            prediction = self.model.predict(df_input)[0]
            probability = self.model.predict_proba(df_input)[0][1]

            return {
                "is_fraud": int(prediction),
                "probability": float(probability)
            }

        except Exception as e:
            logging.error(f"❌ Prediction failed: {str(e)}")
            raise
############################################

# Singleton instance (loads once)
model_service = ModelService()