"""Find RetroDeck-managed, bundled, or user-configured emulator executables."""
import os
import platform
import shutil
from pathlib import Path

from app.emulators.catalog import EMULATOR_CATALOG, SYSTEM_DEFAULTS
from app.emulators.managed_installer import application_data_dir


def current_platform():
    if os.name == "nt":
        return "windows"
    if platform.system() == "Linux":
        return "linux"
    return platform.system().lower()


def current_architecture():
    """Return a normalized architecture name for package and bundle lookup."""
    machine = platform.machine().lower()
    aliases = {
        "aarch64": "arm64",
        "arm64": "arm64",
        "x86_64": "x86_64",
        "amd64": "x86_64",
        "i386": "x86",
        "i686": "x86",
        "armv7l": "armhf",
    }
    return aliases.get(machine, machine or "unknown")


def project_root():
    return Path(__file__).resolve().parents[2]


def emulator_candidates(emulator_id, configured_path=None, root=None):
    profile = EMULATOR_CATALOG.get(emulator_id)
    if profile is None:
        return
    platform_name = current_platform()
    names = profile["executables"].get(platform_name, [])
    if configured_path:
        yield Path(configured_path).expanduser()

    # RetroDeck-managed versions are installed outside the source checkout.
    managed_root = application_data_dir() / "emulators" / emulator_id
    if managed_root.is_dir():
        for version_dir in sorted(
            (entry for entry in managed_root.iterdir() if entry.is_dir()),
            reverse=True,
        ):
            for name in names:
                yield version_dir / name

    base = Path(root) if root is not None else project_root()
    architecture = current_architecture()
    for name in names:
        yield base / "emulators" / "bin" / platform_name / architecture / name
    for name in names:
        yield base / "emulators" / "bin" / platform_name / name

    if platform_name == "linux":
        for directory in ("/usr/games", "/usr/bin", "/usr/local/bin"):
            for name in names:
                yield Path(directory) / name
    for name in names:
        located = shutil.which(name)
        if located:
            yield Path(located)


def resolve_emulator(emulator_id, configured_path=None, root=None):
    for candidate in emulator_candidates(emulator_id, configured_path, root):
        try:
            if candidate.is_file():
                return candidate.resolve()
        except OSError:
            continue
    return None


def emulator_for_system(system):
    return SYSTEM_DEFAULTS.get(system)


def emulator_status(emulator_id, configured_path=None, root=None):
    profile = EMULATOR_CATALOG.get(emulator_id)
    if profile is None:
        return {"available": False, "path": None, "reason": "Unknown emulator."}
    executable = resolve_emulator(emulator_id, configured_path, root)
    if executable is None:
        return {
            "available": False,
            "path": None,
            "reason": "Emulator is not installed or bundled for this platform.",
        }
    return {"available": True, "path": str(executable), "reason": ""}
