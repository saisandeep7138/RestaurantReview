import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_environment = os.getenv("PINECONE_ENV")

# Initialize Pinecone instance
pc = Pinecone(api_key=pinecone_api_key)

# Define index name
index_name = "restaurant-reviews"

# Connect to the index or create it if it does not exist
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,  # Specify the dimension based on your embeddings
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region=pinecone_environment)
    )

# Connect to the existing index
index = pc.Index(index_name)

# Delete all vectors in the index
index.delete(delete_all=True)
print(f"All vectors in index '{index_name}' have been deleted.")
