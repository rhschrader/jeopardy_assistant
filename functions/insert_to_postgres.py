import pandas as pd
import sys
sys.path.insert(1, '../../functions')
from functions.db_functions import load_data_sql, create_postgres_connection
from sqlalchemy.exc import SQLAlchemyError
import logging

def insert_to_postgres(df, table_name = 'vectors'):
    
    try:
        # connect to postgres db. this utilizes pgvector for vector store
        engine = create_postgres_connection() 

        # insert into db
        df.to_sql(table_name, engine, if_exists='append', index = False)
        print(f"Successfully inserted {len(df)} rows into {table_name}.")

    except SQLAlchemyError as e:
        logging.error(f"SQLAlchemy error while inserting into {table_name}: {e}")
        print(f"SQLAlchemy error while inserting into {table_name}: {e}")
    
    except ValueError as e:
        logging.error(f"Value error (likely a dataframe/column issue): {e}")
        print(f"Value error (likely a dataframe/column issue): {e}")
    
    except Exception as e:
        logging.error(f"Unexpected error during insert: {e}")
        print(f"Unexpected error during insert: {e}")
    return
