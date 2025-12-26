from typing import Any

import pytest
from aioresponses import aioresponses

from pypi_json import PackageNotFoundError, PyPIJson, PyPIServerError


@pytest.fixture
def mock_package_response() -> dict[str, Any]:
    return {
        "info": {
            "name": "requests",
            "version": "2.31.0",
            "summary": "Python HTTP for Humans.",
            "classifiers": [],
            "package_url": "https://pypi.org/project/requests/",
            "release_url": "https://pypi.org/project/requests/2.31.0/",
        },
        "releases": {
            "2.30.0": [
                {
                    "filename": "requests-2.30.0.tar.gz",
                    "url": "https://files.pythonhosted.org/packages/requests-2.30.0.tar.gz",
                    "size": 110000,
                    "packagetype": "sdist",
                    "python_version": "source",
                    "requires_python": ">=3.7",
                    "upload_time": "2023-05-01T00:00:00",
                    "upload_time_iso_8601": "2023-05-01T00:00:00Z",
                    "digests": {"md5": "a", "sha256": "b", "blake2b_256": "c"},
                    "yanked": False,
                    "yanked_reason": None,
                }
            ],
            "2.31.0": [
                {
                    "filename": "requests-2.31.0.tar.gz",
                    "url": "https://files.pythonhosted.org/packages/requests-2.31.0.tar.gz",
                    "size": 115000,
                    "packagetype": "sdist",
                    "python_version": "source",
                    "requires_python": ">=3.7",
                    "upload_time": "2023-05-22T00:00:00",
                    "upload_time_iso_8601": "2023-05-22T00:00:00Z",
                    "digests": {"md5": "d", "sha256": "e", "blake2b_256": "f"},
                    "yanked": False,
                    "yanked_reason": None,
                }
            ],
        },
        "urls": [
            {
                "filename": "requests-2.31.0.tar.gz",
                "url": "https://files.pythonhosted.org/packages/requests-2.31.0.tar.gz",
                "size": 115000,
                "packagetype": "sdist",
                "python_version": "source",
                "requires_python": ">=3.7",
                "upload_time": "2023-05-22T00:00:00",
                "upload_time_iso_8601": "2023-05-22T00:00:00Z",
                "digests": {"md5": "d", "sha256": "e", "blake2b_256": "f"},
                "yanked": False,
                "yanked_reason": None,
            }
        ],
        "last_serial": 12345678,
        "vulnerabilities": [],
    }


@pytest.fixture
def mock_release_response() -> dict[str, Any]:
    return {
        "info": {
            "name": "requests",
            "version": "2.31.0",
            "summary": "Python HTTP for Humans.",
            "classifiers": [],
            "package_url": "https://pypi.org/project/requests/",
            "release_url": "https://pypi.org/project/requests/2.31.0/",
        },
        "urls": [
            {
                "filename": "requests-2.31.0.tar.gz",
                "url": "https://files.pythonhosted.org/packages/requests-2.31.0.tar.gz",
                "size": 115000,
                "packagetype": "sdist",
                "python_version": "source",
                "requires_python": ">=3.7",
                "upload_time": "2023-05-22T00:00:00",
                "upload_time_iso_8601": "2023-05-22T00:00:00Z",
                "digests": {"md5": "d", "sha256": "e", "blake2b_256": "f"},
                "yanked": False,
                "yanked_reason": None,
            }
        ],
        "last_serial": 12345678,
        "vulnerabilities": [],
    }


async def test_get_package(mock_package_response: dict[str, Any]) -> None:
    with aioresponses() as m:
        m.get(
            "https://pypi.org/pypi/requests/json",
            payload=mock_package_response,
        )

        async with PyPIJson() as client:
            pkg = await client.get_package("requests")

        assert pkg.info.name == "requests"
        assert pkg.info.version == "2.31.0"
        assert len(pkg.releases) == 2
        assert len(pkg.urls) == 1


async def test_get_release(mock_release_response: dict[str, Any]) -> None:
    with aioresponses() as m:
        m.get(
            "https://pypi.org/pypi/requests/2.31.0/json",
            payload=mock_release_response,
        )

        async with PyPIJson() as client:
            release = await client.get_release("requests", "2.31.0")

        assert release.info.name == "requests"
        assert release.info.version == "2.31.0"
        assert len(release.urls) == 1


async def test_package_not_found() -> None:
    with aioresponses() as m:
        m.get("https://pypi.org/pypi/nonexistent/json", status=404)

        async with PyPIJson() as client:
            with pytest.raises(PackageNotFoundError):
                await client.get_package("nonexistent")


async def test_server_error_with_retry() -> None:
    with aioresponses() as m:
        m.get("https://pypi.org/pypi/test/json", status=500)
        m.get("https://pypi.org/pypi/test/json", status=500)
        m.get("https://pypi.org/pypi/test/json", status=500)

        async with PyPIJson(max_retries=3, retry_backoff=0.01) as client:
            with pytest.raises(PyPIServerError):
                await client.get_package("test")


async def test_caching(mock_package_response: dict[str, Any]) -> None:
    with aioresponses() as m:
        m.get(
            "https://pypi.org/pypi/requests/json",
            payload=mock_package_response,
        )

        async with PyPIJson(cache_ttl=300) as client:
            pkg1 = await client.get_package("requests")
            pkg2 = await client.get_package("requests")

        assert pkg1 is pkg2


async def test_custom_base_url(mock_package_response: dict[str, Any]) -> None:
    with aioresponses() as m:
        m.get(
            "https://custom.pypi.org/pypi/requests/json",
            payload=mock_package_response,
        )

        async with PyPIJson(base_url="https://custom.pypi.org") as client:
            pkg = await client.get_package("requests")

        assert pkg.info.name == "requests"


async def test_clear_cache(mock_package_response: dict[str, Any]) -> None:
    with aioresponses() as m:
        m.get(
            "https://pypi.org/pypi/requests/json",
            payload=mock_package_response,
        )
        m.get(
            "https://pypi.org/pypi/requests/json",
            payload=mock_package_response,
        )

        async with PyPIJson(cache_ttl=300) as client:
            await client.get_package("requests")
            client.clear_cache()
            await client.get_package("requests")


async def test_no_cache(mock_package_response: dict[str, Any]) -> None:
    with aioresponses() as m:
        m.get(
            "https://pypi.org/pypi/requests/json",
            payload=mock_package_response,
        )
        m.get(
            "https://pypi.org/pypi/requests/json",
            payload=mock_package_response,
        )

        async with PyPIJson(cache_ttl=None) as client:
            pkg1 = await client.get_package("requests")
            pkg2 = await client.get_package("requests")

        assert pkg1 is not pkg2
