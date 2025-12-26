import asyncio
from types import TracebackType

import aiohttp

from ._cache import TTLCache
from .exceptions import PackageNotFoundError, PyPIServerError, RateLimitError
from .models import PackageMetadata, ReleaseMetadata


class PyPIJson:
    """Async client for the PyPI JSON API."""

    def __init__(
        self,
        base_url: str = "https://pypi.org",
        cache_ttl: int | None = 300,
        max_retries: int = 3,
        retry_backoff: float = 1.0,
        timeout: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._cache_ttl = cache_ttl
        self._max_retries = max_retries
        self._retry_backoff = retry_backoff
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: aiohttp.ClientSession | None = None
        self._cache: TTLCache | None = TTLCache(cache_ttl) if cache_ttl else None

    async def __aenter__(self) -> "PyPIJson":
        self._session = aiohttp.ClientSession(timeout=self._timeout)
        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: TracebackType | None,
    ) -> None:
        if self._session:
            await self._session.close()
            self._session = None

    def _get_cache_key(self, package: str, version: str | None = None) -> str:
        if version:
            return f"{self._base_url}:{package}:{version}"
        return f"{self._base_url}:{package}"

    async def _request(self, url: str) -> dict:
        if not self._session:
            raise RuntimeError("Client not initialized. Use 'async with' context.")

        last_exception: Exception | None = None

        for attempt in range(self._max_retries):
            try:
                async with self._session.get(url) as response:
                    match response.status:
                        case 200:
                            return await response.json()
                        case 404:
                            raise PackageNotFoundError(url)
                        case 429:
                            retry_after = response.headers.get("Retry-After")
                            raise RateLimitError(
                                int(retry_after) if retry_after else None
                            )
                        case status if status >= 500:
                            raise PyPIServerError(status)
                        case status:
                            raise PyPIServerError(
                                status, f"Unexpected status: {status}"
                            )
            except (aiohttp.ClientError, PyPIServerError, RateLimitError) as e:
                last_exception = e
                if isinstance(e, PackageNotFoundError):
                    raise
                if attempt < self._max_retries - 1:
                    delay = self._retry_backoff * (2**attempt)
                    await asyncio.sleep(delay)

        if last_exception:
            raise last_exception
        raise RuntimeError("Request failed with no exception")

    async def get_package(self, package: str) -> PackageMetadata:
        """Get metadata for a package at its latest version.

        Args:
            package: The package name.

        Returns:
            PackageMetadata with info, releases, urls, and vulnerabilities.

        Raises:
            PackageNotFoundError: If the package doesn't exist.
            RateLimitError: If rate limited by PyPI.
            PyPIServerError: If PyPI returns a server error.
        """
        cache_key = self._get_cache_key(package)

        if self._cache:
            cached = self._cache.get(cache_key)
            if cached:
                return cached

        url = f"{self._base_url}/pypi/{package}/json"
        data = await self._request(url)
        result = PackageMetadata.from_dict(data)

        if self._cache:
            self._cache.set(cache_key, result)

        return result

    async def get_release(self, package: str, version: str) -> ReleaseMetadata:
        """Get metadata for a specific release of a package.

        Args:
            package: The package name.
            version: The version string.

        Returns:
            ReleaseMetadata with info, urls, and vulnerabilities.

        Raises:
            PackageNotFoundError: If the package or version doesn't exist.
            RateLimitError: If rate limited by PyPI.
            PyPIServerError: If PyPI returns a server error.
        """
        cache_key = self._get_cache_key(package, version)

        if self._cache:
            cached = self._cache.get(cache_key)
            if cached:
                return cached

        url = f"{self._base_url}/pypi/{package}/{version}/json"
        data = await self._request(url)
        result = ReleaseMetadata.from_dict(data)

        if self._cache:
            self._cache.set(cache_key, result)

        return result

    def clear_cache(self) -> None:
        """Clear all cached responses."""
        if self._cache:
            self._cache.clear()
