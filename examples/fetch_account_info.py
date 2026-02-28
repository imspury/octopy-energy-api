"""Example: Fetch account information and display properties."""

# Standard library import
import asyncio

# Custom imports
from octopy import Octopy
from octopy.config import get_settings


async def main() -> None:
    """Fetch and display account information."""
    settings = get_settings()

    async with Octopy(settings) as client:
        # Get account information
        account = await client.get_account()

        print(f"Account Number: {account.number}")
        print(f"Total Properties: {len(account.properties)}")
        print()

        # Display each property
        for i, property in enumerate(account.properties, 1):
            print(f"Property {i}:")
            address_parts = [
                property.address_line_1,
                property.address_line_2,
                property.address_line_3,
            ]
            print(f"  Address: {', '.join(line for line in address_parts if line)}")
            print(f"  Postcode: {property.postcode}")
            print()

            # Display electricity meters
            if property.electricity_meter_points:
                print(f"  Electricity Meter Points:")
                for emp in property.electricity_meter_points:
                    print(f"    MPAN: {emp.mpan}")
                    for meter in emp.meters:
                        print(f"      Meter Serial: {meter.serial_number}")
                    for agreement in emp.agreements:
                        status = "Active" if agreement.is_active else "Inactive"
                        print(f"      Tariff: {agreement.tariff_code} ({status})")
                print()

            # Display gas meters
            if property.gas_meter_points:
                print(f"  Gas Meter Points:")
                for gmp in property.gas_meter_points:
                    print(f"    MPRN: {gmp.mprn}")
                    for meter in gmp.meters:
                        print(f"      Meter Serial: {meter.serial_number}")
                    for agreement in gmp.agreements:
                        status = "Active" if agreement.is_active else "Inactive"
                        print(f"      Tariff: {agreement.tariff_code} ({status})")
                print()


if __name__ == "__main__":
    asyncio.run(main())
