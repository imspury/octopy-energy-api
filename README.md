# Octopy Energy API

An async Python client library for the [Octopus Energy REST API](https://developer.octopus.energy/rest/)

## Features

- **Async API Client** - Full async/await support with `httpx`
- **Comprehensive Data Models** - Fully typed Pydantic models for all API responses
- **Secure** - Built-in API key authentication
- **Type-Safe** - Complete type hints for better IDE support

## Installation

...

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

## API Coverage

- **Account Details** - Account, properties, and meter information
- **Consumption Data** - Electricity and gas consumption
- **Products & Tariffs** - List and retrieve product details
- **Unit Rates** - Electricity and gas unit rates with date filtering
- **Standing Charges** - Daily standing charges for tariffs

## Usage Examples

See the [examples/](examples/) directory for complete working examples:

- **[fetch_account_info.py](examples/fetch_account_info.py)** - Display account, properties, and meters
- **[fetch_consumption.py](examples/fetch_consumption.py)** - Fetch consumption data with statistics
- **[compare_tariffs.py](examples/compare_tariffs.py)** - Compare unit rates and standing charges across products