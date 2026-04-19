CREATE DATABASE IF NOT EXISTS vehicle_fraud_db;

USE vehicle_fraud_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fraud_claims (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    make VARCHAR(50),
    accident_area VARCHAR(50),
    sex VARCHAR(20),
    marital_status VARCHAR(50),
    fault VARCHAR(50),
    vehicle_category VARCHAR(50),
    vehicle_price VARCHAR(50),
    year VARCHAR(10),
    driver_rating INT,
    days_policy_accident VARCHAR(50),
    days_policy_claim VARCHAR(50),
    past_number_of_claims VARCHAR(50),
    age_of_vehicle VARCHAR(50),
    age_of_policy_holder VARCHAR(50),
    police_report_filed VARCHAR(10),
    witness_present VARCHAR(10),
    agent_type VARCHAR(20),
    number_of_suppliments VARCHAR(50),
    address_change_claim VARCHAR(50),
    number_of_cars VARCHAR(50),
    base_policy VARCHAR(50),
    prediction INT,
    probability FLOAT,
    claim_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
