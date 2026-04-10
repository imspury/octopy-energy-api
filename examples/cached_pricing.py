"""Example: Caching API responses to reduce API calls.

Energy pricing data doesn't change frequently, so caching can significantly
reduce API calls and improve performance. This example shows how to implement
basic caching using the cachetools library.

Install cachetools: pip install cachetools
"""

import asyncio
from datetime import datetime, timedelta
from functools import wraps
from typing import Any

from cachetools import TTLCache

from octopy import Octopy, UnitRatesResponse
from octopy.config import get_settings

# Create a cache with 100-item capacity and 1-hour TTL
cache = TTLCache(maxsize=100, ttl=3600)


def async_cache(cache_obj: TTLCache):
    """Decorator to cache async function results.

    Args:
        cache_obj: The TTLCache instance to use for caching.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create a cache key from function name and arguments
            cache_key = (
                func.__name__,
                args,
                tuple(sorted(kwargs.items())),
            )

            # Return cached result if available
            if cache_key in cache_obj:
                print(f"✓ Cache hit for {func.__name__}")
                return cache_obj[cache_key]

            # Call function and cache result
            print(f"✗ Cache miss for {func.__name__}, fetching from API...")
            result = await func(*args, **kwargs)
            cache_obj[cache_key] = result
            return result

        return wrapper

    return decorator


class CachedOctopyClient:
    """Wrapper around Octopy client with caching for pricing endpoints."""

    def __init__(self, client: Octopy):
        self.client = client

    @async_cache(cache)
    async def get_unit_rates(
        self,
        product_code: str,
        tariff_code: str,
        fuel: str = "electricity",
        **kwargs: Any,
    ) -> UnitRatesResponse:
        """Get unit rates with caching.

        Pricing data is cached for 1 hour (configurable via TTLCache ttl parameter).
        """
        return await self.client.get_unit_rates(
            product_code=product_code,
            tariff_code=tariff_code,
            fuel=fuel,
            **kwargs,
        )

    @async_cache(cache)
    async def get_standing_charges(
        self,
        product_code: str,
        tariff_code: str,
        fuel: str = "electricity",
        **kwargs: Any,
    ):
        """Get standing charges with caching."""
        return await self.client.get_standing_charges(
            product_code=product_code,
            tariff_code=tariff_code,
            fuel=fuel,
            **kwargs,
        )


async def main():
    """Demonstrate caching with multiple requests."""
    settings = get_settings()

    async with Octopy(settings) as client:
        cached_client = CachedOctopyClient(client)

        # Example: Agile tariff for London region
        product_code = "AGILE-24-10-01"
        tariff_code = "E-1R-AGILE-24-10-01-C"

        print("=" * 70)
        print("Caching Example: Fetching Unit Rates")
        print("=" * 70)

        # First request - will hit API
        print("\n1. First request (should fetch from API):")
        rates1 = await cached_client.get_unit_rates(
            product_code=product_code,
            tariff_code=tariff_code,
            auto_paginate=False,
        )
        print(f"   Retrieved {len(rates1.results)} rates")

        # Second identical request - will use cache
        print("\n2. Second identical request (should use cache):")
        rates2 = await cached_client.get_unit_rates(
            product_code=product_code,
            tariff_code=tariff_code,
            auto_paginate=False,
        )
        print(f"   Retrieved {len(rates2.results)} rates")

        # Third request with different parameters - will hit API
        print("\n3. Request with different parameters (should fetch from API):")
        rates3 = await cached_client.get_unit_rates(
            product_code=product_code,
            tariff_code=tariff_code,
            period_from=datetime.now() - timedelta(days=7),
            auto_paginate=False,
        )
        print(f"   Retrieved {len(rates3.results)} rates")

        # Check cache statistics
        print("\n" + "=" * 70)
        print("Cache Statistics:")
        print("=" * 70)
        print(f"Cache size: {len(cache)}/{cache.maxsize}")
        print(f"Cache TTL: {cache.ttl} seconds ({cache.ttl / 3600:.1f} hours)")
        print("\nCached entries:")
        for key in cache.keys():
            func_name, args, kwargs = key
            print(f"  - {func_name}")

        print("\n" + "=" * 70)
        print("Caching Tips:")
        print("=" * 70)
        print("1. Pricing data changes infrequently - cache for 1-24 hours")
        print("2. Product lists change occasionally - cache for several hours")
        print("3. Consumption data is real-time - don't cache or use short TTL")
        print("4. Account data rarely changes - cache for hours/days")
        print("5. Use different cache instances for different data types")
        print("6. Monitor cache hit rate and adjust TTL accordingly")


if __name__ == "__main__":
    asyncio.run(main())
