"""Tests for core Octopy client functionality."""

# Third-party imports
import httpx
import pytest

# Custom imports
from octopy import Octopy
from octopy.config import Settings


class TestOctopyInitialisation:
    """Tests for Octopy client initialisation."""

    def test_client_initialisation(self, mock_settings: Settings) -> None:
        """Test Octopy client initialises with settings."""
        client = Octopy(mock_settings)

        assert client.settings == mock_settings
        assert isinstance(client.client, httpx.AsyncClient)
        assert str(client.client.base_url).rstrip("/") == mock_settings.octopus_api_base_url

    def test_client_auth_configuration(self, mock_settings: Settings) -> None:
        """Test client is configured with HTTP Basic Auth."""
        client = Octopy(mock_settings)

        # Check auth is configured
        assert client.client.auth is not None
        # Auth should be BasicAuth with api_key as username
        assert isinstance(client.client.auth, httpx.BasicAuth)
        # Verify the credentials by checking the auth flow
        auth = client.client.auth
        assert auth._auth_header.startswith("Basic ")

    @pytest.mark.asyncio
    async def test_client_context_manager(self, mock_settings: Settings) -> None:
        """Test Octopy works as async context manager."""
        async with Octopy(mock_settings) as client:
            assert isinstance(client, Octopy)
            assert client.client is not None

    @pytest.mark.asyncio
    async def test_client_close(self, mock_settings: Settings) -> None:
        """Test client close method."""
        client = Octopy(mock_settings)
        await client.close()

        # After closing, the client should be closed
        assert client.client.is_closed


class TestErrorHandling:
    """Tests for error handling methods."""

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_handle_401_unauthorised(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test 401 Unauthorised raises OctopusAuthError."""
        from octopy.exceptions import OctopusAuthError

        respx_mock.get("/accounts/A-12345678/").mock(
            return_value=httpx.Response(401, text="Unauthorised")
        )

        async with Octopy(mock_settings) as client:
            with pytest.raises(OctopusAuthError):
                await client.get_account()

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_handle_403_forbidden(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test 403 Forbidden raises OctopusAuthError."""
        from octopy.exceptions import OctopusAuthError

        respx_mock.get("/accounts/A-12345678/").mock(
            return_value=httpx.Response(403, text="Forbidden")
        )

        async with Octopy(mock_settings) as client:
            with pytest.raises(OctopusAuthError):
                await client.get_account()

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_handle_404_not_found(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test 404 Not Found raises OctopusAPIError."""
        from octopy.exceptions import OctopusAPIError

        respx_mock.get("/accounts/A-NOTFOUND/").mock(
            return_value=httpx.Response(404, text="Not Found")
        )

        async with Octopy(mock_settings) as client:
            with pytest.raises(OctopusAPIError) as exc_info:
                await client.get_account(account_number="A-NOTFOUND")

            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_handle_500_server_error(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test 500 Server Error raises OctopusAPIError."""
        from octopy.exceptions import OctopusAPIError

        respx_mock.get("/accounts/A-12345678/").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )

        async with Octopy(mock_settings) as client:
            with pytest.raises(OctopusAPIError) as exc_info:
                await client.get_account()

            assert exc_info.value.status_code == 500


class TestDateTimeFormatting:
    """Tests for datetime formatting helper."""

    def test_format_datetime_from_datetime_with_tz(
        self, mock_settings: Settings
    ) -> None:
        """Test _format_datetime with timezone-aware datetime."""
        from datetime import datetime

        client = Octopy(mock_settings)
        dt = datetime(2024, 3, 19, 10, 30, 0)

        formatted = client._format_datetime(dt)

        assert formatted == "2024-03-19T10:30:00Z"

    def test_format_datetime_from_date(self, mock_settings: Settings) -> None:
        """Test _format_datetime from date object."""
        from datetime import date

        client = Octopy(mock_settings)
        d = date(2024, 3, 19)

        formatted = client._format_datetime(d)

        assert formatted == "2024-03-19T00:00:00Z"

    def test_format_datetime_from_date_end_of_day(
        self, mock_settings: Settings
    ) -> None:
        """Test _format_datetime from date with end_of_day flag."""
        from datetime import date

        client = Octopy(mock_settings)
        d = date(2024, 3, 19)

        formatted = client._format_datetime(d, end_of_day=True)

        assert formatted == "2024-03-19T23:59:59Z"
