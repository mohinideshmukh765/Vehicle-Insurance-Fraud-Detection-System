import os
import mysql.connector
import logging

DB_CONFIG = {
    'host': os.environ.get('DB_HOST'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'database': os.environ.get('DB_NAME'),
    'port': 3306,
    'ssl_disabled': False,   # Required for Azure MySQL
    'connection_timeout': 10
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn

    except mysql.connector.Error as err:
        logging.error(f"Database Connection Error: {err}")
        return None