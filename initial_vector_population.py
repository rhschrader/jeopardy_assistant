# -------- Imports --------
import pandas as pd
from functions.db_functions import MySQL, PostGreSQL
from functions.openai_functions import OpenAI_Client
from tqdm import tqdm



# -------- Constants --------
RATE_LIMIT = 1000 # max requests per minute
TOKEN_LIMIT = 8191 # max token size
UPLOAD_INTERVAL = 100 # upload every 100 rows to the db
TIME_INTERVAL = 60 # 60s is the limit for 1500 requests
PG_TABLE_NAME = 'jeopardy_embeddings'
MYSQL_TABLE_NAME = 'main_data'

def reset_embedding_dict():
    return {'id':[], 'content':[], 'embedding':[]}

def initial_vector_population():

    # Load in custom openai class for all openai API calls
    openai_client = OpenAI_Client()

    # Load in custom mysql class for all mysql API calls
    mysql_client = MySQL()

    # Load in custom postgres class for all postgres API calls
    postgres_client = PostGreSQL()

    # Check the last id in the table
    ## I do this because it will take a very long time to load all the vectors, if the task crashes we can restart from the last id
    last_id = postgres_client.get_last_id(PG_TABLE_NAME)
    print(f'Last id in {PG_TABLE_NAME} is {last_id}')

    # Load in the data from mysql - only loading a chunk of rows to save memory
    df = mysql_data = mysql_client.load_from_last_id(chunk_size=UPLOAD_INTERVAL, last_id=last_id, table_name=MYSQL_TABLE_NAME)

    # Get total rows to process
    rows_to_process = mysql_client.get_table_size(MYSQL_TABLE_NAME) - int(last_id)
    print(f'Total rows to process: {rows_to_process}')

    # Create a dict to store embeddings
    embeddings = reset_embedding_dict()

    # keep track of any rows that are skipped
    skipped_rows = []

    # first row of df
    i = 0

    for _ in tqdm(range(rows_to_process)):
        # Get the row to process
        row = df.iloc[i]

        # Get the embedding for the row
        result = openai_client.get_embedding(row['string_for_embedding'])

        # check that result is not empty, append to the embedding dict
        if result is None:
            id = row['id']
            skipped_rows.append(id)
            print(f"Token size too long. Skipping row {id}")
            continue
        else:
            # append 3 columns
            embeddings['id'].append(row['id'])
            embeddings['content'].append(row['string_for_embedding'])
            embeddings['embedding'].append(result)
        
        # Check if we are at the end of the chunk, upload to postgres and get next chunk
        if row['id'] == df.iloc[-1]['id']:
            # Convert to df for sqlalchemy
            embeddings_df = pd.DataFrame(embeddings)

            # Insert into vector db
            postgres_client.insert_data(embeddings_df, table_name=PG_TABLE_NAME)

            # Reset the dict
            embeddings = reset_embedding_dict()

            # get last id
            last_id = postgres_client.get_last_id(PG_TABLE_NAME)

            # Load in the next chunk of data
            df = mysql_client.load_from_last_id(chunk_size=UPLOAD_INTERVAL, last_id=row['id'], table_name=MYSQL_TABLE_NAME)

            # reset the index
            i = 0
        else:
            # Increment the index
            i += 1

    # Final upload if there are any remaining embeddings
    if len(embeddings['id']) > 0:
        embeddings_df = pd.DataFrame(embeddings)
        postgres_client.insert_data(embeddings_df, table_name=PG_TABLE_NAME)
    print(f'Complete. Uploaded {rows_to_process} to {PG_TABLE_NAME}!')

if __name__ == '__main__':
    initial_vector_population()




        

