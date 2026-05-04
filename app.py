from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from db_config import get_db_connection
from model_service import model_service
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import logging

import sys
# ================= APP INIT =================
app = Flask(__name__)


# ... after app = Flask(__name__) ...

# This forces Flask and your manual logs to show up in the Azure Log Stream
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
)

# Optional: specifically log when the DB connection is attempted
@app.before_request
def log_request_info():
    app.logger.info('Body: %s', request.get_data())

# In app.py
CORS(app, resources={r"/*": {
    "origins": [
        "http://localhost:5173", 
        "https://yellow-flower-046c8bc00.7.azurestaticapps.net"
    ]
}}, supports_credentials=True)

logging.basicConfig(level=logging.INFO)
##########################################################################
# # Secret key (use Azure App Settings in production)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback_secret')


# ================= HEALTH CHECK (IMPORTANT FOR AZURE) =================
@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "API is running"}), 200


# ================= JWT DECORATOR =================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            token = auth_header.split(" ")[1] if auth_header.startswith("Bearer ") else auth_header

            data = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms=["HS256"]
            )

            current_user_id = data['user_id']

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        except Exception as e:
            logging.error(f"JWT error: {str(e)}")
            return jsonify({'message': 'Token error'}), 401

        return f(current_user_id, *args, **kwargs)

    return decorated


# ================= REGISTER =================
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({'message': 'Invalid JSON'}), 400

    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({'message': 'Missing data'}), 400

    hashed_password = generate_password_hash(password)

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Database connection failed'}), 500

    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
            (username, hashed_password, email)
        )
        conn.commit()

        return jsonify({'message': 'User registered successfully'}), 201

    except mysql.connector.Error as err:
        logging.error(str(err))
        return jsonify({'message': 'Registration failed'}), 400

    finally:
        cursor.close()
        conn.close()


# ================= LOGIN =================
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({'message': 'Invalid JSON'}), 400

    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'message': 'User not found'}), 404

        if check_password_hash(user['password'], password):
            token = jwt.encode(
                {
                    'user_id': user['id'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
                },
                app.config['SECRET_KEY'],
                algorithm="HS256"
            )

            return jsonify({
                'token': token,
                'username': user['username']
            })

        return jsonify({'message': 'Invalid credentials'}), 401

    finally:
        cursor.close()
        conn.close()


# ================= PREDICT =================
@app.route('/predict', methods=['POST'])
@token_required
def predict(user_id):
    data = request.get_json(silent=True)

    if not data:
        return jsonify({'message': 'Invalid JSON'}), 400

    try:
        result = model_service.predict(data)

        conn = get_db_connection()
        if not conn:
            return jsonify({'message': 'Database connection failed'}), 500

        cursor = conn.cursor()

        insert_query = """
        INSERT INTO fraud_claims (
            user_id, make, accident_area, sex, marital_status, fault,
            vehicle_category, vehicle_price, year, driver_rating,
            days_policy_accident, days_policy_claim, past_number_of_claims,
            age_of_vehicle, age_of_policy_holder, police_report_filed,
            witness_present, agent_type, number_of_suppliments,
            address_change_claim, number_of_cars, base_policy,
            prediction, probability
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        feature_values = [
            user_id,
            data.get('Make'), data.get('AccidentArea'), data.get('Sex'),
            data.get('MaritalStatus'), data.get('Fault'),
            data.get('VehicleCategory'), data.get('VehiclePrice'),
            data.get('Year'), data.get('DriverRating'),
            data.get('Days_Policy_Accident'), data.get('Days_Policy_Claim'),
            data.get('PastNumberOfClaims'), data.get('AgeOfVehicle'),
            data.get('AgeOfPolicyHolder'), data.get('PoliceReportFiled'),
            data.get('WitnessPresent'), data.get('AgentType'),
            data.get('NumberOfSuppliments'), data.get('AddressChange_Claim'),
            data.get('NumberOfCars'), data.get('BasePolicy'),
            result['is_fraud'], result['probability']
        ]

        cursor.execute(insert_query, feature_values)
        conn.commit()

        return jsonify(result)

    except Exception as e:
        logging.error(f"Prediction error: {str(e)}")
        return jsonify({'message': 'Prediction failed'}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()


# ================= HISTORY =================
@app.route('/history', methods=['GET'])
@token_required
def history(user_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM fraud_claims WHERE user_id = %s ORDER BY claim_date DESC",
            (user_id,)
        )

        claims = cursor.fetchall()
        return jsonify(claims)

    finally:
        cursor.close()
        conn.close()


# ================= MAIN =================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)