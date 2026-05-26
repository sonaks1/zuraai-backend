from app.vector_memory.chroma_db import collection
from app.vector_memory.embedding_service import generate_embedding

def search_memory(query: str):

    embedding = generate_embedding(query)

    results = collection.query(

        query_embeddings=[embedding],

        n_results=3
    )

    return results