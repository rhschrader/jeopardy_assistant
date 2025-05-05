import os
from dotenv import load_dotenv
from google import genai
from IPython.display import Markdown, display, update_display

# Get API key
load_dotenv()
os.environ['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')

def connect_to_client():
    try:
        client = genai.Client(api_key = os.environ['GEMINI_API_KEY'])
        print("Connected to Gemini API client successfully.")
        return client
    except Exception as e:
        print(f"Error connecting to Gemini API client: {e}")
        return None