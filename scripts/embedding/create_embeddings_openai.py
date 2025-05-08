# Imports
import pandas as pd
import openai
import time
import sys
sys.path.insert(1, '../../functions')
sys.path.insert(1, '/embeddings')
from load_data_from_db import load_data_sql, create_postgres_connection
from connect_openai_api import connect_to_openai_client
from insert_to_postgres import insert_to_postgres
from tqdm import tqdm
import tiktoken
import os
import pickle

### REMINDER - CREATE LOGIC TO CHECK TOTAL TOKEN LIMIT

RATE_LIMIT = 1000 # max requests per minute
TOKEN_LIMIT = 8191 # max token size
UPLOAD_INTERVAL = 100 # upload every 500 rows to the db
TIME_INTERVAL = 60 # 60s is the limit for 1500 requests
TABLE_NAME = 'vectors'

# Function to get the embedding for a single row
def get_single_embedding(client, model, row, total_tokens, service='openai'):
    # check token size is under the limit
    #check, total_tokens = count_tokens(row['string_for_embedding'], total_tokens)
    check = True
    if not check:
        id = row['id']
        return None, total_tokens
    else:
        # call embedding api
        for attempt in range(1, 5):
            try:
                response = client.embeddings.create(
                    input=row['string_for_embedding'],
                    model=model
                )
                return response.data[0].embedding, total_tokens
            except Exception as e:
                print(f"Attempt {attempt} failed: {e}")
                if attempt == 4:
                    print("Max attempts reached. Skipping row.")
                    return None, total_tokens
                time.sleep(62)  # wait for 62 seconds before retrying
    
def count_tokens(text, total_tokens):
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    if len(tokens) > total_tokens:
        print(f"Token size too long. {len(tokens)} tokens.")
        return False, total_tokens
    else:
        total_tokens += len(tokens)
        return True, total_tokens

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
    jeopardy_set = load_data_sql(db_name = 'main_data')

    # load google client to create the embeddings
    #client = connect_to_google_client()
    #model = 'text-embedding-004' # see https://ai.google.dev/gemini-api/docs/models 

    # load openai client to create the embeddings
    client = connect_to_openai_client()
    model = "text-embedding-3-small"


    # Empty dict to store embedding results
    embeddings = reset_embedding_dict()

    # keep track of any rows that are skipped
    skipped_rows = []

    # uploaded rows counter
    uploaded_rows = 0

    # list to keep track of timestamps
    timestamps = []

    # total tokens used
    total_tokens = 0

    if os.path.exists('last_i.pkl'):
        with open('last_i.pkl', 'rb') as f:
            last_i = pickle.load(f)
    else:
        last_i = 0
    print(f"Starting from index {last_i}.")

    # loop through the dataframe
    for i, row in tqdm(jeopardy_set[last_i:].iterrows(), total=jeopardy_set[last_i:].shape[0]):
        
        # get embedding result
        result, total_tokens = get_single_embedding(client=client, model=model, row=row, total_tokens=total_tokens)
        
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
            # save progress in case of interruption
            last_i = i
            with open('last_i.pkl', 'wb') as f:
                pickle.dump(last_i, f)

        # save progress in case of interruption
        last_i = i
        with open('last_i.pkl', 'wb') as f:
            pickle.dump(last_i, f)
        
    # final upload
    if len(embeddings['id']) > 0:
        embeddings_df = pd.DataFrame(embeddings)
        insert_to_postgres(embeddings_df)
    
    print(f'Complete. Uploaded {uploaded_rows} to {TABLE_NAME}!')


if __name__ == '__main__':
    create_embeddings()



