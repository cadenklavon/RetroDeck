"""Safe, explicit installation plan for supported Raspberry Pi OS packages.

This module never downloads or executes third-party archives. It only exposes
fixed Debian package names for packages published by the user's configured
Debian/Raspberry Pi OS repositories. The UI must ask for confirmation before
running the package manager.
"""
import os
import platform
from pathlib import Path

from app.emulators.catalog import EMULATOR_CATALOG


def is_debian_family(os_release_path="/etc/os-release"):
    try:
        values = {}
        for line in Path(os_release_path).read_text(encoding="utf-8").splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                values[key] = value.strip().strip('"').lower()
        identifiers = {values.get("ID", "")}
        identifiers.update(values.get("ID_LIKE", "").split())
        return bool(identifiers.intersection({"debian", "raspbian"}))
    except OSError:
        return False


def supported_package_plan(system=None, architecture=None, debian_family=None):
    """Return fixed apt packages available for the supported Pi OS target."""
    system = system or platform.system()
    architecture = architecture or platform.machine().lower()
    architecture = {
        "aarch64": "arm64",
        "arm64": "arm64",
        "amd64": "x86_64",
    }.get(architecture, architecture)
    if system != "Linux" or architecture != "arm64":
        return {}
    if debian_family is None:
        debian_family = is_debian_family()
    if not debian_family:
        return {}

    plan = {}
    for emulator_id, profile in EMULATOR_CATALOG.items():
        packages = profile.get("debian_arm64_packages", [])
        if packages:
            plan[emulator_id] = list(packages)
    return plan


def package_install_command(packages, executable="pkexec"):
    """Build a non-shell privileged command from a trusted package list."""
    safe_packages = [
        package for package in packages
        if isinstance(package, str)
        and package
        and all(character.isalnum() or character in "+.-" for character in package)
    ]
    if not safe_packages or len(safe_packages) != len(packages):
        raise ValueError("Package list contains an invalid package name.")
    return [executable, "apt-get", "install", "-y", *safe_packages]
