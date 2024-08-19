import fire
import os
import json
from pinecone import Pinecone

from sorch.embedding import get_embedding

def get_record_id(path: str, chunking_strategy: str):
    if chunking_strategy != "prefix":
        raise ValueError(f"chunking_strategy={chunking_strategy} was passed but only `prefix` is supported.")
    return f"local:{path}:{chunking_strategy}"

def main(
    model_name: str,
    index_name: str | None = None,
    chunking_strategy: str = "prefix",
    root_dir: str = ".", # TODO: add support for file path restrictions
    num_results: int = 10,
):
    if chunking_strategy != "prefix":
        raise ValueError(f"chunking_strategy={chunking_strategy} was passed but only `prefix` is supported.")

    PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
    pc = Pinecone(api_key=PINECONE_API_KEY)

    available_indexes = pc.list_indexes().names()
    if index_name is None:
        if model_name in available_indexes:
            index_name = model_name
            print(f"Index name not provided, using model name as index name: {index_name}")
        else:
            print("Available indexes:")
            for i, idx_name in enumerate(available_indexes):
                print(f"{i+1}) {idx_name}")
            index_name = input("Enter index name or number: ").strip()
            if index_name.isdigit():
                index_name = available_indexes[int(index_name) - 1]
    if not index_name in pc.list_indexes().names():
        raise ValueError(f"Index {index_name} does not exist.")
    print(f"Using index: {index_name}")

    index = pc.Index(index_name)
    embedding = get_embedding(model_name)
    while True:
        query = input("Enter query (press Enter to exit): ").strip()
        if not query:
            break
        # query = f"Which sentence talks about {query}?"
        embedding_query = embedding.embed_query(query)
        search_results = index.query(
            vector=embedding_query,
            top_k=num_results,
            namespace=chunking_strategy,
        )
        print(f"Search results:")
        paths = [result.id.split(":")[1] for result in search_results.matches]
        for i, result in enumerate(search_results.matches):
            print(f"{i+1}) {result.score:.4f}\n\t{paths[i]}")



if __name__ == "__main__":
    fire.Fire(main)