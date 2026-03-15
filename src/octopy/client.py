# Standard library imports
from datetime import date, datetime
from typing import Any, Literal, TypeVar

# Third-party imports
import httpx
from pydantic import BaseModel

# Custom imports
from octopy.config import Settings
from octopy.exceptions import OctopusAPIError, OctopusAuthError
from octopy.models import (
    Account,
    Region,
    ConsumptionResponse,
    ProductsResponse,
    ProductDetail,
    UnitRatesResponse,
    StandingChargesResponse,
)

# TypeVar for paginated response types
T = TypeVar("T", bound=BaseModel)


class Octopy:
    """Async client for interacting with the Octopus Energy REST API.

    Uses httpx.AsyncClient for async HTTP requests and authenticates using
    HTTP Basic Auth with the API key as username and empty password.

    Attributes:
        settings: Application settings containing API key and base URL.
        client: The httpx async client instance.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialise the Octopus Energy API client.

        Args:
           settings: Application settings with API credentials.
        """
        self.settings = settings
        self.client = httpx.AsyncClient(
            base_url=settings.octopus_api_base_url,
            auth=(settings.octopus_api_key, ""),
            timeout=30.0,
        )

    async def __aenter__(self) -> "Octopy":
        """Async context manager entry.

        Returns:
            The client instance.
        """
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit.

        Args:
            exc_type: Exception type if an exception occurred.
            exc_val: Exception value if an exception occurred.
            exc_tb: Exception traceback if an exception occurred.
        """
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client connection."""
        await self.client.aclose()

    async def _get_url(self, url: str) -> httpx.Response:
        """Fetch data from an arbitrary URL.

        This is used internally for pagination to follow 'next' URLs.

        Args:
            url: Full URL to fetch (can be absolute or relative to base URL).

        Returns:
            The HTTP response object.

        Raises:
            OctopusAuthError: If authentication fails.
            OctopusAPIError: If the API returns a non-2xx response.
        """
        response = await self.client.get(url)

        if not (200 <= response.status_code < 300):
            self._handle_response_error(response)

        return response

    def _handle_response_error(self, response: httpx.Response) -> None:
        """Handle non-2xx responses from the API.

        Args:
            response: The HTTP response object.

        Raises:
            OctopusAuthError: If the response status is 401 or 403.
            OctopusAPIError: For any other non-2xx status code.
        """
        if response.status_code in (401, 403):
            raise OctopusAuthError(detail=f"Authentication failed: {response.text}")
        raise OctopusAPIError(
            status_code=response.status_code,
            detail=f"API request failed: {response.text}",
        )

    def _format_datetime(self, dt: date | datetime, end_of_day: bool = False) -> str:
        """Format a date or datetime for the API.

        Args:
            dt: A date or datetime object.
            end_of_day: If True and dt is a date, use 23:59:59 instead of 00:00:00.

        Returns:
            ISO 8601 formatted string with UTC timezone indicator.
        """
        if isinstance(dt, datetime):
            if dt.tzinfo is None:
                return dt.isoformat() + "Z"
            return dt.isoformat()
        else:
            time_str = "T23:59:59Z" if end_of_day else "T00:00:00Z"
            return f"{dt.isoformat()}{time_str}"

    async def _auto_paginate_response(self, response: T) -> T:
        """Automatically fetch all pages of a paginated response.

        Args:
            response: The initial response object from a paginated endpoint.

        Returns:
            A new response object with all results from all pages combined.
        """
        all_results = list(response.results)
        next_url = getattr(response, "next", None)

        while next_url:
            next_response = await self._get_url(next_url)
            page_data = next_response.json()
            # Parse using the same model type as the original response
            page = type(response)(**page_data)
            all_results.extend(page.results)
            next_url = getattr(page, "next", None)

        # Return a new response with all results
        return type(response)(
            count=response.count,
            next=None,
            previous=None,
            results=all_results,
        )

    async def get_account(self, account_number: str | None = None) -> Account:
        """Fetch account data including properties and meter points.

        Args:
            account_number: The account number (e.g. A-XXXXXXXX).
                If None, uses the account number from settings.

        Returns:
            An Account object with properties and meter points.

        Raises:
            OctopusAuthError: If authentication fails.
            OctopusAPIError: If the API returns a non-2xx response.
        """
        acc_num = account_number or self.settings.octopus_account_number
        url = f"/accounts/{acc_num}/"

        response = await self.client.get(url)

        if not (200 <= response.status_code < 300):
            self._handle_response_error(response)

        data = response.json()
        return Account(**data)

    async def get_grid_supply_point(self, postcode: str) -> Region:
        """Fetch the Grid Supply Point (GSP) code from postcode.

        Args:
            postcode: The postcode to look up.
        
        Returns:
            A Region enum representing the GSP region identifier.

        Raises:
            OctopusAPIError: If the API request fails.
            ValueError: If the postcode is invalid or GSP cannot be found.
        """
        url = "/industry/grid-supply-points/"
        params: dict[str, Any] = {"postcode": postcode}

        response = await self.client.get(url, params=params)

        if not (200 <= response.status_code < 300):
            self._handle_response_error(response)
        
        data = response.json()
        results = data.get("results", [])

        if results:
            group_id = results[0]["group_id"]
            return Region(group_id)
        else:
            raise ValueError(f"No GSP data found for postcode: {postcode}")

    async def get_consumption(
        self,
        meter_point: str,
        serial_number: str,
        fuel: Literal["electricity", "gas"] = "electricity",
        period_from: date | datetime | None = None,
        period_to: date | datetime | None = None,
        page_size: int = 100,
        order_by: str | None = None,
        group_by: str | None = None,
        auto_paginate: bool = True,
    ) -> ConsumptionResponse:
        """Fetch consumption data for a specific meter point and serial number.

        Args:
            meter_point: The meter point reference number.
                For electricity: MPAN (Meter Point Administration Number).
                For gas: MPRN (Meter Point Reference Number).
            serial_number: The meter serial number.
            fuel: The fuel type, either 'electricity' or 'gas' (default: 'electricity').
            period_from: Start of the consumption period (inclusive).
                Can be date (interpreted as midnight) or datetime for specific time.
            period_to: End of the consumption period (inclusive).
                Can be date (interpreted as end of day) or datetime for specific time.
            page_size: Number of results per page (default 100, max 25000).
            order_by: Order results by 'period' for earliest first.
                Without this, latest records are returned first.
            group_by: Aggregate data by 'day', 'week', 'month', or 'quarter'.
                Aggregation is based on local time, not UTC.
            auto_paginate: If True (default), automatically fetch all pages.
                If False, only return the first page.

        Returns:
            A ConsumptionResponse with consumption intervals.
            When auto_paginate is True, all results are included and next/previous are None.

        Note:
            For gas: SMETS1 meters return consumption in kWh, while SMETS2 meters
            return consumption in cubic meters.

        Raises:
            OctopusAuthError: If authentication fails.
            OctopusAPIError: If the API returns a non-2xx response.
        """
        if fuel == "electricity":
            url = f"/electricity-meter-points/{meter_point}/meters/{serial_number}/consumption/"
        else:
            url = f"/gas-meter-points/{meter_point}/meters/{serial_number}/consumption/"

        params: dict[str, Any] = {"page_size": page_size}

        if period_from:
            params["period_from"] = self._format_datetime(period_from)
        if period_to:
            params["period_to"] = self._format_datetime(period_to, end_of_day=True)
        if order_by:
            params["order_by"] = order_by
        if group_by:
            params["group_by"] = group_by

        response = await self.client.get(url, params=params)

        if not (200 <= response.status_code < 300):
            self._handle_response_error(response)

        data = response.json()
        consumption_response = ConsumptionResponse(**data)

        if auto_paginate and consumption_response.next:
            return await self._auto_paginate_response(consumption_response)

        return consumption_response

    async def get_products(
        self,
        is_variable: bool | None = None,
        is_green: bool | None = None,
        is_tracker: bool | None = None,
        is_prepay: bool | None = None,
        is_business: bool | None = None,
        available_at: date | datetime | None = None,
    ) -> ProductsResponse:
        """Fetch available energy products.

        Args:
            is_variable: Filter for variable rate products.
            is_green: Filter for green/renewable products.
            is_tracker: Filter for tracker products that follow wholesale prices.
            is_prepay: Filter for prepayment products.
            is_business: Filter for business products.
            available_at: Filter for products available at a specific date.

        Returns:
            A ProductsResponse with a list of products.

        Raises:
            OctopusAPIError: If the API returns a non-2xx response.
        """
        url = "/products/"
        params: dict[str, Any] = {}

        if is_variable is not None:
            params["is_variable"] = is_variable
        if is_green is not None:
            params["is_green"] = is_green
        if is_tracker is not None:
            params["is_tracker"] = is_tracker
        if is_prepay is not None:
            params["is_prepay"] = is_prepay
        if is_business is not None:
            params["is_business"] = is_business
        if available_at:
            params["available_at"] = self._format_datetime(available_at)

        response = await self.client.get(url, params=params)

        if not (200 <= response.status_code < 300):
            self._handle_response_error(response)

        data = response.json()
        return ProductsResponse(**data)

    async def get_product(self, product_code: str) -> ProductDetail:
        """Fetch detailed information for a specific product.

        Args:
            product_code: The product code (e.g. AGILE-FLEX-22-11-25).

        Returns:
            A ProductDetail object with tariff information.

        Raises:
            OctopusAPIError: If the API returns a non-2xx response.
        """
        url = f"/products/{product_code}/"

        response = await self.client.get(url)

        if not (200 <= response.status_code < 300):
            self._handle_response_error(response)

        data = response.json()
        return ProductDetail(**data)

    async def get_unit_rates(
        self,
        product_code: str,
        tariff_code: str,
        fuel: Literal["electricity", "gas"] = "electricity",
        period_from: date | datetime | None = None,
        period_to: date | datetime | None = None,
        page_size: int = 100,
        auto_paginate: bool = True,
    ) -> UnitRatesResponse:
        """Fetch unit rates for a tariff.

        Args:
            product_code: The product code (e.g. AGILE-FLEX-22-11-25).
            tariff_code: The tariff code.
                For electricity: E-1R-AGILE-FLEX-22-11-25-C
                For gas: G-1R-AGILE-FLEX-22-11-25-C
            fuel: The fuel type, either 'electricity' or 'gas' (default: 'electricity').
            period_from: Start date for rates (inclusive).
            period_to: End date for rates (inclusive).
            page_size: Number of results per page (default 100).
            auto_paginate: If True (default), automatically fetch all pages.
                If False, only return the first page.

        Returns:
            A UnitRatesResponse with unit rates.
            When auto_paginate is True, all results are included and next/previous are None.

        Raises:
            OctopusAPIError: If the API returns a non-2xx response.
        """
        if fuel == "electricity":
            url = f"/products/{product_code}/electricity-tariffs/{tariff_code}/standard-unit-rates/"
        else:
            url = f"/products/{product_code}/gas-tariffs/{tariff_code}/standard-unit-rates/"

        params: dict[str, Any] = {"page_size": page_size}

        if period_from:
            params["period_from"] = self._format_datetime(period_from)
        if period_to:
            params["period_to"] = self._format_datetime(period_to, end_of_day=True)

        response = await self.client.get(url, params=params)

        if not (200 <= response.status_code < 300):
            self._handle_response_error(response)

        data = response.json()
        unit_rate_response = UnitRatesResponse(**data)

        if auto_paginate and unit_rate_response.next:
            return await self._auto_paginate_response(unit_rate_response)

        return unit_rate_response

    async def get_standing_charges(
        self,
        product_code: str,
        tariff_code: str,
        fuel: Literal["electricity", "gas"] = "electricity",
        period_from: date | datetime | None = None,
        period_to: date | datetime | None = None,
        auto_paginate: bool = True,
    ) -> StandingChargesResponse:
        """Fetch standing charges for a tariff.

        Args:
            product_code: The product code (e.g. AGILE-FLEX-22-11-25).
            tariff_code: The tariff code.
                For electricity: E-1R-AGILE-FLEX-22-11-25-C
                For gas: G-1R-AGILE-FLEX-22-11-25-C
            fuel: The fuel type, either 'electricity' or 'gas' (default: 'electricity').
            period_from: Start date for charges (inclusive).
            period_to: End date for charges (inclusive).
            auto_paginate: If True (default), automatically fetch all pages.
                If False, only return the first page.

        Returns:
            A StandingChargesResponse with daily standing charges.
            When auto_paginate is True, all results are included and next/previous are None.

        Raises:
            OctopusAPIError: If the API returns a non-2xx response.
        """
        if fuel == "electricity":
            url = f"/products/{product_code}/electricity-tariffs/{tariff_code}/standing-charges/"
        else:
            url = (
                f"/products/{product_code}/gas-tariffs/{tariff_code}/standing-charges/"
            )

        params: dict[str, Any] = {}

        if period_from:
            params["period_from"] = self._format_datetime(period_from)
        if period_to:
            params["period_to"] = self._format_datetime(period_to, end_of_day=True)

        response = await self.client.get(url, params=params)

        if not (200 <= response.status_code < 300):
            self._handle_response_error(response)

        data = response.json()
        standing_charge_response = StandingChargesResponse(**data)

        if auto_paginate and standing_charge_response.next:
            return await self._auto_paginate_response(standing_charge_response)
        
        return standing_charge_response
