class PyPIError(Exception):
    """Base exception for all PyPI API errors."""


class PackageNotFoundError(PyPIError):
    """Raised when a package or version is not found (404)."""

    def __init__(self, package: str, version: str | None = None) -> None:
        self.package = package
        self.version = version
        if version:
            msg = f"Package '{package}' version '{version}' not found"
        else:
            msg = f"Package '{package}' not found"
        super().__init__(msg)


class RateLimitError(PyPIError):
    """Raised when the API rate limit is exceeded (429)."""

    def __init__(self, retry_after: int | None = None) -> None:
        self.retry_after = retry_after
        msg = "Rate limit exceeded"
        if retry_after:
            msg += f", retry after {retry_after} seconds"
        super().__init__(msg)


class PyPIServerError(PyPIError):
    """Raised when the PyPI server returns a 5xx error."""

    def __init__(self, status_code: int, message: str | None = None) -> None:
        self.status_code = status_code
        msg = f"PyPI server error: {status_code}"
        if message:
            msg += f" - {message}"
        super().__init__(msg)
