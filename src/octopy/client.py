# Standard library imports
from datetime import date, datetime
from typing import Any, Literal

# Third-party import
import httpx

# Custom imports
from octopy.config import Settings
from octopy.exceptions import OctopusAPIError, OctopusAuthError
from octopy.models import (
    Account,
    ConsumptionResponse,
)

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
    
    async def __aenter__(self):
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

        if response.status_code != 200:
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
            raise OctopusAuthError(
                detail=f"Authentication failed: {response.text}"
            )
        raise OctopusAPIError(
            status_code=response.status_code,
            detail=f"API request failed: {response.text}"
        )

    def _format_datetime(
            self, dt: date | datetime, end_of_day: bool = False
    ) -> str:
        """Format a date or datetime for the API.
        
        Args:
            dt: A date or datetime object.
            end_of_day: If True and dt is a date, use 23:59:59 instead of 00:00:00.
        
        Returns:
            ISO 8601 formatted string with UTC timezone indicator.
        """
        if isinstance(dt, datetime):
            return dt.isoformat() + "Z" if dt.tzinfo is None else dt.isoformat()
        else:
            time_str = "T23:59:59Z" if end_of_day else "T00:00:00Z"
            return f"{dt.isoformat()}{time_str}"

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

        if response.status_code != 200:
            self._handle_response_error(response)
        
        data = response.json()
        return Account(**data)
    
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
        
        Returns:
            A ConsumptionResponse with consumption intervals.

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

        if response.status_code != 200:
            self._handle_response_error(response)
        
        data = response.json()
        return ConsumptionResponse(**data)
