import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv
from mysql.connector import Error
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

# Start connection
conn = create_connection()
cursor = conn.cursor()

# Load data
df = pd.read_csv('../data/cleansed_jeopardy_set.csv')
df = df.replace({np.nan : None}) # for MySQL

# 3. Write the INSERT statement
insert_sql = """
    INSERT INTO qa_pairs (round, clue_value, daily_double_value, category, comments, answer, question, air_date, notes)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

# 4. Loop through DataFrame rows
for i, row in tqdm(df.iterrows(), total = df.shape[0]:
    values = (
        row['round'],
        row['clue_value'],
        row['daily_double_value'],
        row['category'],
        row['comments'],
        row['answer'],
        row['question'],
        row['air_date'],
        row['notes']
    )
    cursor.execute(insert_sql, values)
    if i % 500 == 0:
        conn.commit()

# 5. Commit and close
conn.commit()
cursor.close()
conn.close()
