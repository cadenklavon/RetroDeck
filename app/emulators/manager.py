"""Find bundled or user-configured emulator executables."""
import os
import platform
import shutil
from pathlib import Path

from app.emulators.catalog import EMULATOR_CATALOG, SYSTEM_DEFAULTS


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
    base = Path(root) if root is not None else project_root()

    # New releases use an architecture-specific folder. Keep the old
    # platform-only location as a compatibility fallback for existing builds.
    architecture = current_architecture()
    for name in names:
        yield base / "emulators" / "bin" / platform_name / architecture / name
    for name in names:
        yield base / "emulators" / "bin" / platform_name / name
    if platform_name == "linux":
        # Debian and Raspberry Pi OS place game applications in /usr/games,
        # which is not guaranteed to be included in a desktop PATH.
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
            "available": False, "path": None,
            "reason": "Emulator is not installed or bundled for this platform.",
        }
    return {"available": True, "path": str(executable), "reason": ""}
