# This script is designed to create a Retrieval-Augmented Generation (RAG) bot to interact with the Jeopardy dataset.


# -------- Imports --------

import pandas as pd
from functions.openai_functions import OpenAI_Client
from functions.db_functions import MySQL, PostGreSQL

# -------- Connections --------

# Load in custom openai class for all openai API calls
openai_client = OpenAI_Client()
# Load in custom postgres class for all postgres API calls
postgres = PostGreSQL(create_psycopg2_connection=True)

# -------- Functions --------

# This function is used to get the user query
def get_user_query(prompt = "Enter your query for the jeopardy trivia bot: "):
    user_query = input(prompt)
    if user_query.lower() == 'exit':
        print("Exiting...")
        sys.exit()
    return user_query

def rag_bot():
    # This function is used to create a RAG bot to interact with the Jeopardy dataset
    # It uses the OpenAI API to get embeddings and the Postgres API to get the data from the vector database

    more_questions = True

    while more_questions:
        # Get the user query
        user_query = get_user_query()

        # Get the embedding for the user query
        print("Getting most similar jeopardy questions for your request...")
        embedding = openai_client.get_embedding(user_query) #embedding of the user query
        prompt_vector = '[' + ','.join(map(str, embedding)) + ']' # formatting

        # get the most similar rows from the postgres database
        results = postgres.cosine_search(prompt_vector = prompt_vector, match_count = 10)

        # create a context string from the results
        context = [row[1] for row in results]
        context_str = "\n\n".join(context)
        prompt = f"Context:\n{context_str}\n\nOriginal user question: {user_query}"
        messages = [
            {"role": "system", "content": """You are a helpful assistant using context to answer questions. 
            The context is comes from the show Jeopardy, and is question - answer pairs. 
            Preferably, use the context provided to create fun trivia questions for a game night. 
            If the context is not sufficient, you can use your own knowledge."""},
            {"role": "user", "content": prompt}
        ]

        # Get response from LLM
        print("Creating response...")
        response = openai_client.chat_with_llm(messages)
        print(response)

        more_questions = get_user_query("Do you want to ask another question? (y/n): ")
        if more_questions.lower() == 'y':
            more_questions = True
        else:
            more_questions = False
            print("Goodbye! Exiting...")
            break

if __name__ == "__main__":
    # Run the RAG bot
    rag_bot()

