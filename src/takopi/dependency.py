from google import genai

from common.core.settings import settings

def get_client():
    return genai.Client(vertexai=False,api_key=settings.GOOGLE_API_KEY)

def get_gemini_model():
    client = get_client()
    return client.aio.models
