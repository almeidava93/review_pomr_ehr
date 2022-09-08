import streamlit as st
import nbib
import pandas as pd
import uuid

st.title("Passo 1: Revisão títulos e resumos")
#st.header("Revisão títulos e resumos ")

filepath = "/Users/viniciusanjosdealmeida/review_pomr_ehr/articles.nbib"

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

def get_article_keys(articles_data): # articles_data is a list of dictionaries with articles data
    keys = []
    for article in articles_data:
        keys.extend(list(article.keys()))
    keys = set(keys)
    return keys # returns a list of unique keys that are present at least once in articles_data

articles_df = pd.DataFrame.from_records(articles_data) 
articles_df["included"] = 0
articles_df = articles_df.astype(str)
# st.dataframe(data=articles_df[articles_df["included"] != 1])
# print(articles_df.info())

articles_reviewed = articles_df[articles_df["included"] != 1].to_dict('records')
st.subheader(articles_reviewed[0]['title'])
st.write(articles_reviewed[0]['abstract'])
st.write(f"https://pubmed.ncbi.nlm.nih.gov/{articles_reviewed[0]['pubmed_id']}/")


column_a, column_b = st.columns(2)

with column_a:
    st.markdown("**Critérios de exclusão**")
    exclusion_criteria = ["Outra língua que não português ou inglês", 
                            "Não tem como objetivo estudar a aplicação de RCOP ou algum de seus componentes em um prontuário eletrônico", 
                            "Não tem como objetivo estudar o impacto de RCOP em um prontuário eletrônico para o paciente ou para o profissional"]
    exclusion_checkboxes = [st.checkbox(x) for x in exclusion_criteria]
    # st.write(exclusion_checkboxes)
    indices = [i for i, x in enumerate(exclusion_checkboxes) if x == True]
    selected_exclusion_criteria = [exclusion_criteria[i] for i in indices]
    # st.write(selected_exclusion_criteria)


with column_b:
    st.markdown("**Critérios de inclusão**")
    inclusion_criteria = ["Alguma aplicação do RCOP em um prontuário eletrônico (p.e., organizar lista de problemas, episódios de cuidado, SOAP ou outras maneiras de registro orientado por problemas)", 
                       "Estudo de impactos do uso do RCOP para o paciente", 
                       "Estudo de impactos do uso do RCOP para o profissional de saúde"]
    inclusion_checkboxes = [st.checkbox(x) for x in inclusion_criteria]
    # st.write(inclusion_checkboxes)
    indices = [i for i, x in enumerate(inclusion_checkboxes) if x == True]
    selected_inclusion_criteria = [inclusion_criteria[i] for i in indices]
    # for i in indices:
    #     st.write(inclusion_criteria[i])
    # st.write(selected_inclusion_criteria)






column_a, column_b = st.columns(2)

with column_a:
    excluded = st.button("Excluir", key="bt_excluded", help=None, on_click=None, args=None, kwargs=None)

with column_b:
    included = st.button("Incluir", key="bt_included", help=None, on_click=None, args=None, kwargs=None)


if len(selected_inclusion_criteria) > 0 and len(selected_exclusion_criteria) > 0:
    error_message = "Um mesmo artigo não pode ter selecionados critérios de inclusão e de exclusão."
    st.error(error_message)


if included:
    if len(selected_inclusion_criteria) == 0:
        inclusion_error_message = "Para **incluir** este artigo, selecione ao menos um dos critérios de inclusão."
        st.error(inclusion_error_message)
    else:
        st.success("O artigo foi **incluído** com sucesso na revisão.")

if excluded:
    if len(selected_exclusion_criteria) == 0:
        exclusion_error_message = "Para **excluir** este artigo, selecione ao menos um dos critérios de inclusão."
        st.error(exclusion_error_message)
    else:
        st.success("O artigo foi **excluído** com sucesso da revisão.")


#STYLING
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css('style.css')


# def header(content):
#      st.markdown(f'<p style="background-color:#ffffff;color:#33ff33;font-size:24px;border-radius:2%;position: fixed;top: 0;width: 100%">{content}</p>', unsafe_allow_html=True)
# header("Olá, Mundo!")

with st.sidebar:
    st.write("""**Artigos incluídos**: 17""")    
    st.markdown("""**Artigos excluídos**: 32""")
    st.markdown("""**Artigos não avaliados**: 100""")

