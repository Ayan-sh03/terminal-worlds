import json
from datetime import datetime

def save_story(conversation_history, filename=None):
    """
    Save the conversation history to a JSON file.
    If filename is not provided, generate one with a timestamp.
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Extract snippet from first system or assistant message
        snippet = ""
        for msg in conversation_history:
            if msg.get("role") in ("system", "assistant"):
                content = msg.get("content", "")
                words = content.strip().split()
                snippet = "_".join(words[:5]).lower()
                # Remove punctuation and limit length
                import re
                snippet = re.sub(r'\W+', '_', snippet)
                snippet = snippet[:20]
                break

        filename = f"story_{timestamp}"
        if snippet:
            filename += f"_{snippet}"
        filename += ".json"
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