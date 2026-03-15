"""Example: Fetch electricity consumption and calculate statistics."""

# Standard library imports
import asyncio
from datetime import date, timedelta

# Custom imports
from octopy import Octopy
from octopy.config import get_settings

async def main() -> None:
    """Fetch consumption data and calculate statistics."""
    settings = get_settings()

    try:
        async with Octopy(settings) as client:
            # Get account to find meter details
            account = await client.get_account()
            property = account.properties[0]
            meter_point = property.electricity_meter_points[0]
            meter = meter_point.meters[0]

            # Fetch last 7 days of consumption grouped by day
            period_to = date.today()
            period_from = period_to - timedelta(days=7)

            print(f"Fetching electricity consumption for {meter.serial_number}")
            print(f"Period: {period_from} to {period_to}")
            print()

            consumption = await client.get_consumption(
                meter_point=meter_point.mpan,
                serial_number=meter.serial_number,
                fuel="electricity",
                period_from=period_from,
                period_to=period_to,
                order_by="period",
                group_by="day",
            )

            # Display daily consumption
            print("Daily Consumption:")
            print("-" * 30)

            total_kwh = 0.0
            for interval in consumption.results:
                kwh = interval.consumption
                total_kwh += kwh
                date_str = interval.interval_start.strftime("%Y-%m-%d %A")
                print(f"{date_str}: {kwh:>8.2f} kWh")
            
            # Display statistics
            print("-" * 30)
            print(f"Total Consumption: {total_kwh:.2f} kWh")
            if consumption.results:
                avg_kwh = total_kwh / len(consumption.results)
                print(f"Average Daily Consumption: {avg_kwh:.2f} kWh")
    except IndexError:
        print("Error: Could not find meter point or meter. Check your account has meters configured.")
    except Exception as e:
        print(f"Error fetching consumption data: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())