# Purpose of this is to connect to the openai client
import os
from dotenv import load_dotenv
import openai

# Get API key
load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
def connect_to_openai_client():
    try:
        openai.api_key = os.environ['OPENAI_API_KEY']
        print("Connected to OpenAI API client successfully.")
        return openai
    except Exception as e:
        print(f"Error connecting to OpenAI API client: {e}")
        return None