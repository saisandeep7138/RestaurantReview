import streamlit as st
from dotenv import load_dotenv
from Conversation.get_relevant_data import get_recommendations  # Ensure this import is correct
from Conversation.prompts import generate_recommendation_response  # Import the function you created

# Load environment variables
load_dotenv()

# Streamlit app setup
st.title("Restaurant Query and Recommendations")

# Initialize session state for conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Display conversation history
for message in st.session_state.conversation_history:
    if message['role'] == 'user':
        st.markdown(f"**You:** {message['text']}")
    elif message['role'] == 'bot':
        st.markdown(f"**Bot:** {message['text']}")

# User input for the query
query = st.text_input("Enter your question:")

# Add a button to trigger recommendation generation
if st.button("Ask"):
    if query:
        with st.spinner('Processing your request...'):
            # Add user query to conversation history
            st.session_state.conversation_history.append({"role": "user", "text": query})
            
            # Call the function to get restaurant recommendations
            query, recommendations = get_recommendations(query)
            
            # Call the function to generate the detailed recommendation response based on the recommendations
            response = generate_recommendation_response(query, recommendations)
            
            # Add bot response to conversation history
            st.session_state.conversation_history.append({"role": "bot", "text": response})

            # Display the updated conversation
            st.experimental_rerun()  # Re-run to update UI with new conversation content
    else:
        st.warning("Please enter a valid query to get restaurant recommendations.")
