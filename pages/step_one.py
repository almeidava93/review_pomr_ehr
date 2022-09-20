import streamlit as st
import streamlit.components.v1 as components

import nbib
import pandas as pd
import uuid
import time

#Custom imports
import main
import functions



st.title("Passo 1: Revisão títulos e resumos")

st.write(f"Você logou como: {functions.current_user}")

st.markdown("""***""")

dashboard_data = main.get_dashboard_data(functions.current_user)
not_reviewed_articles = dashboard_data[(dashboard_data['excluded']==0) & (dashboard_data["included"]==0)]
current_article_pmid = not_reviewed_articles.iloc[0]['pubmed_id']

current_article_data = functions.get_current_article_data(current_article_pmid)

try:
    st.markdown(functions.card(current_article_data), unsafe_allow_html=True)
except:
    st.write(current_article_data)

st.markdown("***")

column_a, column_b = st.columns(2)

exclusion_form = st.form("exclusion", clear_on_submit=True)
with exclusion_form:
    st.markdown("**Critérios de exclusão**")
    exclusion_criteria = ["Outra língua que não português ou inglês", 
                            "Não tem como objetivo estudar a aplicação de RCOP ou algum de seus componentes em um prontuário eletrônico ou de estudar o impacto de RCOP em um prontuário eletrônico para o paciente ou para o profissional"]

    exclusion_checkboxes = [st.checkbox(x, key=x) for x in exclusion_criteria]
    # st.write(exclusion_checkboxes)
    indices = [i for i, x in enumerate(exclusion_checkboxes) if x == True]
    selected_exclusion_criteria = [exclusion_criteria[i] for i in indices]
    # st.write(sum(exclusion_checkboxes))

    excluded = st.form_submit_button("Excluir", help=None, kwargs=None)

inclusion_form = st.form("inclusion", clear_on_submit=True)
with inclusion_form:
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
    # st.write(sum(inclusion_checkboxes))

    included = st.form_submit_button("Incluir", help=None, kwargs=None)


# if sum(inclusion_checkboxes) > 0 and sum(exclusion_checkboxes) > 0:
#     error_message = "Um mesmo artigo não pode ter selecionados critérios de inclusão e de exclusão."
#     st.error(error_message)

with inclusion_form:
    if included:
        if sum(inclusion_checkboxes) == 0:
            inclusion_error_message = "Para **incluir** este artigo, selecione ao menos um dos critérios de inclusão."
            st.error(inclusion_error_message)
            for key in st.session_state.keys():
                del st.session_state[key]

        # elif sum(inclusion_checkboxes) > 0 and sum(exclusion_checkboxes) > 0:
        #     error_message = "Um mesmo artigo não pode ter selecionados critérios de inclusão e de exclusão."
        #     st.error(error_message)
        #     for key in st.session_state.keys():
        #         del st.session_state[key]

        else:
            doc_ref = main.firestore_client.collection("articles_first_review").document(functions.current_user).collection("articles").document(current_article_pmid)
            doc_ref.update(
                {
                    "included": True,
                    "excluded": False,
                    "inclusion_criteria": selected_inclusion_criteria,
                    "timestamp": time.time()
                }
            )
            st.success("O artigo foi **incluído** com sucesso na revisão.")
            for key in st.session_state.keys():
                del st.session_state[key]

            #Reloading page
            st.experimental_rerun()

with exclusion_form:
    if excluded:
        if sum(exclusion_checkboxes) == 0:
            exclusion_error_message = "Para **excluir** este artigo, selecione ao menos um dos critérios de exclusão."
            st.error(exclusion_error_message)
            for key in st.session_state.keys():
                del st.session_state[key]


        # elif sum(inclusion_checkboxes) > 0 and sum(exclusion_checkboxes) > 0:
        #     error_message = "Um mesmo artigo não pode ter selecionados critérios de inclusão e de exclusão."
        #     st.error(error_message)
        #     for key in st.session_state.keys():
        #         del st.session_state[key]

        else:
            doc_ref = main.firestore_client.collection("articles_first_review").document(functions.current_user).collection("articles").document(current_article_pmid)
            doc_ref.update(
                {
                    "included": False,
                    "excluded": True,
                    "exclusion_criteria": selected_exclusion_criteria,
                    "timestamp": time.time()
                }
            )
            st.success("O artigo foi **excluído** com sucesso da revisão.")
            for key in st.session_state.keys():
                del st.session_state[key]

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

