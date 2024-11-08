import requests
from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")


def fetch_restaurant_reviews(query,location,radius=5000):
    api_key=os.getenv("GOOGLE_API_KEY")
    endpoint=f"https://maps.googleapis.com/maps/api/place/textsearch/json"
    search_query=f"restaurants {query}"

    params={
        'query':search_query,
        'location':location,
        'radius':radius,
        'key':api_key
    }

    response=requests.get(endpoint,params=params)
    if response.status_code==200:
        results=response.json().get("results",[])
        reviews_data=[]
        for result in results[:3]:
            restaurant_name=result["name"]
            place_id=result["place_id"]
            review_data=get_reviews_for_place(place_id,api_key)
            reviews_data.append({
                'name':restaurant_name,
                'reviews':review_data
            })
        return reviews_data
    else:
        return []

def get_reviews_for_place(place_id,api_key):
    reviews=[]
    review_endpoint=f"https://maps.googleapis.com/maps/api/place/details/json"
    params={
        'place_id':place_id,
        'fields':'review',
        'key':api_key
    }
    response=requests.get(review_endpoint,params=params)
    if response.status_code==200:
        result=response.json().get("result",{})
        reviews=result.get("reviews",[])

        return [review['text'] for review in reviews]

# if __name__=="__main__":
#     query="Hyderabad"
#     location="17.3580,78.4867"

#     reviews=fetch_restaurant_reviews(query,location)
#     print(reviews)

#     if reviews:
#         for restaurant in reviews:
#             print(f"restaurant name:{restaurant['name']}")
#             print("Reviews:")
#             for review in restaurant['reviews']:
#                 print(f"- {review}")
#     else:
#         print("No reviews found or error occurred")
