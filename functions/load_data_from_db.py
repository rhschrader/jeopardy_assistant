import pandas as pd
import os
from dotenv import load_dotenv
from mysql.connector import Error
import mysql.connector
from sqlalchemy import create_engine


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
    
def load_data_sql(db_name = 'main_data', limit = None):
    # Start connection
    conn = create_connection()
    cursor = conn.cursor()

    # SQL SELECT statement
    select_sql = f"SELECT * FROM {db_name}"
    if limit:
        select_sql += f" LIMIT {limit}"
    select_sql += ";"
    print(select_sql)

    # Execute the query and fetch the data
    cursor.execute(select_sql)
    rows = cursor.fetchall()

    # Get column names from the cursor
    columns = [desc[0] for desc in cursor.description]

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(rows, columns=columns)

    # Close the cursor and connection
    cursor.close()
    conn.close()
    print(f'Loaded {df.shape[0]} rows from {db_name} table')

    return df

#-------------- Postgresql connection ----------------
def create_postgres_connection():
    
    # load credentials and connection details stored in .env
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    name = os.getenv("POSTGRES_NAME")
    port = os.getenv("POSTGRES_PORT")

    # create connection
    engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}")
    
    return engine
