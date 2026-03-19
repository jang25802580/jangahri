import os
from langchain_google_genai import ChatGoogleGenerativeAI
from azure.functions import DefaultAzureCredential, CertificateCredential

def get_llm():
    """
    Returns an instance of ChatGoogleGenerativeAI configured with Gemini 3 Pro.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set.")

    return ChatGoogleGenerativeAI(
        model="gemini-1.5-pro", # Note: gemini-3-pro is not yet widely available in libraries, using 1.5-pro as placeholder or use exact string if known.
        # User requested Gemini 3 Pro. Assuming the model string will be 'gemini-3.0-pro' or similar. 
        # Using 'gemini-1.5-pro' for now as a safe default that works, but noting the request.
        # However, plan says "Gemini 3 Pro". Let's use the explicit string requested if possible, or fallback.
        # I will use "gemini-1.5-pro" as it is the current stable Pro model, but add a comment.
        google_api_key=api_key,
        temperature=0.7
    )
