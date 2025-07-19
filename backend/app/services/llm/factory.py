from typing import Optional

from app.core.config import settings
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI


class LLMFactory:
    @staticmethod
    def create(provider: Optional[str] = None) -> BaseChatModel:
        provider = provider or settings.CHAT_PROVIDER.lower()
        if provider == "gemini":
            return ChatGoogleGenerativeAI(
                model=settings.GOOGLE_GENAI_MODEL,
                api_key=settings.GOOGLE_API_KEY,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
