import streamlit as st
from dotenv import load_dotenv
from Conversation.get_relevant_data import get_recommendations  # Ensure this import is correct
from Conversation.prompts import generate_recommendation_response  # Import the function you created

# Load environment variables
load_dotenv()

# Streamlit app setup
st.title("Restaurant Query and Recommendations")

# User input for the query
query = st.text_input("Enter a query (e.g., 'Good restaurants for paneer butter masala in Hyderabad')")

# Add a button to trigger recommendation generation
if st.button("Get Recommendations"):
    if query:
        with st.spinner('Processing your request...'):
            # Call the function to get restaurant recommendations

            query, recommendations = get_recommendations(query)
            print(query)
            print(recommendations)
            
            # Check if the city was correctly extracted and handle any error
            # if isinstance(query, str):  # Check if an error message is returned
            #     st.error(query)  # Show error message
            # else:
                # Call the function to generate the detailed recommendation response based on the recommendations
            response = generate_recommendation_response(query, recommendations)
                
                # Display the detailed response in Streamlit
            st.success("Here are your restaurant recommendations:")
            st.write(response)  # Display the response content in Streamlit
    else:
        st.warning("Please enter a valid query to get restaurant recommendations.")

