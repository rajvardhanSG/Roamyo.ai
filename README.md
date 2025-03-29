# Roamyo.ai - AI-Powered Travel Planner

An intelligent travel planning assistant that creates personalized travel itineraries based on user preferences and requirements.

## Features

- Interactive conversation to gather travel preferences
- Smart extraction of key travel details
- Personalized activity suggestions
- Detailed day-by-day itinerary generation
- Flexible input handling

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Start the application
2. Enter your travel preferences in the chat interface
3. The AI will ask clarifying questions if needed
4. Receive personalized travel suggestions and itineraries

## Project Structure

- `app.py`: Main Streamlit application
- `prompts.py`: AI system prompts and conversation logic
- `requirements.txt`: Project dependencies
- `.env`: Environment variables (create this file) 