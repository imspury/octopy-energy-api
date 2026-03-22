"""Tests for configuration management."""

# Third-party imports
import pytest
from pydantic import ValidationError
from pydantic_settings import SettingsConfigDict

# Custom import
from octopy.config import Settings, get_settings


class TestSettings:
    """Tests for the Settings class."""

    def test_settings_with_all_values(self) -> None:
        """Test Settings initialisation with all values provided."""
        settings = Settings(
            octopus_api_key="test_key",
            octopus_account_number="A-12345678",
            octopus_api_base_url="https://test.api.url",
        )

        assert settings.octopus_api_key == "test_key"
        assert settings.octopus_account_number == "A-12345678"
        assert settings.octopus_api_base_url == "https://test.api.url"

    def test_settings_with_default_base_url(self) -> None:
        """Test Settings uses default base URL when not provided."""
        settings = Settings(
            octopus_api_key="test_key",
            octopus_account_number="A-12345678",
        )

        assert settings.octopus_api_base_url == "https://api.octopus.energy/v1"

    def test_settings_missing_required_fields(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test Settings raises ValidationError when required fields are missing."""
        # Clear any existing environment variables
        monkeypatch.delenv("OCTOPUS_API_KEY", raising=False)
        monkeypatch.delenv("OCTOPUS_ACCOUNT_NUMBER", raising=False)
        monkeypatch.delenv("OCTOPUS_API_BASE_URL", raising=False)

        # Temporarily disable .env file loading for this test
        original_config = Settings.model_config
        monkeypatch.setattr(
            Settings,
            "model_config",
            SettingsConfigDict(env_file=None, env_file_encoding="utf-8"),
        )

        try:
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            errors = exc_info.value.errors()
            error_fields = {error["loc"][0] for error in errors}

            assert "octopus_api_key" in error_fields
            assert "octopus_account_number" in error_fields
        finally:
            # Restore original config
            Settings.model_config = original_config

    def test_settings_from_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Settings loads from environment variables."""
        monkeypatch.setenv("OCTOPUS_API_KEY", "env_key")
        monkeypatch.setenv("OCTOPUS_ACCOUNT_NUMBER", "A-87654321")
        monkeypatch.setenv("OCTOPUS_API_BASE_URL", "https://env.api.url")

        settings = Settings()

        assert settings.octopus_api_key == "env_key"
        assert settings.octopus_account_number == "A-87654321"
        assert settings.octopus_api_base_url == "https://env.api.url"

    def test_settings_explicit_overrides_environment(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test explicit parameters override environment variables."""
        monkeypatch.setenv("OCTOPUS_API_KEY", "env_key")
        monkeypatch.setenv("OCTOPUS_ACCOUNT_NUMBER", "A-87654321")

        settings = Settings(
            octopus_api_key="explicit_key",
            octopus_account_number="A-99999999",
        )

        assert settings.octopus_api_key == "explicit_key"
        assert settings.octopus_account_number == "A-99999999"


class TestGetSettings:
    """Tests for the get_settings function."""

    def test_get_settings_returns_settings_instance(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test get_settings returns a Settings instance."""
        monkeypatch.setenv("OCTOPUS_API_KEY", "test_key")
        monkeypatch.setenv("OCTOPUS_ACCOUNT_NUMBER", "A-12345678")

        settings = get_settings()

        assert isinstance(settings, Settings)
        assert settings.octopus_api_key == "test_key"
        assert settings.octopus_account_number == "A-12345678"

    def test_get_settings_raises_on_missing_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test get_settings raises ValidationError when env vars are missing."""
        # Clear any existing environment variables
        monkeypatch.delenv("OCTOPUS_API_KEY", raising=False)
        monkeypatch.delenv("OCTOPUS_ACCOUNT_NUMBER", raising=False)
        monkeypatch.delenv("OCTOPUS_API_BASE_URL", raising=False)

        # Temporarily disable .env file loading for this test
        original_config = Settings.model_config
        monkeypatch.setattr(
            Settings,
            "model_config",
            SettingsConfigDict(env_file=None, env_file_encoding="utf-8"),
        )

        try:
            with pytest.raises(ValidationError):
                get_settings()
        finally:
            # Restore original config
            Settings.model_config = original_config
