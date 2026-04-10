"""Shared pytest fixtures for testing Octopy."""

# Standard library imports
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

# Third-party import
import pytest

# Custom imports
from octopy import Octopy
from octopy.config import Settings
from octopy.models import (
    Account,
    Agreement,
    ConsumptionInterval,
    ElectricityMeterPoint,
    GasMeterPoint,
    Meter,
    Product,
    Property,
)


@pytest.fixture(autouse=True)
def mock_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch _sleep to a no-op so retry tests do not incur real delays."""

    async def _instant_sleep(self: Octopy, seconds: float) -> None:
        pass

    monkeypatch.setattr(Octopy, "_sleep", _instant_sleep)


@pytest.fixture
def mock_settings() -> Settings:
    """Create mock settings for testing.

    Returns:
        A Settings instance with test API credentials.
    """
    return Settings(
        octopus_api_key="sk_live_testapikey123",
        octopus_account_number="A-12345678",
        octopus_api_base_url="https://api.octopus.energy/v1",
    )


@pytest.fixture
async def client(mock_settings: Settings) -> AsyncGenerator[Octopy, None]:
    """Create an Octopy client for testing.

    Args:
        mock_settings: The mock settings fixture.

    Returns:
        An Octopy client instance.
    """
    async with Octopy(mock_settings) as client:
        yield client


@pytest.fixture
def mock_meter() -> Meter:
    """Create a mock meter for testing.

    Returns:
        A Meter instance with test data.
    """
    return Meter(
        serial_number="12A3456789",
        registers=[],
    )


@pytest.fixture
def mock_agreement() -> Agreement:
    """Create a mock agreement for testing.

    Returns:
        An Agreement instance with test data.
    """
    return Agreement(
        tariff_code="E-1R-AGILE-FLEX-22-11-25-C",
        valid_from=datetime(2022, 11, 25, 0, 0, 0),
        valid_to=None,
    )


@pytest.fixture
def mock_electricity_meter_point(
    mock_meter: Meter, mock_agreement: Agreement
) -> ElectricityMeterPoint:
    """Create a mock electricity meter point for testing.

    Args:
        mock_meter: The mock meter fixture.
        mock_agreement: The mock agreement fixture.

    Returns:
        An ElectricityMeterPoint instance with test data.
    """
    return ElectricityMeterPoint(
        mpan="1234567890123",
        profile_class=1,
        consumption_standard=3500,
        meters=[mock_meter],
        agreements=[mock_agreement],
        is_export=False,
    )


@pytest.fixture
def mock_gas_meter_point(mock_meter: Meter, mock_agreement: Agreement) -> GasMeterPoint:
    """Create a mock gas meter point for testing.

    Args:
        mock_meter: The mock meter fixture.
        mock_agreement: The mock agreement fixture.

    Returns:
        A GasMeterPoint instance with test data.
    """
    return GasMeterPoint(
        mprn="9876543210",
        consumption_standard=12000,
        meters=[mock_meter],
        agreements=[mock_agreement],
    )


@pytest.fixture
def mock_property(
    mock_electricity_meter_point: ElectricityMeterPoint,
    mock_gas_meter_point: GasMeterPoint,
) -> Property:
    """Create a mock property for testing.

    Args:
        mock_electricity_meter_point: The mock electricity meter point fixture.
        mock_gas_meter_point: The mock gas meter point fixture.

    Returns:
        A Property instance with test data.
    """
    return Property(
        id=12345,
        moved_in_at=datetime(2022, 1, 1, 0, 0, 0),
        moved_out_at=None,
        address_line_1="123 Test Street",
        address_line_2=None,
        address_line_3=None,
        town="London",
        county="Greater London",
        postcode="SW1A 1AA",
        electricity_meter_points=[mock_electricity_meter_point],
        gas_meter_points=[mock_gas_meter_point],
    )


@pytest.fixture
def mock_account(mock_property: Property) -> Account:
    """Create a mock account for testing.

    Args:
        mock_property: The mock property fixture.

    Returns:
        An Account instance with test data.
    """
    return Account(
        number="A-12345678",
        properties=[mock_property],
    )


@pytest.fixture
def mock_consumption_interval() -> ConsumptionInterval:
    """Create a mock consumption interval for testing.

    Returns:
        A ConsumptionInterval instance with test data.
    """
    return ConsumptionInterval(
        interval_start=datetime(2024, 3, 19, 0, 0, 0),
        interval_end=datetime(2024, 3, 19, 0, 30, 0),
        consumption=0.123,
    )


@pytest.fixture
def mock_product() -> Product:
    """Create a mock product for testing.

    Returns:
        A Product instance with test data.
    """
    return Product(
        code="AGILE-FLEX-22-11-25",
        direction="IMPORT",
        full_name="Agile Octopus November 2022 v1",
        display_name="Agile Octopus",
        description="With Agile Octopus, prices are adjusted every 30 minutes based on wholesale prices.",
        is_variable=True,
        is_green=True,
        is_tracker=False,
        is_prepay=False,
        is_business=False,
        is_restricted=False,
        term=None,
        available_from=datetime(2022, 11, 25, 0, 0, 0),
        available_to=None,
        brand="OCTOPUS_ENERGY",
        links=[],
    )


@pytest.fixture
def mock_account_response(mock_account: Account) -> dict[str, Any]:
    """Create a mock account API response.

    Args:
        mock_account: The mock account fixture.

    Returns:
        A dictionary representing the API response.
    """
    return mock_account.model_dump(mode="json")


@pytest.fixture
def mock_consumption_response(
    mock_consumption_interval: ConsumptionInterval,
) -> dict[str, Any]:
    """Create a mock consumption API response.

    Args:
        mock_consumption_interval: The mock consumption interval fixture.

    Returns:
        A dictionary representing the API response.
    """
    return {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [mock_consumption_interval.model_dump(mode="json")],
    }


@pytest.fixture
def mock_products_response(mock_product: Product) -> dict[str, Any]:
    """Create a mock products API response.

    Args:
        mock_product: The mock product fixture.

    Returns:
        A dictionary representing the API response.
    """
    return {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [mock_product.model_dump(mode="json")],
    }
