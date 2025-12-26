from datetime import UTC, datetime

from packaging.version import Version

from pypi_json.models import (
    Digests,
    PackageInfo,
    PackageMetadata,
    ReleaseFile,
    ReleaseMetadata,
    Vulnerability,
)


def test_digests_from_dict() -> None:
    data = {
        "md5": "abc123",
        "sha256": "def456",
        "blake2b_256": "ghi789",
    }
    digests = Digests.from_dict(data)
    assert digests.md5 == "abc123"
    assert digests.sha256 == "def456"
    assert digests.blake2b_256 == "ghi789"


def test_digests_from_dict_missing_fields() -> None:
    data: dict[str, str] = {}
    digests = Digests.from_dict(data)
    assert digests.md5 == ""
    assert digests.sha256 == ""
    assert digests.blake2b_256 == ""


def test_release_file_from_dict() -> None:
    data = {
        "filename": "package-1.0.0.tar.gz",
        "url": "https://files.pythonhosted.org/packages/...",
        "size": 12345,
        "packagetype": "sdist",
        "python_version": "source",
        "requires_python": ">=3.8",
        "upload_time": "2024-01-01T12:00:00",
        "upload_time_iso_8601": "2024-01-01T12:00:00Z",
        "digests": {
            "md5": "abc",
            "sha256": "def",
            "blake2b_256": "ghi",
        },
        "yanked": False,
        "yanked_reason": None,
    }
    release_file = ReleaseFile.from_dict(data)
    assert release_file.filename == "package-1.0.0.tar.gz"
    assert release_file.size == 12345
    assert release_file.packagetype == "sdist"
    assert release_file.requires_python == ">=3.8"
    assert release_file.upload_time == datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    assert not release_file.yanked


def test_vulnerability_from_dict() -> None:
    data = {
        "id": "VULN-001",
        "source": "osv",
        "link": "https://example.com/vuln",
        "aliases": ["CVE-2024-0001"],
        "details": "A security vulnerability",
        "summary": "Summary",
        "fixed_in": ["1.0.1", "1.1.0"],
        "withdrawn": None,
    }
    vuln = Vulnerability.from_dict(data)
    assert vuln.id == "VULN-001"
    assert vuln.source == "osv"
    assert vuln.aliases == ("CVE-2024-0001",)
    assert vuln.fixed_in == ("1.0.1", "1.1.0")


def test_package_info_from_dict_minimal() -> None:
    data = {
        "name": "test-package",
        "version": "1.0.0",
        "classifiers": [],
        "package_url": "https://pypi.org/project/test-package/",
        "release_url": "https://pypi.org/project/test-package/1.0.0/",
    }
    info = PackageInfo.from_dict(data)
    assert info.name == "test-package"
    assert info.version == "1.0.0"
    assert info.parsed_version == Version("1.0.0")


def test_package_info_parsed_version() -> None:
    data = {
        "name": "test",
        "version": "2.3.4",
        "classifiers": [],
        "package_url": "https://pypi.org/project/test/",
        "release_url": "https://pypi.org/project/test/2.3.4/",
    }
    info = PackageInfo.from_dict(data)
    assert info.parsed_version == Version("2.3.4")
    assert info.parsed_version > Version("2.3.3")
    assert info.parsed_version < Version("2.3.5")


def test_package_info_python_specifier() -> None:
    data = {
        "name": "test",
        "version": "1.0.0",
        "requires_python": ">=3.8,<4.0",
        "classifiers": [],
        "package_url": "https://pypi.org/project/test/",
        "release_url": "https://pypi.org/project/test/1.0.0/",
    }
    info = PackageInfo.from_dict(data)
    specifier = info.python_specifier
    assert specifier is not None
    assert "3.9" in specifier
    assert "3.7" not in specifier
    assert "4.0" not in specifier


def test_package_metadata_versions_sorted() -> None:
    data = {
        "info": {
            "name": "test",
            "version": "2.0.0",
            "classifiers": [],
            "package_url": "https://pypi.org/project/test/",
            "release_url": "https://pypi.org/project/test/2.0.0/",
        },
        "releases": {
            "1.0.0": [],
            "2.0.0": [],
            "1.5.0": [],
            "0.9.0": [],
        },
        "urls": [],
        "last_serial": 12345,
        "vulnerabilities": [],
    }
    metadata = PackageMetadata.from_dict(data)
    versions = metadata.versions
    assert versions == [
        Version("0.9.0"),
        Version("1.0.0"),
        Version("1.5.0"),
        Version("2.0.0"),
    ]


def test_package_metadata_latest_version_stable() -> None:
    data = {
        "info": {
            "name": "test",
            "version": "2.0.0",
            "classifiers": [],
            "package_url": "https://pypi.org/project/test/",
            "release_url": "https://pypi.org/project/test/2.0.0/",
        },
        "releases": {
            "1.0.0": [],
            "2.0.0": [],
            "3.0.0a1": [],
        },
        "urls": [],
        "last_serial": 12345,
        "vulnerabilities": [],
    }
    metadata = PackageMetadata.from_dict(data)
    assert metadata.latest_version == Version("2.0.0")


def test_package_metadata_latest_version_prerelease_only() -> None:
    data = {
        "info": {
            "name": "test",
            "version": "1.0.0a2",
            "classifiers": [],
            "package_url": "https://pypi.org/project/test/",
            "release_url": "https://pypi.org/project/test/1.0.0a2/",
        },
        "releases": {
            "1.0.0a1": [],
            "1.0.0a2": [],
        },
        "urls": [],
        "last_serial": 12345,
        "vulnerabilities": [],
    }
    metadata = PackageMetadata.from_dict(data)
    assert metadata.latest_version == Version("1.0.0a2")


def test_release_metadata_from_dict() -> None:
    data = {
        "info": {
            "name": "test",
            "version": "1.0.0",
            "classifiers": [],
            "package_url": "https://pypi.org/project/test/",
            "release_url": "https://pypi.org/project/test/1.0.0/",
        },
        "urls": [],
        "last_serial": 12345,
        "vulnerabilities": [],
    }
    metadata = ReleaseMetadata.from_dict(data)
    assert metadata.info.name == "test"
    assert metadata.info.version == "1.0.0"
    assert metadata.last_serial == 12345
