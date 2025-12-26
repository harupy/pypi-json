import asyncio

from pypi_json import PyPIJson

PACKAGES = [
    "numpy",
    "scikit-learn",
    "pandas",
    "requests",
    "flask",
]


async def main() -> None:
    async with PyPIJson() as client:
        tasks = [client.get_package(name) for name in PACKAGES]
        packages = await asyncio.gather(*tasks)

        print(f"{'Package':<15} {'Version':<12} {'Release Date'}")
        print("-" * 45)

        for pkg in packages:
            if pkg.urls:
                release_date = pkg.urls[0].upload_time.strftime("%Y-%m-%d")
            else:
                release_date = "N/A"
            print(f"{pkg.info.name:<15} {pkg.info.version:<12} {release_date}")


if __name__ == "__main__":
    asyncio.run(main())
