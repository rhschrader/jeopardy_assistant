import sys
sys.path.insert(1, '../functions')
from db_functions import PostGreSQL

if __name__ == "__main__":
    # Create a Postgres client
    postgres_client = PostGreSQL()

    # Create the index
    postgres_client.create_hnsw_index(table_name='jeopardy_embeddings')

