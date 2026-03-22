"""Tests for Octopy client pricing endpoints."""

from datetime import date
from typing import Any

import httpx
import pytest

from octopy import Octopy
from octopy.config import Settings
from octopy.exceptions import OctopusAPIError
from octopy.models import StandingChargesResponse, UnitRatesResponse


class TestGetUnitRates:
    """Tests for get_unit_rates method."""

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_unit_rates_electricity_success(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test get_unit_rates for electricity returns rates."""
        rates_response = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "value_exc_vat": 20.5,
                    "value_inc_vat": 21.525,
                    "valid_from": "2024-03-19T00:00:00Z",
                    "valid_to": "2024-03-19T00:30:00Z",
                    "payment_method": None,
                }
            ],
        }

        respx_mock.get(
            "/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-C/standard-unit-rates/"
        ).mock(return_value=httpx.Response(200, json=rates_response))

        async with Octopy(mock_settings) as client:
            rates = await client.get_unit_rates(
                product_code="AGILE-FLEX-22-11-25",
                tariff_code="E-1R-AGILE-FLEX-22-11-25-C",
                fuel="electricity",
            )

            assert isinstance(rates, UnitRatesResponse)
            assert len(rates.results) == 1
            assert rates.results[0].value_exc_vat == 20.5
            assert rates.results[0].value_inc_vat == 21.525

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_unit_rates_gas_success(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test get_unit_rates for gas returns rates."""
        rates_response = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "value_exc_vat": 10.0,
                    "value_inc_vat": 10.5,
                    "valid_from": "2024-03-19T00:00:00Z",
                    "valid_to": None,
                    "payment_method": None,
                }
            ],
        }

        respx_mock.get(
            "/products/VAR-22-11-01/gas-tariffs/G-1R-VAR-22-11-01-C/standard-unit-rates/"
        ).mock(return_value=httpx.Response(200, json=rates_response))

        async with Octopy(mock_settings) as client:
            rates = await client.get_unit_rates(
                product_code="VAR-22-11-01",
                tariff_code="G-1R-VAR-22-11-01-C",
                fuel="gas",
            )

            assert isinstance(rates, UnitRatesResponse)
            assert len(rates.results) == 1

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_unit_rates_with_date_filters(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test get_unit_rates with date filters."""
        rates_response = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "value_exc_vat": 20.5,
                    "value_inc_vat": 21.525,
                    "valid_from": "2024-03-19T00:00:00Z",
                    "valid_to": "2024-03-19T00:30:00Z",
                    "payment_method": None,
                }
            ],
        }

        period_from = date(2024, 3, 1)
        period_to = date(2024, 3, 19)

        route = respx_mock.get(
            "/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-C/standard-unit-rates/"
        ).mock(return_value=httpx.Response(200, json=rates_response))

        async with Octopy(mock_settings) as client:
            rates = await client.get_unit_rates(
                product_code="AGILE-FLEX-22-11-25",
                tariff_code="E-1R-AGILE-FLEX-22-11-25-C",
                fuel="electricity",
                period_from=period_from,
                period_to=period_to,
            )

            assert isinstance(rates, UnitRatesResponse)

        assert route.called
        request = route.calls.last.request
        assert "period_from" in str(request.url)
        assert "period_to" in str(request.url)

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_unit_rates_with_pagination(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test get_unit_rates auto-paginates results."""
        # First page
        first_page = {
            "count": 2,
            "next": "/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-C/standard-unit-rates/?page=2",
            "previous": None,
            "results": [
                {
                    "value_exc_vat": 20.5,
                    "value_inc_vat": 21.525,
                    "valid_from": "2024-03-19T00:00:00Z",
                    "valid_to": "2024-03-19T00:30:00Z",
                    "payment_method": None,
                }
            ],
        }

        # Second page
        second_page = {
            "count": 2,
            "next": None,
            "previous": "/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-C/standard-unit-rates/?page=1",
            "results": [
                {
                    "value_exc_vat": 18.0,
                    "value_inc_vat": 18.9,
                    "valid_from": "2024-03-19T00:30:00Z",
                    "valid_to": "2024-03-19T01:00:00Z",
                    "payment_method": None,
                }
            ],
        }

        # Mock second page using full URL pattern - register FIRST before base path
        # so it has priority when matching requests with query parameters
        respx_mock.route(url__regex=r".*/standard-unit-rates/\?page=2$").mock(
            return_value=httpx.Response(200, json=second_page)
        )

        # Mock first page - will match requests without page parameter
        respx_mock.get(
            "/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-C/standard-unit-rates/"
        ).mock(return_value=httpx.Response(200, json=first_page))

        async with Octopy(mock_settings) as client:
            rates = await client.get_unit_rates(
                product_code="AGILE-FLEX-22-11-25",
                tariff_code="E-1R-AGILE-FLEX-22-11-25-C",
                fuel="electricity",
                auto_paginate=True,
            )

            assert len(rates.results) == 2
            assert rates.next is None

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_unit_rates_no_auto_paginate(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test get_unit_rates without auto-pagination."""
        rates_response = {
            "count": 2,
            "next": "https://api.octopus.energy/v1/rates/?page=2",
            "previous": None,
            "results": [
                {
                    "value_exc_vat": 20.5,
                    "value_inc_vat": 21.525,
                    "valid_from": "2024-03-19T00:00:00Z",
                    "valid_to": "2024-03-19T00:30:00Z",
                    "payment_method": None,
                }
            ],
        }

        respx_mock.get(
            "/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-C/standard-unit-rates/"
        ).mock(return_value=httpx.Response(200, json=rates_response))

        async with Octopy(mock_settings) as client:
            rates = await client.get_unit_rates(
                product_code="AGILE-FLEX-22-11-25",
                tariff_code="E-1R-AGILE-FLEX-22-11-25-C",
                fuel="electricity",
                auto_paginate=False,
            )

            assert len(rates.results) == 1
            assert rates.next is not None

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_unit_rates_api_error(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test get_unit_rates handles API errors."""
        respx_mock.get(
            "/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-C/standard-unit-rates/"
        ).mock(return_value=httpx.Response(500, text="Server Error"))

        async with Octopy(mock_settings) as client:
            with pytest.raises(OctopusAPIError):
                await client.get_unit_rates(
                    product_code="AGILE-FLEX-22-11-25",
                    tariff_code="E-1R-AGILE-FLEX-22-11-25-C",
                    fuel="electricity",
                )


class TestGetStandingCharges:
    """Tests for get_standing_charges method."""

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_standing_charges_success(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test get_standing_charges returns charges."""
        charges_response = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "value_exc_vat": 45.0,
                    "value_inc_vat": 47.25,
                    "valid_from": "2024-01-01T00:00:00Z",
                    "valid_to": None,
                    "payment_method": None,
                }
            ],
        }

        respx_mock.get(
            "/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-C/standing-charges/"
        ).mock(return_value=httpx.Response(200, json=charges_response))

        async with Octopy(mock_settings) as client:
            charges = await client.get_standing_charges(
                product_code="AGILE-FLEX-22-11-25",
                tariff_code="E-1R-AGILE-FLEX-22-11-25-C",
                fuel="electricity",
            )

            assert isinstance(charges, StandingChargesResponse)
            assert len(charges.results) == 1
            assert charges.results[0].value_exc_vat == 45.0
            assert charges.results[0].value_inc_vat == 47.25

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_standing_charges_gas(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test get_standing_charges for gas tariff."""
        charges_response = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "value_exc_vat": 30.0,
                    "value_inc_vat": 31.5,
                    "valid_from": "2024-01-01T00:00:00Z",
                    "valid_to": None,
                    "payment_method": None,
                }
            ],
        }

        respx_mock.get(
            "/products/VAR-22-11-01/gas-tariffs/G-1R-VAR-22-11-01-C/standing-charges/"
        ).mock(return_value=httpx.Response(200, json=charges_response))

        async with Octopy(mock_settings) as client:
            charges = await client.get_standing_charges(
                product_code="VAR-22-11-01",
                tariff_code="G-1R-VAR-22-11-01-C",
                fuel="gas",
            )

            assert isinstance(charges, StandingChargesResponse)

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_standing_charges_with_date_filters(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test get_standing_charges with date filters."""
        charges_response = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "value_exc_vat": 45.0,
                    "value_inc_vat": 47.25,
                    "valid_from": "2024-01-01T00:00:00Z",
                    "valid_to": None,
                    "payment_method": None,
                }
            ],
        }

        period_from = date(2024, 1, 1)
        period_to = date(2024, 3, 19)

        route = respx_mock.get(
            "/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-C/standing-charges/"
        ).mock(return_value=httpx.Response(200, json=charges_response))

        async with Octopy(mock_settings) as client:
            charges = await client.get_standing_charges(
                product_code="AGILE-FLEX-22-11-25",
                tariff_code="E-1R-AGILE-FLEX-22-11-25-C",
                fuel="electricity",
                period_from=period_from,
                period_to=period_to,
            )

            assert isinstance(charges, StandingChargesResponse)

        assert route.called
        request = route.calls.last.request
        assert "period_from" in str(request.url)
        assert "period_to" in str(request.url)

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_standing_charges_with_pagination(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test get_standing_charges auto-paginates results."""
        # First page
        first_page = {
            "count": 2,
            "next": "/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-C/standing-charges/?page=2",
            "previous": None,
            "results": [
                {
                    "value_exc_vat": 45.0,
                    "value_inc_vat": 47.25,
                    "valid_from": "2024-01-01T00:00:00Z",
                    "valid_to": "2024-06-30T23:59:59Z",
                    "payment_method": None,
                }
            ],
        }

        # Second page
        second_page = {
            "count": 2,
            "next": None,
            "previous": "/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-C/standing-charges/?page=1",
            "results": [
                {
                    "value_exc_vat": 48.0,
                    "value_inc_vat": 50.4,
                    "valid_from": "2024-07-01T00:00:00Z",
                    "valid_to": None,
                    "payment_method": None,
                }
            ],
        }

        # Mock second page using full URL pattern - register FIRST before base path
        # so it has priority when matching requests with query parameters
        respx_mock.route(url__regex=r".*/standing-charges/\?page=2$").mock(
            return_value=httpx.Response(200, json=second_page)
        )

        # Mock first page - will match requests without page parameter
        respx_mock.get(
            "/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-C/standing-charges/"
        ).mock(return_value=httpx.Response(200, json=first_page))

        async with Octopy(mock_settings) as client:
            charges = await client.get_standing_charges(
                product_code="AGILE-FLEX-22-11-25",
                tariff_code="E-1R-AGILE-FLEX-22-11-25-C",
                fuel="electricity",
                auto_paginate=True,
            )

            assert len(charges.results) == 2
            assert charges.next is None

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_standing_charges_api_error(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test get_standing_charges handles API errors."""
        respx_mock.get(
            "/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-C/standing-charges/"
        ).mock(return_value=httpx.Response(500, text="Server Error"))

        async with Octopy(mock_settings) as client:
            with pytest.raises(OctopusAPIError):
                await client.get_standing_charges(
                    product_code="AGILE-FLEX-22-11-25",
                    tariff_code="E-1R-AGILE-FLEX-22-11-25-C",
                    fuel="electricity",
                )
