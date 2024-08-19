import fire
import os
import tqdm
from pinecone import Pinecone, ServerlessSpec

from sorch.embedding import get_embedding
from sorch.file_utils import get_file_paths, is_indexable_file
from sorch.pinecone_utils import record_exists

def get_record_id(path: str, chunking_strategy: str):
    if chunking_strategy != "prefix":
        raise ValueError(f"chunking_strategy={chunking_strategy} was passed but only `prefix` is supported.")
    return f"local:{path}"

def main(
    model_name: str, 
    index_name: str | None = None,
    root_dir: str = ".",
    overwrite: bool = False,
    batch_size: int = 128,
    chunking_strategy: str = "prefix",
):
    if chunking_strategy != "prefix":
        raise ValueError(f"chunking_strategy={chunking_strategy} was passed but only `prefix` is supported.")

    PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
    pc = Pinecone(api_key=PINECONE_API_KEY)

    if index_name is None:
        index_name = model_name
        print(f"Index name not provided, using model name as index name: {index_name}")
    embedding = get_embedding(model_name)
    print("Embedding model loaded")

    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=embedding.dim,
            metric="cosine",
            spec=ServerlessSpec(
                cloud='aws', 
                region='us-east-1'
            ) 
        )
        print(f"Index created: {index_name}")
    else:
        print(f"Index already exists: {index_name}")
    
    index = pc.Index(index_name)
    paths = get_file_paths(root_dir)
    print(f"Found {len(paths)} files in {root_dir}")
    paths = list(filter(is_indexable_file, paths))
    print(f"Found {len(paths)} indexable files")

    paths_batch = []
    pbar = tqdm.tqdm(range(len(paths)))
    skipped = 0
    for i in pbar:
        if not overwrite and record_exists(index, get_record_id(paths[i], chunking_strategy)):
            skipped += 1
            pbar.set_postfix({"skipped": skipped, "indexed": i - skipped})
            continue
        paths_batch.append(paths[i])
        if len(paths_batch) < batch_size and i < len(paths) - 1:
            continue
        contents = []
        for path in paths_batch:
            with open(path, "r") as f:
                content = f.read()
                contents.append(content)
        embeddings = embedding.embed_document(contents, chunking_strategy=chunking_strategy)
        entries = []
        for j, path in enumerate(paths_batch):
            record_id = get_record_id(path, chunking_strategy)
            values = embeddings[j]

            metadata = {
                "path": path,
            }
            entry = {
                "id": record_id,
                "values": values,
                "metadata": metadata,
            }
            entries.append(entry)
        index.upsert(
            vectors=entries,
            namespace=chunking_strategy,
        )
        pbar.set_postfix({"skipped": skipped, "indexed": i - skipped})
        paths_batch = []


if __name__ == "__main__":
    fire.Fire(main)