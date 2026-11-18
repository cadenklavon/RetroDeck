"""Verified, per-user emulator package installation.

Only reviewed manifest entries can be installed. Downloads are HTTPS-only,
SHA-256 checked before extraction, and installed into per-user application data.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import stat
import tarfile
import tempfile
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

APP_NAME = "RetroDeck"
MAX_DOWNLOAD_BYTES = 1_500_000_000
MAX_EXTRACTED_BYTES = 3_000_000_000


def application_data_dir():
    """Return the platform's per-user, non-privileged application-data path."""
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
    elif platform.system() == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    return base / APP_NAME


def load_manifest(path=None):
    manifest_path = (
        Path(path) if path else
        Path(__file__).resolve().parents[2] / "app" / "emulators" / "manifest.json"
    )
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read emulator manifest: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("packages"), list):
        raise ValueError("Emulator manifest must contain a packages list.")
    return data


def validate_package(package, allowed_hosts):
    required = (
        "id", "version", "platform", "architecture", "url",
        "sha256", "archive", "executable",
    )
    if not isinstance(package, dict) or any(not package.get(key) for key in required):
        raise ValueError("Emulator package entry is missing required fields.")
    if not all(isinstance(package[key], str) for key in required):
        raise ValueError("Package metadata fields must be strings.")
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", package["id"]):
        raise ValueError("Package ID contains unsafe characters.")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+-]*", package["version"]):
        raise ValueError("Package version contains unsafe characters.")
    executable_path = PurePosixPath(package["executable"].replace("\\", "/"))
    if executable_path.is_absolute() or any(
        part in ("", ".", "..") for part in executable_path.parts
    ):
        raise ValueError("Package executable path is unsafe.")
    parsed = urllib.parse.urlparse(package["url"])
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.hostname.lower() not in allowed_hosts
    ):
        raise ValueError("Emulator downloads must use an approved HTTPS host.")
    digest = package["sha256"].lower()
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise ValueError("Package SHA-256 must be 64 hexadecimal characters.")
    if package["archive"] not in ("appimage", "appimage_zip", "zip", "tar.xz", "tar.gz"):
        raise ValueError("Unsupported emulator archive format.")
    return package


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_member_path(root, member_name):
    normalized = member_name.replace("\\", "/")
    pure = PurePosixPath(normalized)
    if pure.is_absolute() or any(part in ("", ".", "..") for part in pure.parts):
        raise ValueError("Archive contains an unsafe path.")
    destination = (root / Path(*pure.parts)).resolve()
    if root.resolve() not in destination.parents and destination != root.resolve():
        raise ValueError("Archive path escapes the installation directory.")
    return destination


def _extract_archive(archive_path, destination, archive_type):
    destination.mkdir(parents=True, exist_ok=True)
    extracted_bytes = 0
    if archive_type == "zip":
        with zipfile.ZipFile(archive_path) as archive:
            for info in archive.infolist():
                target = _safe_member_path(destination, info.filename)
                unix_mode = info.external_attr >> 16
                if stat.S_ISLNK(unix_mode):
                    raise ValueError("Archive contains a symbolic link.")
                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                extracted_bytes += info.file_size
                if extracted_bytes > MAX_EXTRACTED_BYTES:
                    raise ValueError("Archive expands beyond the extraction size limit.")
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output)
                if unix_mode & 0o111:
                    target.chmod(target.stat().st_mode | 0o111)
    elif archive_type in ("tar.xz", "tar.gz"):
        mode = "r:xz" if archive_type == "tar.xz" else "r:gz"
        with tarfile.open(archive_path, mode) as archive:
            for member in archive.getmembers():
                target = _safe_member_path(destination, member.name)
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                elif member.isfile():
                    extracted_bytes += member.size
                    if extracted_bytes > MAX_EXTRACTED_BYTES:
                        raise ValueError("Archive expands beyond the extraction size limit.")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    source = archive.extractfile(member)
                    if source is None:
                        raise ValueError("Could not read archive member.")
                    with source, target.open("wb") as output:
                        shutil.copyfileobj(source, output)
                    if member.mode & 0o111:
                        target.chmod(target.stat().st_mode | 0o111)
                else:
                    raise ValueError("Archive contains a link or special file.")


def install_package(package, destination_root=None, allowed_hosts=None, opener=None, progress_callback=None):
    """Download, verify, and atomically install one manifest package."""
    allowed_hosts = {host.lower() for host in (allowed_hosts or set())}
    validate_package(package, allowed_hosts)
    root = Path(destination_root) if destination_root else application_data_dir() / "emulators"
    root.mkdir(parents=True, exist_ok=True)
    install_dir = root / package["id"] / package["version"]
    executable_relative = Path(*PurePosixPath(package["executable"]).parts)
    if install_dir.exists():
        executable = install_dir / executable_relative
        if executable.is_file():
            return executable
        raise ValueError("An incomplete installation already exists. Use repair first.")

    with tempfile.TemporaryDirectory(prefix="retrodeck-download-") as temporary:
        temporary = Path(temporary)
        download_path = temporary / "package.download"
        request = urllib.request.Request(
            package["url"], headers={"User-Agent": "RetroDeck/0.1"}
        )
        open_url = opener or urllib.request.urlopen
        with open_url(request, timeout=60) as response, download_path.open("wb") as output:
            final_url = getattr(response, "geturl", lambda: package["url"])()
            final = urllib.parse.urlparse(final_url)
            if (
                final.scheme != "https"
                or not final.hostname
                or final.hostname.lower() not in allowed_hosts
            ):
                raise ValueError("Emulator download redirected to an unapproved host.")
            downloaded = 0
            try:
                total_size = int(response.headers.get("Content-Length", 0))
            except (AttributeError, TypeError, ValueError):
                total_size = 0
            if total_size <= 0:
                total_size = int(package.get("size", 0) or 0)
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                downloaded += len(chunk)
                if downloaded > MAX_DOWNLOAD_BYTES:
                    raise ValueError("Emulator package exceeds the download size limit.")
                output.write(chunk)
                if progress_callback:
                    progress_callback(downloaded, total_size)
            if progress_callback:
                progress_callback(downloaded, total_size or downloaded)

        if sha256_file(download_path) != package["sha256"].lower():
            raise ValueError("Emulator download failed SHA-256 verification.")

        staging = temporary / "staging"
        if package["archive"] == "appimage":
            staging.mkdir()
            staged_executable = staging / executable_relative
            staged_executable.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(download_path, staged_executable)
        else:
            archive_type = "zip" if package["archive"] == "appimage_zip" else package["archive"]
            _extract_archive(download_path, staging, archive_type)
            if package["archive"] == "appimage_zip":
                appimages = list(staging.rglob("*.AppImage")) + list(staging.rglob("*.appimage"))
                if len(appimages) != 1:
                    raise ValueError("Expected exactly one AppImage in the official archive.")
                expected_appimage = staging / executable_relative
                expected_appimage.parent.mkdir(parents=True, exist_ok=True)
                if appimages[0].resolve() != expected_appimage.resolve():
                    shutil.move(str(appimages[0]), str(expected_appimage))

        executable = (staging / executable_relative).resolve()
        if staging.resolve() not in executable.parents or not executable.is_file():
            raise ValueError("Manifest executable was not found inside the package.")
        executable.chmod(executable.stat().st_mode | 0o111)
        install_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(staging), str(install_dir))
    return install_dir / executable_relative
