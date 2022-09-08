#REFERENCES
#Firestore database documentation: https://googleapis.dev/python/firestore/latest/index.html


import streamlit as st
from google.cloud import firestore
import json
import pandas as pd

database_keys = open("pomr-systematic-review-firebase-adminsdk-g6klq-e4f60f5466.json")
service_account_info = json.load(database_keys)


#Connecting with the firestore database
@st.cache(hash_funcs={firestore.Client: id}, ttl=None, show_spinner=True)
def load_firestore_client(service_account_info = service_account_info):
  firestore_client = firestore.Client.from_service_account_info(service_account_info)
  return firestore_client

firestore_client = load_firestore_client() #Loads cached database connection


#Page rendering
st.title("Dashboard de referências")

column_a, column_b, column_c = st.columns(3)

def get_dashboard_data():
  query = firestore_client.collection("articles_first_review").select(["pubmed_id","included","excluded"]).get()
  filtered_collection_dict = [doc.to_dict() for doc in query] #Returns list of dictionaries 
  filtered_collection_dataframe = pd.DataFrame.from_records(filtered_collection_dict) #Returns dataframe
  return filtered_collection_dataframe

dashboard_data = get_dashboard_data()

with column_a:
    st.subheader("Total de artigos")
    st.markdown(f"{len(dashboard_data)}")

with column_b:
    st.subheader("Artigos incluídos")
    st.markdown(f"{len(dashboard_data[dashboard_data['included']==True])}")

with column_c:
    st.subheader("Artigos excluídos")
    st.markdown(f"{len(dashboard_data[dashboard_data['excluded']==True])}")