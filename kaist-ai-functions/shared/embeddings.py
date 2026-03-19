import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def get_embeddings():
    """
    Returns an instance of GoogleGenerativeAIEmbeddings configured with text-embedding-004.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set.")

    return GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=api_key
    )
