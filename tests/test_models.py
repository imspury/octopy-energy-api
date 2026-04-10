"""Tests for Pydantic models."""

# Standard library import
from datetime import UTC, datetime

# Third-party import
import pytest

# Custom import
from octopy.models import (
    Account,
    Agreement,
    ConsumptionInterval,
    ConsumptionResponse,
    ElectricityMeterPoint,
    GasMeterPoint,
    Meter,
    Product,
    Property,
    Region,
    Register,
    StandingCharge,
    UnitRate,
)


class TestRegion:
    """Tests for the Region enum."""

    def test_region_values(self) -> None:
        """Test Region enum has correct values."""
        assert Region.Eastern.value == "_A"
        assert Region.London.value == "_C"
        assert Region.NorthScotland.value == "_P"

    def test_region_from_string(self) -> None:
        """Test Region can be created from string value."""
        region = Region("_C")
        assert region == Region.London

    def test_region_invalid_value(self) -> None:
        """Test Region raises ValueError for invalid values."""
        with pytest.raises(ValueError):
            Region("_Z")


class TestRegister:
    """Tests for the Register model."""

    def test_register_initialisation(self) -> None:
        """Test Register model initialises correctly."""
        register = Register(
            identifier="01",
            rate="STANDARD",
            is_settlement_register=True,
        )

        assert register.identifier == "01"
        assert register.rate == "STANDARD"
        assert register.is_settlement_register is True


class TestMeter:
    """Tests for the Meter model."""

    def test_meter_with_registers(self) -> None:
        """Test Meter model with registers."""
        register = Register(
            identifier="01",
            rate="STANDARD",
            is_settlement_register=True,
        )
        meter = Meter(
            serial_number="12A3456789",
            registers=[register],
        )

        assert meter.serial_number == "12A3456789"
        assert len(meter.registers) == 1
        assert meter.registers[0].identifier == "01"

    def test_meter_without_registers(self) -> None:
        """Test Meter model defaults to empty registers list."""
        meter = Meter(serial_number="12A3456789")

        assert meter.serial_number == "12A3456789"
        assert meter.registers == []


class TestAgreement:
    """Tests for the Agreement model."""

    def test_agreement_active_no_end_date(self) -> None:
        """Test Agreement is active when valid_to is None."""
        agreement = Agreement(
            tariff_code="E-1R-AGILE-FLEX-22-11-25-C",
            valid_from=datetime(2022, 11, 25, 0, 0, 0, tzinfo=UTC),
            valid_to=None,
        )

        assert agreement.is_active is True

    def test_agreement_active_future_end_date(self) -> None:
        """Test Agreement is active when valid_to is in the future."""
        agreement = Agreement(
            tariff_code="E-1R-AGILE-FLEX-22-11-25-C",
            valid_from=datetime(2022, 11, 25, 0, 0, 0, tzinfo=UTC),
            valid_to=datetime(2099, 12, 31, 23, 59, 59, tzinfo=UTC),
        )

        assert agreement.is_active is True

    def test_agreement_inactive_past_end_date(self) -> None:
        """Test Agreement is inactive when valid_to is in the past."""
        agreement = Agreement(
            tariff_code="E-1R-AGILE-FLEX-22-11-25-C",
            valid_from=datetime(2022, 11, 25, 0, 0, 0, tzinfo=UTC),
            valid_to=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
        )

        assert agreement.is_active is False


class TestElectricityMeterPoint:
    """Tests for the ElectricityMeterPoint model."""

    def test_electricity_meter_point_initialisation(self) -> None:
        """Test ElectricityMeterPoint model initialises correctly."""
        meter = Meter(serial_number="12A3456789")
        agreement = Agreement(
            tariff_code="E-1R-AGILE-FLEX-22-11-25-C",
            valid_from=datetime(2022, 11, 25, 0, 0, 0),
            valid_to=None,
        )

        meter_point = ElectricityMeterPoint(
            mpan="1234567890123",
            profile_class=1,
            consumption_standard=3500,
            meters=[meter],
            agreements=[agreement],
            is_export=False,
        )

        assert meter_point.mpan == "1234567890123"
        assert meter_point.profile_class == 1
        assert meter_point.consumption_standard == 3500
        assert len(meter_point.meters) == 1
        assert len(meter_point.agreements) == 1
        assert meter_point.is_export is False


class TestGasMeterPoint:
    """Tests for the GasMeterPoint model."""

    def test_gas_meter_point_initialisation(self) -> None:
        """Test GasMeterPoint model initialises correctly."""
        meter = Meter(serial_number="12G3456789")
        agreement = Agreement(
            tariff_code="G-1R-AGILE-FLEX-22-11-25-C",
            valid_from=datetime(2022, 11, 25, 0, 0, 0),
            valid_to=None,
        )

        meter_point = GasMeterPoint(
            mprn="9876543210",
            consumption_standard=12000,
            meters=[meter],
            agreements=[agreement],
        )

        assert meter_point.mprn == "9876543210"
        assert meter_point.consumption_standard == 12000
        assert len(meter_point.meters) == 1
        assert len(meter_point.agreements) == 1


class TestProperty:
    """Tests for the Property model."""

    def test_property_with_all_fields(self) -> None:
        """Test Property model with all fields."""
        property_obj = Property(
            id=12345,
            moved_in_at=datetime(2022, 1, 1, 0, 0, 0),
            moved_out_at=None,
            address_line_1="123 Test Street",
            address_line_2="Flat 4",
            address_line_3="Building A",
            town="London",
            county="Greater London",
            postcode="SW1A 1AA",
            electricity_meter_points=[],
            gas_meter_points=[],
        )

        assert property_obj.id == 12345
        assert property_obj.address_line_1 == "123 Test Street"
        assert property_obj.postcode == "SW1A 1AA"

    def test_property_with_optional_fields_none(self) -> None:
        """Test Property model with optional fields as None."""
        property_obj = Property(
            id=12345,
            address_line_1="123 Test Street",
            town="London",
            postcode="SW1A 1AA",
        )

        assert property_obj.moved_in_at is None
        assert property_obj.moved_out_at is None
        assert property_obj.address_line_2 is None
        assert property_obj.county is None


class TestAccount:
    """Tests for the Account model."""

    def test_account_initialisation(self) -> None:
        """Test Account model initialises correctly."""
        property_obj = Property(
            id=12345,
            address_line_1="123 Test Street",
            town="London",
            postcode="SW1A 1AA",
        )
        account = Account(
            number="A-12345678",
            properties=[property_obj],
        )

        assert account.number == "A-12345678"
        assert len(account.properties) == 1
        assert account.properties[0].id == 12345


class TestConsumptionInterval:
    """Tests for the ConsumptionInterval model."""

    def test_consumption_interval_initialisation(self) -> None:
        """Test ConsumptionInterval model initialises correctly."""
        interval = ConsumptionInterval(
            interval_start=datetime(2024, 3, 19, 0, 0, 0),
            interval_end=datetime(2024, 3, 19, 0, 30, 0),
            consumption=0.123,
        )

        assert interval.interval_start == datetime(2024, 3, 19, 0, 0, 0)
        assert interval.interval_end == datetime(2024, 3, 19, 0, 30, 0)
        assert interval.consumption == 0.123


class TestConsumptionResponse:
    """Tests for the ConsumptionResponse model."""

    def test_consumption_response_with_pagination(self) -> None:
        """Test ConsumptionResponse with pagination links."""
        interval = ConsumptionInterval(
            interval_start=datetime(2024, 3, 19, 0, 0, 0),
            interval_end=datetime(2024, 3, 19, 0, 30, 0),
            consumption=0.123,
        )
        response = ConsumptionResponse(
            count=100,
            next="https://api.octopus.energy/v1/consumption/?page=2",
            previous=None,
            results=[interval],
        )

        assert response.count == 100
        assert response.next == "https://api.octopus.energy/v1/consumption/?page=2"
        assert response.previous is None
        assert len(response.results) == 1


class TestProduct:
    """Tests for the Product model."""

    def test_product_initialisation(self) -> None:
        """Test Product model initialises correctly."""
        product = Product(
            code="AGILE-FLEX-22-11-25",
            direction="IMPORT",
            full_name="Agile Octopus November 2022 v1",
            display_name="Agile Octopus",
            description="With Agile Octopus, prices are adjusted every 30 minutes.",
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

        assert product.code == "AGILE-FLEX-22-11-25"
        assert product.display_name == "Agile Octopus"
        assert product.is_variable is True
        assert product.is_green is True


class TestUnitRate:
    """Tests for the UnitRate model."""

    def test_unit_rate_initialisation(self) -> None:
        """Test UnitRate model initialises correctly."""
        rate = UnitRate(
            value_exc_vat=20.5,
            value_inc_vat=21.525,
            valid_from=datetime(2024, 3, 19, 0, 0, 0),
            valid_to=datetime(2024, 3, 19, 0, 30, 0),
            payment_method="DIRECT_DEBIT",
        )

        assert rate.value_exc_vat == 20.5
        assert rate.value_inc_vat == 21.525
        assert rate.payment_method == "DIRECT_DEBIT"


class TestStandingCharge:
    """Tests for the StandingCharge model."""

    def test_standing_charge_initialisation(self) -> None:
        """Test StandingCharge model initialises correctly."""
        charge = StandingCharge(
            value_exc_vat=45.0,
            value_inc_vat=47.25,
            valid_from=datetime(2024, 1, 1, 0, 0, 0),
            valid_to=None,
            payment_method="DIRECT_DEBIT",
        )

        assert charge.value_exc_vat == 45.0
        assert charge.value_inc_vat == 47.25
        assert charge.valid_from == datetime(2024, 1, 1, 0, 0, 0)
        assert charge.valid_to is None
