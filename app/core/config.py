from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "infra-lab"
    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = "sqlite:///./infra_lab.db"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:8000"])

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
