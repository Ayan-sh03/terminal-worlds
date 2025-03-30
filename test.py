from .story_cli_groq import initialize_groq_client


def test_initialize_groq_client():
    # Test the Groq client initialization
    client = initialize_groq_client()

    print(client
    )