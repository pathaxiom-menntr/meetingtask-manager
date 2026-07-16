"""
ai/client.py — Azure OpenAI client singleton.

Import `client` from here wherever an LLM call is needed.
The object is constructed once at module import time.
"""

from openai import AzureOpenAI

from app.core.config import settings

client: AzureOpenAI = AzureOpenAI(
    api_key=settings.AZURE_OPENAI_API_KEY,
    api_version=settings.AZURE_OPENAI_API_VERSION,
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
)
