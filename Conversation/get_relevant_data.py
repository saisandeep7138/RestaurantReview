# recommendation_chain.py
import openai 
from langchain.llms import OpenAI
import os
from dotenv import load_dotenv
from langchain.prompts.prompt import PromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from geopy.geocoders import Nominatim
from Data_processing.data_fetcher import fetch_restaurant_reviews
from Data_processing.data_processor import process_reviews_to_chunks,embed_and_store_chunks,search_similar_embeddings
from Data_processing.embedder import get_embeddings
import re
from Conversation.prompts import get_city

# Load environment variables
load_dotenv()


# Initialize geolocator
geolocator = Nominatim(user_agent="restaurant_recommender")

def extract_city(query):
    """Extracts the city name from a query using a simple regex."""
    # match = re.search(r"in (\w+)$", query)
    # if match:
    #     return match.group(1)
    # else:
    #     return None
    #let's try to extract the city from the query using llm call
    response=get_city(query)
    print(response)
    return response


def get_recommendations(query):
    """Processes the user's query and returns restaurant recommendations."""
    # Step 1: Extract city from query
    #print(type(query))
    city = extract_city(query)
    print(f"The extracted city is {city}")

    if not city:
        return "City could not be extracted from the query. Please provide a valid query like 'Good restaurants in [City Name]'."

    # Step 2: Geocode city to get latitude and longitude
    location = geolocator.geocode(city)
    print(location)

    if not location:
        return f"Could not find location for {city}. Please try another city."

    lat, lon = location.latitude, location.longitude
    location_str = f"{lat},{lon}"
    print(location_str)

    # Step 3: Fetch restaurant data
    restaurant_data = fetch_restaurant_reviews(query, location_str)
    print(f"The restaurant data is: \n{restaurant_data}")

    # Step 4: Process data into chunks
    chunks = process_reviews_to_chunks(restaurant_data)
    print(f"The chunks we got from restaurant data:\n{chunks}")

    #step5:embed and store chunks
    embed_and_store_chunks(chunks,location=city)



    # Step 6: Retrieve similar chunks for recommendations
    similar_chunks = search_similar_embeddings(query)
    grouped_texts = {}
    for match in similar_chunks:
        restaurant_name = match['restaurant_name']
        text = match['text']
        #location=match['location']
        if restaurant_name not in grouped_texts:
            grouped_texts[restaurant_name] = []
        
        grouped_texts[restaurant_name].append(text)
        #grouped_texts[restaurant_name].append(location)
        
    #print(similar_chunks)

    # Prepare the formatted recommendation string
    recommendations = ""
    for restaurant_name, texts,in grouped_texts.items():
        recommendations += f"{restaurant_name}:\n" + "\n".join(texts) +"\n\n"

    print(f"The whole data which we'll be sending to the LLM is :\n{recommendations}")

    return  query,recommendations

# if __name__=="__main__":
#     query="provide best restaurants in jubliee hills for biryani"
#     get_recommendations(query)
