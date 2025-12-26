import argparse
import asyncio

from pypi_json import PyPIJson

PYTHON_VERSIONS = [
    "3.8",
    "3.9",
    "3.10",
    "3.11",
    "3.12",
    "3.13",
]


async def main(package: str) -> None:
    async with PyPIJson() as client:
        pkg = await client.get_package(package)

        print(f"Package: {pkg.info.name} {pkg.info.version}")
        print(f"Requires Python: {pkg.info.requires_python}")

        specifier = pkg.info.python_specifier
        if specifier:
            for version in PYTHON_VERSIONS:
                if version in specifier:
                    print(f"Minimum Python version: {version}")
                    break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("package", help="Package name")
    args = parser.parse_args()
    asyncio.run(main(args.package))
