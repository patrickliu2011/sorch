import streamlit as st
import os
from pinecone import Pinecone

from sorch.embedding import get_embedding, EMBEDDING_MODEL_NAMES

def app():
    st.title('Search Files')

    PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
    pc = Pinecone(api_key=PINECONE_API_KEY)

    model_name = st.selectbox("Select embedding model:", EMBEDDING_MODEL_NAMES, key="model_name")
    st.write(f"Selected model: {model_name}")
    index_name = model_name
    embedding = get_embedding(model_name)
    index = pc.Index(index_name)

    chunking_strategy = st.selectbox("Select chunking strategy:", ["prefix"], key="chunking_strategy")
    st.write(f"Selected chunking strategy: {chunking_strategy}")

    query = st.text_input("Enter query: ", key="query")
    st.write(f"Query: {query}")

    num_results = st.number_input("Top results:", min_value=1, max_value=100, value=10, key="num_results")

    if query.strip() == "":
        st.write("Please enter a query to search.")
        st.stop()

    embedding_query = embedding.embed_query(query)
    search_results = index.query(
        vector=embedding_query,
        top_k=num_results,
        namespace=chunking_strategy,
    )
    paths = [result.id.split(":")[1] for result in search_results.matches]

    search_results_box = st.container()
    search_results_box.write("Search results:")
    for i, result in enumerate(search_results.matches):
        result_entry = st.container(border=True)
        result_entry.write(f"{i+1}) {result.score:.4f}")
        result_entry.markdown(f"[{paths[i]}](file:///{paths[i]})")

if __name__ == "__main__":
    app()