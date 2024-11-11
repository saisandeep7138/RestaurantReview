from dotenv import load_dotenv
from langchain.prompts.prompt import PromptTemplate
from langchain_openai import ChatOpenAI
# from prompts import get_recommendations

# Load environment variables
load_dotenv()

def get_city(query):
    """Extracts only the city or street name from the query."""
    city_template = """
    Your task is to analyze the provided query and accurately extract any city or street name present within it. 
    Focus solely on identifying the location name—either a city or a street—and return only this specific name as the output, 
    without any additional text or labels.
    Query: {query}
    """
    city_prompt_template = PromptTemplate(
        input_variables=["query"],
        template=city_template
    )
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    chain = city_prompt_template | llm
    response = chain.invoke(input={"query": query})
    return response.content.strip()
    
    

def generate_recommendation_response(query, recommendations):
    """Generate a detailed recommendation response using LangChain."""
    # Define the summary template for the LLM
    summary_template = """
    You are a helpful assistant. You are given a query and some recommendations related to restaurants. 
    Please provide a detailed response to the query, using the information provided in the recommendations.
    Also provide the answer in bullet points 
    ->Strictly check if the item present in the query is a vegetarian item or a non-vegetarian item if vegetarian provide items similar to it or related to it. If item is non-vegetarian provide related non-vegetarian items or similar items

    Query: {query}

    Recommendations:{recommendations}
    """

    # Create the PromptTemplate instance
    summary_prompt_template = PromptTemplate(
        input_variables=["query", "recommendations"], template=summary_template
    )

    # Initialize the OpenAI LLM
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

    # Chain the prompt template and LLM
    chain = summary_prompt_template | llm

    # Invoke the chain to get the response
    response = chain.invoke(input={"query": query, "recommendations": recommendations})

    return response.content

# if __name__ == "__main__":
#     # Define the user query
#     query = "give me some good restaurants for panner butter masala in hyderabad"
    
#     # Call the function to get restaurant recommendations (returns query and recommendations)
#     query, recommendations = get_recommendations(query)

#     # if isinstance(query, str):  # Check for error messages
#     #     print(query)  # Print the error message
#     # else:
#         # Call the function to generate the response based on the recommendations
#     response = generate_recommendation_response(query, recommendations)
#     print(response.content)

# if __name__=="__main__":
#     query="provide me some best restaurants in lb nagar for biryani"
#     print(get_city(query))
