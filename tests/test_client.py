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
        assert (
            str(client.client.base_url).rstrip("/")
            == mock_settings.octopus_api_base_url
        )

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


class TestRetryLogic:
    """Tests for retry logic and error handling."""

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_retry_on_500_error(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test retry logic on 500 server error."""

        # Mock consecutive failures then success
        route = respx_mock.get("/test")
        route.side_effect = [
            httpx.Response(500, text="Server Error"),
            httpx.Response(200, json={"test": "data"}),
        ]

        async with Octopy(mock_settings) as client:
            # Mock the _sleep method to avoid actual delays
            client._sleep = lambda x: __import__("asyncio").sleep(0)
            response = await client._get_url("/test")
            assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_retry_exhaustion(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test retry logic exhausts and raises error."""
        from octopy.exceptions import OctopusAPIError

        # Mock all attempts to fail
        respx_mock.get("/test").mock(
            return_value=httpx.Response(500, text="Server Error")
        )

        async with Octopy(mock_settings) as client:
            # Mock the _sleep method to avoid actual delays
            client._sleep = lambda x: __import__("asyncio").sleep(0)
            with pytest.raises(OctopusAPIError) as exc_info:
                await client._get_url("/test", retries=2)

            assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_retry_on_timeout(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test retry logic on timeout error."""

        # Mock timeout then success
        route = respx_mock.get("/test")
        route.side_effect = [
            httpx.TimeoutException("Request timeout"),
            httpx.Response(200, json={"test": "data"}),
        ]

        async with Octopy(mock_settings) as client:
            # Mock the _sleep method to avoid actual delays
            client._sleep = lambda x: __import__("asyncio").sleep(0)
            response = await client._get_url("/test")
            assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_retry_on_network_error(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test retry logic on network error."""
        from octopy.exceptions import OctopusAPIError

        # Mock network error
        respx_mock.get("/test").mock(
            side_effect=httpx.NetworkError("Connection failed")
        )

        async with Octopy(mock_settings) as client:
            # Mock the _sleep method to avoid actual delays
            client._sleep = lambda x: __import__("asyncio").sleep(0)
            with pytest.raises(OctopusAPIError) as exc_info:
                await client._get_url("/test", retries=1)

            assert "Network error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_sleep_method(self, mock_settings: Settings) -> None:
        """Test the _sleep method."""
        import time

        client = Octopy(mock_settings)
        start = time.time()
        await client._sleep(0.1)
        elapsed = time.time() - start

        assert elapsed >= 0.1


class TestDateTimeFormatting:
    """Tests for datetime formatting helper."""

    def test_format_datetime_from_datetime_with_tz(
        self, mock_settings: Settings
    ) -> None:
        """Test _format_datetime with timezone-aware datetime."""
        from datetime import datetime
        from zoneinfo import ZoneInfo

        client = Octopy(mock_settings)
        dt = datetime(2024, 3, 19, 10, 30, 0, tzinfo=ZoneInfo("Europe/London"))

        formatted = client._format_datetime(dt)

        # Should preserve timezone info
        assert "2024-03-19" in formatted
        assert "10:30:00" in formatted

    def test_format_datetime_from_datetime_no_tz(self, mock_settings: Settings) -> None:
        """Test _format_datetime with naive datetime."""
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
