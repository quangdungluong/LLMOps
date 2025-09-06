from typing import Optional

from app.core.config import settings
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI


class LLMFactory:
    @staticmethod
    def create(provider: Optional[str] = None) -> BaseChatModel:
        provider = provider or settings.CHAT_PROVIDER.lower()
        if provider == "gemini":
            return ChatOpenAI(
                model=settings.GOOGLE_GENAI_MODEL,
                api_key=settings.API_KEY,
                base_url=settings.MODEL_BASE_URL,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
