import os
import sys
from groq import Groq, RateLimitError, APIError # Import necessary Groq classes

# --- Configuration ---
# Recommended: Load API key from environment variable
# GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
# Fallback for simple prototype (less secure):
GROQ_API_KEY = None # Will prompt user if not set

# --- Groq Interaction ---
def initialize_groq_client():
    """Initializes and returns the Groq client."""
    global GROQ_API_KEY
    if not GROQ_API_KEY:
        # Try getting from environment variable first
        GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
        if not GROQ_API_KEY:
            GROQ_API_KEY = input("Please enter your Groq API Key: ")
            if not GROQ_API_KEY:
                print("API Key is required. Exiting.")
                sys.exit(1)
    try:
        client = Groq(api_key=GROQ_API_KEY)
        # Test connection with a simple request (optional but good practice)
        client.models.list()
        print("Groq client initialized successfully.")
        return client
    except APIError as e:
        print(f"Groq API Error during initialization or connection test: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during client initialization: {e}")
        sys.exit(1)


def generate_story_part(client, conversation_history, model="llama3-8b-8192"):
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
        print("Rate limit reached. Please wait and try again.")
        return None
    except APIError as e:
        print(f"Groq API Error during generation: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during generation: {e}")
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
    groq_client = initialize_groq_client()
    if not groq_client:
        return # Exit if client initialization failed

    conversation = get_initial_prompt()

    print("\nGenerating initial story part...")
    # Generate the very first part based on the initial prompt (system message)
    initial_assistant_response = generate_story_part(groq_client, conversation)

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

        print("\nGenerating next story part...")
        # Generate next part based on the *entire* conversation history
        next_part = generate_story_part(groq_client, conversation)

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