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


  #--------------------------------------------------------
  # Loading the postgres SQL database
  #--------------------------------------------------------

  # database_url=database_url.replace('postgres', 'postgresql')
  # engine = create_engine(database_url)

  
  # sql_query = 'SELECT * FROM "rendeleskicsi_xlsx"'
  # df_existing_customer= pd.read_sql(sql_query, engine)
    

  container_name = 'bigfilefolder'

  #-----------------------
  # Word file reading in
  #-----------------------
  
  source_for_theChatBot_word='r55ertelmezoword.docx'
  blob_service_client_word = BlobServiceClient.from_connection_string(connection_string)
  blob_client_word = blob_service_client_word.get_blob_client(container=container_name, blob=source_for_theChatBot_word)
  blob_content = blob_client_word.download_blob().readall()
  word_content = blob_content
  temp_dir = tempfile.gettempdir()
  temp_file_path_textforChatBot_word = os.path.join(temp_dir, 'r55ertelmezoword.docx')
  with open(temp_file_path_textforChatBot_word, 'wb') as temp_file:
    temp_file.write(word_content)
  
  # Open the Word file as a ZIP archive
  with zipfile.ZipFile(temp_file_path_textforChatBot_word, 'r') as zip_file:
    # Extract the content of 'word/document.xml'
    xml_content = zip_file.read('word/document.xml')
  
  # Parse the XML content
  xml_root = ET.fromstring(xml_content)

  # Extract text content from paragraphs
  text_content = []
  for paragraph in xml_root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
      text_blob = ''.join(run.text for run in paragraph.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
      text_content.append(text_blob)

  # Print the extracted text content
  word_text='\n'.join(text_content)

  # Optionally, remove the temporary file after processing
  os.remove(temp_file_path_textforChatBot_word)





  #-----------------------
  # Excel file reading in
  #-----------------------

  source_for_theChatBot_order='rendeles_kicsi.xlsx'
  blob_service_client_order = BlobServiceClient.from_connection_string(connection_string)
  blob_client_order = blob_service_client_order.get_blob_client(container=container_name, blob=source_for_theChatBot_order)
  temp_dir = tempfile.gettempdir()
  temp_file_path_textforChatBot_order = os.path.join(temp_dir, 'rendeles_kicsi.xlsx')

  with open(temp_file_path_textforChatBot_order, 'wb') as temp_file:
      blob_data = blob_client_order.download_blob()
      blob_data.readinto(temp_file)

  df_existing_customer = pd.read_excel(temp_file_path_textforChatBot_order)



  source_for_theChatBot='tesztexcel_hangszer_150.xlsx'
  blob_service_client = BlobServiceClient.from_connection_string(connection_string)
  blob_client = blob_service_client.get_blob_client(container=container_name, blob=source_for_theChatBot)
  temp_dir = tempfile.gettempdir()
  temp_file_path_textforChatBot = os.path.join(temp_dir, 'tesztexcel_hangszer_150.xlsx')

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

  def divide_text_into_passages(document_text, chunk_length=400):
    passages = []
    passage_id = 1
    for p in document_text.split("\n\n"):
      sentences = p.split('.')
      current_chunk = ""
      

      for i, sentence in enumerate(sentences):
          # Trim leading and trailing whitespace
          sentence = sentence.strip()
          
          # If the sentence is not empty, add a period at the end
          if sentence:
              sentence += '.'
          
          # Check if adding the next sentence exceeds the chunk length
          if len(current_chunk) + len(sentence) > chunk_length:
              # Add the current chunk to passages
              passages.append({
                  "id": passage_id,
                  "text": current_chunk.strip()
              })
              passage_id += 1
              # Start a new chunk with the current sentence
              current_chunk = sentence
          else:
              # Add the sentence to the current chunk
              current_chunk += " " + sentence if current_chunk else sentence

      # Add the last chunk if it's not empty
      if current_chunk.strip():
          passages.append({
              "id": passage_id,
              "text": current_chunk.strip()
          })
          passage_id += 1

    return passages

  passages_word_text=divide_text_into_passages(word_text)
 
  # os.remove(temp_file_path_embeddings)
  # os.remove(temp_file_path_Lines)
  # os.remove(temp_file_path_cross_scores)
  os.remove(temp_file_path_textforChatBot)
  os.remove(temp_file_path_textforChatBot_order)
  # os.remove(temp_file_path_textforChatBot2)
  # os.remove(temp_file_path_textforChatBot3)
  # os.remove(temp_file_path_textforChatBot4)
  # os.remove(temp_file_path_textforChatBot5)
  # os.remove(temp_file_path_textforChatBot6)


  
  
  return df_existing_customer, passages, df, passages_word_text#, passages2, passages3, passages4, passages5, passages6




