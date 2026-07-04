from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./business_coaching.db"

    # API Keys
    google_api_key: str = ""

    # Security
    secret_key: str = "dev-secret-key"
    debug: bool = False
    use_mock_ai: bool = False

    # CORS
    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
