"""Launch a game with a configured standalone emulator."""
import subprocess
from pathlib import Path

from app.emulators.catalog import EMULATOR_CATALOG, SYSTEM_DEFAULTS
from app.emulators.manager import resolve_emulator


class EmulatorLaunchError(RuntimeError):
    pass


def launch_game(game, settings, popen=subprocess.Popen, root=None):
    """Start a game using its configured system emulator.

    Optional settings:
      system_emulators: {system_name: emulator_id}
      emulator_profiles: {emulator_id: {executable: path, arguments: [str, ...]}}
    """
    emulator_id = settings.get("system_emulators", {}).get(game.system)
    emulator_id = emulator_id or SYSTEM_DEFAULTS.get(game.system)
    if not emulator_id or emulator_id not in EMULATOR_CATALOG:
        raise EmulatorLaunchError(f"No emulator is configured for {game.system}.")

    profile = EMULATOR_CATALOG[emulator_id]
    configured = settings.get("emulator_profiles", {}).get(emulator_id, {})
    executable = resolve_emulator(emulator_id, configured.get("executable"), root)
    if executable is None:
        raise EmulatorLaunchError(
            f"{profile['name']} is not available. Install it or place an approved "
            "build in RetroDeck's emulators/bin folder."
        )

    rom_path = Path(game.path).expanduser()
    if not rom_path.is_file():
        raise EmulatorLaunchError(f"Game file was not found: {rom_path}")

    templates = configured.get("arguments", profile["arguments"])
    if not isinstance(templates, list) or not all(isinstance(arg, str) for arg in templates):
        raise EmulatorLaunchError(f"Invalid launch arguments for {profile['name']}.")
    arguments = [arg.replace("{rom}", str(rom_path.resolve())) for arg in templates]
    try:
        return popen([str(executable), *arguments], cwd=str(executable.parent))
    except OSError as exc:
        raise EmulatorLaunchError(f"Could not start {profile['name']}: {exc}") from exc
