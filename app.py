#jtc guitar

from flask import Flask, render_template, request, session, jsonify
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from ChatGPTpart import get_completion_from_messages, extract_client_number, retrieve_client_details #, translation, spacy_context, adjust_query
from ElephantSQL import upload_to_ElephantSQL
from psycopg2 import sql
#from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
import xml.etree.ElementTree as ET
from azure.storage.blob import BlobServiceClient
from readdatain import data_preparation
from sqlalchemy.dialects.postgresql import ARRAY
import logging
from flashrank import Ranker
import time
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from datatransformation_to_sql import dataransfromation_sql
import huspacy
import hu_core_news_lg
import psycopg2

load_dotenv()
# Download HU models if not already downloaded
huspacy.download()

# Load HU language model
nlp = hu_core_news_lg.load()

log_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs/')
os.makedirs(log_directory, exist_ok=True)
logging.basicConfig(filename=os.path.join(log_directory, 'app.log'), level=logging.INFO)




def flask_app(host=None, port=None):

  app=Flask(__name__)
 
  # database_url = os.environ.get('DATABASE_URL')
  # database_url=database_url.replace('postgres', 'postgresql')
  # app.config['SQLALCHEMY_DATABASE_URI']=database_url
  # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  # db = SQLAlchemy()
  

  # class UserChatHistory(db.Model):
  #   __tablename__="chat_messages"
  #   id = db.Column(db.Integer, primary_key=True)
  #   created_at = db.Column(db.DateTime, default=datetime.utcnow)
  #   user_id = db.Column(db.String(50))
  #   message = db.Column(db.Text)
  #   topic = db.Column(db.Text)
    

  #   def __init__(self, user_id, message, topic=None):
  #       self.user_id = user_id
  #       self.message = message
  #       self.topic = topic
        

  # db.init_app(app)
  host = os.environ.get("HOST_")
  dbname = 'ChatProject'
  user = os.environ.get("username")
  password = os.environ.get("password")
  sslmode = "require"

  # Construct connection string
  conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)

  # Connect to the Azure PostgreSQL database
  conn = psycopg2.connect(conn_string) 
  print("Connection established")
  cursor = conn.cursor()

  # Specify the table name
  table_name = 'chat_messages_r55'


  def generate_user_id():
    ip_address = request.remote_addr
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = f"{ip_address}_{timestamp}"
    return ip_address

  app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))
  ranker = Ranker()
  class RerankRequest:

    def __init__(self, query=None, passages=None):
        self.query = query
        self.passages = passages if passages is not None else []

  # bi_encoder = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
  # cross_encoder = CrossEncoder('nreimers/mmarco-mMiniLMv2-L12-H384-v1')
  textvariable=""
  
#-----------------------------------------------------------------------------------------------
#             Important variables
#-----------------------------------------------------------------------------------------------

  
  df_existing_customer, passages, catalogue=data_preparation()

  client_details_placeholder = "placeholder for client details"
  extracted_relevant_paragraphs = "placeholder for extracted paragraph"
  chat_history_for_contextcreator = []
  
  
  context = [
  
  {'role': 'system', 'content': f"""You are a sales assistant for question-answering tasks in a music store. You speak in Hungarian \
      In case of techincal and general question about a music porduct you can use external sources.\
      In case you got question regarding the availability of a product in the shop, prices, general questions like opening hours, transportation \
      relating to the shop don't use external source, please retrive infromation from this document: \n{extracted_relevant_paragraphs}\n\n. Here you can find sublists in a list. \
      Each sublist represents a product item sold by the store or a topic related to the store. First item of the sublist 'termék' shows the type of the product. For example don't consider 'álvány', 'capo', 'pánt', 'erősítő' as a guitar!\
      Second item 'típus' details the subtype of the product, third item 'márka' the brand name etc. \
      For exampe: if the user asks something like this: 'what kind of guitars are on stock?' you have to find those 'termék' items which are 'gitár' in the sublists. If you got a question about Conn AS-501-xx-2 saxophone, first check the sublists which contains this expression Conn AS-501-xx-2 and saxophone, and then answer the question. \
      Share all information found regarding 'ár', 'készlet állapot / kapható-e', 'leírás' you can find in the sublist.
      If you find nan regarding 'típus' , 'gyártó', 'készlet állapot / kapható-e', 'ár' it means that the query is a general topic relating to store like opening hours, transportation etc. Retrieve the information in the 'leírás'.
  
      Note: if you got question about a broader product category(gitar, piano, violin etc.) what  types are on stock like  " What guitars are available on stock?" In the first sentence of your response say something like this in Hungarian: on this platform I can't list all the items available, but I can give some insight,
      but if you find row where you can see information in the 'termék' and 'leírás' columns only, it means the line item is not about a product but a general topic about the store, so you don't need to say  "on this platform I can't list all the items available but I can give some insight. "
      Answer in 6 sentences maximum retrieving all the information you can find in the sublists and keep the answer concise. \
      
      Guitar Brands the shop sells: Ibanez, Gibson, Ovation, Fernandez, Yamaha, Stagg, Raimundo, Alhambra, Fender
      Pianos the shop sells: Yamaha, Bösendorfer, Stenway and sons.
   
      If the user has a question regarding the ongoing order, ask for the identifier number in Hungarian langauge.\        
      User: Can you give me the identifier number? Assistant: Please provide your identifier number.\
      If the identifier number is provided, answer the user question according to the retrieved document: \n{client_details_placeholder}\n\n.\
      If you can find any details, inform the user accordingly.\
    

      If the user asks a question outside music business, you can politely reject it with a response  like:\
      User: What's biology? Assistant: Ebben a témában sajnos nem tudok segíteni.  
    
      Your response should be in one installment, not multiple parts, in Hungarian language. Always ask if you can help with anything else.


  
  """}
  ]
#-----------------------------------------------------------------------------------------------
#             Flask ROUTING
#-----------------------------------------------------------------------------------------------


  # @app.route("/")
  # @app.route('/home')
  # def index():
  #   return render_template('index.html')
  
  @app.route("/clear_session", methods=["GET"])
  def clear_session():
    session.clear()
    session['textvariable'] = ""
    session['client_details_placeholder'] = "placeholder for client details"
    session['extracted_relevant_paragraphs'] = "placeholder for extracted paragraph"
    session['chat_history_for_contextcreator'] = []
    
    return "Session cleared!"

  
  @app.route("/")
  def messengerchat():
    
    if 'textvariable' not in session: 
      session['textvariable'] = ""
    if session['textvariable']!="":
      #output_file_creation(df_existing_customer_tracking, df_potential_customer, session['textvariable'])
      session['textvariable']=""
    session.clear()
    session['client_details_placeholder'] = "placeholder for client details"
    session['extracted_relevant_paragraphs'] = "placeholder for extracted paragraph"
    session['chat_history_for_contextcreator'] = []
    return render_template('messengerchat.html')

  @app.route("/chat")
  def AIChatBot():
    return render_template('chat.html')
 
  @app.route("/get", methods=["GET", "POST"])
  def chat():
    if 'textvariable' not in session:
        session['textvariable'] = ""
    if 'client_details_placeholder' not in session:
        session['client_details_placeholder'] = "placeholder for client details"
    if 'extracted_relevant_paragraphs' not in session:
        session['extracted_relevant_paragraphs'] = "placeholder for extracted paragraph"
    if 'chat_history_for_contextcreator' not in session:
        session['chat_history_for_contextcreator'] = []


    msg=request.form["msg"]
    input=msg
    client_number=extract_client_number(input)
    if client_number:
      context.append({'role':'user', 'content':f"{input}"})
      df_existing_customer_row=retrieve_client_details(client_number, df_existing_customer)
      context[0]['content'] = context[0]['content'].replace(session['client_details_placeholder'], str(df_existing_customer_row))
      session['client_details_placeholder']=df_existing_customer_row
      print(context[0]['content'])
      response=get_completion_from_messages(context)
      #session['textvariable']+=("USER: " + input + " | " + "ASSISTANT: " + response)
      user_id = generate_user_id()
      new_user_message ="USER: " + input + " | " + "ASSISTANT: " + response
      created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      topic=[]
      insert_query = f"INSERT INTO {table_name} (created_at, user_id, message, topic) VALUES (%s, %s, %s, %s);"
      # Execute the SQL query
      cursor.execute(insert_query, (created_at, user_id, new_user_message, topic))
      conn.commit()
      # db.session.add(new_user_message)
      # db.session.commit()
      context.append({'role':'assistant', 'content':f"{response}"})
      return response
    else:
      
      context.append({'role':'user', 'content':f"{input}"})
      start_time = time.time()
      rerankrequest = RerankRequest(query=input, passages=passages)
      # rerankrequest2 = RerankRequest(query=input, passages=passages2)
      # rerankrequest3 = RerankRequest(query=input, passages=passages3)
      # rerankrequest4 = RerankRequest(query=input, passages=passages4)
      # rerankrequest5 = RerankRequest(query=input, passages=passages5)
      # rerankrequest6 = RerankRequest(query=input, passages=passages6)
      
      #extracted_paragraphs='\n'.join(data['text'] for data in ranker.rerank(rerankrequest)[:20])
      extracted_paragraphs= []

      def extracted_para_creation(rerankrequest):
        extracted_paragraphs00=ranker.rerank(rerankrequest)[:3]
        extracted_paragraphs01 = pd.DataFrame([d['text'].split('   ') for d in extracted_paragraphs00], columns=['termék', 'típus', 'gyártó', 'márka', 'készlet állapot', 'ár', 'leírás'])
        for index, row in extracted_paragraphs01.iterrows():
          sentence = f"termék: {row['termék']}, típus: {row['típus']}, 'gyártó':{row['gyártó']}, márka: {row['márka']}, készlet állapot / kapható-e: {row['készlet állapot']}, ár: {row['ár']} Ft, leírás: {row['leírás'][:150]}"
          extracted_paragraphs.append([sentence])

      extracted_para_creation(rerankrequest)
      # extracted_para_creation(rerankrequest2)
      # extracted_para_creation(rerankrequest3)
      # extracted_para_creation(rerankrequest4)
      # extracted_para_creation(rerankrequest5)
      # extracted_para_creation(rerankrequest6)


      end_time = time.time()
      elapsed_time = end_time - start_time
      context[0]['content'] = context[0]['content'].replace(session['extracted_relevant_paragraphs'], str(extracted_paragraphs))
      session['extracted_relevant_paragraphs'] = str(extracted_paragraphs)
      logging.debug("EXTRACTED PARAGRAPH: ")
      logging.debug(extracted_paragraphs)
      logging.debug(session['extracted_relevant_paragraphs'])
      logging.debug("CONTEXT")
      logging.debug(context)
      response=get_completion_from_messages(context)
      session['chat_history_for_contextcreator']=response
      logging.debug("RESPONSE: ")
      logging.debug(response)
      logging.debug(session['chat_history_for_contextcreator'])
      #session['textvariable']+=("USER: " + input + " | " + "ASSISTANT: " + response)
      topic_to_load=dataransfromation_sql("USER: " + input + " | " + "ASSISTANT: " + response, catalogue, nlp)
      user_id = generate_user_id()
      created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      new_user_message = "USER: " + input + " | " + "ASSISTANT: " + response
      # Execute the SQL query
      insert_query = f"INSERT INTO {table_name} (created_at, user_id, message, topic) VALUES (%s, %s, %s, %s);"
      cursor.execute(insert_query, (created_at, user_id, new_user_message, topic_to_load))

      # Commit the transaction
      conn.commit()

      context.append({'role':'assistant', 'content':f"{response}"})

      #LangChain
      # message_fromMainChatbot = [HumanMessage(content=input), AIMessage(content=response)]
      # session['chat_history_for_contextcreator']=json.dumps([message.__dict__ for message in message_fromMainChatbot])
      # print(session['chat_history_for_contextcreator'])

      return response
    
    
      


  
  return app

