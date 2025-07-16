from app.core.config import settings
from langchain_ollama import OllamaEmbeddings


class EmbeddingFactory:
    @staticmethod
    def create():
        embedding_provider = settings.EMBEDDING_PROVIDER.lower()

        if embedding_provider == "ollama":
            return OllamaEmbeddings(
                model=settings.OLLAMA_EMBEDDINGS_MODEL,
                base_url=settings.OLLAMA_API_BASE,
            )
        else:
            raise ValueError(f"Unsupported embedding provider: {embedding_provider}")
