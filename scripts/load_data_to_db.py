# scripts/load_csv_to_db.py

import os
import pandas as pd
from dotenv import load_dotenv
#import mysql.connector
#from mysql.connector import Error
#from setup_schema import create_connection
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import text
import numpy as np

load_dotenv()

def get_db_creds():
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    name = os.getenv("DB_NAME")
    table = os.getenv("TABLE_NAME")
    return host, user, password, name, table

def sanitize_input(input_str):
    return input_str.str.replace("\\", " ").str.replace('"', "'")  # Escaping single quotes and backslashes.replace("'", "''")


def load_jeopardy_data(fpath):
    df = pd.read_csv(fpath, sep='\t') #load tab-separated file
    df = df.replace({np.nan : None}) # for MySQL
    #df['question'] = df['question'].str.replace('"', "'").str.replace('\\', '').str.replace("'", "''")
    #df['answer'] = df['answer'].str.replace('"', "'").str.replace('\\', '')
    return df

def load_db():
    data = load_jeopardy_data('../data/cleansed_jeopardy_set.tsv') #load data
    host, user, password, name, table = get_db_creds()
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{name}", echo = True)
    with engine.connect() as connection:
        data.to_sql(table, con=engine, if_exists='append', index=False, chunksize=500)
    """db = create_connection() # connect to MySQL database
    cursor = db.cursor() # cursor
    sql_query = """
    #INSERT INTO jeopardy.qa_pairs (round, clue_value, daily_double_value, category, comments, answer, question, air_date, notes)
    #VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    """for _, row in data.iterrows():
        cursor.execute(sql_query, row.values)
    #db.commit()
    #print(f"Inserted {cursor.rowcount} rows!")
    cursor.close()
    db.close()
    print('Connection closed.')"""

if __name__ == "__main__":
    load_db()


