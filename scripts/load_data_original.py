import mysql.connector
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from mysql.connector import Error
from cleanse_data import cleanse_data
from tqdm import tqdm

load_dotenv()  # Load from .env file

def create_connection(): # Create DB connection
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

def insert_data():
    # Start connection
    conn = create_connection()
    cursor = conn.cursor()

    # Load data and cleanse data
    df = cleanse_data('../data/combined_season1-40.tsv', sep = '\t')

    # SQL INSERT statement
    insert_sql = """
        INSERT INTO original_file (round, clue_value, daily_double_value, category, comments, answer, question, air_date, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    # Loop through the dataframe. This will take a few hours
    for i, row in tqdm(df.iterrows(), total = df.shape[0]):
        values = (
            row['round'],
            row['clue_value'],
            row['daily_double_value'],
            row['category'],
            row['comments'],
            row['answer'],
            row['question'],
            row['air_date'],
            row['notes'],
        )
        cursor.execute(insert_sql, values)
        if i % 500 == 0: # commit every 500 rows
            conn.commit()

    conn.commit() # commit final batch
    cursor.close() 
    conn.close()
    print(f'Data insert successful. Inserted {df.shape[0]} rows.')

if __name__ == "__main__":
    insert_data()