import streamlit as st
from prompts import TravelPlanner
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    st.error("""
        Please set your OpenAI API key in the .env file.
        
        Steps to fix:
        1. Create a `.env` file in the project root
        2. Add your OpenAI API key: `OPENAI_API_KEY=your_api_key_here`
        3. Restart the application
    """)
    st.stop()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "travel_planner" not in st.session_state:
    try:
        st.session_state.travel_planner = TravelPlanner()
    except Exception as e:
        logger.error(f"Error initializing TravelPlanner: {str(e)}")
        st.error("Failed to initialize the travel planner. Please check your API key and try again.")
        st.stop()

# Set page config
st.set_page_config(
    page_title="Roamyo.ai - AI Travel Planner",
    page_icon="✈️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e6f3ff;
    }
    .assistant-message {
        background-color: #f0f2f6;
    }
    .error-message {
        background-color: #ffebee;
        color: #c62828;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("✈️ Roamyo.ai - AI Travel Planner")
st.markdown("""
    Welcome to your AI-powered travel planning assistant! I'll help you create a personalized travel itinerary.
    Just tell me about your travel plans, and I'll guide you through the process.
""")

# Chat interface
for message in st.session_state.messages:
    with st.container():
        message_class = "error-message" if message.get("error", False) else f"{message['role']}-message"
        st.markdown(f"""
            <div class="chat-message {message_class}">
                <div>{message['content']}</div>
            </div>
        """, unsafe_allow_html=True)

# User input
if prompt := st.chat_input("Tell me about your travel plans..."):
    try:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.container():
            st.markdown(f"""
                <div class="chat-message user-message">
                    <div>{prompt}</div>
                </div>
            """, unsafe_allow_html=True)
        
        # Get AI response
        with st.spinner("Thinking..."):
            response = st.session_state.travel_planner.process_user_input(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Display AI response
            with st.container():
                st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <div>{response}</div>
                    </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Error processing user input: {str(e)}")
        error_message = "I apologize, but I encountered an error while processing your request. Please try again."
        st.session_state.messages.append({"role": "assistant", "content": error_message, "error": True})
        with st.container():
            st.markdown(f"""
                <div class="chat-message error-message">
                    <div>{error_message}</div>
                </div>
            """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("About Roamyo.ai")
    st.markdown("""
        Roamyo.ai is your intelligent travel planning assistant that helps you create
        personalized travel itineraries based on your preferences and requirements.
        
        ### Features:
        - Interactive conversation to gather travel preferences
        - Smart extraction of key travel details
        - Personalized activity suggestions
        - Detailed day-by-day itinerary generation
        - Flexible input handling
    """)
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.travel_planner = TravelPlanner()
        st.rerun() 