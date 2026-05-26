import chromadb

client = chromadb.Client()

collection = client.create_collection(
    name="zuraai_memory"
)