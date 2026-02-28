# Standard library imports
from datetime import date
from typing import Any, Literal

# Third-party imports
import httpx

# Custom imports
from octopy.config import Settings
from octopy.exceptions import OctopusAPIError, OctopusAuthError

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
