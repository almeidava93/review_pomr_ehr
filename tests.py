import streamlit as st
import pandas as pd
import nbib
import json
from google.cloud import firestore


import functions

database_keys = open("pomr-systematic-review-firebase-adminsdk-g6klq-e4f60f5466.json")
service_account_info = json.load(database_keys)
reviewers = [
  "almeida.va93@gmail.com",
  "henrique.t.arai@gmail.com",
  "mariela204@gmail.com"
]


#Connecting with the firestore database
@st.cache(hash_funcs={firestore.Client: id}, ttl=None, show_spinner=True)
def load_firestore_client(service_account_info = service_account_info):
  firestore_client = firestore.Client.from_service_account_info(service_account_info)
  return firestore_client

firestore_client = load_firestore_client() #Loads cached database connection


def get_dashboard_data(user=st.experimental_user.email):
  query = firestore_client.collection("articles_first_review").document(user).collection("articles").get()
  filtered_collection_dict = [doc.to_dict() for doc in query] #Returns list of dictionaries 
  filtered_collection_dataframe = pd.DataFrame.from_records(filtered_collection_dict) #Returns dataframe
  return filtered_collection_dataframe


# call back function -> runs BEFORE the rest of the app
def reset_button():
    st.session_state["p"] = False
    return

#button to control reset
reset=st.button('Reset', on_click=reset_button)

#checkbox you want the button to un-check
check_box = st.checkbox("p", key='p')

#write out the current state to see that our flow works
st.write(st.session_state)

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
article = articles_df.iloc[0]
print(article['pubmed_id'])
print(article['authors'])
all_authors = ""
for author in article['authors']:
    all_authors += author['author'] + "; "
print(all_authors)


dashboard_data = get_dashboard_data("almeida.va93@gmail.com")
not_reviewed_articles = dashboard_data[(dashboard_data['excluded']==0) & (dashboard_data["included"]==0)]
current_article_pmid = not_reviewed_articles.iloc[0]['pubmed_id']

def get_current_article_data(article_pmid):
    query = firestore_client.collection("articles_full").document(article_pmid).get()
    filtered_collection_dict = query.to_dict()#Returns list of dictionaries 
    filtered_collection_dataframe = pd.DataFrame.from_records(filtered_collection_dict, index=[0]) #Returns dataframe
    return filtered_collection_dataframe

current_article_data = get_current_article_data(current_article_pmid)

st.markdown(functions.card(current_article_data), unsafe_allow_html=True)