"""Example: Compare tariff rates across different products."""

# Standard library imports
import asyncio
from datetime import date, timedelta
from statistics import mean

# Custom imports
from octopy import Octopy
from octopy.config import get_settings


async def main() -> None:
    """Compare unit rates across different tariffs."""
    settings = get_settings()

    async with Octopy(settings) as client:
        # Fetch available green products
        print("Fetching available green energy products...")
        products_response = await client.get_products(is_green=True)

        # Take first 3 products for comparison
        products = products_response.results[:3]

        print(f"Comparing {len(products)} products:")
        for product in products:
            print(f" - {product.display_name}")
        print()

        # Compare rates for yesterday (most recent complete day)
        yesterday = date.today() - timedelta(days=1)

        for product in products:
            print(f"{product.display_name}")
            print("-" * 30)

            # Get product details to find tariff codes
            product_detail = await client.get_product(product.code)

            # Get tariff codes for singular register electricity
            if product_detail.single_register_electricity_tariffs:
                # Take first tariff
                first_region_data = next(iter(product_detail.single_register_electricity_tariffs.values()))
                if first_region_data.prepayment:
                    tariff_code = first_region_data.prepayment.code
                else:
                    tariff_code = first_region_data.direct_debit_monthly.code

                # Fetch unit rates for yesterday
                rates_response = await client.get_unit_rates(
                    product_code=product.code,
                    tariff_code=tariff_code,
                    fuel="electricity",
                    period_from=yesterday,
                    period_to=yesterday + timedelta(days=1),
                )

                if rates_response.results:
                    # Calculate rate statistics
                    rates = [rate.value_inc_vat for rate in rates_response.results]
                    avg_rate = mean(rates)
                    min_rate = min(rates)
                    max_rate = max(rates)

                    print(f"Tariff Code: {tariff_code}")
                    print(f"Average Rate: {avg_rate:.2f}p/kWh")
                    print(f"Minimum Rate: {min_rate:.2f}p/kWh")
                    print(f"Maximum Rate: {max_rate:.2f}p/kWh")

                    # Fetch standing charges for yesterday
                    standing_response = await client.get_standing_charges(
                        product_code=product.code,
                        tariff_code=tariff_code,
                        fuel="electricity",
                    )
                    print(standing_response)

                    if standing_response.results:
                        standing = standing_response.results[0].value_inc_vat
                        print(f"Standing Charge: {standing:.2f}p/day")
                else:
                    print("No rates available for this period.")
            else:
                print("No single register electricity tariffs available.")



if __name__ == "__main__":
    asyncio.run(main())
