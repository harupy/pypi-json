from dataclasses import dataclass
from datetime import datetime
from typing import Any, Self

from packaging.specifiers import SpecifierSet
from packaging.version import Version


@dataclass(frozen=True, slots=True)
class Digests:
    """File digest hashes."""

    md5: str | None
    sha256: str | None
    blake2b_256: str | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            md5=data.get("md5"),
            sha256=data.get("sha256"),
            blake2b_256=data.get("blake2b_256"),
        )


@dataclass(frozen=True, slots=True)
class ReleaseFile:
    """A downloadable file for a release."""

    filename: str
    url: str
    size: int
    packagetype: str
    python_version: str
    requires_python: str | None
    upload_time: datetime
    digests: Digests
    yanked: bool
    yanked_reason: str | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        upload_time = datetime.fromisoformat(
            data["upload_time_iso_8601"].replace("Z", "+00:00")
        )
        return cls(
            filename=data["filename"],
            url=data["url"],
            size=data["size"],
            packagetype=data["packagetype"],
            python_version=data["python_version"],
            requires_python=data.get("requires_python"),
            upload_time=upload_time,
            digests=Digests.from_dict(data["digests"]),
            yanked=data.get("yanked", False),
            yanked_reason=data.get("yanked_reason"),
        )


@dataclass(frozen=True, slots=True)
class Vulnerability:
    """Security vulnerability information."""

    id: str
    source: str
    link: str
    aliases: tuple[str, ...]
    details: str
    summary: str | None
    fixed_in: tuple[str, ...]
    withdrawn: str | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            id=data["id"],
            source=data["source"],
            link=data["link"],
            aliases=tuple(data.get("aliases", [])),
            details=data["details"],
            summary=data.get("summary"),
            fixed_in=tuple(data.get("fixed_in", [])),
            withdrawn=data.get("withdrawn"),
        )


@dataclass(frozen=True, slots=True)
class PackageInfo:
    """Core package metadata."""

    name: str
    version: str
    summary: str | None
    description: str | None
    description_content_type: str | None
    author: str | None
    author_email: str | None
    maintainer: str | None
    maintainer_email: str | None
    license: str | None
    license_expression: str | None
    keywords: str | None
    classifiers: tuple[str, ...]
    requires_python: str | None
    requires_dist: tuple[str, ...] | None
    provides_extra: tuple[str, ...] | None
    project_urls: dict[str, str] | None
    home_page: str | None
    download_url: str | None
    docs_url: str | None
    bugtrack_url: str | None
    package_url: str
    release_url: str
    platform: str | None
    yanked: bool
    yanked_reason: str | None

    @property
    def parsed_version(self) -> Version:
        """Return the version as a packaging.version.Version object."""
        return Version(self.version)

    @property
    def python_specifier(self) -> SpecifierSet | None:
        """Return requires_python as a SpecifierSet for comparison."""
        if self.requires_python:
            return SpecifierSet(self.requires_python)
        return None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        requires_dist = data.get("requires_dist")
        provides_extra = data.get("provides_extra")
        return cls(
            name=data["name"],
            version=data["version"],
            summary=data.get("summary"),
            description=data.get("description"),
            description_content_type=data.get("description_content_type"),
            author=data.get("author"),
            author_email=data.get("author_email"),
            maintainer=data.get("maintainer"),
            maintainer_email=data.get("maintainer_email"),
            license=data.get("license"),
            license_expression=data.get("license_expression"),
            keywords=data.get("keywords"),
            classifiers=tuple(data.get("classifiers", [])),
            requires_python=data.get("requires_python"),
            requires_dist=tuple(requires_dist) if requires_dist else None,
            provides_extra=tuple(provides_extra) if provides_extra else None,
            project_urls=data.get("project_urls"),
            home_page=data.get("home_page"),
            download_url=data.get("download_url"),
            docs_url=data.get("docs_url"),
            bugtrack_url=data.get("bugtrack_url"),
            package_url=data["package_url"],
            release_url=data["release_url"],
            platform=data.get("platform"),
            yanked=data.get("yanked", False),
            yanked_reason=data.get("yanked_reason"),
        )


@dataclass(frozen=True, slots=True)
class PackageMetadata:
    """Full package metadata including all releases."""

    info: PackageInfo
    releases: dict[Version, tuple[ReleaseFile, ...]]
    urls: tuple[ReleaseFile, ...]
    last_serial: int
    vulnerabilities: tuple[Vulnerability, ...]

    @property
    def versions(self) -> list[Version]:
        """Return all versions as sorted packaging.version.Version objects."""
        return sorted(self.releases)

    @property
    def latest_version(self) -> Version:
        """Return the latest non-prerelease version, or latest overall."""
        versions = self.versions
        stable = [v for v in versions if not v.is_prerelease]
        return stable[-1] if stable else versions[-1]

    def get_files(self, version: str | Version) -> tuple[ReleaseFile, ...]:
        """Get release files for a specific version."""
        if isinstance(version, str):
            version = Version(version)
        return self.releases.get(version, ())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        releases = {
            Version(version): tuple(ReleaseFile.from_dict(f) for f in files)
            for version, files in data.get("releases", {}).items()
        }
        return cls(
            info=PackageInfo.from_dict(data["info"]),
            releases=releases,
            urls=tuple(ReleaseFile.from_dict(f) for f in data.get("urls", [])),
            last_serial=data["last_serial"],
            vulnerabilities=tuple(
                Vulnerability.from_dict(v) for v in data.get("vulnerabilities", [])
            ),
        )


@dataclass(frozen=True, slots=True)
class ReleaseMetadata:
    """Metadata for a specific release (no releases dict)."""

    info: PackageInfo
    urls: tuple[ReleaseFile, ...]
    last_serial: int
    vulnerabilities: tuple[Vulnerability, ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            info=PackageInfo.from_dict(data["info"]),
            urls=tuple(ReleaseFile.from_dict(f) for f in data.get("urls", [])),
            last_serial=data["last_serial"],
            vulnerabilities=tuple(
                Vulnerability.from_dict(v) for v in data.get("vulnerabilities", [])
            ),
        )
