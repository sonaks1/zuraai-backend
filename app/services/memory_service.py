import random
from app.vector_memory.chroma_db import (
    collection
)

from app.vector_memory.embedding_service import (
    generate_embedding
)

def save_memory(
    user_id: int,
    message: str,
    emotion: str = "neutral",
    intent: str = "General chat"
):

    embedding = generate_embedding(
        message
    )

    collection.add(
        ids=[f"{user_id}_{message[:10]}_{random.randint(0, 999)}"],
        documents=[message],
        embeddings=[embedding],
        metadatas=[{
            "user_id": user_id,
            "emotion": emotion,
            "intent": intent
        }]
    )