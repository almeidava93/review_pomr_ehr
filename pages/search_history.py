import streamlit as st
import streamlit.components.v1 as components
import nbib
import pandas as pd
import uuid
import time

#Custom imports
import functions


st.title("Histórico de revisões")

current_user = st.experimental_user.email

#Get users already reviewed articles
dashboard_data = functions.get_dashboard_data(current_user)
reviewed_articles = dashboard_data[(dashboard_data['excluded']!=0) | (dashboard_data["included"]!=0)]

#Sort then from the most recent review to the firt review
reviewed_articles = reviewed_articles.sort_values(by="timestamp", ascending=False).reset_index(drop=True)

#Select how many results to show to the user
n_results = st.number_input("Selecione quantos resultados deseja consultar", min_value=1, max_value=len(reviewed_articles), value=10, step=None, format=None, key=None, help=None, on_change=None, args=None, kwargs=None, disabled=False)

#Show each article data with title, abstract, pubmed link, exclusion ou inclusion criteria, if the article was included or excluded, 
#a button to undo the review and put the article back to the queue
for index, reviewed_article in reviewed_articles.iterrows():
    if index > (n_results - 1):
        break
    else:
        article_data = functions.get_current_article_data(reviewed_article['pubmed_id'])
        functions.article_history_expander(article_data, reviewed_article)


#Show articles list in blocks that can move forward or backwards


#Styling
functions.local_css()
components.html(functions.js_script(), width=0, height=0)