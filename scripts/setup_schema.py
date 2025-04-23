# scripts/setup_schema.py

import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv()  # Load from .env file

def create_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database = os.getenv("DB_NAME")
        )
        if connection.is_connected():
            print("Connection successful!")
        return connection
    except Error as e:
        print(f"Connection error: {e}")
        return None

def create_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS qa_pairs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        round VARCHAR(50),
        clue_value VARCHAR(20),
        daily_double_value VARCHAR(20),
        category VARCHAR(255),
        comments TEXT,
        answer TEXT NOT NULL,
        question TEXT NOT NULL,
        air_date DATE,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    try:
        db = create_connection() # connect to MySQL database
        cursor = db.cursor() # create cursor
        cursor.execute(create_table_query)
        db.commit()
        print("Table created!")
    except Error as e:
        print(f"Error in creation: {e}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()
        print('Connection closed')

if __name__ == "__main__":
    create_table()
