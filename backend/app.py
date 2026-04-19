from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from db_config import get_db_connection, DB_CONFIG
from model_service import model_service
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your_secret_key_12345' # In production, use environment variable

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            if token.startswith('Bearer '):
                token = token.split(" ")[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user_id = data['user_id']
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401
        return f(current_user_id, *args, **kwargs)
    return decorated

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({'message': 'Missing data'}), 400

    hashed_password = generate_password_hash(password, method='sha256')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", 
                       (username, hashed_password, email))
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except mysql.connector.Error as err:
        return jsonify({'message': f'Registration failed: {err}'}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and check_password_hash(user['password'], password):
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'])
        return jsonify({'token': token, 'username': user['username']})

    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/predict', methods=['POST'])
@token_required
def predict(user_id):
    data = request.json
    # Expecting the 21 features in the request body
    try:
        result = model_service.predict(data)
        
        # Save to database
        conn = get_db_connection()
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
        return jsonify({'message': f'Prediction failed: {str(e)}'}), 500

@app.route('/history', methods=['GET'])
@token_required
def history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM fraud_claims WHERE user_id = %s ORDER BY claim_date DESC", (user_id,))
    claims = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(claims)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
