from pinecone import Index

def record_exists(index: Index, record_id: str):
    result = index.fetch(ids=[record_id])
    return record_id in result['vectors']