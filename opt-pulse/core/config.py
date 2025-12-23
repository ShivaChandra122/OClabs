from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from schemas.models import DBSettings


class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables.
    """
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db: DBSettings = DBSettings()
    openai_api_key: str = "" # To be filled in .env


@lru_cache()
def get_settings():
    """
    Get cached application settings.
    """
    return Settings()
