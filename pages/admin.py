import streamlit as st
import nbib
import pandas as pd
import uuid
import time

#Custom imports
import main
import functions

if functions.current_user != "almeida.va93@gmail.com":
    exclusion_error_message = "Você não tem permissão para ver esta página."
    st.error(exclusion_error_message)

else:
    st.title("Funções de administrador")

    #FUNÇÃO: Adicionar novas referências conforme se atualiza a busca no pubmed
    with st.expander("Adicionar artigos"):
        column_a, column_b = st.columns([2,1])
        
        with column_a:
            file = st.file_uploader("Upload de referências/citações", 
                                        type=['nbib'], 
                                        help="Apenas arquivos .nbib gerado das buscas no pubmed")
            search_strategy = st.text_input("Cole aqui a busca realizada para encontrar esses artigos no pubmed", help="É o texto que você digitou na busca do pubmed")
        
        with column_b:
            add_articles_button = st.button("Adicionar artigos")
        
        if add_articles_button and file is not None:                            
            functions.add_new_articles(file, search_strategy)

        pass