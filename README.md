---
title: Jeopardy Assistant
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.24.0
app_file: app.py
pinned: false
---

# jeopardy_assistant
### Project Overview
My goal is to create a RAG chatbot based on all Jeopardy questions from the past 40 years. Ideally, this can be used as a resource to develop trivia questions for trivia nights, team building activities, or Ethan Erusha's Tuesday Trivia.

### Project Goals
This is a learning experience for me to get more familiar with LLM's and databases, as well as dipping my toe in Cloud with AWS.

## Project Structure
### Models
- **Embedding Model**: OpenAI's 'text-embedding-3-small'
- **LLM**: TBD, but will use an OpenAI model

### Storage
I'm using a MySQL database to store the original Jeopardy questions and answers, and a Postgres database with pgvector to store the embeddings. Both databases are hosted on AWS RDS.
- **MySQL Database**: 
    - **Engine**: MySQL
    - **Schema**: 
        - `id`: INT
        - `question`: TEXT
        - `answer`: TEXT
        - `category`: TEXT
        - `air_date`: DATE
        - `show_number`: INT
- **Vector Store**:
    - **Engine**: Postgres
    - **Extension**: pgvector
    - **Schema**: 
        - `id`: BIGSERIAL PRIMARY KEY
        - `content`: TEXT
        - `embedding`: VECTOR(1536)

### Compute
I'm using AWS EC2 instances to create the embeddings (this took >1 day) and host the interface. The instances are configured with the following:
- **Instance Type**: t2.micro
- **Operating System**: Amazon Linux 2023
- **Python Version**: 3.9
Development and testing is done on a local Macbook.


### Data
- **Source**: https://github.com/jwolle1/jeopardy_clue_dataset
