from app.services.openai_service import client

async def generate_embedding(text: str):
    """
    Uses OpenAI's text-embedding-3-small for faster, offloaded embeddings.
    """
    try:
        response = await client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding Error: {e}")
        # Return a zero vector as fallback
        return [0.0] * 1536