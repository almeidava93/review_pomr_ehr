import streamlit as st
import nbib
import pandas as pd
import streamlit.components.v1 as components


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

articles_df = pd.DataFrame.from_records(articles_data) 
articles_df["included"] = 0
articles_df = articles_df.astype(str)

print(len(articles_df))


st.title("Dashboard de referências")

column_a, column_b, column_c = st.columns(3)

with column_a:
    st.subheader("Total de artigos")
    st.markdown(f"{len(articles_df)}")

with column_b:
    st.subheader("Artigos incluídos")
    st.markdown(f"{len(articles_df)}")

with column_c:
    st.subheader("Artigos excluídos")
    st.markdown(f"{len(articles_df)}")

searchbox = st.text_input("Pesquisar artigos")

def show_article_expander(article_index):
    with st.expander(articles_df.at[article_index,'title']):
        st.write(articles_df.at[article_index,'abstract'])
        st.write(f"https://pubmed.ncbi.nlm.nih.gov/{articles_df.at[article_index,'pubmed_id']}/")



def show_articles_list(start=0, stop=9):
    for index, row in articles_df.iterrows():
        if index >= start:
            show_article_expander(index)
            if index == stop: break

articles_list = st.empty()
articles_list = show_articles_list()

column_a, column_b, column_c = st.columns(3)

current_page = 1
total_pages = 12

with column_a:
    st.button('Anterior')

with column_b:
    st.write(f'Página {current_page} de {total_pages}')

with column_c:
    st.button('Próxima')






#STYLING
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css('style.css')


#https://www.youtube.com/watch?v=gr_KyGfO_eU