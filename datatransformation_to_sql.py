# import huspacy
# huspacy.download()
# import hu_core_news_lg
# nlp = hu_core_news_lg.load()
from datetime import datetime
import pandas as pd
import os
from sqlalchemy import create_engine, text as sql_text
import re
from collections import Counter
import numpy as np
from collections import defaultdict
import json


def dataransfromation_sql(message_to_analyize, catalogue, nlp):


  # path="tesztexcel_hangszer.xlsx"
  df = catalogue
  df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
  df.fillna("####", inplace=True)

  stopwords="""a
  abban
  ahhoz
  ahogy
  ahol
  aki
  akik
  akkor
  alatt
  amely
  amelyek
  amelyekben
  amelyeket
  amelyet
  amelynek
  ami
  amikor
  amit
  amolyan
  amíg
  annak
  arra
  arról
  az
  azok
  azon
  azonban
  azt
  aztán
  azután
  azzal
  azért
  be
  belül
  benne
  bár
  cikk
  cikkek
  cikkeket
  csak
  de
  e
  ebben
  eddig
  egy
  egyes
  egyetlen
  egyik
  egyre
  egyéb
  egész
  ehhez
  ekkor
  el
  ellen
  első
  elég
  elő
  először
  előtt
  emilyen
  ennek
  erre
  ez
  ezek
  ezen
  ezt
  ezzel
  ezért
  fel
  felé
  hanem
  hiszen
  hogy
  hogyan
  igen
  ill
  ill.
  illetve
  ilyen
  ilyenkor
  ismét
  ison
  itt
  jobban
  jó
  jól
  kell
  kellett
  keressünk
  keresztül
  ki
  kívül
  között
  közül
  legalább
  legyen
  lehet
  lehetett
  lenne
  lenni
  lesz
  lett
  maga
  magát
  majd
  majd
  meg
  mellett
  mely
  melyek
  mert
  mi
  mikor
  milyen
  minden
  mindenki
  mindent
  mindig
  mint
  mintha
  mit
  mivel
  miért
  most
  már
  más
  másik
  még
  míg
  nagy
  nagyobb
  nagyon
  ne
  nekem
  neki
  nem
  nincs
  néha
  néhány
  nélkül
  olyan
  ott
  pedig
  persze
  rá
  s
  saját
  sem
  semmi
  sok
  sokat
  sokkal
  szemben
  szerint
  szinte
  számára
  talán
  tehát
  teljes
  tovább
  továbbá
  több
  ugyanis
  utolsó
  után
  utána
  vagy
  vagyis
  vagyok
  valaki
  valami
  valamint
  való
  van
  vannak
  vele
  vissza
  viszont
  volna
  volt
  voltak
  voltam
  voltunk
  által
  általában
  át
  én
  éppen
  és
  így
  ő
  ők
  őket
  össze
  úgy
  új
  újabb
  újra"""

  lista=[]
  for index, row in df.iterrows():
    lista.append(row['termék'].strip()) 
    lista.append(row['típus'].strip())
    lista.append(row['gyártó'].strip())
    lista.append(row['márka'].strip())

  # extract all the unique word from the DF dataframe like "guitar, Ibanez, piano etc."
  lista=list(set(lista))
  music_list = [value for value in lista if value == value]  # KEYWORDS (PRODUCTS, TYPES, MANUFACTURES, BRAND NAMES)

  topic_list = []
  cleaned=[]
  temp=[]

  
  # Choose a language


  for k in message_to_analyize.split():
    if k.lower() not in stopwords:
      if k[-1]=='.' or k[-1]=='?' or k[-1]=='!':
        k=k[:-1]
      temp.append(k)
  cleaned.append(" ".join(temp))
  #LEMMATIZATION
  text=[]
  for i in cleaned:
    doc=nlp(i)
    lemmas=[]
    for token in doc:
      lemmas.append(token.lemma_)
    text.append(' '.join(lemmas))

  text=" ".join(text).lower()    # MESSAGE WITHOUT STOPWORDS AND INFLECTIONS
  print("TEXT: ", text)
  list_extraction = []    # CONTAINS THE KEYWORDS FOUND IN EACH MESSAGE


  # REGEX: finding the keywords in the messages

  for i in music_list:
    # Define the pattern using regular expression
    pattern = r"\b" + re.escape(i.lower()) + r"\b"

    # Search for the pattern in the text
    matches = re.findall(pattern, text.lower())

    if matches:
        # Iterate over the matches and add them to the list_extraction
        for match in matches:
            list_extraction.append(match.strip())

  list_extraction=list(set(list_extraction))
  print(list_extraction)

  finalization_list=[]                                       # manufacturer, brand can also be detected
  # finalization_list contains a detected categories in the chat (product, type, manufacturer, brand)
  for p in list_extraction:
    # if any(p in sublist for sublist in finalization_list):
    #   continue
    for index, row in df.iterrows():
      if not pd.isna(row['termék']):
        if p==row['termék'].strip().lower():
          temporary_list=[]
          temporary_list.append([p])
          for i in list_extraction:
            if not pd.isna(row['típus']):
              if i==row['típus'].strip().lower():
                temporary_list.append([row['termék'], row['típus']])
            if not pd.isna(row['gyártó']):
              if i==row['gyártó'].strip().lower() and row['típus'].strip().lower() in list_extraction:
                temporary_list.append([row['termék'], row['típus'], row['gyártó']])
              if i==row['gyártó'].strip().lower() and row['típus'].strip().lower() not in list_extraction:
                temporary_list.append([row['termék'], "típust nem említett", row['gyártó']])
            if not pd.isna(row['márka']):
              if i==row['márka'].strip().lower():
                temporary_list.append([row['termék'], row['típus'], row['gyártó'], row['márka']])
          longest_element = max(temporary_list, key=len)
          finalization_list.append(longest_element)

      if not pd.isna(row['típus']):
        if p==row['típus'].strip().lower():
          temp_list2=[]
          for i in list_extraction:
            if not pd.isna(row['termék']):
              if i==row['termék'].strip().lower():
                temp_list2.append(i)

          if len(temp_list2)==0:
            temporary_list=[]
            temporary_list.append(["terméket nem említett", row['típus']])
            for i in list_extraction:
              if not pd.isna(row['gyártó']):
                if i==row['gyártó'].strip().lower():
                  temporary_list.append(["terméket nem említett", row['típus'], row['gyártó']])
              if not pd.isna(row['márka']):
                if i==row['márka'].strip().lower():
                  temporary_list.append([row['termék'], row['típus'], row['gyártó'], row['márka']])


            longest_element = max(temporary_list, key=len)
            finalization_list.append(longest_element)


      if not pd.isna(row['gyártó']):
        if p==row['gyártó'].strip().lower():
          temp_list3=[]
          for i in list_extraction:
            if not pd.isna(row['termék']):
              if i==row['termék'].strip().lower():
                temp_list3.append(i)
            if not pd.isna(row['típus']):
              if i==row['típus'].strip().lower():
                temp_list3.append(i)
          if len(temp_list3)==0:
            temporary_list=[]
            temporary_list.append([row['gyártó']])
            for i in list_extraction:
              if not pd.isna(row['márka']):
                if i==row['márka'].strip().lower():
                  temporary_list.append([row['termék'], row['típus'], row['gyártó'], row['márka']])
            longest_element = max(temporary_list, key=len)
            finalization_list.append(longest_element)

      if p==row['márka'].strip().lower():
        temp_list4=[]
        for i in list_extraction:
          if not pd.isna(row['termék']):
            if i==row['termék'].strip().lower():
              temp_list4.append(i)
          if not pd.isna(row['típus']):
            if i==row['típus'].strip().lower():
              temp_list4.append(i)
          if not pd.isna(row['gyártó']):
            if i==row['gyártó'].strip().lower():
              temp_list4.append(i)
        if len(temp_list4)==0:
          temporary_list.append([row['termék'], row['típus'], row['gyártó'], row['márka']])
  ###############################################################################################################################
  # IN THE finalization_list WE CAN HAVE MANY REDUNDANT LIST AS WE WERE ITERATING THROUGH THE list_extraction AND DID THE CHECK
  # FOR EACH ELEMENT BELONGING TO THE SAME PRODUCT LINE. SO WE HAVE TO DETECT THEM AND REMOVE THE IDENTICAL LISTS OR ELEMENTS
  ###############################################################################################################################
  #---------------------------------------
  # SMALLER THIRD PART OF THE BOTTLENECK -
  #---------------------------------------
  for sublist in finalization_list:
        # Iterate through each element in the sublist
        for i in range(len(sublist)):
            # Convert each element to lowercase
            sublist[i] = sublist[i].lower()

  def check_elements(a, b):
      for item_a in a:
          found = False
          for item_b in b:
              if item_a in item_b:
                  found = True
                  break
          if not found:
              return False
      return True




  for sublist in finalization_list:
    for sublist2 in finalization_list:
      if len(sublist) == 4 and len(sublist2) == 3 and sublist[0] == sublist2[0] and sublist[2] == sublist2[2]:
        finalization_list = [i for i in finalization_list if i != sublist2]
      if len(sublist) == 4 and len(sublist2) == 2 and sublist[1] == sublist2[1] and sublist2[0] == "terméket nem említett":
        finalization_list = [i for i in finalization_list if i != sublist2]
      if len(sublist) == 4 and len(sublist2) == 3 and sublist[2] == sublist2[2] and sublist2[1] == "típust nem említett":
        finalization_list = [i for i in finalization_list if i != sublist2]
      if len(sublist) == 4 and len(sublist2) == 2 and sublist[0] == sublist2[0]:
        finalization_list = [i for i in finalization_list if i != sublist2]
      if len(sublist) == 3 and len(sublist2) == 3 and sublist!=sublist2 and sublist[0] == sublist2[0] and sublist[2] == sublist2[2] and sublist2[1] == "típust nem említett":
        finalization_list = [i for i in finalization_list if i != sublist2]
      if len(sublist) == 3 and len(sublist2) == 3 and sublist!=sublist2 and sublist[1] == sublist2[1] and sublist[2] == sublist2[2] and sublist2[0] == "terméket nem említett":
        finalization_list = [i for i in finalization_list if i != sublist2]
      if len(sublist) == 3 and len(sublist2) == 2 and sublist[1] == sublist2[1] and sublist2[0] == "terméket nem említett":
        finalization_list = [i for i in finalization_list if i != sublist2]
      if len(sublist) == 2 and len(sublist2) == 2 and sublist!=sublist2 and sublist[1] == sublist2[1] and sublist2[0] == "terméket nem említett":
        finalization_list = [i for i in finalization_list if i != sublist2]







    # Convert each sublist into a tuple
  tuple_list = [tuple(sublist) for sublist in finalization_list]




  # Convert the list of tuples into a set to remove duplicates
  unique_elements_set = set(tuple_list)

  tuple_list = list(unique_elements_set)

  # Initialize a list to store tuples that should be discarded
  to_discard = []

  # Iterate through each tuple
  for i in range(len(tuple_list)):
      # Check if the current tuple is a subset of any other tuple
      for j in range(len(tuple_list)):
          if i != j and all(item in tuple_list[j] for item in tuple_list[i]):
              to_discard.append(tuple_list[i])
              break  # Once a match is found, no need to continue checking

  # Remove the tuples that should be discarded from the original set
  result = unique_elements_set - set(to_discard)


  result = [list(item) for item in result]
  print("Result: ", result)


  has_length_one = any(len(sublist) == 1 for sublist in result)

  if has_length_one:

    checking=[]
    tocheck=[]
    elements_to_delete=[]
    for i in result:
      if len(i)==1:
        checking.append(i)
      else:
        tocheck.append(i)

    index_=[]
    for i in tocheck:
      for p in i:
        for index, row in df.iterrows():
          if p==row['termék'].strip().lower() or p==row['típus'].strip().lower() or p==row['gyártó'].strip().lower() or p==row['márka'].strip().lower():
            index_.append(index)

    element_counts = Counter(index_)
    duplicates = [element for element, count in element_counts.items() if count >1]


    for k in checking:
      a=True
      for i in duplicates:
        if a==True:
          lowercased_arr = np.array([str(item).lower() for item in df.iloc[i].values], dtype=object)
          for i in lowercased_arr:
            if k[0] in i:
              result.remove([k[0]])
              a=False
              break

  # topic_list.append(result)
  
  return str(result)



  # Add the list as a new column named 'topic' to the DataFrame
  # df_pandas['topic'] = topic_list2
  # df_pandas['topic']

