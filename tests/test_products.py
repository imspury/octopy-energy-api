"""Tests for Octopy client product endpoints."""

# Standard library imports
from datetime import date
from typing import Any

# Third-party imports
import httpx
import pytest

# Custom imports
from octopy import Octopy
from octopy.config import Settings
from octopy.exceptions import OctopusAPIError
from octopy.models import ProductDetail, ProductsResponse


class TestGetProducts:
    """Tests for get_products method."""

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_products_success(
        self,
        mock_settings: Settings,
        mock_products_response: dict[str, Any],
        respx_mock: pytest.MonkeyPatch,
    ) -> None:
        """Test get_products returns products list."""
        respx_mock.get("/products/").mock(
            return_value=httpx.Response(200, json=mock_products_response)
        )

        async with Octopy(mock_settings) as client:
            products = await client.get_products()

            assert isinstance(products, ProductsResponse)
            assert products.count == 1
            assert len(products.results) == 1

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_products_with_is_green_filter(
        self,
        mock_settings: Settings,
        mock_products_response: dict[str, Any],
        respx_mock: pytest.MonkeyPatch,
    ) -> None:
        """Test get_products with is_green filter."""
        route = respx_mock.get("/products/").mock(
            return_value=httpx.Response(200, json=mock_products_response)
        )

        async with Octopy(mock_settings) as client:
            products = await client.get_products(is_green=True)

            assert isinstance(products, ProductsResponse)

        assert route.called
        request = route.calls.last.request
        assert "is_green=true" in str(request.url).lower()

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_products_with_is_variable_filter(
        self,
        mock_settings: Settings,
        mock_products_response: dict[str, Any],
        respx_mock: pytest.MonkeyPatch,
    ) -> None:
        """Test get_products with is_variable filter."""
        route = respx_mock.get("/products/").mock(
            return_value=httpx.Response(200, json=mock_products_response)
        )

        async with Octopy(mock_settings) as client:
            products = await client.get_products(is_variable=False)

            assert isinstance(products, ProductsResponse)

        assert route.called
        request = route.calls.last.request
        assert "is_variable=false" in str(request.url).lower()

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_products_with_multiple_filters(
        self,
        mock_settings: Settings,
        mock_products_response: dict[str, Any],
        respx_mock: pytest.MonkeyPatch,
    ) -> None:
        """Test get_products with multiple filter parameters."""
        route = respx_mock.get("/products/").mock(
            return_value=httpx.Response(200, json=mock_products_response)
        )

        async with Octopy(mock_settings) as client:
            products = await client.get_products(
                is_green=True,
                is_variable=True,
                is_tracker=False,
                is_prepay=True,
                is_business=False,
            )

            assert isinstance(products, ProductsResponse)

        assert route.called
        request = route.calls.last.request
        url_str = str(request.url).lower()
        assert "is_green=true" in url_str
        assert "is_variable=true" in url_str
        assert "is_tracker=false" in url_str
        assert "is_prepay=true" in url_str
        assert "is_business=false" in url_str

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_products_with_available_at_filter(
        self,
        mock_settings: Settings,
        mock_products_response: dict[str, Any],
        respx_mock: pytest.MonkeyPatch,
    ) -> None:
        """Test get_products with available_at date filter."""
        available_at = date(2024, 3, 19)

        route = respx_mock.get("/products/").mock(
            return_value=httpx.Response(200, json=mock_products_response)
        )

        async with Octopy(mock_settings) as client:
            products = await client.get_products(available_at=available_at)

            assert isinstance(products, ProductsResponse)

        assert route.called
        request = route.calls.last.request
        assert "available_at" in str(request.url)

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_products_api_error(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test get_products handles API errors."""
        respx_mock.get("/products/").mock(
            return_value=httpx.Response(500, text="Server Error")
        )

        async with Octopy(mock_settings) as client:
            with pytest.raises(OctopusAPIError):
                await client.get_products()


class TestGetProduct:
    """Tests for get_product method."""

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_product_success(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test get_product returns product details."""
        product_detail_data = {
            "code": "AGILE-FLEX-22-11-25",
            "full_name": "Agile Octopus November 2022 v1",
            "display_name": "Agile Octopus",
            "description": "Agile Octopus pricing.",
            "is_variable": True,
            "is_green": True,
            "is_tracker": False,
            "is_prepay": False,
            "is_business": False,
            "is_restricted": False,
            "term": None,
            "available_from": "2022-11-25T00:00:00Z",
            "available_to": None,
            "brand": "OCTOPUS_ENERGY",
            "links": [],
            "single_register_electricity_tariffs": {},
            "dual_register_electricity_tariffs": {},
            "single_register_gas_tariffs": {},
            "sample_quotes": {},
            "sample_consumption": {},
        }

        respx_mock.get("/products/AGILE-FLEX-22-11-25/").mock(
            return_value=httpx.Response(200, json=product_detail_data)
        )

        async with Octopy(mock_settings) as client:
            product = await client.get_product("AGILE-FLEX-22-11-25")

            assert isinstance(product, ProductDetail)
            assert product.code == "AGILE-FLEX-22-11-25"
            assert product.display_name == "Agile Octopus"
            assert product.is_green is True

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_product_with_tariffs(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test get_product returns product with tariff information."""
        product_detail_data = {
            "code": "AGILE-FLEX-22-11-25",
            "full_name": "Agile Octopus November 2022 v1",
            "display_name": "Agile Octopus",
            "description": "Agile pricing.",
            "is_variable": True,
            "is_green": True,
            "is_tracker": False,
            "is_prepay": False,
            "is_business": False,
            "is_restricted": False,
            "term": None,
            "available_from": "2022-11-25T00:00:00Z",
            "available_to": None,
            "brand": "OCTOPUS_ENERGY",
            "links": [],
            "single_register_electricity_tariffs": {
                "_A": {
                    "direct_debit_monthly": {
                        "code": "E-1R-AGILE-FLEX-22-11-25-A",
                        "standing_charge_exc_vat": 41.0,
                        "standing_charge_inc_vat": 43.05,
                        "online_discount_exc_vat": 0.0,
                        "dual_fuel_discount_exc_vat": 0.0,
                        "exit_fees_exc_vat": 0.0,
                        "exit_fees_inc_vat": 0.0,
                        "exit_fees_type": "NONE",
                        "links": [],
                    }
                }
            },
            "dual_register_electricity_tariffs": {},
            "single_register_gas_tariffs": {},
            "sample_quotes": {},
            "sample_consumption": {},
        }

        respx_mock.get("/products/AGILE-FLEX-22-11-25/").mock(
            return_value=httpx.Response(200, json=product_detail_data)
        )

        async with Octopy(mock_settings) as client:
            product = await client.get_product("AGILE-FLEX-22-11-25")

            assert isinstance(product, ProductDetail)
            assert len(product.single_register_electricity_tariffs) > 0

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_product_not_found(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test get_product raises error for non-existent product."""
        respx_mock.get("/products/INVALID-PRODUCT-CODE/").mock(
            return_value=httpx.Response(404, text="Not Found")
        )

        async with Octopy(mock_settings) as client:
            with pytest.raises(OctopusAPIError) as exc_info:
                await client.get_product("INVALID-PRODUCT-CODE")

            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    @pytest.mark.respx(base_url="https://api.octopus.energy/v1")
    async def test_get_product_api_error(
        self, mock_settings: Settings, respx_mock: pytest.MonkeyPatch
    ) -> None:
        """Test get_product handles API errors."""
        respx_mock.get("/products/AGILE-FLEX-22-11-25/").mock(
            return_value=httpx.Response(500, text="Server Error")
        )

        async with Octopy(mock_settings) as client:
            with pytest.raises(OctopusAPIError):
                await client.get_product("AGILE-FLEX-22-11-25")
