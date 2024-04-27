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



  sql_query2 = 'SELECT * FROM "questions_potentialcustomers"'
  df_potential_customer = pd.read_sql(sql_query2, engine)
  sql_query = 'SELECT * FROM "orders_instrument_hu_tracking"'
  df_existing_customer_tracking = pd.read_sql(sql_query, engine)
    
  sql_query_orders = sql_text('SELECT * FROM "orders_instrument_hu"')
  with engine.connect() as connection:
      # Execute the SQL query
      #sql_query_orders = 'SELECT * FROM "orders"'
      result = connection.execute(sql_query_orders)

      # Fetch all rows
      rows = result.fetchall()
      

  # # Extract column names
  columns = result.keys()
  df_existing_customer = pd.DataFrame(rows, columns=columns)

  # # Format data as a string
  # data_rows = []
  # for row in rows:
  #     data_rows.append(" | ".join(map(str, row)))

  # # Create the final string
  # df_existing_customer = " | ".join(columns) + "\n" + "\n".join(data_rows)

  #----------------------------------------------------------------
  # Creating the text file from dowloaded blob (now I won't use it)
  #----------------------------------------------------------------

  # container_name = 'filefolder'
  # filename='Cars_services.docx'

  # blob_service_client = BlobServiceClient.from_connection_string(connection_string)

  # blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)
  # blob_content = blob_client.download_blob().readall()

  # # Assuming blob_content contains the binary data of the Word file
  # word_content = blob_content

  # # Create a temporary file to save the Word content
  # temp_dir = tempfile.gettempdir()
  # temp_file_path = os.path.join(temp_dir, 'temp_word_file.docx')

  # with open(temp_file_path, 'wb') as temp_file:
  #     temp_file.write(word_content)

  # # Open the Word file as a ZIP archive
  # with zipfile.ZipFile(temp_file_path, 'r') as zip_file:
  #     # Extract the content of 'word/document.xml'
  #     xml_content = zip_file.read('word/document.xml')

  # # Parse the XML content
  # xml_root = ET.fromstring(xml_content)

  # # Extract text content from paragraphs
  # text_content = []
  # for paragraph in xml_root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
  #     text_blob = ''.join(run.text for run in paragraph.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
  #     text_content.append(text_blob)

  # # Print the extracted text content
  # word_text='\n'.join(text_content)

  # # Optionally, remove the temporary file after processing
  # os.remove(temp_file_path)

  #----------------------------------------------------------------
  # Download the embeddings and Chunk file to speed up the process
  #----------------------------------------------------------------

  
  # embeddings_all_blob='output_embeddings_hangszer_hu.npy'
  # Lines_blob='my_list_hangszer_hu.pkl'
  # cross_scores_blob='cross_scores.pkl'
  #source_for_theChatBot='set_entire_text_chatbot_withoutpaginationandSP_short.txt'
  
  # blob_client_embeddings = blob_service_client.get_blob_client(container=container_name, blob=embeddings_all_blob)
  # blob_client_Lines = blob_service_client.get_blob_client(container=container_name, blob=Lines_blob)
  # blob_client_cross_scores=blob_service_client.get_blob_client(container=container_name, blob=cross_scores_blob)

  # blob_content_embeddings = blob_client_embeddings.download_blob().readall()
  # blob_content_Lines = blob_client_Lines.download_blob().readall()
  # blob_content_cross_scores=blob_client_cross_scores.download_blob().readall()

  # text_for_theChatBot = blob_service_client.get_blob_client(container=container_name, blob=source_for_theChatBot)
  # text_for_theChatBot = text_for_theChatBot.download_blob().readall()


      
  # Assuming blob_content contains the binary data of the Word file
  # embeddings_all01 = blob_content_embeddings
  # Lines01=blob_content_Lines
  # cross_scores01=blob_content_cross_scores

  # Create a temporary file to save the Word content
  
  # temp_file_path_embeddings = os.path.join(temp_dir, 'output_embeddings.npy')
  # temp_file_path_Lines = os.path.join(temp_dir, 'my_list.pkl')
  # temp_file_path_cross_scores = os.path.join(temp_dir, 'cross_scores.pkl')
  

  # with open(temp_file_path_embeddings, 'wb') as temp_file:
  #     temp_file.write(embeddings_all01)

  # with open(temp_file_path_Lines, 'wb') as temp_file:
  #     temp_file.write(Lines01)

  # with open(temp_file_path_Lines, 'wb') as temp_file:
  #   temp_file.write(cross_scores01)

  # embeddings_all = np.load(temp_file_path_embeddings)

  # with open(temp_file_path_Lines, 'rb') as file:
  #     Lines = pickle.load(file)

  # with open(temp_file_path_cross_scores, 'rb') as file:
  #     cross_scores = pickle.load(file)

  #-----------------------------------------
  # with open(temp_file_path_textforChatBot, 'wb') as temp_file:
  #   temp_file.write(text_for_theChatBot)

  # with open(temp_file_path_textforChatBot, 'r', encoding='utf-8', errors='replace') as file:
  #   file_content = file.read()

  # set_entire_text_chatbot_withoutpaginationandSP_short.txt hez

  # passages=[]

  # rawtext=file_content.split("\n\n")

  # rawtext = [element for element in rawtext if element !='']
  # #rawtext=re.split(r'\n\s*\n', file_content)
  # for index, text in enumerate(rawtext):
  #   passages.append({"id":index+1, "text": text})





  # def get_chunks(fulltext:str,chunk_length =800) -> list:
  #   text = fulltext

  #   chunks = []
  #   while len(text) > chunk_length:
  #     last_period_index = text[:chunk_length].rfind('.')
  #     if last_period_index == -1:
  #         last_period_index = chunk_length
  #     chunks.append(text[:last_period_index])
  #     text = text[last_period_index+1:]
    
  #   chunks.append(text)

  #   return chunks

  # # List to store ids to delete
  # ids_to_delete = []
  # new_list_tobeprocessed=[]

  # for i in range(len(passages)):
  #     if len(passages[i]['text']) > 150:
  #         ids_to_delete.append(passages[i]['id'])
  #         new_list_tobeprocessed.append(passages[i])

  # passages = [passage for passage in passages if passage["id"] not in ids_to_delete]
  # passages_=[]
  # for index, text in enumerate(passages):
  #   passages_.append({"id":index+1, "text":text["text"]})

  # passages=passages_


  # for i in range(len(new_list_tobeprocessed)):
  #   first_row=(new_list_tobeprocessed[i]['text'][:40])
  #   chunks=get_chunks(new_list_tobeprocessed[i]['text'], 150)
  #   for index, text in enumerate(chunks):
  #     if index==0:                   
  #       passages.append({"id":index+1+len(passages), "text": text})
  #     else:                          
  #       passages.append({"id":1+len(passages), "text": first_row+" | " +text})

  #-----------------------------------------

  container_name = 'bigfilefolder'

  source_for_theChatBot='tesztexcel_hangszer_400.xlsx'
  blob_service_client = BlobServiceClient.from_connection_string(connection_string)
  blob_client = blob_service_client.get_blob_client(container=container_name, blob=source_for_theChatBot)
  temp_dir = tempfile.gettempdir()
  temp_file_path_textforChatBot = os.path.join(temp_dir, 'tesztexcel_hangszer_400.xlsx')

  with open(temp_file_path_textforChatBot, 'wb') as temp_file:
      blob_data = blob_client.download_blob()
      blob_data.readinto(temp_file)

  df = pd.read_excel(temp_file_path_textforChatBot)
  

  source_for_theChatBot2='tesztexcel_hangszer_400_800.xlsx'
  blob_service_client2 = BlobServiceClient.from_connection_string(connection_string)
  blob_client2 = blob_service_client2.get_blob_client(container=container_name, blob=source_for_theChatBot2)
  temp_dir = tempfile.gettempdir()
  temp_file_path_textforChatBot2 = os.path.join(temp_dir, 'tesztexcel_hangszer_400_800.xlsx')

  with open(temp_file_path_textforChatBot2, 'wb') as temp_file:
      blob_data = blob_client2.download_blob()
      blob_data.readinto(temp_file)

  df2 = pd.read_excel(temp_file_path_textforChatBot2)
  



  source_for_theChatBot3='tesztexcel_hangszer_800_1200.xlsx'
  blob_service_client3 = BlobServiceClient.from_connection_string(connection_string)
  blob_client3 = blob_service_client3.get_blob_client(container=container_name, blob=source_for_theChatBot3)
  temp_dir = tempfile.gettempdir()
  temp_file_path_textforChatBot3 = os.path.join(temp_dir, 'tesztexcel_hangszer_800_1200.xlsx')

  with open(temp_file_path_textforChatBot3, 'wb') as temp_file:
      blob_data = blob_client3.download_blob()
      blob_data.readinto(temp_file)

  df3 = pd.read_excel(temp_file_path_textforChatBot3)
  



  
  source_for_theChatBot4='tesztexcel_hangszer_1200_1600.xlsx'
  blob_service_client4 = BlobServiceClient.from_connection_string(connection_string)
  blob_client4 = blob_service_client4.get_blob_client(container=container_name, blob=source_for_theChatBot4)
  temp_dir = tempfile.gettempdir()
  temp_file_path_textforChatBot4 = os.path.join(temp_dir, 'tesztexcel_hangszer_1200_1600.xlsx')

  with open(temp_file_path_textforChatBot4, 'wb') as temp_file:
    blob_data = blob_client4.download_blob()
    blob_data.readinto(temp_file)

  df4 = pd.read_excel(temp_file_path_textforChatBot4)
  


  
  source_for_theChatBot5='tesztexcel_hangszer_1600_2000.xlsx'
  blob_service_client5 = BlobServiceClient.from_connection_string(connection_string)
  blob_client5 = blob_service_client5.get_blob_client(container=container_name, blob=source_for_theChatBot5)
  temp_dir = tempfile.gettempdir()
  temp_file_path_textforChatBot5 = os.path.join(temp_dir, 'tesztexcel_hangszer_1600_2000.xlsx')

  with open(temp_file_path_textforChatBot5, 'wb') as temp_file:
    blob_data = blob_client5.download_blob()
    blob_data.readinto(temp_file)

  df5 = pd.read_excel(temp_file_path_textforChatBot5)
  


  source_for_theChatBot6='tesztexcel_hangszer_2000_2400.xlsx'
  blob_service_client6 = BlobServiceClient.from_connection_string(connection_string)
  blob_client6 = blob_service_client6.get_blob_client(container=container_name, blob=source_for_theChatBot6)
  temp_dir = tempfile.gettempdir()
  temp_file_path_textforChatBot6 = os.path.join(temp_dir, 'tesztexcel_hangszer_2000_2400.xlsx')

  with open(temp_file_path_textforChatBot6, 'wb') as temp_file:
    blob_data = blob_client6.download_blob()
    blob_data.readinto(temp_file)

  df6 = pd.read_excel(temp_file_path_textforChatBot6)
  
    
  

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
  passages2=passage_creation(df2)
  passages3=passage_creation(df3)
  passages4=passage_creation(df4)
  passages5=passage_creation(df5)
  passages6=passage_creation(df6)




  # os.remove(temp_file_path_embeddings)
  # os.remove(temp_file_path_Lines)
  # os.remove(temp_file_path_cross_scores)
  os.remove(temp_file_path_textforChatBot)
  os.remove(temp_file_path_textforChatBot2)
  os.remove(temp_file_path_textforChatBot3)
  os.remove(temp_file_path_textforChatBot4)
  os.remove(temp_file_path_textforChatBot5)
  os.remove(temp_file_path_textforChatBot6)



  
  return df_existing_customer_tracking, df_existing_customer, df_potential_customer, passages, passages2, passages3, passages4, passages5, passages6

