import os
import openai
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY not found in environment variables.")
    
    client = openai.OpenAI(api_key=api_key)
except Exception as e:
    print(f"Warning: OpenAI API initialization failed: {e}")
    client = None

# Base system message that applies to all roles
BASE_SYSTEM_MESSAGE = "IMPORTANT: All responses must use plain text formatting only. Use '*' or '-' for bullet points, capitalize headers, and use spacing to enhance readability. Do not use Markdown or HTML formatting as the text will be displayed in plain text. This also applies when writing scientific or mathematical equations - format them in plain text without using markdown syntax. Do not use '*' on both sides of a word to make it italic, and don't use '**' to make text bold, it won't work."
BASE_SYSTEM_MESSAGE += "\nIMPORTANT: Whenever a subject and assignment type are provided, make sure to use that information to tailor the response to the specific subject and assignment type."

# Role-specific system messages
ROLE_SYSTEM_MESSAGES = {
    "general": "You are a helpful assistant for students. Provide detailed, accurate, and educational responses.",
    "note_taker": "You are a skilled note-taker for students. Create clear, well-structured notes based on the given topic / main goal and context. Focus on organizing information in a way that makes it easy to understand, remember, and revisit later.",
    "feedback_giver": "You are a feedback provider for student assignments. Review the submitted assignment text and provide constructive, detailed feedback. Include suggestions for improvement, highlight strengths, identify areas needing more work, and provide actionable steps the student can take to improve. Be encouraging but honest in your assessment. Consider the subject area when providing subject-specific feedback.",
    "assignment_starter": "You are an assignment starter helper for students. Based on the assignment description, subject, and assignment type, create an outline or starter content to help the student begin their work. Include key points to address, suggested structure, potential resources to explore, and initial ideas. The goal is to help overcome writer's block and provide a solid foundation, not to complete the assignment. Tailor your suggestions to the specific subject and assignment type."
}

def generate_response(
    topic: str, 
    context: str, 
    role: str = "general",
    model: str = None,
    max_completion_tokens: int = None,
    custom_system_message: str = None
) -> str:
    """
    Generate a response from OpenAI API based on topic and context
    
    Parameters:
    - topic: The main question or topic
    - context: Additional context or information
    - role: The role of the AI (general, note_taker, schedule_planner, assignment_helper)
    - model: The OpenAI model to use
    - max_completion_tokens: Maximum tokens in the response
    - custom_system_message: Optional custom system message to override the role-based one
    
    Returns:
    - The AI generated response as a string
    """
    if client is None:
        return "Error: OpenAI API client not initialized. Please check your API key."
    
    # Get parameters from environment variables if not specified
    if model is None:
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    if max_completion_tokens is None:
        max_tokens_str = os.getenv("MAX_TOKENS", "1000")
        max_completion_tokens = int(max_tokens_str)
    
    # Get the appropriate system message based on role
    if custom_system_message:
        system_message = custom_system_message
    else:
        # Combine base system message with role-specific message
        role_message = ROLE_SYSTEM_MESSAGES.get(role, ROLE_SYSTEM_MESSAGES["general"])
        system_message = f"{BASE_SYSTEM_MESSAGE}\n\n{role_message}"
    
    # Create the user message with topic and context
    user_message = f"Topic: {topic}\n\nContext: {context}"
    
    # Create messages array
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]
    
    try:
        # Make the API call
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_completion_tokens=max_completion_tokens
        )
        
        # Extract and return the response text
        return response.choices[0].message.content or ""
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Function to test if the API key is valid
def test_api_connection() -> bool:
    """Test if the connection to OpenAI API is working"""
    if client is None:
        print("API client not initialized")
        return False
    
    try:
        # Make a simple API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello!"}],
            max_tokens=5
        )
        return True
    except openai.AuthenticationError as e:
        print(f"API authentication failed: {e}")
        return False
    except openai.RateLimitError as e:
        print(f"API rate limit exceeded: {e}")
        return False
    except openai.APIConnectionError as e:
        print(f"API connection error: {e}")
        return False
    except Exception as e:
        print(f"API connection test failed with unknown error: {e}")
        return False 