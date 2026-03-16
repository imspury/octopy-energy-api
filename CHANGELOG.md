# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.1.0]: https://github.com/imspury/octopy-energy-api/releases/tag/v0.1.0
