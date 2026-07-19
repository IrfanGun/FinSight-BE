#app/shared/config.py
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FinSight API"
    database_url: str = "postgresql+psycopg://postgres:4@127.0.0.1:5142/finsight_ai"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    secret_key: str = ""
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property 
    def normalized_secret_key(self) -> str:
        return self.secret_key.strip().strip('"').strip("'")

    @property
    def normalized_database_url(self) -> str:
        return self.database_url.strip().strip('"').strip("'")


@lru_cache
def get_settings() -> Settings:
    return Settings()
