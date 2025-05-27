import pandas as pd
import os
from dotenv import load_dotenv
from mysql.connector import Error
import mysql.connector
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import psycopg2

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
    def __init__(self, table_name = 'main_data'):
        self.host=os.getenv("DB_HOST")
        self.user=os.getenv("DB_USER")
        self.password=os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_NAME")
        self.table_name = table_name
        self.url = f"mysql+pymysql://{self.user}:{self.password}@{self.host}:3306/{self.database}"
        self.engine = create_engine(self.url)
        self.last_id = 0

    # Load 500 rows at a time
    def load_chunk(self, table = None, chunk_size = 500):
        if chunk_size:
            self.chunk_size = chunk_size
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
            
    def load_from_last_id(self, chunk_size = 100, last_id = None, table_name = None):
        if table_name:
            self.table_name = table_name
        if last_id:
            self.last_id = last_id
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE id > {self.last_id}
            ORDER BY id ASC
            LIMIT {chunk_size};
        """
        with self.engine.connect() as connection:
            try:
                df = pd.read_sql(query, connection)
                if not df.empty:
                    self.last_id = df['id'].iloc[-1]
                return df
            except SQLAlchemyError as e:
                print(f"Error loading from last id: {e}")
                return pd.DataFrame()
            
    def get_table_size(self, table_name = None):
        if table_name:
            self.table_name = table_name
        query = f"""
            SELECT COUNT(*) FROM {self.table_name};
        """
        with self.engine.connect() as connection:
            try:
                result = connection.execute(text(query))
                return result.scalar()
            except SQLAlchemyError as e:
                print(f'Error getting table size: {e}')
                return None
            

class PostGreSQL:
    def __init__(self, table_name = 'jeopardy_embeddings', create_psycopg2_connection = False):
        # load credentials and connection details stored in .env
        self.user = os.getenv("POSTGRES_USER")
        self.password = os.getenv("POSTGRES_PASSWORD")
        self.host = os.getenv("POSTGRES_HOST")
        self.port = os.getenv("POSTGRES_PORT")
        self.db_name = os.getenv("POSTGRES_NAME")
        self.table_name = table_name
        # create a sqlalchemy engine
        self.engine = create_engine(f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}")
        # create a psycopg2 connection
        if create_psycopg2_connection:
            self.connection = psycopg2.connect(
                dbname=self.db_name,
                user=self.user,
                password=self.password,
                host=self.host,
            )

    # ----- Insert data to DB -----
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
    
    # ----- Read data from DB -----
    def read_data(self, query, table_name = None):
        with self.engine.connect() as connection:
            try:
                df = pd.read_sql(query, connection)
                return df
            except SQLAlchemyError as e:
                print(f'Error executing query: {query} - {e}')
                return None
    
    # ----- Create vector DB -----
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
                print(f"Table {table_name} created successfully.")
                return result
            except SQLAlchemyError as e:
                print(f"Error creating table {table_name}: {e}")
                return None

    # ----- Execute custom query -----   
    def execute_query(self, query, table_name = None):
        with self.engine.connect() as connection:
            try:
                result = connection.execute(text(query))
                return result
            except SQLAlchemyError as e:
                print(f'Error executing query: {query} - {e}')
                return None
    
    # ----- Get last id from table -----
    # This is used to get the last id from the table after inserting data
    def get_last_id(self, table_name = None):
        if table_name:
            self.table_name = table_name
        query = f"""
            SELECT MAX(id) FROM {self.table_name}
        """
        with self.engine.connect() as connection:
            try:
                result = connection.execute(text(query))
                last_id = result.scalar()
                if last_id is None:
                    last_id = 0
                return last_id
            except SQLAlchemyError as e:
                print(f'Error getting last id from {self.table_name}: {e}')
                return None

    def cosine_search(self, prompt_vector, table_name = None, match_count = 5, match_threshold = 0.5):
        if table_name is None:
            table_name = self.table_name
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(f"""
                               SELECT id, content, 1 - (embedding <=> %(prompt_vector)s) AS similarity
                               FROM {table_name} 
                               ORDER BY similarity DESC LIMIT %(match_count)s;
                               """,
                    {'prompt_vector': prompt_vector, 'match_count': match_count}
                    )
                results = cursor.fetchall()
                return results
            except Error as e:
                print(f'Error executing query: {e}')
                return None
            
    def create_hnsw_index(self, table_name = None):
        if table_name is None:
            table_name = self.table_name
        query = f"""
            CREATE INDEX IF NOT EXISTS idx_embedding 
            ON {table_name} 
            USING hnsw (embedding vector_cosine_ops)
            WITH (m = 4, ef_construction = 10);
        """
        # Build the index
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(query)
                self.connection.commit()
                print(f"Index created on {table_name} successfully.")
            except Error as e:
                print(f"Error creating index on {table_name}: {e}")
                self.connection.rollback()
        
        # Update the statistics for the query planner
        # to ensure that the index is used for the vector similarity search
        ## REFERENCE: https://github.com/dmagda/openai-cookbook/blob/main/examples/vector_databases/postgresql/getting_started_with_postgresql_pgvector.ipynb
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(f"VACUUM ANALYZE {table_name};")
                self.connection.commit()
                print(f"Statistics validated for {table_name}.")
                print("Index created successfully!")
            except Error as e:
                print(f"Error updating statistics for {table_name}: {e}")
                self.connection.rollback()
            