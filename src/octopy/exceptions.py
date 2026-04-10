"""Custom exceptions for Octopus Energy API interactions."""


class OctopusAPIError(Exception):
    """Base exception for Octopus Energy API errors.

    Raised when the Octopus Energy API returns a non-2xx response.

    Attributes:
        status_code: HTTP status code from the API response.
        detail: Error message or additional details.
    """

    def __init__(self, status_code: int, detail: str) -> None:
        """Initialise the OctopusAPIError.

        Args:
            status_code: HTTP status code from the API response.
            detail: Error message or additional details.
        """
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Octopus API error {status_code}: {detail}")


class OctopusAuthError(OctopusAPIError):
    """Exception raised for authentication failures (401/403).

    Raised when the API key is invalid or lacks permissions.
    """

    def __init__(self, detail: str = "Authentication failed") -> None:
        """Initialise the OctopusAuthError.

        Args:
            detail: Error message or additional details.
        """
        super().__init__(status_code=401, detail=detail)
