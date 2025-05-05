# Imports
import pandas as pd
from google import genai
from google.genai import types
import time
import sys
sys.path.insert(1, '../functions')
sys.path.insert(1, '../scripts/embedding')
from load_data_from_db import load_data_sql, create_postgres_connection
from connect_google_api import connect_to_client
from insert_to_postgres import insert_to_postgres
from tqdm import tqdm

RATE_LIMIT = 500 # max requests per minute
TOKEN_LIMIT = 2048 # max token size
UPLOAD_INTERVAL = 150 # upload every 500 rows to the db
TIME_INTERVAL = 60 # 60s is the limit for 1500 requests
TABLE_NAME = 'vectors'


def get_single_embedding(client, model, row):
    # check token size is under the limit
    total_tokens = len(row['string_for_embedding']) / 4 # rough estimate of token size
    if total_tokens > TOKEN_LIMIT:
        id = row['id']
        return None
    else:
        # call embedding api
        result = client.models.embed_content(
            model=model,
            contents=row['string_for_embedding'],
            config = types.EmbedContentConfig(task_type = 'RETRIEVAL_DOCUMENT')
        )
        return result.embeddings[0].values
    
def request_per_minute_check(timestamps):
    if len(timestamps) >= RATE_LIMIT:
        sleep_time = TIME_INTERVAL - (timestamps[-1] - timestamps[0])
        print(f'Rate limit hit. Sleeping for {sleep_time:.2f} seconds.')
        time.sleep(sleep_time)
    return

def reset_embedding_dict():
    return {'id':[], 'qa_text':[], 'embedding':[]}


def create_embeddings():

    # dataframe of the jeopardy dataset
    jeopardy_set = load_data_sql(db_name = 'main_data', limit = 1100)

    # load google client to create the embeddings
    client = connect_to_client()
    model = 'text-embedding-004' # see https://ai.google.dev/gemini-api/docs/models 

    # Empty dict to store embedding results
    embeddings = reset_embedding_dict()

    # keep track of any rows that are skipped
    skipped_rows = []

    # uploaded rows counter
    uploaded_rows = 0

    # list to keep track of timestamps
    timestamps = []
    
    for i, row in tqdm(jeopardy_set[:1100].iterrows(), total=jeopardy_set[:1100].shape[0]):
        
        # get embedding result
        result = get_single_embedding(client=client, model=model, row=row)
        
        # check that we are below the allowed request limit. In this case it's 1500 requests / 60s
        now = time.time()
        timestamps = [times for times in timestamps if now - times < TIME_INTERVAL] # all iteration timestamps in last 60s
        #request_per_minute_check(timestamps=timestamps) # sleep if it's reached the limit
        sleep_time = TIME_INTERVAL / RATE_LIMIT
        time.sleep(sleep_time) # sleep to avoid rate limit

        # check that token size was not too long
        if result is None:
            id = row['id']
            skipped_rows.append(id)
            print(f"Token size too long. Skipping row {id}")
            continue
        else:
            # append 3 columns
            embeddings['id'].append(row['id'])
            embeddings['qa_text'].append(row['string_for_embedding'])
            embeddings['embedding'].append(result)

        # Upload to postgres table every 500 iterations
        if len(embeddings['id']) % UPLOAD_INTERVAL == 0:
            embeddings_df = pd.DataFrame(embeddings) # convert to df for sqlalchemy
            insert_to_postgres(embeddings_df, table_name=TABLE_NAME) # insert into db
            uploaded_rows += len(embeddings['id']) # to track total rows
            embeddings = reset_embedding_dict() # save memory, clear the dict after it's uploaded
        
    # final upload
    if len(embeddings['id']) > 0:
        embeddings_df = pd.DataFrame(embeddings)
        insert_to_postgres(embeddings_df)
    
    print(f'Complete. Uploaded {uploaded_rows} to {TABLE_NAME}!')


if __name__ == '__main__':
    create_embeddings()



