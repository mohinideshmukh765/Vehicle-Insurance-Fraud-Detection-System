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

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Logging
logging.basicConfig(level=logging.INFO)

# Secret Key
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback_secret')


# ================= JWT DECORATOR =================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
            else:
                token = auth_header

            data = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms=["HS256"]
            )

            current_user_id = data['user_id']

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401

        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        except Exception as e:
            logging.error(str(e))
            return jsonify({'message': 'Token processing error'}), 401

        return f(current_user_id, *args, **kwargs)

    return decorated


# ================= REGISTER =================
@app.route('/register', methods=['POST'])
def register():
    data = request.json

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
        return jsonify({'message': f'Registration failed: {err}'}), 400

    finally:
        cursor.close()
        conn.close()


# ================= LOGIN =================
@app.route('/login', methods=['POST'])
def login():
    data = request.json

    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

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

        return jsonify({'token': token, 'username': user['username']})

    return jsonify({'message': 'Invalid credentials'}), 401


# ================= PREDICT =================
@app.route('/predict', methods=['POST'])
@token_required
def predict(user_id):
    try:
        data = request.json

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
            user_id, data.get('Make'), data.get('AccidentArea'), data.get('Sex'),
            data.get('MaritalStatus'), data.get('Fault'), data.get('VehicleCategory'),
            data.get('VehiclePrice'), data.get('Year'), data.get('DriverRating'),
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

        cursor.close()
        conn.close()

        return jsonify(result)

    except Exception as e:
        logging.error(str(e))
        return jsonify({'message': 'Prediction failed'}), 500


# ================= HISTORY =================
@app.route('/history', methods=['GET'])
@token_required
def history(user_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM fraud_claims WHERE user_id = %s ORDER BY claim_date DESC",
        (user_id,)
    )

    claims = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(claims)


if __name__ == '__main__':
    app.run()