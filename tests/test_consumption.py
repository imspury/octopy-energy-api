"""Tests for Octopy client consumption endpoints."""

from datetime import date, datetime
from typing import Any

import httpx
import pytest

from octopy import Octopy
from octopy.config import Settings
from octopy.exceptions import OctopusAPIError
from octopy.models import ConsumptionResponse


class TestGetConsumption:
    """Tests for get_consumption method."""

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_consumption_electricity_success(
        self,
        mock_settings: Settings,
        mock_consumption_response: dict[str, Any],
        respx_mock: pytest.MonkeyPatch,
    ) -> None:
        """Test get_consumption for electricity returns data."""
        respx_mock.get(
            "/electricity-meter-points/1234567890123/meters/12A3456789/consumption/"
        ).mock(return_value=httpx.Response(200, json=mock_consumption_response))

        async with Octopy(mock_settings) as client:
            consumption = await client.get_consumption(
                meter_point="1234567890123",
                serial_number="12A3456789",
                fuel="electricity",
            )

            assert isinstance(consumption, ConsumptionResponse)
            assert consumption.count == 1
            assert len(consumption.results) == 1

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_consumption_gas_success(
        self,
        mock_settings: Settings,
        mock_consumption_response: dict[str, Any],
        respx_mock: pytest.MonkeyPatch,
    ) -> None:
        """Test get_consumption for gas returns data."""
        respx_mock.get(
            "/gas-meter-points/9876543210/meters/12G3456789/consumption/"
        ).mock(return_value=httpx.Response(200, json=mock_consumption_response))

        async with Octopy(mock_settings) as client:
            consumption = await client.get_consumption(
                meter_point="9876543210",
                serial_number="12G3456789",
                fuel="gas",
            )

            assert isinstance(consumption, ConsumptionResponse)

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_consumption_with_date_filters(
        self,
        mock_settings: Settings,
        mock_consumption_response: dict[str, Any],
        respx_mock: pytest.MonkeyPatch,
    ) -> None:
        """Test get_consumption with date filters."""
        period_from = date(2024, 3, 1)
        period_to = date(2024, 3, 19)

        route = respx_mock.get(
            "/electricity-meter-points/1234567890123/meters/12A3456789/consumption/"
        ).mock(return_value=httpx.Response(200, json=mock_consumption_response))

        async with Octopy(mock_settings) as client:
            consumption = await client.get_consumption(
                meter_point="1234567890123",
                serial_number="12A3456789",
                fuel="electricity",
                period_from=period_from,
                period_to=period_to,
            )

            assert isinstance(consumption, ConsumptionResponse)

        # Verify the request was made with date parameters
        assert route.called
        request = route.calls.last.request
        assert "period_from" in str(request.url)
        assert "period_to" in str(request.url)

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_consumption_with_datetime_filters(
        self,
        mock_settings: Settings,
        mock_consumption_response: dict[str, Any],
        respx_mock: pytest.MonkeyPatch,
    ) -> None:
        """Test get_consumption with datetime filters."""
        period_from = datetime(2024, 3, 1, 10, 0, 0)
        period_to = datetime(2024, 3, 19, 18, 30, 0)

        route = respx_mock.get(
            "/electricity-meter-points/1234567890123/meters/12A3456789/consumption/"
        ).mock(return_value=httpx.Response(200, json=mock_consumption_response))

        async with Octopy(mock_settings) as client:
            consumption = await client.get_consumption(
                meter_point="1234567890123",
                serial_number="12A3456789",
                fuel="electricity",
                period_from=period_from,
                period_to=period_to,
            )

            assert isinstance(consumption, ConsumptionResponse)

        assert route.called

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_consumption_with_grouping(
        self,
        mock_settings: Settings,
        mock_consumption_response: dict[str, Any],
        respx_mock: pytest.MonkeyPatch,
    ) -> None:
        """Test get_consumption with grouping parameter."""
        route = respx_mock.get(
            "/electricity-meter-points/1234567890123/meters/12A3456789/consumption/"
        ).mock(return_value=httpx.Response(200, json=mock_consumption_response))

        async with Octopy(mock_settings) as client:
            consumption = await client.get_consumption(
                meter_point="1234567890123",
                serial_number="12A3456789",
                fuel="electricity",
                group_by="day",
            )

            assert isinstance(consumption, ConsumptionResponse)

        assert route.called
        request = route.calls.last.request
        assert "group_by=day" in str(request.url)

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_consumption_with_ordering(
        self,
        mock_settings: Settings,
        mock_consumption_response: dict[str, Any],
        respx_mock: pytest.MonkeyPatch,
    ) -> None:
        """Test get_consumption with order_by parameter."""
        route = respx_mock.get(
            "/electricity-meter-points/1234567890123/meters/12A3456789/consumption/"
        ).mock(return_value=httpx.Response(200, json=mock_consumption_response))

        async with Octopy(mock_settings) as client:
            consumption = await client.get_consumption(
                meter_point="1234567890123",
                serial_number="12A3456789",
                fuel="electricity",
                order_by="period",
            )

            assert isinstance(consumption, ConsumptionResponse)

        assert route.called
        request = route.calls.last.request
        assert "order_by=period" in str(request.url)

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_consumption_with_pagination(
        self,
        mock_settings: Settings,
        mock_consumption_response: dict[str, Any],
        respx_mock: pytest.MonkeyPatch,
    ) -> None:
        """Test get_consumption auto-paginates results."""
        # Create two different consumption intervals for testing
        interval1 = {
            "interval_start": "2024-03-19T00:00:00Z",
            "interval_end": "2024-03-19T00:30:00Z",
            "consumption": 0.123,
        }
        interval2 = {
            "interval_start": "2024-03-19T00:30:00Z",
            "interval_end": "2024-03-19T01:00:00Z",
            "consumption": 0.456,
        }

        # First page response
        first_page = {
            "count": 2,
            "next": "https://api.octopus.energy/v1/electricity-meter-points/1234567890123/meters/12A3456789/consumption/?page=2",
            "previous": None,
            "results": [interval1],
        }

        # Second page response
        second_page = {
            "count": 2,
            "next": None,
            "previous": "https://api.octopus.energy/v1/electricity-meter-points/1234567890123/meters/12A3456789/consumption/?page=1",
            "results": [interval2],
        }

        # Mock second page using full URL pattern - register FIRST before base path
        # so it has priority when matching requests with query parameters
        respx_mock.route(url__regex=r".*/consumption/\?page=2$").mock(
            return_value=httpx.Response(200, json=second_page)
        )

        # Mock first page - will match requests without page parameter
        respx_mock.get(
            "/electricity-meter-points/1234567890123/meters/12A3456789/consumption/"
        ).mock(return_value=httpx.Response(200, json=first_page))

        async with Octopy(mock_settings) as client:
            consumption = await client.get_consumption(
                meter_point="1234567890123",
                serial_number="12A3456789",
                fuel="electricity",
                auto_paginate=True,
            )

            # Should have combined results from both pages
            assert len(consumption.results) == 2
            assert consumption.next is None
            assert consumption.results[0].consumption == 0.123
            assert consumption.results[1].consumption == 0.456

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_consumption_no_auto_paginate(
        self,
        mock_settings: Settings,
        mock_consumption_response: dict[str, Any],
        respx_mock: pytest.MonkeyPatch,
    ) -> None:
        """Test get_consumption without auto-pagination."""
        response_with_next = mock_consumption_response.copy()
        response_with_next["next"] = "https://api.octopus.energy/v1/consumption/?page=2"

        respx_mock.get(
            "/electricity-meter-points/1234567890123/meters/12A3456789/consumption/"
        ).mock(return_value=httpx.Response(200, json=response_with_next))

        async with Octopy(mock_settings) as client:
            consumption = await client.get_consumption(
                meter_point="1234567890123",
                serial_number="12A3456789",
                fuel="electricity",
                auto_paginate=False,
            )

            # Should only have first page results
            assert len(consumption.results) == 1
            assert consumption.next is not None

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_consumption_api_error(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test get_consumption handles API errors."""
        respx_mock.get(
            "/electricity-meter-points/1234567890123/meters/12A3456789/consumption/"
        ).mock(return_value=httpx.Response(500, text="Server Error"))

        async with Octopy(mock_settings) as client:
            with pytest.raises(OctopusAPIError):
                await client.get_consumption(
                    meter_point="1234567890123",
                    serial_number="12A3456789",
                    fuel="electricity",
                )

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_consumption_custom_page_size(
        self,
        mock_settings: Settings,
        mock_consumption_response: dict[str, Any],
        respx_mock: pytest.MonkeyPatch,
    ) -> None:
        """Test get_consumption with custom page size."""
        route = respx_mock.get(
            "/electricity-meter-points/1234567890123/meters/12A3456789/consumption/"
        ).mock(return_value=httpx.Response(200, json=mock_consumption_response))

        async with Octopy(mock_settings) as client:
            consumption = await client.get_consumption(
                meter_point="1234567890123",
                serial_number="12A3456789",
                fuel="electricity",
                page_size=500,
            )

            assert isinstance(consumption, ConsumptionResponse)
            assert consumption.count == 1
            assert len(consumption.results) == 1
            assert consumption.results[0].consumption == 0.123

        assert route.called
        request = route.calls.last.request
        assert "page_size=500" in str(request.url)
