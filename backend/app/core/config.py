import os
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "LLMOps"
    VERSION: str = "0.0.1"
    API_V1_STR: str = "/api/v1"

    # PostgreSQL Settings
    POSTGRESQL_SERVER: str = os.getenv("POSTGRESQL_SERVER", "localhost")
    POSTGRESQL_PORT: int = int(os.getenv("POSTGRESQL_PORT", "5432"))
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

    @property
    def get_database_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return (
            f"postgresql+asyncpg://{self.POSTGRESQL_USER}:{self.POSTGRESQL_PASSWORD}"
            f"@{self.POSTGRESQL_SERVER}:{self.POSTGRESQL_PORT}/{self.POSTGRESQL_DATABASE}"
        )

    class Config:
        env_file = ".env"


settings = Settings()
