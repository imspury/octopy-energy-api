"""Pydantic models for Octopus Energy API requests and responses."""

# Standard library imports
from datetime import datetime
from enum import Enum

# Third-party import
from pydantic import BaseModel


class Region(str, Enum):
    """Mapping of UK Electricity Grid Supply Point (GSP) Group IDs to geographic regions."""

    Eastern = "_A"
    EastMidlands = "_B"
    London = "_C"
    Merseyside = "_D"
    Midlands = "_E"
    NorthEastern = "_F"
    NorthWestern = "_G"
    Southern = "_H"
    SouthEastern = "_J"
    SouthWales = "_K"
    SouthWestern = "_L"
    Yorkshire = "_M"
    SouthScotland = "_N"
    NorthScotland = "_P"


class ConsumptionInterval(BaseModel):
    """Model for a consumption interval.

    Attributes:
        interval_start: Start of the consumption interval.
        interval_end: End of the consumption interval.
        consumption: Energy consumption in kWh for the interval.
    """

    interval_start: datetime
    interval_end: datetime
    consumption: float


class ConsumptionResponse(BaseModel):
    """Response model for consumption endpoint.

    Attributes:
        count: Total number of results.
        next: URL for next page of results, if any.
        previous: URL for previous page of results, if any.
        results: List of consumption intervals.
    """

    count: int
    next: str | None = None
    previous: str | None = None
    results: list[ConsumptionInterval]


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


class Product(BaseModel):
    """Model for an energy product.

    Attributes:
        code: Unique product code.
        direction: IMPORT or EXPORT.
        full_name: Full product name.
        display_name: Display name for the product.
        description: Product description.
        is_variable: Whether pricing is variable.
        is_green: Whether the product is 100% renewable.
        is_tracker: Whether pricing tracks wholesale costs.
        is_prepay: Whether this is a prepay product.
        is_business: Whether this is a business product.
        is_restricted: Whether availability is restricted.
        term: Contract term in months, if any.
        available_from: When the product became available.
        available_to: When the product stops being available, if any.
        brand: Brand name (OCTOPUS_ENERGY, COOP_ENERGY, LONDON_POWER).
        links: Links to product detail and other resources.
    """

    code: str
    direction: str
    full_name: str
    display_name: str
    description: str
    is_variable: bool
    is_green: bool
    is_tracker: bool
    is_prepay: bool
    is_business: bool
    is_restricted: bool
    term: int | None = None
    available_from: datetime
    available_to: datetime | None = None
    brand: str
    links: list[dict[str, str]]


class ProductsResponse(BaseModel):
    """Response model for products list endpoint.

    Attributes:
        count: Total number of products.
        next: URL for next page of results, if any.
        previous: URL for previous page of results, if any.
        results: List of products.
    """

    count: int
    next: str | None = None
    previous: str | None = None
    results: list[Product]


class UnitRate(BaseModel):
    """Model for a unit rate.

    Attributes:
        value_exc_vat: Price excluding VAT in pence per kWh.
        value_inc_vat: Price including VAT in pence per kWh.
        valid_from: When the rate becomes effective.
        valid_to: When the rate expires, if any.
        payment_method: Payment method filter (DIRECT_DEBIT, etc.), if any.
    """

    value_exc_vat: float
    value_inc_vat: float
    valid_from: datetime
    valid_to: datetime | None = None
    payment_method: str | None = None


class UnitRatesResponse(BaseModel):
    """Response model for unit rates endpoint.

    Attributes:
        count: Total number of rate records.
        next: URL for next page of results, if any.
        previous: URL for previous page of results, if any.
        results: List of unit rates.
    """

    count: int
    next: str | None = None
    previous: str | None = None
    results: list[UnitRate]


class StandingCharge(BaseModel):
    """Model for a standing charge.

    Attributes:
        value_exc_vat: Daily charge excluding VAT in pence.
        value_inc_vat: Daily charge including VAT in pence.
        valid_from: When the charge becomes effective.
        valid_to: When the charge expires, if any.
        payment_method: Payment method filter, if any.
    """

    value_exc_vat: float
    value_inc_vat: float
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    payment_method: str | None = None


class StandingChargesResponse(BaseModel):
    """Response model for standing charges endpoint.

    Attributes:
        count: Total number of charge records.
        next: URL for next page of results, if any.
        previous: URL for previous page of results, if any.
        results: List of standing charges.
    """

    count: int
    next: str | None = None
    previous: str | None = None
    results: list[StandingCharge]


class TariffDetail(BaseModel):
    """Model for a tariff within a product.

    Attributes:
        code: Tariff code (e.g. E-1R-AGILE-FLEX-22-11-25-C).
        standing_charge_exc_vat: Current standing charge excluding VAT, if available.
        standing_charge_inc_vat: Current standing charge including VAT, if available.
        online_discount_exc_vat: Online discount excluding VAT.
        dual_fuel_discount_exc_vat: Dual fuel discount excluding VAT.
        exit_fees_exc_vat: Exit fees excluding VAT.
        exit_fees_inc_vat: Exit fees including VAT.
        exit_fees_type: Type of exit fees.
        links: Links to standing charges and unit rates endpoints.
    """

    code: str
    standing_charge_exc_vat: float | None = None
    standing_charge_inc_vat: float | None = None
    online_discount_exc_vat: float
    dual_fuel_discount_exc_vat: float
    exit_fees_exc_vat: float
    exit_fees_inc_vat: float
    exit_fees_type: str
    links: list[dict[str, str]]


class PaymentOptions(BaseModel):
    """Model for payment options available for a tariff.
    
    Attributes:
        direct_debit_monthly: Tariff details for monthly direct debit payment method, if available.
        prepayment: Tariff details for prepayment method, if available.
    """

    direct_debit_monthly: TariffDetail | None = None
    prepayment: TariffDetail | None = None


class ProductDetail(BaseModel):
    """Model for detailed product information.

    Attributes:
        code: Unique product code.
        full_name: Full product name.
        display_name: Display name for the product.
        description: Product description.
        is_variable: Whether pricing is variable.
        is_green: Whether the product is 100% renewable.
        is_tracker: Whether pricing tracks wholesale costs.
        is_prepay: Whether this is a prepay product.
        is_business: Whether this is a business product.
        is_restricted: Whether availability is restricted.
        term: Contract term in months, if any.
        available_from: When the product became available.
        available_to: When the product stops being available, if any.
        brand: Brand name.
        links: Links to product resources.
        single_register_electricity_tariffs: Tariffs for single register electricity meters.
        dual_register_electricity_tariffs: Tariffs for dual register electricity meters.
        single_register_gas_tariffs: Tariffs for single register gas meters.
        sample_quotes: Sample pricing quotes for different regions.
        sample_consumption: Sample consumption data used for quotes.
    """

    code: str
    full_name: str
    display_name: str
    description: str
    is_variable: bool
    is_green: bool
    is_tracker: bool
    is_prepay: bool
    is_business: bool
    is_restricted: bool
    term: int | None = None
    available_from: datetime
    available_to: datetime | None = None
    brand: str
    links: list[dict[str, str]]
    single_register_electricity_tariffs: dict[str, PaymentOptions] = {}
    dual_register_electricity_tariffs: dict[str, PaymentOptions] = {}
    single_register_gas_tariffs: dict[str, PaymentOptions] = {}
    sample_quotes: dict[str, dict] = {}
    sample_consumption: dict = {}
