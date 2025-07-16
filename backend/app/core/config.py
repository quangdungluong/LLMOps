import os
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "LLMOps"
    VERSION: str = "0.0.1"
    API_V1_STR: str = "/api/v1"
    MEDIA_ROOT: str = os.getenv("MEDIA_ROOT", "media")

    # PostgreSQL Settings
    POSTGRESQL_SERVER: str = os.getenv("POSTGRESQL_SERVER", "localhost")
    POSTGRESQL_PORT: int = int(os.getenv("POSTGRESQL_PORT", "54320"))
    POSTGRESQL_USER: str = os.getenv("POSTGRESQL_USER", "llmops")
    POSTGRESQL_PASSWORD: str = os.getenv("POSTGRESQL_PASSWORD", "llmops")
    POSTGRESQL_DATABASE: str = os.getenv("POSTGRESQL_DATABASE", "llmops")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080")
    )

    # Embedding Settings
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "ollama")

    # Vector Store Settings
    VECTOR_STORE_PROVIDER: str = os.getenv("VECTOR_STORE_PROVIDER", "milvus")

    # Ollama Settings
    OLLAMA_API_BASE: str = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
    OLLAMA_EMBEDDINGS_MODEL: str = os.getenv(
        "OLLAMA_EMBEDDINGS_MODEL", "nomic-embed-text"
    )

    # Milvus Settings
    MILVUS_URI: str = os.getenv("MILVUS_URI", "http://localhost:19530")

    @property
    def get_database_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return (
            f"postgresql+asyncpg://{self.POSTGRESQL_USER}:{self.POSTGRESQL_PASSWORD}"
            f"@{self.POSTGRESQL_SERVER}:{self.POSTGRESQL_PORT}/{self.POSTGRESQL_DATABASE}"
        )

    @property
    def get_database_url_sync(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return (
            f"postgresql://{self.POSTGRESQL_USER}:{self.POSTGRESQL_PASSWORD}"
            f"@{self.POSTGRESQL_SERVER}:{self.POSTGRESQL_PORT}/{self.POSTGRESQL_DATABASE}"
        )

    class Config:
        env_file = ".env"


settings = Settings()
