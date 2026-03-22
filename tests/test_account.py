"""Tests for Octopy client account endpoints."""

# Standard library import
from typing import Any

# Third-party imports
import httpx
import pytest

# Custom imports
from octopy import Octopy
from octopy.config import Settings
from octopy.exceptions import OctopusAPIError, OctopusAuthError
from octopy.models import Account, Region


class TestGetAccount:
    """Tests for get_account method."""

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_account_success(
        self,
        mock_settings: Settings,
        mock_account_response: dict[str, Any],
        respx_mock: pytest.MonkeyPatch,
    ) -> None:
        """Test get_account returns account data successfully."""
        respx_mock.get("/accounts/A-12345678/").mock(
            return_value=httpx.Response(200, json=mock_account_response)
        )

        async with Octopy(mock_settings) as client:
            account = await client.get_account()

            assert isinstance(account, Account)
            assert account.number == "A-12345678"
            assert len(account.properties) > 0

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_account_with_custom_number(
        self,
        mock_settings: Settings,
        mock_account_response: dict[str, Any],
        respx_mock: pytest.MonkeyPatch,
    ) -> None:
        """Test get_account with custom account number."""
        custom_response = mock_account_response.copy()
        custom_response["number"] = "A-99999999"

        respx_mock.get("/accounts/A-99999999/").mock(
            return_value=httpx.Response(200, json=custom_response)
        )

        async with Octopy(mock_settings) as client:
            account = await client.get_account(account_number="A-99999999")

            assert account.number == "A-99999999"

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_account_auth_error(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test get_account raises OctopusAuthError on 401."""
        respx_mock.get("/accounts/A-12345678/").mock(
            return_value=httpx.Response(401, text="Unauthorised")
        )

        async with Octopy(mock_settings) as client:
            with pytest.raises(OctopusAuthError) as exc_info:
                await client.get_account()

            assert exc_info.value.status_code == 401
            assert "Authentication failed" in str(exc_info.value)

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_account_api_error(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test get_account raises OctopusAPIError on non-2xx response."""
        respx_mock.get("/accounts/A-12345678/").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )

        async with Octopy(mock_settings) as client:
            with pytest.raises(OctopusAPIError) as exc_info:
                await client.get_account()

            assert exc_info.value.status_code == 500


class TestGetGridSupplyPoint:
    """Tests for get_grid_supply_point method."""

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_grid_supply_point_success(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test get_grid_supply_point returns region successfully."""
        response_data = {
            "count": 1,
            "results": [{"group_id": "_C"}],
        }

        respx_mock.get(
            "/industry/grid-supply-points/", params={"postcode": "SW1A 1AA"}
        ).mock(return_value=httpx.Response(200, json=response_data))

        async with Octopy(mock_settings) as client:
            region = await client.get_grid_supply_point("SW1A 1AA")

            assert region == Region.London

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    @pytest.mark.parametrize(
        "group_id,expected_region",
        [
            ("_A", Region.Eastern),
            ("_B", Region.EastMidlands),
            ("_C", Region.London),
            ("_P", Region.NorthScotland),
        ],
    )
    async def test_get_grid_supply_point_different_regions(
        self,
        mock_settings: Settings,
        respx_mock: pytest.MonkeyPatch,
        group_id: str,
        expected_region: Region,
    ) -> None:
        """Test get_grid_supply_point with different UK regions."""
        response_data = {"count": 1, "results": [{"group_id": group_id}]}

        respx_mock.get(
            "/industry/grid-supply-points/", params={"postcode": "TEST"}
        ).mock(return_value=httpx.Response(200, json=response_data))

        async with Octopy(mock_settings) as client:
            region = await client.get_grid_supply_point("TEST")
            assert region == expected_region

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_grid_supply_point_not_found(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test get_grid_supply_point raises ValueError when no results."""
        response_data = {"count": 0, "results": []}

        respx_mock.get(
            "/industry/grid-supply-points/", params={"postcode": "INVALID"}
        ).mock(return_value=httpx.Response(200, json=response_data))

        async with Octopy(mock_settings) as client:
            with pytest.raises(ValueError) as exc_info:
                await client.get_grid_supply_point("INVALID")

            assert "No GSP data found" in str(exc_info.value)

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_grid_supply_point_api_error(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test get_grid_supply_point handles API errors."""
        respx_mock.get("/industry/grid-supply-points/").mock(
            return_value=httpx.Response(500, text="Server Error")
        )

        async with Octopy(mock_settings) as client:
            with pytest.raises(OctopusAPIError):
                await client.get_grid_supply_point("SW1A 1AA")
