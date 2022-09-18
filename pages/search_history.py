import streamlit as st
import nbib
import pandas as pd
import uuid
import time

#Custom imports
import functions


st.title("Histórico de revisões")

#Get users already reviewed articles
dashboard_data = functions.get_dashboard_data(user = "almeida.va93@gmail.com")
reviewed_articles = dashboard_data[(dashboard_data['excluded']!=0) | (dashboard_data["included"]!=0)]
reviewed_articles = reviewed_articles.sort_values(by="timestamp", ascending=False)
#st.write(reviewed_articles.sort_values(by="timestamp", ascending=False))

#Sort then from the most recent review to the firt review


#Show each article data with title, abstract, pubmed link, exclusion ou inclusion criteria, if the article was included or excluded, 
#a button to undo the review and put the article back to the queue
for index, reviewed_article in reviewed_articles.iterrows():
    article_data = functions.get_current_article_data(reviewed_article['pubmed_id'])
    functions.article_history_expander(article_data, reviewed_article)






#Show articles list in blocks that can move forward or backwards


#Styling
functions.local_css()