import os
import pandas as pd
import os
from openai import OpenAI
import json

import pandas as pd
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
import re

from openai import OpenAI
import re

load_dotenv()


import itertools

api_key = os.getenv("OPENAI_API_KEY")
api_key=str(api_key)
client = OpenAI(api_key=api_key)

api_key_translator = os.getenv("Azure_translator_key")
api_key_DeepL=os.getenv("api_key_deepL")


def get_completion_from_messages(messages, model="gpt-4o-mini", temperature=0):   #  gpt-3.5-turbo
  response = client.chat.completions.create(model=model,
  messages=messages,
  temperature=temperature)
  return response.choices[0].message.content


def get_Chat_response(context):
  response=get_completion_from_messages(context) 
  #context.append({'role':'assistant', 'content':f"{response}"})
  return response


def get_completion(prompt, model="gpt-4o-mini",temperature=0): 
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(model=model,
    messages=messages,
    temperature=temperature)
    return response.choices[0].message.content

    


def extract_client_number(user_input):
    # Using a regular expression to extract a client number from the user input
    match = re.search(r'\b\d{6}\b', user_input)
    if match:
      return match.group()
    else:
      return None
    
def retrieve_client_details(client_number, df_existing_customer_BIG):
  # Assuming df_existing_customer is a pandas DataFrame
  client_row = df_existing_customer_BIG[df_existing_customer_BIG['Azonosító szám'].astype(str).str.strip() == str(client_number).strip()]
  return client_row.to_string(index=False)
















