import streamlit as st
import pandas as pd
import nbib
import json
from google.cloud import firestore
from sklearn.metrics import cohen_kappa_score
from fleiss import fleissKappa

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


def get_dashboard_data(user):
  query = firestore_client.collection("articles_first_review").document(user).collection("articles").get()
  filtered_collection_dict = [doc.to_dict() for doc in query] #Returns list of dictionaries 
  filtered_collection_dataframe = pd.DataFrame.from_records(filtered_collection_dict) #Returns dataframe
  return filtered_collection_dataframe

reviewed_articles_dataframes = []
for reviewer in reviewers:
  reviews_data = get_dashboard_data(reviewer)
  reviewed_articles = reviews_data[(reviews_data['excluded']==1) | (reviews_data["included"]==1)]
  reviewed_articles = reviewed_articles[['pubmed_id', 'excluded', 'included']]
  reviewed_articles.columns = ['pubmed_id', f'{reviewer}_excluded', f'{reviewer}_included']
  reviewed_articles.set_index('pubmed_id', inplace=True)
  reviewed_articles_dataframes.append(reviewed_articles)

#print(reviewed_articles_dataframes)
reviewed_articles_df = pd.concat(reviewed_articles_dataframes, axis=1, join='outer').dropna()
#print(reviewed_articles_df.head())

def get_current_article_data(article_pmid):
    query = firestore_client.collection("articles_full").document(article_pmid).get()
    filtered_collection_dict = query.to_dict()#Returns list of dictionaries 
    filtered_collection_dataframe = pd.DataFrame.from_records(filtered_collection_dict, index=[0]) #Returns dataframe
    return filtered_collection_dataframe

st.markdown("***")

st.markdown("""
### Coeficiente Kappa de Cohen
##### Avaliação da concordância entre pares de avaliadores
""")

reviewer_pairs = list()
for reviewer_1 in reviewers:
  for reviewer_2 in reviewers:
    if reviewer_1 != reviewer_2 and set((reviewer_1, reviewer_2)) not in reviewer_pairs:
      reviewer_pairs.append(set((reviewer_1, reviewer_2)))

cohen_kappa_results = list()
for reviewer_pair in reviewer_pairs:
  reviewer_1, reviewer_2 = reviewer_pair
  kappa_inclusion = cohen_kappa_score(list(reviewed_articles_df[f'{reviewer_1}_included']), list(reviewed_articles_df[f'{reviewer_2}_included']))
  kappa_exclusion = cohen_kappa_score(list(reviewed_articles_df[f'{reviewer_1}_excluded']), list(reviewed_articles_df[f'{reviewer_2}_excluded']))
  cohen_kappa_results.append((reviewer_1, reviewer_2, kappa_inclusion, kappa_exclusion))
  st.write(f"""
  Comparando {reviewer_1} com {reviewer_2}:
  - Para inclusão de artigos: {round(kappa_inclusion,3)}
  - Para exclusão de artigos: {round(kappa_exclusion,3)}
  """)

st.markdown("***")

#Implement Fleiss kappa
#https://github.com/Shamya/FleissKappa/blob/master/fleiss.py
#https://www.statsmodels.org/dev/generated/statsmodels.stats.inter_rater.fleiss_kappa.html

st.markdown("""
### Coeficiente Kappa de Fleiss
##### Avaliação da concordância entre grupos de três ou mais avaliadores
""")
reviewed_articles_df['excluded'] = reviewed_articles_df['almeida.va93@gmail.com_excluded'] + reviewed_articles_df['henrique.t.arai@gmail.com_excluded'] + reviewed_articles_df['mariela204@gmail.com_excluded']
reviewed_articles_df['included'] = reviewed_articles_df['almeida.va93@gmail.com_included'] + reviewed_articles_df['henrique.t.arai@gmail.com_included'] + reviewed_articles_df['mariela204@gmail.com_included']

fleiss_kappa = fleissKappa(reviewed_articles_df[['included','excluded']].to_numpy(),3)
st.write("Fleiss kappa: " + str(round(fleiss_kappa,3)))

st.markdown("***")

#Calculating the proportion in which all raters agree
st.markdown("""
### Proporção de concordância
""")
total_agreement = len(reviewed_articles_df[['included','excluded']][(reviewed_articles_df['included']==3) | (reviewed_articles_df['excluded']==3)])
proportion_agreement = total_agreement/len(reviewed_articles_df)
st.write("Proporção das avaliações que concordam totalmente: ", str(round(proportion_agreement*100,2)), "%")

st.markdown("***")

st.markdown("""
### Interpretação do coeficiente kappa
""")
st.image("kappa_interpretation.png", use_column_width="always")