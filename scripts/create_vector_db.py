# Imports
import pandas as pd
import sys
import os
sys.path.insert(1, '../functions')
from load_data_from_db import create_postgres_connection
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


def create_table():
    engine = create_postgres_connection()
    
    query = """
    CREATE TABLE IF NOT EXISTS vectors  (
        id INTEGER PRIMARY KEY
        text TEXT NOT NULL
        embedding vector(1))"""

    try:
        with engine.connect() as connection:
            connection.execute(text(query))
            print('Table created successfully')
    except SQLAlchemyError as e:
        print(f'An error occurred while creating the table. {e}')


if __name__ == "__main__":
    create_table()






