import streamlit as st
import pandas as pd
import nbib

import functions

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


st.markdown(functions.card(article), unsafe_allow_html=True)