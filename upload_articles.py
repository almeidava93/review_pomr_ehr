#REFERENCES
#Firestore database documentation: https://googleapis.dev/python/firestore/latest/index.html




import streamlit as st
from google.cloud import firestore
import json
import nbib
import pandas as pd
from tqdm import tqdm





database_keys = open("/Users/viniciusanjosdealmeida/review_pomr_ehr/pomr-systematic-review-firebase-adminsdk-g6klq-e4f60f5466.json")
service_account_info = json.load(database_keys)


#Connecting with the firestore database
@st.cache(hash_funcs={firestore.Client: id}, ttl=None, show_spinner=True)
def load_firestore_client(service_account_info = service_account_info):
  firestore_client = firestore.Client.from_service_account_info(service_account_info)
  return firestore_client

firestore_client = load_firestore_client() #Loads cached database connection





filepath = "data/search_results_08.09.2022.nbib"

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
print(articles_df.info())


def upload_articles_data(search_strategy: str, articles_df=articles_df, firestore_client=firestore_client):
  #Collection with articles full data:
  for index, article in tqdm(articles_df.iterrows()):
    doc_ref = firestore_client.collection("articles_full").document(str(article['pubmed_id']))
    doc_ref.set({column_name : str(data) for column_name, data in article.iteritems()})

  #Collection with articles simplified data:
  for index, article in tqdm(articles_df[['pubmed_id', 'title', 'abstract']].iterrows()):
    doc_ref = firestore_client.collection("articles_simplified").document(str(article['pubmed_id']))
    doc_ref.set({column_name : str(data) for column_name, data in article.iteritems()})

  #Saving related search strategy:
  query = firestore_client.collection("search_strategies").get()
  doc_ref = firestore_client.collection("search_strategies").document(f"search_strategy_{len(query)+1}")
  doc_ref.set({"search_strategy": search_strategy})

search_strategy = '("problem-oriented medical record" OR "problem-oriented record" OR "problem-oriented patient record" OR "episode of care" OR "problems list" OR "problem-oriented" OR "SOAP" OR "APSO") AND ("electronic patient record" OR "EPR" OR "electronic health record" OR "electronic health records" OR "EHR" OR "electronic medical record" OR "electronic medical records" OR "EMR" OR "electronic records" OR "electronic patient record" OR "electronic patient records")'
upload_articles_data(search_strategy)