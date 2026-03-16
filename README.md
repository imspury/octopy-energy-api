# Octopy Energy API

An async Python client library for the [Octopus Energy REST API](https://developer.octopus.energy/rest/)

## Features

- **Async API Client** - Full async/await support with `httpx`
- **Comprehensive Data Models** - Fully typed Pydantic models for all API responses
- **Secure** - Built-in API key authentication
- **Type-Safe** - Complete type hints for better IDE support
- **Automatic Pagination** - Seamlessly fetch all pages of data

## Installation

```bash
pip install octopy-energy-api
```

## Requirements

- An Octopus Energy account and API key (if using the Account and Consumption endpoints)

## Configuration

Create a `.env` file in your project root:

```env
OCTOPUS_API_KEY=sk_live_xxxxxxxxxxxxxxxxxxxxx
OCTOPUS_ACCOUNT_NUMBER=A-XXXXXXXX
```

Or set environment variables directly:

```bash
export OCTOPUS_API_KEY=sk_live_xxxxxxxxxxxxxxxxxxxxx
export OCTOPUS_ACCOUNT_NUMBER=A-XXXXXXXX
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OCTOPUS_API_KEY` | Yes | - | Your Octopus Energy API key |
| `OCTOPUS_ACCOUNT_NUMBER` | Yes | - | Your account number (A-XXXXXXXX format) |
| `OCTOPUS_API_BASE_URL` | No | `https://api.octopus.energy/v1` | API base URL |

## Quick Start

```python
import asyncio
from octopy import Octopy
from octopy.config import get_settings

async def main():
    # Load settings from environment variables or .env file
    settings = get_settings()

    # Use the client as an async context manager
    async with Octopy(settings) as client:
        # Get account information
        account = await client.get_account()
        print(f"Account Number: {account.number}")

        # Get consumption data
        property = account.properties[0]
        meter_point = property.electricity_meter_points[0]
        meter = meter_point.meters[0]

        consumption = await client.get_consumption(
            meter_point=meter_point.mpan,
            serial_number=meter.serial_number,
            fuel="electricity"
        )

        for interval in consumption.results[:5]:
            print(f"{interval.interval_start}: {interval.consumption} kWh")

if __name__ == "__main__":
    asyncio.run(main())
```

## API Coverage

### Account Management

- **`get_account()`** - Get account details with properties and meter points
- **`get_grid_supply_point(postcode)`** - Get GSP region from postcode

### Consumption Data

- **`get_consumption()`** - Fetch electricity or gas consumption with filtering and grouping

### Products & Tariffs

- **`get_products()`** - List available products with filters
- **`get_product(product_code)`** - Get detailed product information

### Pricing

- **`get_unit_rates()`** - Get electricity/gas unit rates with date filtering
- **`get_standing_charges()`** - Get daily standing charges for tariffs

All paginated endpoints support automatic pagination with `auto_paginate=True` (default).

## Usage Examples

See the [examples/](examples/) directory for complete working examples:

- **[fetch_account_info.py](examples/fetch_account_info.py)** - Display account, properties, and meters
- **[fetch_consumption.py](examples/fetch_consumption.py)** - Fetch consumption data with statistics
- **[compare_tariffs.py](examples/compare_tariffs.py)** - Compare unit rates and standing charges across products

## Data Models

All API responses are returned as fully typed Pydantic models:

- `Account` - Account information with properties
- `Property` - Property with address and meter points
- `ElectricityMeterPoint` / `GasMeterPoint` - Meter point details
- `Meter` - Physical meter with serial number
- `Agreement` - Tariff agreement with validity dates
- `ConsumptionInterval` - Energy consumption for a time period
- `Product` / `ProductDetail` - Energy product information
- `UnitRate` - Unit rate pricing
- `StandingCharge` - Daily standing charge
- `Region` - Grid Supply Point (GSP) region enum

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.