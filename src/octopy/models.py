"""Pydantic models for Octopus Energy API requests and responses."""

# Standard library imports
from datetime import datetime

# Third-party imports
from pydantic import BaseModel


class Register(BaseModel):
    """Model for a meter register.
    
    Attributes:
        identifier: Register identifier.
        rate: Rate name (e.g. STANDARD, DAY, NIGHT).
        is_settlement_register: Whether this is the settlement register.
    """
    
    identifier: str
    rate: str
    is_settlement_register: bool


class Meter(BaseModel):
    """Model for a physical meter.
    
    Attributes:
        serial_number: The meter serial number.
        registers: List of registers on the meter (electricity only).
    """

    serial_number: str
    registers: list[Register] = []


class Agreement(BaseModel):
    """Model for a tariff agreement.
    
    Attributes:
        tariff_code: The tariff code (e.g. E-1R-AGILE-FLEX-22-11-25-C).
        valid_from: Start date of the agreement.
        valid_to: End date of the agreement, if any.
        is_active: Property indicating if the agreement is currently active.
    """

    tariff_code: str
    valid_from: datetime
    valid_to: datetime | None = None

    @property
    def is_active(self) -> bool:
        """Check if the agreement is currently active.
        
        An agreement is considered active if it has no end date (valid_to is None)
        or if the end date is in the future.

        Returns:
            True if the agreement is currently active, False otherwise.
        """
        if self.valid_to is None:
            return True
        return self.valid_to > datetime.now(self.valid_to.tzinfo)


class ElectricityMeterPoint(BaseModel):
    """Model for an electricity meter point.
    
    Attributes:
        mpan: Meter Point Administration Number.
        profile_class: Profile class (e.g. 1 for domestic).
        consumption_standard: Estimated annual consumption in kWh (single-rate meters).
        consumption_day: Estimated annual day consumption in kWh (dual-rate meters).
        consumption_night: Estimated annual night consumption in kWh (dual-rate meters).
        meters: List of meters at this meter point.
        agreements: List of tariff agreements.
        is_export: Whether this is an export meter point.
    """

    mpan: str
    profile_class: int
    consumption_standard: int | None = None
    consumption_day: int | None = None
    consumption_night: int | None = None
    meters: list[Meter]
    agreements: list[Agreement]
    is_export: bool


class GasMeterPoint(BaseModel):
    """Model for a gas meter point.
    
    Attributes:
        mprn: Meter Point Reference Number.
        consumption_standard: Estimated annual consumption in kWh.
        meters: List of meters at this meter point.
        agreements: List of tariff agreements.
    """

    mprn: str
    consumption_standard: int
    meters: list[Meter]
    agreements: list[Agreement]


class Property(BaseModel):
    """Model for a property in the account.
    
    Attributes:
        id: Property ID.
        moved_in_at: Date when the customer moved in.
        moved_out_at: Date when the customer moved out, if any.
        address_line_1: First line of the address.
        address_line_2: Second line of the address.
        address_line_3: Third line of the address.
        town: Town or city.
        county: County.
        postcode: Postcode.
        electricity_meter_points: List of electricity meter points.
        gas_meter_points: List of gas meter points.
    """
    
    id: int
    moved_in_at: datetime | None = None
    moved_out_at: datetime | None = None
    address_line_1: str
    address_line_2: str | None = None
    address_line_3: str | None = None
    town: str
    county: str | None = None
    postcode: str
    electricity_meter_points: list[ElectricityMeterPoint] = []
    gas_meter_points: list[GasMeterPoint] = []


class Account(BaseModel):
    """Model for an Octopus Energy account.
    
    Attributes:
        number: Account number in A-XXXXXXXX format.
        properties: List of properties associated with the account.
    """

    number: str
    properties: list[Property]
