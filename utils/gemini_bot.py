import os
import re
from datetime import datetime
from google.generativeai import GenerativeModel, configure, list_models

# Configure Gemini once at import
configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_gemini_model():
    """Initialize and return the Gemini model with fallback."""
    try:
        primary_model = "gemini-1.5-pro"
        print(f"Attempting to load model: {primary_model}")
        model = GenerativeModel(primary_model)
        model.generate_content("Hello")  # Test connection
        return model
    except Exception as e:
        print(f"Error with specified model: {e}")
        print("Trying fallback models...")
        fallback_models = [
            "gemini-2.5-pro-preview-03-25",
            "gemini-2.0-flash-lite",
            "gemini-1.5-pro-latest"
        ]
        for name in fallback_models:
            try:
                print(f"Trying {name}")
                model = GenerativeModel(name)
                model.generate_content("Hi")
                print(f"Connected to fallback model: {name}")
                return model
            except:
                continue
        return None

def get_gemini_response(user_input, history=None):
    """Return Gemini response based on input and history."""
    if history is None:
        history = []

    model = get_gemini_model()
    if not model:
        raise Exception("API Limit Exceeded or model unavailable.")

    chat = model.start_chat(history=history)
    response = chat.send_message(user_input)
    return response.text

# # Initialize the Gemini model
# def get_gemini_model():
#     """Initialize and return the Gemini model with proper error handling."""
#     try:
#         # First try the requested model
#         model_name = "gemini-1.5-pro"        
#         try:
#             model = GenerativeModel(model_name)
#             # Test the model with a simple prompt to verify it works
#             response = model.generate_content("Hello")
#             return model
#         except Exception as first_error:
#             print(f"Error with specified model: {first_error}")
            
#             # Get available models and try an alternative
#             models = check_available_models()
            
#             # Try alternative model names
#             alternatives = [
#                 "gemini-2.0-flash-lite",
#                 "gemini-2.0-flash",
#                 "gemini-2.5-pro-preview-03-25",
#                 # Filter for any model containing "gemini" in the name from available models
#                 *[m.name.split("/")[-1] for m in models if "gemini" in m.name.lower()]
#             ]
            
#             for alt_model in alternatives:
#                 try:
#                     print(f"Trying alternative model: {alt_model}")
#                     model = GenerativeModel(alt_model)
#                     # Test with simple prompt
#                     response = model.generate_content("Hello")
#                     print(f"Successfully connected using model: {alt_model}")
#                     return model
#                 except Exception as alt_error:
#                     print(f"Failed with {alt_model}: {alt_error}")
            
#             raise Exception("Could not find a working Gemini model")
#     except Exception as e:
#         print(f"Error initializing Gemini model: {e}")
#         print(f"[Gemini Error] {first_error}")  # 🧨 get error
#         return None

# def get_gemini_response(user_input, history=None):
#     """Get a response from Gemini based on user input and chat history."""
#     try:
#         if history is None:
#             history = []
        
#         model = get_gemini_model()
#         if not model:
#             return "Failed to initialize Gemini model. Please check your API key and connection."
        
#         # Create a chat session to maintain context
#         chat = model.start_chat(history=history)
        
#         # Generate response
#         response = chat.send_message(user_input)
#         response_text = response.text
        
#         # Process text while preserving code blocks
#         processed_text = ""
#         lines = response_text.splitlines()
        
#         in_code_block = False
#         code_block_content = []
#         code_language = ""
        
#         for line in lines:
#             # Check for code block markers
#             if line.startswith("```"):
#                 in_code_block = not in_code_block
#                 if in_code_block:
#                     # Start of code block
#                     if len(line) > 3:
#                         code_language = line[3:].strip()
#                     processed_text += f"```{code_language}\n"
#                 else:
#                     # End of code block
#                     processed_text += "```\n"
#             elif in_code_block:
#                 # Inside code block - keep as is
#                 processed_text += line + "\n"
#             else:
#                 # Outside code block - remove formatting markers
#                 # Remove bold and italic markers but keep the text
#                 cleaned_line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
#                 cleaned_line = re.sub(r'\*(.*?)\*', r'\1', cleaned_line)
                
#                 # For inline code, keep the backticks to preserve code formatting
#                 processed_text += cleaned_line + "\n"
        
#             return processed_text
#     except Exception as e:
#         if "quota" in str(e).lower() or "rate" in str(e).lower() or "limit" in str(e).lower():
#             raise Exception("API Limit Exceeded. Please try again later.")
#         return f"Error getting response from Gemini: {str(e)}"
