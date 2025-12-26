import time
from typing import Any


class TTLCache:
    """Simple in-memory cache with TTL expiration."""

    def __init__(self, ttl: int) -> None:
        self._ttl = ttl
        self._cache: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        """Get a value from cache if it exists and hasn't expired."""
        if key not in self._cache:
            return None

        expires_at, value = self._cache[key]
        if time.monotonic() > expires_at:
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: Any) -> None:
        """Store a value in cache with TTL."""
        expires_at = time.monotonic() + self._ttl
        self._cache[key] = (expires_at, value)

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()

    def _cleanup_expired(self) -> None:
        """Remove expired entries from cache."""
        now = time.monotonic()
        expired_keys = [k for k, (exp, _) in self._cache.items() if now > exp]
        for key in expired_keys:
            del self._cache[key]
