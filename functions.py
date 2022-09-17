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


#Function for articles data upload to the database
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
  with st.spinner('Avaliando artigos...'):
  
    #Load current database articles
    query = firestore_client.collection("articles_simplified").get()
    data = [doc.to_dict() for doc in query]
    df1 = pd.DataFrame.from_records(data)[['pubmed_id']].astype('int32')

    #Load new articles
    ##To convert to a string based IO:
    stringio = io.StringIO(file.getvalue().decode("utf-8"))

    ##To read file as string:
    string_data = stringio.read()
    
    articles_data = nbib.read(string_data)
    df2 = pd.DataFrame.from_records(articles_data)[['pubmed_id']].astype('int32')

    #Check differences and drop duplicates based on pubmed_id
    df_diff = pd.concat([df1,df2]).drop_duplicates(subset=['pubmed_id'], keep=False, ignore_index=True)

    if len(df_diff) == 0:
      st.warning('Nenhum artigo novo foi encontrado nas referências que você nos enviou. Nossa base de dados continua igual.', icon="🚨")
    
    else:
      #Select only the new articles based on pubmed_id
      new_articles_df = pd.DataFrame.from_records(articles_data)
      new_articles_df['pubmed_id'] = new_articles_df['pubmed_id'].astype('int32')

      articles_indices = new_articles_df.index[new_articles_df["pubmed_id"].isin(df_diff['pubmed_id'])]
      new_articles_df = new_articles_df.iloc[articles_indices,:]

      #Save articles at the database
      upload_articles_data(search_strategy, new_articles_df)
      st.success(f"Deu certo! **{len(new_articles_df)}** novos artigos foram adicionados à base de dados para compor nossa revisão.")


def card(article_data_series):
  all_authors = ""
  for author in article_data_series['authors']:
      all_authors += author['author'] + "; "
  
  
  return f"""
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
  <div class="card">
    <div class="card-body">
      <h5 class="card-title">{article_data_series['title']}</h5>
      <h6 class="card-subtitle mb-2 text-muted">{all_authors}</h6>
      <p class="card-text">{article_data_series['abstract']}</p>
      <a href="https://pubmed.ncbi.nlm.nih.gov/{article_data_series['pubmed_id']}/" class="card-link">Ver no Pubmed</a>
    </div>
  </div>
  """