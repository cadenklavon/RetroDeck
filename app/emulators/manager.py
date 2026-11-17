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


def project_root():
    return Path(__file__).resolve().parents[2]


def emulator_candidates(emulator_id, configured_path=None, root=None):
    profile = EMULATOR_CATALOG.get(emulator_id)
    if profile is None:
        return
    names = profile["executables"].get(current_platform(), [])
    if configured_path:
        yield Path(configured_path).expanduser()
    base = Path(root) if root is not None else project_root()
    for name in names:
        yield base / "emulators" / "bin" / current_platform() / name
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
