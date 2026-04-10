"""Configuration settings for Octopy using pydantic-settings."""

import re

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from octopy.constants import ACCOUNT_NUMBER_PATTERN, API_KEY_PATTERN

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
    octopus_api_base_url: str = "https://api.octopus.energy/v1"

    @field_validator("octopus_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format.

        Args:
            v: The API key to validate.

        Returns:
            The validated API key.

        Raises:
            ValueError: If the API key format is invalid.
        """
        if not re.match(API_KEY_PATTERN, v):
            raise ValueError(
                "API key must start with 'sk_live_' or 'sk_test_' "
                "followed by alphanumeric characters"
            )
        return v

    @field_validator("octopus_account_number")
    @classmethod
    def validate_account_number(cls, v: str) -> str:
        """Validate account number format.

        Args:
            v: The account number to validate.

        Returns:
            The validated account number.

        Raises:
            ValueError: If the account number format is invalid.
        """
        if not re.match(ACCOUNT_NUMBER_PATTERN, v):
            raise ValueError(
                "Account number must be in format 'A-XXXXXXXX' "
                "where X is an alphanumeric character"
            )
        return v


def get_settings() -> Settings:
    """Get the application settings instance.

    Returns:
        A Settings object loaded from environment variables.
    """
    return Settings()
