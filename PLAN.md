# Plan: Interactive Story CLI with Groq AI (v2 - Model Selection)

**Project Goal:** Create a command-line interactive story generator in a single Python file, using Groq AI for story generation, and allowing the user to select the specific Groq model via an interactive menu.

**Core Functionality:**

1.  **Setup:**
    *   Install required Python libraries: `groq`, `pick` (`pip install groq pick`).
    *   Obtain a Groq API key.
    *   Securely manage the API key (e.g., using environment variables).
2.  **Initialize Groq Client & Fetch Models:**
    *   Create an instance of the Groq client using the API key.
    *   Fetch the list of available models from the Groq API (`client.models.list()`).
3.  **Model Selection:**
    *   Present the fetched model IDs to the user in an interactive list using the `pick` library.
    *   Allow navigation with arrow keys and selection with Enter.
    *   Store the chosen model ID.
4.  **Get Initial Prompt:** Ask the user for starting parameters (genre, setting, etc.).
5.  **Maintain Story Context (Conversation History):** Keep track of the story as a list of messages (`[{'role': '...', 'content': '...'}, ...]`).
6.  **Initial Generation:** Send the initial prompt *and the selected model ID* to Groq to generate the first part of the story. Add the AI's response to the conversation history.
7.  **User Interaction Loop:** Continuously display the latest story part, ask for user input, and handle exit commands.
8.  **Subsequent Generation:** Add user input to history, send the entire history *and the selected model ID* to Groq, receive the next part, and add it to history.
9.  **Error Handling:** Basic handling for potential API errors and errors during model fetching/selection.

**Proposed Python File Structure (`story_cli_groq.py` - Conceptual Changes):**

```python
import os
import sys
from groq import Groq, RateLimitError, APIError
from pick import pick # <-- Add import

# ... (GROQ_API_KEY setup) ...

def initialize_groq_client():
    # ... (Initialize client as before) ...
    try:
        # ... (Client initialization) ...
        print("Fetching available models...")
        models_response = client.models.list()
        # Example filtering: Keep models suitable for chat-like interactions
        available_models = sorted([model.id for model in models_response.data if "chat" in model.id or "instruct" in model.id])
        print("Groq client initialized successfully.")
        return client, available_models # <-- Return models too
    except Exception as e:
        # ... (Error handling) ...
        return None, None # <-- Return None for models on error

def select_groq_model(models):
    """Uses 'pick' to let the user select a model."""
    if not models:
        print("Could not fetch models or no suitable models found. Using default.")
        return "llama3-8b-8192" # Fallback default

    title = "Please choose a Groq model to use for the story (navigate with arrows, select with Enter):"
    options = models
    # Try to find a sensible default like llama3-8b
    default_index = 0
    try:
        default_index = options.index("llama3-8b-8192")
    except ValueError:
        pass # Keep default_index 0 if llama3-8b isn't found

    try:
        selected_model, index = pick(options, title, indicator='=>', default_index=default_index)
        print(f"Using model: {selected_model}")
        return selected_model
    except Exception as e: # Catch potential errors during pick usage
        print(f"Error during model selection: {e}. Using default.")
        return "llama3-8b-8192" # Fallback default


def generate_story_part(client, conversation_history, model): # <-- Add model parameter
    """Generates the next story part using the specified Groq model."""
    try:
        # Use the 'model' parameter passed in
        completion = client.chat.completions.create(
            messages=conversation_history,
            model=model,
            temperature=0.7,
            max_tokens=250,
            top_p=1,
            stop=None,
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

# ... (get_initial_prompt remains the same) ...

def run_story_app():
    groq_client, available_models = initialize_groq_client() # <-- Get models
    if not groq_client:
        return

    selected_model = select_groq_model(available_models) # <-- Select model

    conversation = get_initial_prompt()

    print("\nGenerating initial story part...")
    initial_assistant_response = generate_story_part(groq_client, conversation, selected_model) # <-- Pass selected model

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

        conversation.append({"role": "user", "content": user_action})

        print("\nGenerating next story part...")
        next_part = generate_story_part(groq_client, conversation, selected_model) # <-- Pass selected model

        if next_part:
            conversation.append({"role": "assistant", "content": next_part})
            print("\n--- Story Continues ---")
            print(next_part)
            print("---------------------\n")
        else:
            print("Failed to generate the next part. Try again or type 'quit'.")
            if conversation[-1]["role"] == "user":
                 conversation.pop()


# ... (Entry point remains the same) ...
```

**Visual Flow (Mermaid Diagram - Updated):**

```mermaid
graph TD
    A[Start] --> B(Install Groq & Pick Libs?);
    B --> C(Get/Set API Key);
    C --> D(Initialize Groq Client);
    D --> D1(Fetch Available Models);
    D1 -- Success --> D2{Select Model (Pick UI)};
    D1 -- Failure --> D3[Use Default Model];
    D2 --> E(Get Initial Prompt);
    D3 --> E;
    E --> F[Build Initial Conversation History];
    F --> G(Call Groq API - Initial w/ Selected Model);
    G -- Success --> H[Add AI Response to History];
    G -- Failure --> X[Handle API Error / Exit];
    H --> I{Display Current Story Part};
    I --> J{Ask User: "What next? / quit"};
    J --> K{Read User Input};
    K -- Input is 'quit' --> L[End];
    K -- Input is action --> M[Add User Input to History];
    M --> N(Call Groq API - Subsequent w/ Selected Model);
    N -- Success --> O[Add AI Response to History];
    N -- Failure --> P[Handle API Error / Ask Again];
    O --> I;
    P --> J;