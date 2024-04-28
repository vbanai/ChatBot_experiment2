import os
import re
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv, dotenv_values
import tempfile
from sqlalchemy import create_engine, text as sql_text
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from azure.storage.blob import BlobServiceClient
import numpy as np
import pickle
import openpyxl




#-----------------------------------------------------------------------------------------------
#             READING THE DATA IN NECESSARY FOR THE PROCESS 
#-----------------------------------------------------------------------------------------------



def data_preparation():
    
  if os.getenv("FLASK_ENV") == "development":
    
    load_dotenv()
    # Explicitly load environment variables from .env
    env_vars = dotenv_values(".env")

    # Get the connection string with quotes
    connection_string_with_quotes = env_vars.get("CONNECTION_STRING")

    # Remove the quotes if present
    if connection_string_with_quotes:
        connection_string = connection_string_with_quotes.replace('"', '') 
    #connection_string = os.getenv("CONNECTION_STRING")
    database_url = os.getenv('DATABASE_URL')
    cohere_key=os.getenv('cohere_key')
    
  else:
    # Retrieve the private key from the environment variable
    #private_key_str = os.environ.get('PRIVATE_KEY')
    connection_string = os.environ.get("CONNECTION_STRING")
    database_url = os.environ.get('DATABASE_URL')
    cohere_key=os.environ.get('cohere_key')


  #--------------------------------------------------------
  # Loading the postgres SQL database
  #--------------------------------------------------------

  database_url=database_url.replace('postgres', 'postgresql')
  engine = create_engine(database_url)

  
  sql_query = 'SELECT * FROM "rendeleskicsi_xlsx"'
  df_existing_customer= pd.read_sql(sql_query, engine)
    

  container_name = 'bigfilefolder'

  source_for_theChatBot='tesztexcel_hangszer_65.xlsx'
  blob_service_client = BlobServiceClient.from_connection_string(connection_string)
  blob_client = blob_service_client.get_blob_client(container=container_name, blob=source_for_theChatBot)
  temp_dir = tempfile.gettempdir()
  temp_file_path_textforChatBot = os.path.join(temp_dir, 'tesztexcel_hangszer_65.xlsx')

  with open(temp_file_path_textforChatBot, 'wb') as temp_file:
      blob_data = blob_client.download_blob()
      blob_data.readinto(temp_file)

  df = pd.read_excel(temp_file_path_textforChatBot)
  

  # source_for_theChatBot2='tesztexcel_hangszer_400_800.xlsx'
  # blob_service_client2 = BlobServiceClient.from_connection_string(connection_string)
  # blob_client2 = blob_service_client2.get_blob_client(container=container_name, blob=source_for_theChatBot2)
  # temp_dir = tempfile.gettempdir()
  # temp_file_path_textforChatBot2 = os.path.join(temp_dir, 'tesztexcel_hangszer_400_800.xlsx')

  # with open(temp_file_path_textforChatBot2, 'wb') as temp_file:
  #     blob_data = blob_client2.download_blob()
  #     blob_data.readinto(temp_file)

  # df2 = pd.read_excel(temp_file_path_textforChatBot2)
  



  # source_for_theChatBot3='tesztexcel_hangszer_800_1200.xlsx'
  # blob_service_client3 = BlobServiceClient.from_connection_string(connection_string)
  # blob_client3 = blob_service_client3.get_blob_client(container=container_name, blob=source_for_theChatBot3)
  # temp_dir = tempfile.gettempdir()
  # temp_file_path_textforChatBot3 = os.path.join(temp_dir, 'tesztexcel_hangszer_800_1200.xlsx')

  # with open(temp_file_path_textforChatBot3, 'wb') as temp_file:
  #     blob_data = blob_client3.download_blob()
  #     blob_data.readinto(temp_file)

  # df3 = pd.read_excel(temp_file_path_textforChatBot3)
  



  
  # source_for_theChatBot4='tesztexcel_hangszer_1200_1600.xlsx'
  # blob_service_client4 = BlobServiceClient.from_connection_string(connection_string)
  # blob_client4 = blob_service_client4.get_blob_client(container=container_name, blob=source_for_theChatBot4)
  # temp_dir = tempfile.gettempdir()
  # temp_file_path_textforChatBot4 = os.path.join(temp_dir, 'tesztexcel_hangszer_1200_1600.xlsx')

  # with open(temp_file_path_textforChatBot4, 'wb') as temp_file:
  #   blob_data = blob_client4.download_blob()
  #   blob_data.readinto(temp_file)

  # df4 = pd.read_excel(temp_file_path_textforChatBot4)
  


  
  # source_for_theChatBot5='tesztexcel_hangszer_1600_2000.xlsx'
  # blob_service_client5 = BlobServiceClient.from_connection_string(connection_string)
  # blob_client5 = blob_service_client5.get_blob_client(container=container_name, blob=source_for_theChatBot5)
  # temp_dir = tempfile.gettempdir()
  # temp_file_path_textforChatBot5 = os.path.join(temp_dir, 'tesztexcel_hangszer_1600_2000.xlsx')

  # with open(temp_file_path_textforChatBot5, 'wb') as temp_file:
  #   blob_data = blob_client5.download_blob()
  #   blob_data.readinto(temp_file)

  # df5 = pd.read_excel(temp_file_path_textforChatBot5)
  


  # source_for_theChatBot6='tesztexcel_hangszer_2000_2400.xlsx'
  # blob_service_client6 = BlobServiceClient.from_connection_string(connection_string)
  # blob_client6 = blob_service_client6.get_blob_client(container=container_name, blob=source_for_theChatBot6)
  # temp_dir = tempfile.gettempdir()
  # temp_file_path_textforChatBot6 = os.path.join(temp_dir, 'tesztexcel_hangszer_2000_2400.xlsx')

  # with open(temp_file_path_textforChatBot6, 'wb') as temp_file:
  #   blob_data = blob_client6.download_blob()
  #   blob_data.readinto(temp_file)

  # df6 = pd.read_excel(temp_file_path_textforChatBot6)
  
    
  

  def passage_creation(df):
    passages = []

    # Iterate through DataFrame rows
    for index, row in df.iterrows():
        passage = {
            "id": index + 1,  # Adding 1 to start ids from 1
            "text": f"{row['termék']}   {row['típus']}   {row['gyártó']}   {row['márka']}   {row['készlet állapot']}   {row['ár']}   {row['leírás']}"
        }
        passages.append(passage)
    return passages
  
  passages=passage_creation(df)
  # passages2=passage_creation(df2)
  # passages3=passage_creation(df3)
  # passages4=passage_creation(df4)
  # passages5=passage_creation(df5)
  # passages6=passage_creation(df6)




  # os.remove(temp_file_path_embeddings)
  # os.remove(temp_file_path_Lines)
  # os.remove(temp_file_path_cross_scores)
  os.remove(temp_file_path_textforChatBot)
  # os.remove(temp_file_path_textforChatBot2)
  # os.remove(temp_file_path_textforChatBot3)
  # os.remove(temp_file_path_textforChatBot4)
  # os.remove(temp_file_path_textforChatBot5)
  # os.remove(temp_file_path_textforChatBot6)



  
  return df_existing_customer, passages#, passages2, passages3, passages4, passages5, passages6

