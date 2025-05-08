import pandas as pd
import os
from dotenv import load_dotenv
from mysql.connector import Error
import mysql.connector
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()  # Load from .env file

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

class MySQL:
    def __init__(self, table_name = 'main_data', chunk_size = 500):
        self.host=os.getenv("DB_HOST"),
        self.user=os.getenv("DB_USER"),
        self.password=os.getenv("DB_PASSWORD"),
        self.database = os.getenv("DB_NAME")
        self.table_name = table_name
        self.chunk_size = chunk_size
        self.url = f"mysql+pymysql://{self.user}:{self.password}@{self.host}/{self.table_name}"
        self.engine = create_engine(self.url)
        self.last_id = 0

    # Load 500 rows at a time
    def load_chunk(self, table = None):
        if table:
            self.table_name = table
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE id > {self.last_id}
            ORDER BY id ASC
            LIMIT {self.chunk_size};
        """
        with self.engine.connect() as connection:
            try:
                df = pd.read_sql(query, connection)
                if not df.empty:
                    self.last_id = df['id'].iloc[-1]
                return df
            except SQLAlchemyError as e:
                print(f"Error loading chunk: {e}")
                return pd.DataFrame()
        
    def load_table(self, table = None):
        if table:
            self.table_name = table
        query = f"""
            SELECT * FROM {self.table_name};
        """
        with self.engine.connect() as connection:
            try:
                df = pd.read_sql(query, connection)
                if not df.empty:
                    self.last_id = df['id'].iloc[-1]
                return df
            except SQLAlchemyError as e:
                print(f"Error loading table: {e}")
                return pd.DataFrame()
            
    def custom_query(self, query):
        with self.engine.connect() as connection:
            try:
                result = connection.execute(text(query))
                return result
            except SQLAlchemyError as e:
                print(f'Error executing query: {query}: {e}')
                return None

            

class PostGreSQL:
    def __init__(self, table_name = 'vectors'):
        # load credentials and connection details stored in .env
        self.user = os.getenv("POSTGRES_USER")
        self.password = os.getenv("POSTGRES_PASSWORD")
        self.host = os.getenv("POSTGRES_HOST")
        self.port = os.getenv("POSTGRES_PORT")
        self.table_name = table_name
        self.engine = create_engine(f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.table_name}")

    def insert_data(self, df, table_name = None):
        if not table_name:
            table_name = self.table_name
        with self.engine.connect() as connection:
            try:
                df.to_sql(table_name, connection, if_exists='append', index = False)
                print(f"Inserted {df.shape[0]} rows into {table_name}")
                return
            except SQLAlchemyError as e:
                print(f'Error inserting {df.shape[0]} rows into {table_name}: {e}')
                return None
    
    def read_data(self, query, table_name = None):
        with self.engine.connect() as connection:
            try:
                df = pd.read_sql(query, connection)
                return df
            except SQLAlchemyError as e:
                print(f'Error executing query: {query} - {e}')
                return None
    
    def create_vector_db(self, table_name):
        query = f"""
            CREATE TABLE {table_name} (
            id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            content TEXT,
            embedding VECTOR(1536)
            );
            """
        with self.engine.connect() as connection:
            try:
                result = connection.execute(text(query))


