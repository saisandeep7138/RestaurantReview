
import os
import openai
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_environment = os.getenv("PINECONE_ENV")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI API
openai.api_key = openai_api_key

# Initialize Pinecone with the new Pinecone instance-based approach
pc = Pinecone(api_key=pinecone_api_key)

# Define index name
index_name = "restaurant-reviews"

# Create index if it doesn't already exist
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,  # Adjust dimension according to your embedding model (text-embedding-ada-002)
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region=pinecone_environment)
    )

# Connect to the index
index = pc.Index(index_name)

def process_reviews_to_chunks(restaurant_data):
    chunks = []
    for restaurant in restaurant_data:
        restaurant_name = restaurant['name']
        reviews = "\n".join(restaurant['reviews'])
        chunk = f"Restaurant: {restaurant_name}\nReviews:\n{reviews}"
        chunks.append((restaurant_name, chunk))
    return chunks

def chunk_text(text, chunk_size=300):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def embed_and_store_chunks(restaurant_data):
    for restaurant_name, chunk in restaurant_data:
        text_chunks = chunk_text(chunk)
        
        for i, chunk in enumerate(text_chunks):
            # Generate the embedding
            response = openai.embeddings.create(input=chunk, model="text-embedding-ada-002")
            embedding = response.data[0].embedding
            
            # Check that embedding was successfully generated
            if embedding:
                unique_id = f"{restaurant_name}_chunk_{i}"
                metadata = {"restaurant_name": restaurant_name, "text": chunk}

                # Upsert to Pinecone
                upsert_response = index.upsert([{
                    "id": unique_id,
                    "values": embedding,
                    "metadata": metadata
                }])

                # Check the response for successful upsert
                print(f"Upserted {unique_id}: {upsert_response}")
            else:
                print(f"Failed to generate embedding for {restaurant_name} chunk {i}")

# def check_existing_data(query):
#     #check if similar data alreaady exists
#     #generate embedding for the query
#     response=openai.embeddings.create(input=query,model="text-embedding-ada-002")
#     query_embedding=response.data[0].embedding

#     search_result=index.query(
#         vector=query_embedding,
#         top_k=3,
#         include_medata=True
#     )
#     print(search_result)
#     if search_result['matches']:
#         return True, search_result['matches'][0]
    
#     return False,None

def search_similar_embeddings(query, top_k=3):
    # Generate embedding for the query
    response = openai.embeddings.create(input=query, model="text-embedding-ada-002")
    query_embedding = response.data[0].embedding    
    # Perform the search in Pinecone
    results = index.query(
        vector=query_embedding,   # Query vector (embedding of the user's query)
        top_k=top_k,              # Number of top results to fetch
        include_metadata=True     # Include metadata in results (to get restaurant names and text)
    )
    
    # Extract the relevant metadata and text from the results
    similar_documents = []
    for match in results['matches']:
        restaurant_name = match['metadata']['restaurant_name']
        text = match['metadata']['text']
        similarity_score = match['score']
        similar_documents.append({
            "restaurant_name": restaurant_name,
            "text": text,
            "similarity_score": similarity_score
        })
    
    return similar_documents

# if __name__ == "__main__":
#     query="give me some good restaurants to try pav bhaji in mumbai"
#     check_existing_data(query)