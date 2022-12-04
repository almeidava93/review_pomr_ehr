import streamlit as st
import pandas as pd
import time
from tqdm import tqdm
import random 
import pdb


#Custom module
import functions

# """
# Step by step:
# 1) retrieve all included articles
# 2) check if there are any new articles to be included in the review to be completely read
# 3) update included articles
# 4) attribute new articles to a main reviewer for information extraction
# 5) elaborate a form for the reviwer evaluation 
# """

#UPDATING ARTICLES THAT MUST BE FULLY READ 
#1) Retrieve all articles that were reviewed by all reviewers
reviewed_articles_df = functions.retrieve_fully_reviewed_articles()

#2) Update database with articles that were included or excluded by unanimity
@st.cache(ttl = 1800)
def update_database_1():
    reviewed_articles_df['excluded'] = reviewed_articles_df['almeida.va93@gmail.com_excluded'] + reviewed_articles_df['henrique.t.arai@gmail.com_excluded'] + reviewed_articles_df['mariela204@gmail.com_excluded']
    reviewed_articles_df['included'] = reviewed_articles_df['almeida.va93@gmail.com_included'] + reviewed_articles_df['henrique.t.arai@gmail.com_included'] + reviewed_articles_df['mariela204@gmail.com_included']

    included_articles = reviewed_articles_df['included'][reviewed_articles_df['included']==3]
    excluded_articles = reviewed_articles_df['excluded'][reviewed_articles_df['excluded']==3]
    undefined_articles = reviewed_articles_df[(reviewed_articles_df['excluded']!=3) & (reviewed_articles_df['included']!=3)]

    return included_articles, excluded_articles, undefined_articles

included_articles, excluded_articles, undefined_articles = update_database_1()

#3) Set up a new collection of articles for step two. They will have the following structure: pubmed_id, included, excluded. Retrieve 
#the articles that are already in that collection
@st.cache(ttl = 1800)
def update_database_2():
    articles_df = functions.get_dashboard_data_step_two()

    if len(articles_df) > 0:
        #A) add to the collection the included articles
        for article_id in tqdm(included_articles.index):
            if article_id not in articles_df["pubmed_id"].values:
                doc_ref = functions.firestore_client.collection("articles_second_review").document(f"{article_id}")
                doc_ref.set({
                    "pubmed_id": article_id,
                    "included": True,
                    "excluded": False        
                })

        #B) add to the collection the excluded articles
        for article_id in tqdm(excluded_articles.index):
            if article_id not in articles_df["pubmed_id"].values:
                doc_ref = functions.firestore_client.collection("articles_second_review").document(f"{article_id}")
                doc_ref.set({
                    "pubmed_id": article_id,
                    "included": False,
                    "excluded": True        
                })

        #C) add to the collection the undefined articles
        for article_id in tqdm(undefined_articles.index):
            if article_id not in articles_df["pubmed_id"].values:
                doc_ref = functions.firestore_client.collection("articles_second_review").document(f"{article_id}")
                doc_ref.set({
                    "pubmed_id": article_id,
                    "included": False,
                    "excluded": False        
                })

    else:
        #A) add to the collection the included articles
        for article_id in tqdm(included_articles.index):
                doc_ref = functions.firestore_client.collection("articles_second_review").document(f"{article_id}")
                doc_ref.set({
                    "pubmed_id": article_id,
                    "included": True,
                    "excluded": False        
                })

        #B) add to the collection the excluded articles
        for article_id in tqdm(excluded_articles.index):
                doc_ref = functions.firestore_client.collection("articles_second_review").document(f"{article_id}")
                doc_ref.set({
                    "pubmed_id": article_id,
                    "included": False,
                    "excluded": True        
                })

        #C) add to the collection the undefined articles
        for article_id in tqdm(undefined_articles.index):
                doc_ref = functions.firestore_client.collection("articles_second_review").document(f"{article_id}")
                doc_ref.set({
                    "pubmed_id": article_id,
                    "included": False,
                    "excluded": False   
                })

update_database_2()

#4) Get all included articles from articles_second_review, check if it is already present in articles_third_review
#   and, if not, add to articles_third_review to be reevaluated
def update_database_3():
    query_ref_2 = functions.firestore_client.collection("articles_second_review").where("included", "==", True)
    query = query_ref_2.get()
    data = [doc.to_dict() for doc in query]
    df = pd.DataFrame.from_records(data)

    if len(functions.firestore_client.collection("articles_third_review").get()) == 0:
        print("Including all articles...")
        doc_ref = functions.firestore_client.collection("articles_third_review")
        for article_id in tqdm(df["pubmed_id"]):
            doc_ref.document(f"{article_id}").set({
                "pubmed_id": article_id,
                "included": False,
                "excluded": False,
                "article_data": "",
                "reviewer": random.choice(functions.reviewers),
                "concluded": False
            })

    elif len(functions.firestore_client.collection("articles_third_review").get()) > 0:
        print("Checking for any new articles to include...")
        doc_ref = functions.firestore_client.collection("articles_third_review")
        query = doc_ref.get()
        data = [doc.to_dict() for doc in query]
        df1 = pd.DataFrame.from_records(data)
        for article_id in tqdm(df["pubmed_id"]):
            if article_id not in list(df1["pubmed_id"]):
                doc_ref.document(f"{article_id}").set({
                    "pubmed_id": article_id,
                    "included": False,
                    "excluded": False,
                    "article_data": "",
                    "reviewer": random.choice(functions.reviewers),
                    "concluded": False
                })
                print(f"article with pubmed_id {article_id} modified")
    
    return df1

df1 = update_database_3()

st.title("Passo 3: Lendo artigos completos")
st.markdown("""***""")

#current_user = st.experimental_user.email
current_user = "almeida.va93@gmail.com"


# review_info = f"""
# - mariela204@gmail.com: {df1["reviewer"].value_counts()["mariela204@gmail.com"]} artigos
# --> concluídos: {df1[df1['reviewer']=='almeida.va93@gmail.com']['concluded'].value_counts()[True]}
# --> pendentes: {df1[df1['reviewer']=='almeida.va93@gmail.com']['concluded'].value_counts()[False]}
# - henrique.t.arai@gmail.com: {df1["reviewer"].value_counts()["henrique.t.arai@gmail.com"]} artigos
# --> concluídos: {df1[df1['reviewer']=='almeida.va93@gmail.com']['concluded'].value_counts()[True]}
# --> pendentes: {df1[df1['reviewer']=='almeida.va93@gmail.com']['concluded'].value_counts()[False]}
# - almeida.va93@gmail.com: {df1["reviewer"].value_counts()["almeida.va93@gmail.com"]} artigos
# --> concluídos: {df1[df1['reviewer']=='almeida.va93@gmail.com']['concluded'].value_counts()[True]}
# --> pendentes: {df1[df1['reviewer']=='almeida.va93@gmail.com']['concluded'].value_counts()[False]}
# """

# with st.sidebar:
#     st.markdown(review_info, unsafe_allow_html=True)

for reviewer in functions.reviewers:
    total = df1["reviewer"].value_counts()[reviewer]
    pendent = df1[df1['reviewer']==reviewer]['concluded'].value_counts()[False]
    
    review_info = f"""{reviewer}: {total} artigos
--> concluídos: {total - pendent}
--> pendentes: {pendent}
"""
    with st.sidebar:
        st.markdown(review_info, unsafe_allow_html=True)

doc_ref = functions.firestore_client.collection("articles_third_review")
query = doc_ref.get()
data = [doc.to_dict() for doc in query]
df = pd.DataFrame.from_records(data)
current_article_pmid = df[(df["reviewer"] == current_user) & (df["concluded"]==False)]["pubmed_id"].iloc[0]
current_article_data = functions.get_current_article_data(current_article_pmid)

try:
    st.markdown(functions.card_full_text(current_article_data), unsafe_allow_html=True)
except:
    st.write(current_article_data)

st.markdown("")

doc_ref = functions.firestore_client.collection("articles_third_review")
query = doc_ref.document(current_article_pmid).get()
article_review_data = query.to_dict()
review_keys = ["tags", "objective", "methods", "results", "limitations", "concluded"]

for review_key in review_keys:
    if review_key not in article_review_data.keys():
        article_review_data[review_key] = ""
    if len(article_review_data["tags"])==0:
        article_review_data["tags"] = []

def format_func(x):
    if x==True: return "Incluir"
    elif x==False: return "Excluir"
    else: return None

included = st.radio("Incluir ou excluir?", [True, False], index=1, format_func=format_func, horizontal=True, label_visibility="visible")

form = st.form(key="article_data_form")

with form:
    if included:
        article_review_data["included"] = True
        article_review_data["excluded"] = False
        tags = st.multiselect("Quais as características deste estudo? Selecione todas as que se aplicam",
            options=["estudo epidemiologico",
                "lista de problemas",
                "episodio de cuidado",
                "SOAP e outros modelos",
                "CID",
                "CIAP",
                "outras classificacoes internacionais",
                "elaboracao de prontuario eletronico",
                "minimum basic data set"
            ],
            default=article_review_data["tags"]
        )
        objective = st.text_area("Objetivo", value=article_review_data["objective"])
        methods = st.text_area("Métodos", value=article_review_data["methods"])
        results = st.text_area("Principais resultados", value=article_review_data["results"])
        limitations = st.text_area("Limitações", value=article_review_data["limitations"])

    elif included==False:
        article_review_data["included"] = False
        article_review_data["excluded"] = True


st.markdown("***")

with form:
    a,b = st.columns([1,1])
    save = form.form_submit_button("Salvar")   
    if save:
        if article_review_data["included"] == True:
            article_review_data["objective"] = objective
            article_review_data["methods"] = methods
            article_review_data["results"] = results
            article_review_data["limitations"] = limitations
            article_review_data["tags"] = tags
        
        doc_ref = functions.firestore_client.collection("articles_third_review")
        doc_ref.document(current_article_pmid).set(
            article_review_data,
            merge=True
        )    

    next = form.form_submit_button("Concluir revisão e ir para o próximo artigo")
    if next:
        if article_review_data["included"] == True:
            article_review_data["objective"] = objective
            article_review_data["methods"] = methods
            article_review_data["results"] = results
            article_review_data["limitations"] = limitations
            article_review_data["tags"] = tags
        
        article_review_data["concluded"] = True
        
        doc_ref = functions.firestore_client.collection("articles_third_review")
        doc_ref.document(current_article_pmid).set(
            article_review_data,
            merge=True
        )    
        st.experimental_rerun()

functions.local_css()