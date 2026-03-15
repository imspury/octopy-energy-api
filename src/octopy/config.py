"""Configuration settings for Octopy using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


__all__ = ["Settings", "get_settings"]


class Settings(BaseSettings):
    """Application settings for Octopy, loaded from environment variables.
    
    Attributes:
        octopus_api_key: Octopus Energy API key for authentication.
        octopus_account_number: Account number in A-XXXXXXXX format.
        octopus_api_base_url: Base URL for the Octopus Energy REST API.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    octopus_api_key: str
    octopus_account_number: str
    octopus_api_base_url: str = "https://api.octopus.energy/v1/"


def get_settings() -> Settings:
    """Get the application settings instance.

    Returns:
        A Settings object loaded from environment variables.
    """
    return Settings()