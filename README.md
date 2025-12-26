# pypi-json

Async Python client for the [PyPI JSON API](https://docs.pypi.org/api/json/).

## Installation

```bash
pip install git+https://github.com/harupy/pypi-json.git
```

## Usage

```python
import asyncio
from pypi_json import PyPIJson

async def main():
    async with PyPIJson() as client:
        pkg = await client.get_package("requests")
        print(f"{pkg.info.name} {pkg.info.version}")

asyncio.run(main())
```

## Features

- Async-native with `aiohttp`
- Response caching with configurable TTL
- Automatic retries with exponential backoff
- Version parsing via `packaging` library

## API

### PyPIJson

```python
PyPIJson(
    base_url="https://pypi.org",  # Custom index support
    cache_ttl=300,                 # Cache TTL in seconds (None to disable)
    max_retries=3,                 # Retry attempts
    retry_backoff=1.0,             # Backoff multiplier
    timeout=30.0,                  # Request timeout
)
```

### Methods

```python
await client.get_package("requests")        # Get package metadata
await client.get_release("requests", "2.31.0")  # Get specific release
client.clear_cache()                         # Clear response cache
```

### Models

- `PackageMetadata` - Full package info with all releases
- `ReleaseMetadata` - Single release info
- `PackageInfo` - Core metadata (name, version, summary, etc.)
- `ReleaseFile` - Downloadable file info
- `Vulnerability` - Security vulnerability info

### Version Helpers

```python
pkg.info.parsed_version      # packaging.version.Version
pkg.info.python_specifier    # packaging.specifiers.SpecifierSet
pkg.versions                 # Sorted list of all versions
pkg.latest_version           # Latest stable version
pkg.get_files("2.31.0")      # Files for a specific version
```

## Development

```bash
# Setup
uv sync --all-extras

# Run tests
uv run pytest

# Lint & format
uv run ruff check .
uv run ruff format .

# Type check
uv run ty check
```

## License

MIT
