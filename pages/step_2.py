
#Here we consolidate all inclusions and exclusions by unanimity and solve all disagreements in study selection.
import streamlit as st
import pandas as pd
import time
from tqdm import tqdm

#Custom module
import functions

#1) Retrieve all articles that were reviewed by all reviewers
reviewed_articles_df = functions.retrieve_fully_reviewed_articles()

#2) Update database with articles that were included or excluded by unanimity
reviewed_articles_df['excluded'] = reviewed_articles_df['almeida.va93@gmail.com_excluded'] + reviewed_articles_df['henrique.t.arai@gmail.com_excluded'] + reviewed_articles_df['mariela204@gmail.com_excluded']
reviewed_articles_df['included'] = reviewed_articles_df['almeida.va93@gmail.com_included'] + reviewed_articles_df['henrique.t.arai@gmail.com_included'] + reviewed_articles_df['mariela204@gmail.com_included']

included_articles = reviewed_articles_df['included'][reviewed_articles_df['included']==3]
excluded_articles = reviewed_articles_df['excluded'][reviewed_articles_df['excluded']==3]
undefined_articles = reviewed_articles_df[(reviewed_articles_df['excluded']!=3) & (reviewed_articles_df['included']!=3)]

#3) Set up a new collection of articles for step two. They will have the following structure: pubmed_id, included, excluded. Retrieve 
#the articles that are already in that collection
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


#3) Evaluate disagreements and define final exclusion or inclusion

st.title("Passo 2: Resolvendo discord??ncias")
st.markdown("""***""")

articles_df = functions.get_dashboard_data_step_two()
pendent_articles = articles_df[(articles_df["included"]==False) & (articles_df["excluded"]==False)]
current_article_pmid = pendent_articles["pubmed_id"].iloc[0]
current_article_data = functions.get_current_article_data(current_article_pmid)

try:
    st.markdown(functions.card(current_article_data), unsafe_allow_html=True)
except:
    st.write(current_article_data)

st.markdown("***")

column_a, column_b = st.columns(2)

exclusion_form = st.form("exclusion", clear_on_submit=True)
with exclusion_form:
    st.markdown("**Crit??rios de exclus??o**")
    exclusion_criteria = ["Outra l??ngua que n??o portugu??s ou ingl??s", 
                            "N??o tem como objetivo estudar a aplica????o de RCOP ou algum de seus componentes em um prontu??rio eletr??nico ou de estudar o impacto de RCOP em um prontu??rio eletr??nico para o paciente ou para o profissional"]
    exclusion_checkboxes = [st.checkbox(x, key=x) for x in exclusion_criteria]
    indices = [i for i, x in enumerate(exclusion_checkboxes) if x == True]
    selected_exclusion_criteria = [exclusion_criteria[i] for i in indices]
    excluded = st.form_submit_button("Excluir", help=None, kwargs=None)

inclusion_form = st.form("inclusion", clear_on_submit=True)
with inclusion_form:
    st.markdown("**Crit??rios de inclus??o**")
    inclusion_criteria = ["Alguma aplica????o do RCOP em um prontu??rio eletr??nico (p.e., organizar lista de problemas, epis??dios de cuidado, SOAP ou outras maneiras de registro orientado por problemas)", 
                       "Estudo de impactos do uso do RCOP para o paciente", 
                       "Estudo de impactos do uso do RCOP para o profissional de sa??de",
                       "N??o foi poss??vel avaliar"]
    inclusion_checkboxes = [st.checkbox(x, key=x) for x in inclusion_criteria]
    indices = [i for i, x in enumerate(inclusion_checkboxes) if x == True]
    selected_inclusion_criteria = [inclusion_criteria[i] for i in indices]
    included = st.form_submit_button("Incluir", help=None, kwargs=None)


with inclusion_form:
    if included:
        if sum(inclusion_checkboxes) == 0:
            inclusion_error_message = "Para **incluir** este artigo, selecione ao menos um dos crit??rios de inclus??o."
            st.error(inclusion_error_message)
            for key in st.session_state.keys():
                del st.session_state[key]

        else:
            doc_ref = functions.firestore_client.collection("articles_second_review").document(current_article_pmid)
            doc_ref.set(
                {
                    "included": True,
                    "excluded": False,
                    "inclusion_criteria": selected_inclusion_criteria,
                    "timestamp": time.time(),
                    "pubmed_id": current_article_pmid
                }
            )
            st.success("O artigo foi **inclu??do** com sucesso na revis??o.")
            for key in st.session_state.keys():
                del st.session_state[key]

            #Reloading page
            st.experimental_rerun()

with exclusion_form:
    if excluded:
        if sum(exclusion_checkboxes) == 0:
            exclusion_error_message = "Para **excluir** este artigo, selecione ao menos um dos crit??rios de exclus??o."
            st.error(exclusion_error_message)
            for key in st.session_state.keys():
                del st.session_state[key]

        else:
            doc_ref = functions.firestore_client.collection("articles_second_review").document(current_article_pmid)
            doc_ref.set(
                {
                    "included": False,
                    "excluded": True,
                    "exclusion_criteria": selected_exclusion_criteria,
                    "timestamp": time.time(),
                    "pubmed_id": current_article_pmid
                }
            )
            st.success("O artigo foi **exclu??do** com sucesso da revis??o.")
            for key in st.session_state.keys():
                del st.session_state[key]

            #Reloading page
            st.experimental_rerun()

with st.sidebar:
    st.markdown(f"""**Artigos n??o avaliados**: {len(undefined_articles)}""")


functions.local_css()