import asyncio

from pypi_json import PyPIJson


async def main():
    async with PyPIJson() as client:
        pkg = await client.get_package("requests")
        print(f"{pkg.info.name} {pkg.info.version}: {pkg.info.summary}")


if __name__ == "__main__":
    asyncio.run(main())
