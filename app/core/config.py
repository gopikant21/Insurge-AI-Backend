from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Database
    database_url: str = Field(
        description="Database connection URL",
    )

    # Redis
    redis_url: str = Field(
        description="Redis connection URL"
    )

    # JWT
    secret_key: str = Field(
        description="JWT secret key",
    )
    algorithm: str = Field(description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        description="Access token expiration in minutes"
    )
    refresh_token_expire_days: int = Field(
        description="Refresh token expiration in days"
    )

    # CORS
    allowed_origins: List[str] = Field(
        description="Allowed CORS origins",
    )

    # Environment
    environment: str = Field(description="Environment")
    debug: bool = Field(description="Debug mode")

    # Optional AI
    openai_api_key: Optional[str] = Field(
        default=None, description="OpenAI API key (optional)"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()