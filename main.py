import os
import sys
from groq import Groq, RateLimitError, APIError # Import necessary Groq classes
from pick import pick # Add pick import
from colorama import init, Fore, Style # Import colorama
from openai import OpenAI
import glob
from story_utils import save_story, load_story
from dotenv import load_dotenv
load_dotenv()
import os
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


def generate_story_part(client, conversation_history, model="microsoft/wizardlm-2-8x22b:nitro"): #default model for openrouter
    """Generates the next story part using Groq."""
    try:
        completion = client.chat.completions.create(
            messages=conversation_history,
            model=model,
            temperature=0.8, # Adjust creativity
            max_tokens=512, # Limit response length
            top_p=1,
            stop=None, # Can add stop sequences if needed
            stream=True,
        )

        response_content = ""
        for chunk in completion:
            response_content += chunk.choices[0].delta.content
            print(Fore.CYAN + chunk.choices[0].delta.content, end='', flush=True)

        # response_content = completion.choices[0].message.content
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


def generate_story_part_stream(client, conversation_history, model="microsoft/wizardlm-2-8x22b:nitro"):
    """Generates the next story part using OPENAI with streaming."""
    try:
        completion = client.chat.completions.create(
            messages=conversation_history,
            model=model,
            temperature=0.9, # Adjust creativity
            max_tokens=512, # Limit response length
            top_p=1,
            stop=None, # Can add stop sequences if needed
            stream=True,
        )
        print("\n--- Story Continues ---")

        response_content = ""
        for chunk in completion:
            response_content += chunk.choices[0].delta.content
            print(Fore.CYAN + chunk.choices[0].delta.content, end='', flush=True) # Print in cyan as it streams
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
    base_prompt = os.getenv("SYSTEM_PROMPT", "")
    # Construct a system prompt
    user_details = f" The story is in the {genre} genre, set in {setting}. The story begins with: {situation}."
    system_prompt = base_prompt + user_details

    # Return as the first message(s) in the conversation history
    return [{"role": "system", "content": system_prompt}]


# --- Main Application ---
def run_story_app():
    # groq_client, available_models = initialize_groq_client() # Correct unpacking
    # if not groq_client:
    #     return # Exit if client initialization failed

    # selected_model = select_groq_model(available_models) # Call model selection

    openai_client = initialize_openai_client()

    # Choose to start new or resume
    options = ["Start a new story", "Resume a saved story"]
    choice, _ = pick(options, "Choose an option:", indicator="=>")
    if choice == "Resume a saved story":
        saved_files = glob.glob("story_*.json")
        if not saved_files:
            print("No saved stories found. Starting a new story.")
            conversation = get_initial_prompt()
            # Generate initial story part below
        else:
            selected_file, _ = pick(saved_files, "Select a saved story to resume:", indicator="=>")
            conversation = load_story(selected_file)
            if not conversation:
                print("Failed to load story. Starting a new story.")
                conversation = get_initial_prompt()
            else:
                print(f"Resuming story from {selected_file}")
                # Skip initial generation, jump to interaction loop
                initial_assistant_response = conversation[-1]["content"] if conversation and conversation[-1]["role"] == "assistant" else ""
                print(Fore.GREEN + "\n--- Story Resumed ---")
                print(Fore.CYAN + initial_assistant_response)
    else:
        conversation = get_initial_prompt()

    if len(conversation) == 1 and conversation[0]["role"] == "system":
        print(Fore.GREEN + "\n--- Story Start ---")
        initial_assistant_response = generate_story_part_stream(openai_client, conversation)
        if initial_assistant_response:
            conversation.append({"role": "assistant", "content": initial_assistant_response})
            print(Fore.GREEN + "\n-------------------\n")
        else:
            print("Failed to generate initial story part. Exiting.")
            return
    else:
        # Resumed story, skip initial generation
        pass
    print(Fore.GREEN +"\n--- Story Start ---") #for streaming
    initial_assistant_response = generate_story_part_stream(  openai_client, conversation) # Pass selected model

    if initial_assistant_response:
        conversation.append({"role": "assistant", "content": initial_assistant_response})
        # print(initial_assistant_response)
        print(Fore.GREEN + "\n-------------------\n")
    else:
        print("Failed to generate initial story part. Exiting.")
        return

    # Interaction loop
    while True:
        user_action = input("What do you do next? (Type 'save' to save, 'quit' to exit): ").strip().lower()
        if user_action == 'save':
            save_story(conversation)
            continue
        if user_action == 'quit':
            save_choice = input("Do you want to save the story before exiting? (y/n): ").strip().lower()
            if save_choice == 'y':
                save_story(conversation)
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
            # print("\n--- Story Continues ---")
            # print(Fore.CYAN  + next_part)
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