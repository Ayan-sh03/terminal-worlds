# Plan: Interactive Story CLI with Groq AI (v3 - Colors)

**Project Goal:** Create a command-line interactive story generator in a single Python file, using Groq AI for story generation, allowing model selection, and using colored output for better visual appeal.

**Core Functionality:**

1.  **Setup:**
    *   Install required Python libraries: `groq`, `pick`, `colorama` (`pip install groq pick colorama`).
    *   Obtain a Groq API key.
    *   Securely manage the API key (e.g., using environment variables).
2.  **Initialize Colorama:** Import and initialize `colorama` at the start of the script (`init(autoreset=True)`).
3.  **Initialize Groq Client & Fetch Models:**
    *   Create an instance of the Groq client using the API key.
    *   Fetch the list of available models from the Groq API (`client.models.list()`).
    *   Use colored output for status messages and errors.
4.  **Model Selection:**
    *   Present the fetched model IDs to the user in an interactive list using the `pick` library.
    *   Use colored output for the selection prompt.
    *   Store the chosen model ID.
5.  **Get Initial Prompt:** Ask the user for starting parameters (genre, setting, etc.) using colored prompts.
6.  **Maintain Story Context (Conversation History):** Keep track of the story as a list of messages (`[{'role': '...', 'content': '...'}, ...]`).
7.  **Initial Generation:** Send the initial prompt and the selected model ID to Groq. Use colored status messages.
8.  **User Interaction Loop:**
    *   Display story parts (headings colored, text default).
    *   Ask for user input using colored prompts.
    *   Handle exit commands with colored messages.
9.  **Subsequent Generation:** Add user input to history, send history and model ID to Groq. Use colored status messages.
10. **Error Handling:** Basic handling for potential API errors, model fetching/selection errors, using colored error messages.

**Proposed Python File Structure (`story_cli_groq.py` - Conceptual Changes):**

```python
import os
import sys
from groq import Groq, RateLimitError, APIError
from pick import pick
from colorama import init, Fore, Style # <-- Import colorama

# Initialize colorama
init(autoreset=True) # <-- Initialize with autoreset

# ... (rest of imports and config) ...

# --- Groq Interaction ---
def initialize_groq_client():
    # ... (Use Fore.YELLOW for input prompts, Fore.BLUE for status, Fore.RED for errors) ...

def select_groq_model(models):
    # ... (Use Fore.YELLOW for warnings, Fore.GREEN for title, Fore.BLUE for status, Fore.RED for errors) ...

def generate_story_part(client, conversation_history, model):
    # ... (Use Fore.RED for error messages) ...

# --- Story Logic ---
def get_initial_prompt():
    # ... (Use Style.BRIGHT + Fore.CYAN for heading, Fore.YELLOW for input prompts) ...

# --- Main Application ---
def run_story_app():
    # ... (Calls to initialize/select already have colors) ...
    # ... (Use Fore.BLUE for 'Generating...' status) ...
    # ... (Use Style.BRIGHT + Fore.CYAN for '--- Story Start/Continues ---' headings) ...
    # ... (Use Fore.RED for failure messages) ...
    # ... (Use Fore.YELLOW for 'What do you do next?' prompt) ...
    # ... (Use Fore.MAGENTA for 'Exiting story.' message) ...

# --- Entry Point ---
if __name__ == "__main__":
    # ... (Use Style.BRIGHT + Fore.CYAN for main title) ...
    run_story_app()
```

**Visual Flow (Mermaid Diagram):** (No change from v2, as this primarily affects output presentation)

```mermaid
graph TD
    A[Start] --> B(Install Groq & Pick & Colorama Libs?);
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