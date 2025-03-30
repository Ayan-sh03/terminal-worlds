import os
import sys
from groq import Groq, RateLimitError, APIError # Import necessary Groq classes
from pick import pick # Add pick import
from colorama import init, Fore, Style # Import colorama
from openai import OpenAI
# Initialize colorama
init(autoreset=True) # Autoreset ensures color resets after each print

# --- Configuration ---
# Recommended: Load API key from environment variable
# GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
# Fallback for simple prototype (less secure):
GROQ_API_KEY = None # Will prompt user if not set
OPENAI_API_KEY = None # Not used in this script, but can be set for other purposes
OPENAI_BASE_URL = "https://openrouter.ai/api/v1" # Not used in this script, but can be set for other purposes

# --- Groq Interaction ---
def initialize_groq_client():
    """Initializes and returns the Groq client."""
    global GROQ_API_KEY
    if not GROQ_API_KEY:
        # Try getting from environment variable first
        GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
        if not GROQ_API_KEY:
            GROQ_API_KEY = input(Fore.YELLOW + "Please enter your Groq API Key: " + Style.RESET_ALL) # Yellow prompt
            if not GROQ_API_KEY:
                print(Fore.RED + "API Key is required. Exiting.") # Red error
                sys.exit(1)

    # Note: Adding try...except block here would be ideal for robust error handling with colors
    client = Groq(api_key=GROQ_API_KEY)
    # Test connection and fetch models
    print(Fore.BLUE + "Fetching available models...") # Blue status
    models_response = client.models.list()
    # print(models_response) # Keep debug print for now
    # Filter for models likely suitable for chat/instruction-following and sort them
    available_models = sorted([
        model.id for model in models_response.data
        if "chat" in model.id or "instruct" in model.id or "llama" in model.id or "mixtral" in model.id
    ])
    print(available_models) # Keep debug print for now
    if not available_models:
            print(Fore.YELLOW + "Warning: No suitable models found or failed to parse model list.") # Yellow warning
            # Let select_groq_model handle the default if list is empty
            available_models = []

    print(Fore.BLUE + "Groq client initialized successfully.") # Blue status
    return client, available_models # Return client and models

def initialize_openai_client():
    """Initializes and returns the OpenAI client."""
    global OPENAI_API_KEY, OPENAI_BASE_URL
    if not OPENAI_API_KEY:
        # Try getting from environment variable first
        OPENAI_API_KEY = os.environ.get("OPENROUTER_API_KEY")
        if not OPENAI_API_KEY:
            OPENAI_API_KEY = input(Fore.YELLOW + "Please enter your OpenAI API Key: " + Style.RESET_ALL) # Yellow prompt
            if not OPENAI_API_KEY:
                print(Fore.RED + "API Key is required. Exiting.") # Red error
                sys.exit(1)

    # Note: Adding try...except block here would be ideal for robust error handling with colors
    client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    print(Fore.BLUE + "OpenAI client initialized successfully.") # Blue status
    return client

def select_groq_model(models):
    """Uses 'pick' to let the user select a model."""
    if not models:
        print(Fore.YELLOW + "Could not fetch models or no suitable models found. Using default: llama3-8b-8192") # Yellow warning
        return "llama3-8b-8192" # Fallback default

    title = Fore.GREEN + "Please choose a Groq model (navigate with arrows, select with Enter):" + Style.RESET_ALL # Green title
    options = models
    # Try to find a sensible default like llama3-8b
    default_index = 0
    try:
        # Attempt to find llama3-8b-8192 and set it as default if present
        default_index = options.index("llama3-8b-8192")
    except ValueError:
        pass # Keep default_index 0 if llama3-8b isn't found

    try:
        selected_model, index = pick(options, title, indicator='=>', default_index=default_index)
        print(Fore.BLUE + f"Using model: {selected_model}") # Blue status
        return selected_model
    except Exception as e: # Catch potential errors during pick usage (e.g., user Ctrl+C)
        # Using f-string with color codes requires careful concatenation or multiple prints
        print(Fore.RED + f"\nError during model selection or selection cancelled: {e}. Using default: llama3-8b-8192") # Red error
        return "llama3-8b-8192" # Fallback default


def generate_story_part(client, conversation_history, model="microsoft/wizardlm-2-8x22b"): #default model for openrouter
    """Generates the next story part using Groq."""
    try:
        completion = client.chat.completions.create(
            messages=conversation_history,
            model=model,
            temperature=0.7, # Adjust creativity
            max_tokens=512, # Limit response length
            top_p=1,
            stop=None, # Can add stop sequences if needed
            stream=False,
        )
        response_content = completion.choices[0].message.content
        return response_content
    except RateLimitError:
        print(Fore.RED + "Rate limit reached. Please wait and try again.") # Red error
        return None
    except APIError as e:
        print(Fore.RED + f"Groq API Error during generation: {e}") # Red error
        return None
    except Exception as e:
        print(Fore.RED + f"An unexpected error occurred during generation: {e}") # Red error
        return None

# --- Story Logic ---
def get_initial_prompt():
    """Gets initial story parameters from the user."""
    print("\nLet's start a story!")
    genre = input("Genre (e.g., fantasy, sci-fi): ")
    setting = input("Setting (e.g., a dark forest, a spaceship): ")
    situation = input("Starting situation: ")

    # Construct a system prompt
    system_prompt = f"You are an interactive story generator. Create a compelling narrative in the {genre} genre, set in {setting}. The story begins with: {situation}. Continue the story based on user actions, keeping responses concise (around 1-3 paragraphs)."

    # Return as the first message(s) in the conversation history
    return [{"role": "system", "content": system_prompt}]


# --- Main Application ---
def run_story_app():
    # groq_client, available_models = initialize_groq_client() # Correct unpacking
    # if not groq_client:
    #     return # Exit if client initialization failed

    # selected_model = select_groq_model(available_models) # Call model selection

    openai_client = initialize_openai_client()
    conversation = get_initial_prompt()

    # print(f"\nGenerating initial story part using {selected_model}...") # Indicate model used
    # Generate the very first part based on the initial prompt (system message)
    initial_assistant_response = generate_story_part(  openai_client, conversation) # Pass selected model

    if initial_assistant_response:
        conversation.append({"role": "assistant", "content": initial_assistant_response})
        print("\n--- Story Start ---")
        print(initial_assistant_response)
        print("-------------------\n")
    else:
        print("Failed to generate initial story part. Exiting.")
        return

    # Interaction loop
    while True:
        user_action = input("What do you do next? (Type 'quit' to exit): ")
        if user_action.lower() == 'quit':
            print("\nExiting story.")
            break

        # Add user action to conversation
        conversation.append({"role": "user", "content": user_action})

        # print(f"\nGenerating next story part using {selected_model}...") # Indicate model used
        # Generate next part based on the *entire* conversation history
        # next_part = generate_story_part(  openai_client, conversation, selected_model) # Pass selected model
        next_part = generate_story_part(  openai_client, conversation) # Pass selected model

        if next_part:
            conversation.append({"role": "assistant", "content": next_part})
            print("\n--- Story Continues ---")
            print(next_part)
            print("---------------------\n")
        else:
            print("Failed to generate the next part. Try again or type 'quit'.")
            # Optional: remove the last user message if generation failed
            if conversation[-1]["role"] == "user":
                 conversation.pop()


# --- Entry Point ---
if __name__ == "__main__":
    print("Interactive Story Generator using Groq AI")
    print("========================================")
    print("Note: You'll need a Groq API key.")
    print("You can set the GROQ_API_KEY environment variable or enter it when prompted.")
    run_story_app()