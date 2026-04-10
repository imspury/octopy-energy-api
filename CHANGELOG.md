# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-04-10

### Added
- Automatic retry logic with exponential backoff for transient network errors (408, 429, 500, 502, 503, 504) on all API requests
- Debug logging support for API requests and responses
- Input validation for API keys (must start with sk_live_ or sk_test_)
- Input validation for account numbers (must match A-XXXXXXXX format)
- Constants module for centralised configuration values
- `page_size` parameter for `get_standing_charges`, consistent with `get_unit_rates` and `get_consumption`
- Caching example demonstrating response caching with TTL
- Performance tips section in README
- Known Limitations section in README documenting API constraints
- Package badges in README (PyPI version, Python versions, license, code style)

### Changed
- Updated README with clearer configuration instructions
- Extracted magic numbers to named constants for better maintainability

### Fixed
- Retry and backoff logic now correctly applies to all initial API requests; previously, it only applied to pagination follow-up requests, leaving first-page calls unprotected
- Resolved pre-release code quality issues: ruff formatting, mypy type annotation errors, and modernised `timezone.utc` to `datetime.UTC`

## [0.2.0] - 2026-03-23

### Added
- Comprehensive unit test suite with pytest
- Test coverage for all client methods and endpoints
- Tests for account management endpoints (get_account, get_grid_supply_point)
- Tests for consumption data endpoint with pagination and filtering
- Tests for pricing endpoints (get_unit_rates, get_standing_charges)
- Tests for product endpoints (get_products, get_product)
- Tests for exception classes (OctopusAPIError, OctopusAuthError)
- Tests for configuration management and environment variable handling
- Tests for Pydantic models and data validation
- Tests for datetime formatting and pagination logic
- Test fixtures for mock data and client setup
- HTTP mocking with respx for isolated testing
- pytest-asyncio for async test support
- pytest-cov for coverage reporting

### Changed
- Updated development dependencies in pyproject.toml
- Improved test configuration with strict markers and coverage reporting

## [0.1.0] - 2026-03-16

### Added
- Initial release of Octopy Energy API client
- Async API client with full async/await support using httpx
- Comprehensive Pydantic models for all API responses
- HTTP Basic Auth authentication with API key
- Account management endpoints
 - Get account details with properties and meter points
 - Get Grid Supply Point (GSP) region from postcode
- Consumption data endpoints
 - Fetch electricity and gas consumption
 - Support for date filtering, grouping, and ordering
 - Automatic pagination support
- Product and tariff endpoints
 - List available products with filters
 - Get detailed product information
 - Access tariff codes for different regions
- Pricing endpoints
 - Get unit rates for electricity and gas tariffs
 - Get standing charges for tariffs
 - Date filtering support
- Type safety features
 - Complete type hints throughout
 - py.typed marker for type checking support
 - Pydantic validation for all data models
- Working examples
 - fetch_account_info.py - Display account information
 - fetch_consumption.py - Fetch and analyse consumption data
 - compare_tariffs.py - Compare tariff rates
- Configuration via environment variables or .env file
- MIT License
- Comprehensive documentation

### Fixed
- Removed trailing slash from default API base URL to prevent double-slash issues

[0.3.0]: https://github.com/imspury/octopy-energy-api/releases/tag/v0.3.0
[0.2.0]: https://github.com/imspury/octopy-energy-api/releases/tag/v0.2.0
[0.1.0]: https://github.com/imspury/octopy-energy-api/releases/tag/v0.1.0
