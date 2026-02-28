# Standard library imports
from datetime import date
from typing import Any, Literal

# Third-party imports
import httpx

# Custom imports
from octopy.config import Settings

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