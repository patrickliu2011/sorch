import streamlit as st

def app():
    st.set_page_config(page_title="Sorch", page_icon="🌟")
    st.title('Sorch')

    st.write(
        "Welcome to Sorch! This is a simple search engine that allows "
        "you to do semantic search over your local files!"
    )

if __name__ == "__main__":
    app()