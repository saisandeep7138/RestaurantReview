import os
import openai
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import hashlib

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
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def embed_and_store_chunks(restaurant_data, location, similarity_threshold=0.9):
    for restaurant_name, chunk in restaurant_data:
        text_chunks = chunk_text(chunk)
        
        for i, chunk in enumerate(text_chunks):
            # Generate the embedding
            response = openai.embeddings.create(input=chunk, model="text-embedding-ada-002")
            embedding = response.data[0].embedding
            
            if embedding:
                # Generate a unique hash ID based on the query and location
                unique_id = hashlib.sha256(f"{restaurant_name}_{location}_chunk_{i}".encode('utf-8')).hexdigest()
                
                # Search Pinecone to check if this chunk already exists in the index
                search_results = index.query(
                    vector=embedding,
                    top_k=1,  # We only need to check the top match
                    filter={"location": location},  # Filter by location
                    include_metadata=True
                )
                
                if search_results['matches']:
                    existing_match = search_results['matches'][0]
                    # If the similarity score of the existing match is high enough, skip the upsert
                    if existing_match['score'] >= similarity_threshold:
                        print(f"Skipping duplicate chunk for {restaurant_name} at location {location}")
                        continue  # Skip the current chunk since it's a duplicate
                
                # If it's not a duplicate, upsert the embedding
                metadata = {
                    "restaurant_name": restaurant_name,
                    "text": chunk,
                    "location": location  # Include location in the metadata
                }

                upsert_response = index.upsert([{
                    "id": unique_id,
                    "values": embedding,
                    "metadata": metadata
                }])

                print(f"Upserted {unique_id} with location {location}: {upsert_response}")
            else:
                print(f"Failed to generate embedding for {restaurant_name} chunk {i}")


def search_similar_embeddings(query, top_k=5):
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
        #location=match['metadata']['location']
        similarity_score = match['score']
        similar_documents.append({
            "restaurant_name": restaurant_name,
            "text": text,
            #"location":location,
            "similarity_score": similarity_score
        })
    
    return similar_documents


# if __name__ == "__main__":
#     query = "give me some good restaurants to try pav bhaji in mumbai"
#     check_existing_data(query)
