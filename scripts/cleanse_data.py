## This function will cleanse the dataframe, ensuring it's able to be inserted into the MySQL database

import pandas as pd
import numpy as np

def cleanse_data(fpath, sep = ','):
    df = pd.read_csv(fpath, sep=sep) # load jeopardy dataset to a dataframe
    df = df.replace({np.nan:''}) # replace all null values with blank. This is due to MySQL
    
    # Remove single backslashes, single quotes, double quotes, new lines. 
    # These were causing trouble with the SQL db and are not needed for RAG
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.replace(r'\\', r'', regex=True).str.replace(r"'", r'', regex=True).str.replace(r'"', r'', regex=True) 
            df[col] = df[col].str.replace('\n', '').str.replace('\r', '')
    
    return df
