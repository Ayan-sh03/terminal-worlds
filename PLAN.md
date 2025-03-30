# Plan: Interactive Story CLI with Groq AI

**Project Goal:** Create a command-line interactive story generator in a single Python file, using Groq AI for story generation.

**Core Functionality:**

1.  **Setup:**
    *   Install the `groq` Python library (`pip install groq`).
    *   Obtain a Groq API key.
    *   Securely manage the API key (e.g., using environment variables is recommended).
2.  **Get Initial Prompt:** Ask the user for starting parameters (genre, setting, etc.).
3.  **Initialize Groq Client:** Create an instance of the Groq client using the API key.
4.  **Maintain Story Context (Conversation History):** Keep track of the story as a list of messages (`[{'role': '...', 'content': '...'}, ...]`).
5.  **Initial Generation:** Send the initial prompt to Groq to generate the first part of the story. Add the AI's response to the conversation history.
6.  **User Interaction Loop:** Continuously display the latest story part, ask for user input, and handle exit commands.
7.  **Subsequent Generation:** Add user input to history, send the entire history to Groq, receive the next part, and add it to history.
8.  **Error Handling:** Basic handling for potential API errors (e.g., rate limits, general API issues).

**Proposed Python File Structure (`story_cli_groq.py`):**

```python
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
        GROQ_API_KEY = input("Please enter your Groq API Key: ")
        if not GROQ_API_KEY:
            print("API Key is required. Exiting.")
            sys.exit(1)
    try:
        client = Groq(api_key=GROQ_API_KEY)
        return client
    except APIError as e:
        print(f"Groq API Error during initialization: {e}")
        sys.exit(1)

def generate_story_part(client, conversation_history, model="llama3-8b-8192"):
    """Generates the next story part using Groq."""
    try:
        completion = client.chat.completions.create(
            messages=conversation_history,
            model=model,
            temperature=0.7, # Adjust creativity
            max_tokens=250, # Limit response length
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
        print(f"An unexpected error occurred: {e}")
        return None

# --- Story Logic ---
def get_initial_prompt():
    """Gets initial story parameters from the user."""
    print("Let's start a story!")
    genre = input("Genre (e.g., fantasy, sci-fi): ")
    setting = input("Setting (e.g., a dark forest, a spaceship): ")
    situation = input("Starting situation: ")
    # Construct a system prompt or initial user prompt
    # Example system prompt:
    system_prompt = f"You are an interactive story generator. Create a compelling narrative in the {genre} genre, set in {setting}. The story begins with: {situation}. Continue the story based on user actions."
    # Or initial user prompt:
    # initial_user_prompt = f"Start a {genre} story set in {setting}, beginning with: {situation}"

    # Return as the first message(s) in the conversation history
    # Using system prompt approach here:
    return [{"role": "system", "content": system_prompt}]
    # Using initial user prompt approach:
    # return [{"role": "user", "content": initial_user_prompt}]


# --- Main Application ---
def run_story_app():
    groq_client = initialize_groq_client()
    if not groq_client:
        return # Exit if client initialization failed

    conversation = get_initial_prompt()

    print("\nGenerating initial story part...")
    # Generate the very first part based on the initial prompt
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
            conversation.pop()


# --- Entry Point ---
if __name__ == "__main__":
    print("Interactive Story Generator using Groq AI")
    print("========================================")
    print("Note: You'll need a Groq API key.")
    print("Consider setting the GROQ_API_KEY environment variable for security.")
    run_story_app()
```

**Visual Flow (Mermaid Diagram):**

```mermaid
graph TD
    A[Start] --> B(Install Groq Lib?);
    B --> C(Get/Set API Key);
    C --> D(Initialize Groq Client);
    D --> E(Get Initial Prompt);
    E --> F[Build Initial Conversation History];
    F --> G(Call Groq API - Initial);
    G -- Success --> H[Add AI Response to History];
    G -- Failure --> X[Handle API Error / Exit];
    H --> I{Display Current Story Part};
    I --> J{Ask User: "What next? / quit"};
    J --> K{Read User Input};
    K -- Input is 'quit' --> L[End];
    K -- Input is action --> M[Add User Input to History];
    M --> N(Call Groq API - Subsequent);
    N -- Success --> O[Add AI Response to History];
    N -- Failure --> P[Handle API Error / Ask Again];
    O --> I;
    P --> J;