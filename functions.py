#REFERENCES
#Firestore database documentation: https://googleapis.dev/python/firestore/latest/index.html


import string
import streamlit as st
import streamlit.components.v1 as components
from streamlit_javascript import st_javascript

from google.cloud import firestore
import json
import nbib
import pandas as pd
from tqdm import tqdm
import io


database_keys = open("pomr-systematic-review-firebase-adminsdk-g6klq-e4f60f5466.json")
service_account_info = json.load(database_keys)


#Connecting with the firestore database
@st.cache(hash_funcs={firestore.Client: id}, ttl=None, show_spinner=True)
def load_firestore_client(service_account_info = service_account_info):
  firestore_client = firestore.Client.from_service_account_info(service_account_info)
  return firestore_client

firestore_client = load_firestore_client() #Loads cached database connection

def nbib_to_dataframe(filepath):
    articles_data = nbib.read_file(filepath)
    # articles_data is a list of dictionaries with articles data
    # those dictionaries keys can include the following: 
        # {'grants', 'journal_abbreviated', 'authors', 'publication_status', 'pubmed_id', 
        #  'descriptors', 'electronic_issn', 'place_of_publication', 'print_issn', 'linking_issn', 
        #  'publication_date', 'corporate_author', 'pii', 'transliterated_title', 'abstract', 
        #  'nlm_journal_id', 'pubmed_time', 'accepted_time', 'journal_issue', 'pages', 'medline_time',
        #  'entrez_time', 'doi', 'pmcid', 'citation_owner', 'conflict_of_interest', 'journal', 
        #  'keywords', 'nlm_status', 'title', 'copyright', 'revised_time', 'received_time', 'journal_volume', 
        #  'language', 'electronic_publication_date', 'last_revision_date', 'publication_types'}
    articles_df = pd.DataFrame.from_records(articles_data) 
    return articles_df

reviewers = [
  "almeida.va93@gmail.com",
  "henrique.t.arai@gmail.com",
  "mariela204@gmail.com"
]

def set_reviewers_data():
  reviewers = [
    "almeida.va93@gmail.com",
    "henrique.t.arai@gmail.com",
    "mariela204@gmail.com"
  ]
  for reviewer in reviewers:
    doc_ref = firestore_client.collection("reviewers").document(reviewer)
    doc_ref.set({"email": reviewer})

def upload_articles_data(search_strategy: str, articles_df: pd.DataFrame, firestore_client=firestore_client):
  #Collection with articles full data:
  for index, article in tqdm(articles_df.iterrows()):
    doc_ref = firestore_client.collection("articles_full").document(str(article['pubmed_id']))
    doc_ref.set({column_name : str(data) for column_name, data in article.iteritems()})

  #Collection with articles simplified data:
  for index, article in tqdm(articles_df[['pubmed_id', 'title', 'abstract']].iterrows()):
    doc_ref = firestore_client.collection("articles_simplified").document(str(article['pubmed_id']))
    doc_ref.set({column_name : str(data) for column_name, data in article.iteritems()})

  #Collection for first articles review data:
  for reviewer in reviewers:
    for index, article in tqdm(articles_df[['pubmed_id']].iterrows()):
      doc_ref = firestore_client.collection("articles_first_review").document(reviewer).collection("articles").document(str(article['pubmed_id']))
      doc_ref.set({column_name : str(data) for column_name, data in article.iteritems()})
      doc_ref.update({"included": False, "excluded": False})

  #Saving related search strategy:
  query = firestore_client.collection("search_strategies").get()
  doc_ref = firestore_client.collection("search_strategies").document(f"search_strategy_{len(query)+1}")
  doc_ref.set({"search_strategy": search_strategy})


def add_new_articles(file, search_strategy):
    #Load current database articles
    query = firestore_client.collection("articles_simplified").get()
    data = [doc.to_dict() for doc in query]
    df1 = pd.DataFrame.from_records(data)

    #Load new articles
    ##To convert to a string based IO:
    stringio = io.StringIO(file.getvalue().decode("utf-8"))
    st.write(stringio)

    ##To read file as string:
    string_data = stringio.read()
    
    articles_data = nbib.read(string_data)
    df2 = pd.DataFrame.from_records(articles_data)  

    #Check differences and drop duplicates based on pubmed_id
    df_diff = pd.concat([df1[['pubmed_id']],df2[['pubmed_id']]])
    df_diff = df_diff.drop_duplicates(subset='pubmed_id', keep=False)
    st.write(f"df_diff: {len(df_diff)}; df1: {len(df1)}; df2: {len(df2)}")


    #Save articles at the database


    pass
