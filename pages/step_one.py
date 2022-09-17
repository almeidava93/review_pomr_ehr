import streamlit as st
import nbib
import pandas as pd
import uuid
import time

#Custom imports
import main
import functions


st.title("Passo 1: Revisão títulos e resumos")

st.write(f"Você logou como: {st.experimental_user.email}")

st.markdown("""***""")

dashboard_data = main.get_dashboard_data(user = st.experimental_user.email)
not_reviewed_articles = dashboard_data[(dashboard_data['excluded']==0) & (dashboard_data["included"]==0)]
current_article_pmid = not_reviewed_articles.iloc[0]['pubmed_id']

def get_current_article_data(article_pmid):
    query = main.firestore_client.collection("articles_full").document(article_pmid).get()
    filtered_collection_dict = query.to_dict()#Returns list of dictionaries 
    filtered_collection_dataframe = pd.DataFrame.from_records(filtered_collection_dict, index=[0]) #Returns dataframe
    return filtered_collection_dataframe

current_article_data = get_current_article_data(current_article_pmid)

st.markdown(functions.card(current_article_data), unsafe_allow_html=True)



# st.subheader(str(current_article_data.at[0,'title']))

# if str(current_article_data.at[0,'abstract']) != 'nan':
#     st.write(str(current_article_data.at[0,'abstract']))
# else:
#     st.markdown("*Este artigo não tem resumo disponível...*")

# st.write(f"https://pubmed.ncbi.nlm.nih.gov/{str(current_article_data.at[0,'pubmed_id'])}/")


st.markdown("***")

column_a, column_b = st.columns(2)

with column_a:
    st.markdown("**Critérios de exclusão**")
    exclusion_criteria = ["Outra língua que não português ou inglês", 
                            "Não tem como objetivo estudar a aplicação de RCOP ou algum de seus componentes em um prontuário eletrônico ou de estudar o impacto de RCOP em um prontuário eletrônico para o paciente ou para o profissional"]

    exclusion_checkboxes = [st.checkbox(x, key=x) for x in exclusion_criteria]
    # st.write(exclusion_checkboxes)
    indices = [i for i, x in enumerate(exclusion_checkboxes) if x == True]
    selected_exclusion_criteria = [exclusion_criteria[i] for i in indices]
    # st.write(selected_exclusion_criteria)


with column_b:
    st.markdown("**Critérios de inclusão**")
    inclusion_criteria = ["Alguma aplicação do RCOP em um prontuário eletrônico (p.e., organizar lista de problemas, episódios de cuidado, SOAP ou outras maneiras de registro orientado por problemas)", 
                       "Estudo de impactos do uso do RCOP para o paciente", 
                       "Estudo de impactos do uso do RCOP para o profissional de saúde",
                       "Não foi possível avaliar"]
    
    inclusion_checkboxes = [st.checkbox(x, key=x) for x in inclusion_criteria]
    # st.write(inclusion_checkboxes)
    indices = [i for i, x in enumerate(inclusion_checkboxes) if x == True]
    selected_inclusion_criteria = [inclusion_criteria[i] for i in indices]
    # for i in indices:
    #     st.write(inclusion_criteria[i])
    # st.write(selected_inclusion_criteria)






column_a, column_b = st.columns(2)

with column_a:
    excluded = st.button("Excluir", key="bt_excluded", help=None, kwargs=None)

with column_b:
    included = st.button("Incluir", key="bt_included", help=None, kwargs=None)

if len(selected_inclusion_criteria) > 0 and len(selected_exclusion_criteria) > 0:
    error_message = "Um mesmo artigo não pode ter selecionados critérios de inclusão e de exclusão."
    st.error(error_message)



if included:
    if len(selected_inclusion_criteria) == 0:
        inclusion_error_message = "Para **incluir** este artigo, selecione ao menos um dos critérios de inclusão."
        st.error(inclusion_error_message)

    elif len(selected_inclusion_criteria) > 0 and len(selected_exclusion_criteria) > 0:
        error_message = "Um mesmo artigo não pode ter selecionados critérios de inclusão e de exclusão."
        st.error(error_message)

    else:
        doc_ref = main.firestore_client.collection("articles_first_review").document(st.experimental_user.email).collection("articles").document(current_article_pmid)
        doc_ref.update(
            {
                "included": True,
                "excluded": False,
                "inclusion_criteria": selected_inclusion_criteria,
                "timestamp": time.time()
            }
        )
        st.success("O artigo foi **incluído** com sucesso na revisão.")

        #Reloading page
        st.experimental_rerun()



if excluded:
    if len(selected_exclusion_criteria) == 0:
        exclusion_error_message = "Para **excluir** este artigo, selecione ao menos um dos critérios de exclusão."
        st.error(exclusion_error_message)


    elif len(selected_inclusion_criteria) > 0 and len(selected_exclusion_criteria) > 0:
        error_message = "Um mesmo artigo não pode ter selecionados critérios de inclusão e de exclusão."
        st.error(error_message)

    else:
        doc_ref = main.firestore_client.collection("articles_first_review").document(st.experimental_user.email).collection("articles").document(current_article_pmid)
        doc_ref.update(
            {
                "included": False,
                "excluded": True,
                "exclusion_criteria": selected_exclusion_criteria,
                "timestamp": time.time()
            }
        )
        st.success("O artigo foi **excluído** com sucesso da revisão.")

        #Reloading page
        st.experimental_rerun()


#Designing the sidebar
n_reviewed_articles = len(dashboard_data[(dashboard_data['included']==1) | (dashboard_data['excluded']==1)])
n_all_articles = len(dashboard_data)

with st.sidebar:
    st.markdown(f"""**Artigos não avaliados**: {n_all_articles - n_reviewed_articles}""")
    st.write(f"""**Artigos incluídos**: {len(dashboard_data[(dashboard_data['included']==1)])}""")    
    st.markdown(f"""**Artigos excluídos**: {len(dashboard_data[(dashboard_data['excluded']==1)])}""")

functions.local_css()
