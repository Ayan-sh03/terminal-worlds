import json
from datetime import datetime

def save_story(conversation_history, filename=None):
    """
    Save the conversation history to a JSON file.
    If filename is not provided, generate one with a timestamp.
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"story_{timestamp}.json"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(conversation_history, f, ensure_ascii=False, indent=2)
        print(f"Story saved to {filename}")
    except Exception as e:
        print(f"Error saving story: {e}")

def load_story(filename):
    """
    Load a conversation history from a JSON file.
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            conversation_history = json.load(f)
        print(f"Story loaded from {filename}")
        return conversation_history
    except Exception as e:
        print(f"Error loading story: {e}")
        return None