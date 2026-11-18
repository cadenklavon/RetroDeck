"""Verified, per-user emulator package installation.

Packages are described by a reviewed manifest. Downloads are HTTPS-only,
SHA-256 checked before extraction, and installed atomically into user data.
No administrator privileges or system package manager are used.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import tarfile
import tempfile
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

APP_NAME = "RetroDeck"\nMAX_DOWNLOAD_BYTES = 1_500_000_000


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
    manifest_path = Path(path) if path else Path(__file__).resolve().parents[2] / "app" / "emulators" / "manifest.json"
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read emulator manifest: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("packages"), list):
        raise ValueError("Emulator manifest must contain a packages list.")
    return data


def validate_package(package, allowed_hosts):
    required = ("id", "version", "platform", "architecture", "url", "sha256", "archive", "executable")
    if not isinstance(package, dict) or any(not package.get(key) for key in required):
        raise ValueError("Emulator package entry is missing required fields.")
    if not all(isinstance(package[key], str) for key in required):
        raise ValueError("Package metadata fields must be strings.")
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", package["id"]):
        raise ValueError("Package ID contains unsafe characters.")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+-]*", package["version"]):
        raise ValueError("Package version contains unsafe characters.")
    executable_path = PurePosixPath(package["executable"].replace("\\", "/"))
    if executable_path.is_absolute() or any(part in ("", ".", "..") for part in executable_path.parts):
        raise ValueError("Package executable path is unsafe.")\n    parsed = urllib.parse.urlparse(package["url"])
    if parsed.scheme != "https" or not parsed.hostname or parsed.hostname.lower() not in allowed_hosts:
        raise ValueError("Emulator downloads must use an approved HTTPS host.")
    digest = package["sha256"].lower()
    if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError("Package SHA-256 must be 64 hexadecimal characters.")
    if package["archive"] not in ("appimage", "zip", "tar.xz", "tar.gz"):
        raise ValueError("Unsupported emulator archive format.")
    if not all(isinstance(package[k], str) for k in required):
        raise ValueError("Package metadata fields must be strings.")
    return package


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_member_path(root, member_name):
    name = member_name.replace("\\", "/")
    pure = PurePosixPath(name)
    if pure.is_absolute() or any(part in ("", ".", "..") for part in pure.parts):
        raise ValueError("Archive contains an unsafe path.")
    destination = (root / Path(*pure.parts)).resolve()
    if root.resolve() not in destination.parents and destination != root.resolve():
        raise ValueError("Archive path escapes the installation directory.")
    return destination


def _extract_archive(archive_path, destination, archive_type):
    destination.mkdir(parents=True, exist_ok=True)
    if archive_type == "zip":
        with zipfile.ZipFile(archive_path) as archive:
            for info in archive.infolist():
                target = _safe_member_path(destination, info.filename)
                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(info) as source, target.open("wb") as output:
                        shutil.copyfileobj(source, output)
    elif archive_type in ("tar.xz", "tar.gz"):
        mode = "r:xz" if archive_type == "tar.xz" else "r:gz"
        with tarfile.open(archive_path, mode) as archive:
            for member in archive.getmembers():
                target = _safe_member_path(destination, member.name)
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                elif member.isfile():
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
    elif archive_type != "appimage":
        raise ValueError("Unsupported archive format.")


def install_package(package, destination_root=None, allowed_hosts=None, opener=None):
    """Download, verify, and atomically install one manifest package."""
    allowed_hosts = {h.lower() for h in (allowed_hosts or set())}
    validate_package(package, allowed_hosts)
    root = Path(destination_root) if destination_root else application_data_dir() / "emulators"
    root.mkdir(parents=True, exist_ok=True)
    install_dir = root / package["id"] / package["version"]
    if install_dir.exists():
        executable = install_dir / package["executable"]
        if executable.is_file():
            return executable
        raise ValueError("An incomplete installation already exists. Use repair first.")

    with tempfile.TemporaryDirectory(prefix="retrodeck-download-") as temporary:
        temporary = Path(temporary)
        download_path = temporary / "package.download"
        request = urllib.request.Request(package["url"], headers={"User-Agent": "RetroDeck/0.1"})
        open_url = opener or urllib.request.urlopen
        with open_url(request, timeout=60) as response, download_path.open("wb") as output:
            shutil.copyfileobj(response, output)
        if sha256_file(download_path) != package["sha256"].lower():
            raise ValueError("Emulator download failed SHA-256 verification.")

        staging = temporary / "staging"
        if package["archive"] == "appimage":
            staging.mkdir()
            staged_executable = staging / Path(package["executable"]).name
            shutil.copy2(download_path, staged_executable)
            staged_executable.chmod(staged_executable.stat().st_mode | 0o111)
        else:
            _extract_archive(download_path, staging, package["archive"])
        executable = (staging / package["executable"]).resolve()
        if staging.resolve() not in executable.parents or not executable.is_file():
            raise ValueError("Manifest executable was not found inside the package.")
        executable.chmod(executable.stat().st_mode | 0o111)
        install_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(staging), str(install_dir))
    return install_dir / package["executable"]
