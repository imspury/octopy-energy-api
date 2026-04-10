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
            octopus_api_key="sk_live_testkey123",
            octopus_account_number="A-12345678",
            octopus_api_base_url="https://test.api.url",
        )

        assert settings.octopus_api_key == "sk_live_testkey123"
        assert settings.octopus_account_number == "A-12345678"
        assert settings.octopus_api_base_url == "https://test.api.url"

    def test_settings_with_default_base_url(self) -> None:
        """Test Settings uses default base URL when not provided."""
        settings = Settings(
            octopus_api_key="sk_live_testkey123",
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
        monkeypatch.setenv("OCTOPUS_API_KEY", "sk_live_envkey123")
        monkeypatch.setenv("OCTOPUS_ACCOUNT_NUMBER", "A-87654321")
        monkeypatch.setenv("OCTOPUS_API_BASE_URL", "https://env.api.url")

        settings = Settings()

        assert settings.octopus_api_key == "sk_live_envkey123"
        assert settings.octopus_account_number == "A-87654321"
        assert settings.octopus_api_base_url == "https://env.api.url"

    def test_settings_explicit_overrides_environment(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test explicit parameters override environment variables."""
        monkeypatch.setenv("OCTOPUS_API_KEY", "sk_live_test123")
        monkeypatch.setenv("OCTOPUS_ACCOUNT_NUMBER", "A-87654321")

        settings = Settings(
            octopus_api_key="sk_live_explicit",
            octopus_account_number="A-99999999",
        )

        assert settings.octopus_api_key == "sk_live_explicit"
        assert settings.octopus_account_number == "A-99999999"

    def test_invalid_api_key_format(self) -> None:
        """Test Settings raises ValidationError for invalid API key format."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                octopus_api_key="invalid_key",
                octopus_account_number="A-12345678",
            )

        errors = exc_info.value.errors()
        assert any(
            error["loc"][0] == "octopus_api_key" and "sk_live_" in str(error["msg"])
            for error in errors
        )

    def test_valid_api_key_formats(self) -> None:
        """Test Settings accepts valid API key formats."""
        # Test sk_live_ format
        settings_live = Settings(
            octopus_api_key="sk_live_abc123XYZ",
            octopus_account_number="A-12345678",
        )
        assert settings_live.octopus_api_key == "sk_live_abc123XYZ"

        # Test sk_test_ format
        settings_test = Settings(
            octopus_api_key="sk_test_def456UVW",
            octopus_account_number="A-12345678",
        )
        assert settings_test.octopus_api_key == "sk_test_def456UVW"

    def test_invalid_account_number_format(self) -> None:
        """Test Settings raises ValidationError for invalid account number format."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                octopus_api_key="sk_live_test123",
                octopus_account_number="invalid",
            )

        errors = exc_info.value.errors()
        assert any(
            error["loc"][0] == "octopus_account_number" and "A-" in str(error["msg"])
            for error in errors
        )

    def test_valid_account_number_format(self) -> None:
        """Test Settings accepts valid account number format."""
        settings = Settings(
            octopus_api_key="sk_live_test123",
            octopus_account_number="A-ABC12345",
        )
        assert settings.octopus_account_number == "A-ABC12345"


class TestGetSettings:
    """Tests for the get_settings function."""

    def test_get_settings_returns_settings_instance(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test get_settings returns a Settings instance."""
        monkeypatch.setenv("OCTOPUS_API_KEY", "sk_live_testkey123")
        monkeypatch.setenv("OCTOPUS_ACCOUNT_NUMBER", "A-12345678")

        settings = get_settings()

        assert isinstance(settings, Settings)
        assert settings.octopus_api_key == "sk_live_testkey123"
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
