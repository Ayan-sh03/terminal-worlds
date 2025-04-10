class ConversationHistoryManager:
    """
    Manages conversation history with undo/redo functionality for an interactive story generator.
    """

    def __init__(self, initial_history):
        """
        Initialize with the current conversation history (list of message dicts).
        """
        self.conversation_history = list(initial_history)  # Make a copy to avoid side effects
        self.redo_stack = []

    def can_undo(self):
        # Prevent undoing past the initial system prompt
        return len(self.conversation_history) > 1

    def can_redo(self):
        return len(self.redo_stack) > 0

    def undo(self):
        """
        Undo the last action (user or assistant message).
        Returns a tuple (success: bool, message: str).
        """
        if self.can_undo():
            last_msg = self.conversation_history.pop()
            self.redo_stack.append(last_msg)
            return True, "Last action undone."
        else:
            return False, "Nothing to undo."

    def redo(self):
        """
        Redo the last undone action.
        Returns a tuple (success: bool, message: str).
        """
        if self.can_redo():
            msg = self.redo_stack.pop()
            self.conversation_history.append(msg)
            return True, "Last undone action redone."
        else:
            return False, "Nothing to redo."

    def add_message(self, msg):
        """
        Add a new message (user or assistant) to the conversation.
        Clears the redo stack.
        """
        self.conversation_history.append(msg)
        self.redo_stack.clear()

    def get_history(self):
        """
        Get the current conversation history (for saving, generating, etc.).
        """
        return self.conversation_history

    def reset(self, new_history):
        """
        Reset the conversation history and clear the redo stack.
        """
        self.conversation_history = list(new_history)
        self.redo_stack.clear()