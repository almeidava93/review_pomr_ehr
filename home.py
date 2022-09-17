import streamlit as st
import sqlite3

# Create a SQL connection to our SQLite database
con = sqlite3.connect("review.sqlite")

cur = con.cursor()


def next_article():
    # Return first result of query
    cur.execute('SELECT * FROM articles WHERE of_interest IS NULL')
    articles = cur.fetchall()


    #PAGE TEMPLATE
    title = st.title("Ferramenta de revisão de artigos")
    st.markdown(f"Temos ao todo **{len(articles)}** artigos que não foram revisados por título e resumo.")
    st.header("Próximo artigo...")
    
    st.subheader(articles[0][1])
    st.write(articles[0][2])
    st.text(articles[0][5])

    cur.execute(f'SELECT abstract FROM abstracts WHERE pmid={articles[0][0]}')
    abstract = cur.fetchone()
    try:
        st.write(abstract[0].split('\n\n')[4].replace('\n',''))
    except:
        st.write(abstract[0].split('\n\n')[-1].replace('\n',''))

    show_everything = st.button('Mostrar tudo')
    if show_everything:
        st.write(articles[0])
        cur.execute(f'SELECT abstract FROM abstracts WHERE pmid={articles[0][0]}')
        abstract = cur.fetchone()
        st.write(abstract[0].split('\n\n'))

    st.subheader("Este artigo se refere à aplicação do registro orientado por problemas em um prontuário eletrônico?")
    column_a, column_b = st.columns(2)

    with column_a:
        clicked_a = st.button('Sim')
    
    if clicked_a:
            print(articles[0][0])
            cur.execute(f"""UPDATE articles SET of_interest = TRUE WHERE pmid={articles[0][0]};""")
            con.commit()
            st.experimental_rerun()
            

    with column_b:
        clicked_b = st.button('Não')
    
    if clicked_b:
            print(articles[0][-1])
            cur.execute(f"""UPDATE articles SET of_interest = FALSE WHERE pmid={articles[0][0]};""")
            con.commit()
            st.experimental_rerun()

next_article()

#UPDATING THE DATABASE



#STYLING
def local_css(file_name='style.css'):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css('style.css')
