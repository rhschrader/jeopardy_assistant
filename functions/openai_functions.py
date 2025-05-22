# Functions used to produce embeddings from OpenAI
import os
from dotenv import load_dotenv
from openai import OpenAI
import openai
import time
import tiktoken

load_dotenv()


def connect_to_openai_client():
    # Creates connection with openai client via API key

    # Get API key
    try:
        openai.api_key = os.environ['OPENAI_API_KEY']
        print("Connected to OpenAI API client successfully.")
        return openai
    except Exception as e:
        print(f"Error connecting to OpenAI API client: {e}")
        return None
    


def count_tokens(string, encoding_name = 'cl100k_base'):
    # Returns the number of tokens in the string to be encoded
    # This will be used to monitor the TPD (tokens per day limit)

    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def get_embedding(string, model, client):
    # Take's a string and gets embedding using OpenAI's model
    
    for attempt in range(0,5):
        # 5 retries in case of error
        try:
            response = client.embeddings.create(input=string, model=model) #embedding from openai
            return response.data[0].embedding # 1536 dimensions
        except openai.APIError as e:
            #Handle API error here, e.g. retry or log
            print(f"OpenAI API returned an API Error: {e}")
            pass
        except openai.APIConnectionError as e:
            #Handle connection error here
            print(f"Failed to connect to OpenAI API: {e}")
            pass
        except openai.RateLimitError as e:
            #Handle rate limit error (we recommend using exponential backoff)
            print(f"OpenAI API request exceeded rate limit: {e}")
            time.sleep(60)
            pass
        # If 5 attempts have been done
        if attempt == 4:
            print("Max attempts reached. Skipping row.")
            return None
        
class OpenAI_Client:
    def __init__(self, embedding_model = 'text-embedding-3-small', encoding_model = 'cl100k_base'):
        self.embedding_model = embedding_model
        self.encoding_model = encoding_model
        self.client = OpenAI(api_key = os.getenv('OPENAI_API_KEY'))
        self.embedding_dims = 1536
        self.total_tokens = 0

    def get_embedding(self, string):
        # Take's a string and gets embedding using OpenAI's model
        for attempt in range(0,5):
            # 5 retries in case of error
            try:
                response = self.client.embeddings.create(input=string, model=self.embedding_model) #embedding from openai
                return response.data[0].embedding # 1536 dimensions
            except openai.APIError as e:
                #Handle API error here, e.g. retry or log
                print(f"OpenAI API returned an API Error: {e}")
                pass
            except openai.APIConnectionError as e:
                #Handle connection error here
                print(f"Failed to connect to OpenAI API: {e}")
                pass
            except openai.RateLimitError as e:
                #Handle rate limit error (we recommend using exponential backoff)
                print(f"OpenAI API request exceeded rate limit: {e}")
                time.sleep(60)
                pass
            # If 5 attempts have been done
            if attempt == 4:
                print("Max attempts reached. Skipping row.")
                return None
    
    def count_tokens(self, string):
    # Returns the number of tokens in the string to be encoded
    # This will be used to monitor the TPD (tokens per day limit)
        encoding = tiktoken.get_encoding(self.encoding_model)
        num_tokens = len(encoding.encode(string))
        self.total_tokens += num_tokens
        return num_tokens