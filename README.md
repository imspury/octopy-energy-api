# Octopy Energy API

[![PyPI version](https://badge.fury.io/py/octopy-energy-api.svg)](https://badge.fury.io/py/octopy-energy-api)
[![Python versions](https://img.shields.io/pypi/pyversions/octopy-energy-api.svg)](https://pypi.org/project/octopy-energy-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

An async Python client library for the [Octopus Energy REST API](https://developer.octopus.energy/rest/)

## Features

- **Async API Client** - Full async/await support with `httpx`
- **Comprehensive Data Models** - Fully typed Pydantic models for all API responses
- **Secure** - Built-in API key authentication
- **Type-Safe** - Complete type hints for better IDE support
- **Automatic Pagination** - Seamlessly fetch all pages of data
- **Automatic Retry** - Exponential backoff on transient errors for all API requests

## Installation

```bash
pip install octopy-energy-api
```

## Requirements

- An Octopus Energy account and API key (if using the Account and Consumption endpoints)

## Configuration

Copy the example environment file and add your credentials:

```bash
cp .env.example .env
```

Then edit `.env` with your Octopus Energy credentials:

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

## Known Limitations

### API Constraints
- **Rate Limiting**: The Octopus Energy API may have rate limits. The client includes automatic retry logic for transient errors (429, 500, 502, 503, 504) with exponential backoff
- **Page Size**: Maximum page size is 25,000 results per request
- **Date Ranges**: Historical data availability varies by meter type and installation date

### Gas Meter Differences
- **SMETS1 meters**: Return consumption in kWh (kilowatt-hours)
- **SMETS2 meters**: Return consumption in cubic meters (m³)

### Authentication
- API keys must be in format `sk_live_*` or `sk_test_*`
- Account numbers must be in format `A-XXXXXXXX`
- Some endpoints (products, pricing) work without authentication, while account and consumption endpoints require valid credentials

### Debugging
Enable debug logging to see detailed API request/response information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Tips

### Response Caching

Since energy pricing data doesn't change frequently, caching API responses can significantly reduce API calls and improve performance. See [examples/cached_pricing.py](https://github.com/imspury/octopy-energy-api/tree/main/examples/cached_pricing.py) for a complete implementation using `cachetools`.

Recommended caching durations:
- **Pricing data** (unit rates, standing charges): 1-24 hours
- **Product lists**: Several hours
- **Consumption data**: Don't cache or use very short TTL (real-time data)
- **Account information**: Hours to days

## Usage Examples

See the [examples/](https://github.com/imspury/octopy-energy-api/tree/main/examples) directory for complete working examples:

- **[fetch_account_info.py](https://github.com/imspury/octopy-energy-api/tree/main/examples/fetch_account_info.py)** - Display account, properties, and meters
- **[fetch_consumption.py](https://github.com/imspury/octopy-energy-api/tree/main/examples/fetch_consumption.py)** - Fetch consumption data with statistics
- **[compare_tariffs.py](https://github.com/imspury/octopy-energy-api/tree/main/examples/compare_tariffs.py)** - Compare unit rates and standing charges across products
- **[cached_pricing.py](https://github.com/imspury/octopy-energy-api/tree/main/examples/cached_pricing.py)** - Cache API responses to reduce API calls

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

## Development

### Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/imspury/octopy-energy-api.git
cd octopy-energy-api
pip install -e ".[dev]"
```

### Testing

This project uses `pytest` for testing with comprehensive test coverage.

#### Run Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/octopy --cov-report=term-missing

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_client.py

# Run specific test
pytest tests/test_client.py::test_get_account
```

#### Test Structure

The test suite includes:

- **Unit tests** for all client methods and API endpoints
- **HTTP mocking** with `respx` for isolated testing (no real API calls)
- **Async test support** with `pytest-asyncio`
- **Comprehensive coverage** of:
 - Account management endpoints
 - Consumption data with pagination and filtering
 - Product and pricing endpoints
 - Exception handling and error cases
 - Configuration management
 - Data model validation

#### Code Quality

```bash
# Run linting
ruff check src/ tests/ examples/

# Auto-fix linting issues
ruff check --fix src/ tests/ examples/

# Format code
ruff format src/ tests/ examples/

# Type checking
mypy src/octopy tests
```

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.