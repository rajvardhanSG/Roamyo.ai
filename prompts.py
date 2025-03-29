import os
from typing import Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
print(os.getenv("OPENAI_API_KEY"))
# Initialize OpenAI client with error handling
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found in environment variables")
    client = OpenAI(
        api_key=api_key,
    )
except Exception as e:
    logger.error(f"Error initializing OpenAI client: {str(e)}")
    raise

class TravelPlanner:
    def __init__(self):
        self.conversation_history = []
        self.user_preferences = {}
        
    def _add_to_history(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})
        
    def _extract_preferences(self, user_input: str) -> Dict:
        """Extract travel preferences from user input using GPT-4."""
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """Extract travel preferences from the user's input.
                    Return a JSON object with the following fields (if found):
                    - destination: The main destination
                    - dates: Travel dates or duration
                    - budget: Budget range or amount
                    - purpose: Main purpose of the trip
                    - preferences: List of specific interests or preferences
                    
                    If a field is not found, omit it from the JSON.
                    Return only the JSON object, no other text."""},
                    {"role": "user", "content": user_input}
                ]
            )
            # Extract JSON from response
            json_str = response.choices[0].message.content.strip()
            # Clean up the response to ensure it's valid JSON
            json_str = re.sub(r'```json\s*|\s*```', '', json_str)
            return eval(json_str)  # Convert string to dict
        except Exception as e:
            logger.error(f"Error extracting preferences: {str(e)}")
            return {}

    def _update_preferences(self, new_preferences: Dict):
        """Update user preferences with new information."""
        for key, value in new_preferences.items():
            if value:  # Only update if value is not empty
                self.user_preferences[key] = value

    def _get_system_prompt(self) -> str:
        return """You are an expert travel planner AI assistant. Your goal is to help users create personalized travel itineraries.
        Follow these guidelines:
        1. Ask clarifying questions to gather all necessary information
        2. Be friendly and conversational
        3. Focus on gathering:
           - Budget
           - Trip duration/dates
           - Destination
           - Purpose
           - Preferences (activities, food, accommodation)
        4. Once you have enough information, provide personalized suggestions
        5. Finally, create a detailed day-by-day itinerary
        
        Keep responses concise and focused on gathering information or providing specific recommendations."""

    def _get_initial_prompt(self) -> str:
        return """Hello! I'm your AI travel planner. I'll help you create a personalized travel itinerary.
        To get started, please tell me:
        1. Where would you like to go?
        2. When are you planning to travel?
        3. What's your budget range?
        4. What's the main purpose of your trip?
        5. Any specific interests or preferences?

        Feel free to share as much or as little as you'd like, and I'll ask follow-up questions as needed."""

    def _get_refinement_prompt(self, missing_info: List[str]) -> str:
        return f"""I notice we're missing some important information. Could you please clarify:
        {', '.join(missing_info)}
        
        This will help me provide more accurate and personalized recommendations."""

    def _get_suggestion_prompt(self, preferences: Dict) -> str:
        return f"""Based on the following preferences:
        {self._format_preferences(preferences)}
        
        Please provide:
        1. Top 5 attractions/activities that match these preferences
        2. 3 hidden gems or off-the-beaten-path experiences
        3. Recommended accommodation options
        4. Local food recommendations
        
        Focus on personalization and unique experiences that match the user's interests."""

    def _get_itinerary_prompt(self, preferences: Dict, suggestions: List[str]) -> str:
        return f"""Create a detailed day-by-day itinerary based on:
        Preferences: {self._format_preferences(preferences)}
        Suggested Activities: {', '.join(suggestions)}
        
        Include:
        1. Logical grouping of activities
        2. Estimated timing for each activity
        3. Travel time between locations
        4. Meal breaks
        5. Flexibility for spontaneous changes
        
        Format the itinerary in a clear, easy-to-follow structure."""

    def _format_preferences(self, preferences: Dict) -> str:
        return "\n".join([f"{k}: {v}" for k, v in preferences.items()])

    def process_user_input(self, user_input: str) -> str:
        try:
            self._add_to_history("user", user_input)
            
            # Extract and update preferences from user input
            new_preferences = self._extract_preferences(user_input)
            self._update_preferences(new_preferences)
            
            # Check if we have enough information
            missing_info = self._check_missing_info()
            if missing_info:
                response = self._get_refinement_prompt(missing_info)
            else:
                # Generate suggestions and itinerary
                suggestions = self._generate_suggestions()
                response = self._generate_itinerary(suggestions)
                
            self._add_to_history("assistant", response)
            return response
        except Exception as e:
            logger.error(f"Error processing user input: {str(e)}")
            return "I apologize, but I encountered an error while processing your request. Please try again or rephrase your question."

    def _check_missing_info(self) -> List[str]:
        required_fields = ["destination", "dates", "budget", "purpose", "preferences"]
        return [field for field in required_fields if field not in self.user_preferences]

    def _generate_suggestions(self) -> List[str]:
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": self._get_suggestion_prompt(self.user_preferences)}
                ]
            )
            return response.choices[0].message.content.split("\n")
        except Exception as e:
            logger.error(f"Error generating suggestions: {str(e)}")
            return ["Error generating suggestions. Please try again."]

    def _generate_itinerary(self, suggestions: List[str]) -> str:
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": self._get_itinerary_prompt(self.user_preferences, suggestions)}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating itinerary: {str(e)}")
            return "I apologize, but I encountered an error while generating your itinerary. Please try again." 