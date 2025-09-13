from app.core.config import settings
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings


class EmbeddingFactory:
    @staticmethod
    def create():
        embedding_provider = settings.EMBEDDING_PROVIDER.lower()

        if embedding_provider == "ollama":
            return OllamaEmbeddings(
                model=settings.OLLAMA_EMBEDDINGS_MODEL,
                base_url=settings.OLLAMA_API_BASE,
            )
        elif embedding_provider == "vllm":
            return OpenAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                base_url=settings.MODEL_BASE_URL,
                api_key=settings.API_KEY,
            )
        else:
            raise ValueError(f"Unsupported embedding provider: {embedding_provider}")
