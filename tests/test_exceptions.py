"""Tests for exception classes."""

# Third-party import
import pytest

# Custom import
from octopy.exceptions import OctopusAPIError, OctopusAuthError


class TestOctopusAPIError:
    """Tests for the OctopusAPIError exception class."""

    def test_octopus_api_error_initialisation(self) -> None:
        """Test OctopusAPIError initialises with status code and detail."""
        error = OctopusAPIError(status_code=500, detail="Internal server error")

        assert error.status_code == 500
        assert error.detail == "Internal server error"
        assert str(error) == "Octopus API error 500: Internal server error"

    def test_octopus_api_error_with_different_codes(self) -> None:
        """Test OctopusAPIError works with various HTTP status codes."""
        test_cases = [
            (400, "Bad request"),
            (404, "Not found"),
            (500, "Server error"),
            (503, "Service unavailable"),
        ]

        for status_code, detail in test_cases:
            error = OctopusAPIError(status_code=status_code, detail=detail)
            assert error.status_code == status_code
            assert error.detail == detail
            assert f"Octopus API error {status_code}: {detail}" in str(error)

    def test_octopus_api_error_is_exception(self) -> None:
        """Test OctopusAPIError is an Exception subclass."""
        error = OctopusAPIError(status_code=500, detail="Error")
        assert isinstance(error, Exception)

    def test_octopus_api_error_can_be_raised(self) -> None:
        """Test OctopusAPIError can be raised and caught."""
        with pytest.raises(OctopusAPIError) as exc_info:
            raise OctopusAPIError(status_code=500, detail="Test error")

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Test error"


class TestOctopusAuthError:
    """Tests for the OctopusAuthError exception class."""

    def test_octopus_auth_error_default_initialisation(self) -> None:
        """Test OctopusAuthError initialises with default message."""
        error = OctopusAuthError()

        assert error.status_code == 401
        assert error.detail == "Authentication failed"
        assert str(error) == "Octopus API error 401: Authentication failed"

    def test_octopus_auth_error_custom_detail(self) -> None:
        """Test OctopusAuthError with custom detail message."""
        error = OctopusAuthError(detail="Invalid API key")

        assert error.status_code == 401
        assert error.detail == "Invalid API key"
        assert str(error) == "Octopus API error 401: Invalid API key"

    def test_octopus_auth_error_is_api_error(self) -> None:
        """Test OctopusAuthError is a subclass of OctopusAPIError."""
        error = OctopusAuthError()
        assert isinstance(error, OctopusAPIError)
        assert isinstance(error, Exception)

    def test_octopus_auth_error_can_be_raised(self) -> None:
        """Test OctopusAuthError can be raised and caught."""
        with pytest.raises(OctopusAuthError) as exc_info:
            raise OctopusAuthError(detail="Unauthorised access")

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Unauthorised access"

    def test_octopus_auth_error_caught_as_api_error(self) -> None:
        """Test OctopusAuthError can be caught as OctopusAPIError."""
        with pytest.raises(OctopusAPIError) as exc_info:
            raise OctopusAuthError(detail="Auth failed")

        # Should be caught as the parent class
        assert isinstance(exc_info.value, OctopusAuthError)
        assert exc_info.value.status_code == 401
