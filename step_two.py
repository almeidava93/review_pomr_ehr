
#Here we consolidate all inclusions and exclusions by unanimity and solve all disagreements in study selection.
import streamlit as st
import pandas as pd
import time

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

# consolidate_reviews = st.button('Consolidar artigos revisados no primeiro passo')
# if consolidate_reviews:
#     #for included articles:
#     for article_id in included_articles.index:
#         doc_ref = functions.firestore_client.collection("articles_second_review").document('included').collection('articles').document(f'{article_id}')
#         if len(doc_ref.get) == 0:
#             doc_ref.set({'pubmed_id': f'{article_id}'})

#     ref = functions.firestore_client.collection("articles_second_review").document('included').collection('articles').get()

#3) Evaluate disagreements and define final exclusion or inclusion



st.title("Passo 2: Resolvendo discordâncias")


update_undefined_articles = st.button('Atualizar artigos com discordância na revisão')
if update_undefined_articles:
    functions.update_undefined_articles(undefined_articles)

st.markdown("""***""")

current_article_pmid = undefined_articles.iloc[:,0].index[0]

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
            doc_ref = functions.firestore_client.collection("articles_second_review").document('included').collection("articles").document(current_article_pmid)
            doc_ref.set(
                {
                    "included": True,
                    "excluded": False,
                    "inclusion_criteria": selected_inclusion_criteria,
                    "timestamp": time.time()
                }
            )
            functions.firestore_client.collection("articles_second_review").document('undefined').collection("articles").document(current_article_pmid).delete()
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
            doc_ref = functions.firestore_client.collection("articles_second_review").document('excluded').collection("articles").document(current_article_pmid)
            doc_ref.set(
                {
                    "included": False,
                    "excluded": True,
                    "exclusion_criteria": selected_exclusion_criteria,
                    "timestamp": time.time()
                }
            )
            functions.firestore_client.collection("articles_second_review").document('undefined').collection("articles").document(current_article_pmid).delete()

            st.success("O artigo foi **excluído** com sucesso da revisão.")
            for key in st.session_state.keys():
                del st.session_state[key]

            #Reloading page
            st.experimental_rerun()

with st.sidebar:
    st.markdown(f"""**Artigos não avaliados**: {len(undefined_articles)}""")


functions.local_css()