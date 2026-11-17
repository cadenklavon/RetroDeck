"""Small JSON settings store for local RetroDeck preferences."""
import json
from pathlib import Path

APP_CONFIG_DIR = Path.home() / ".config" / "retrodeck"
SETTINGS_FILE = APP_CONFIG_DIR / "settings.json"
PROJECT_ROM_DIR = Path(__file__).resolve().parents[2] / "ROMs"


def load_settings():
    defaults = {
        "rom_directories": [],
        "theme": "dark",
        "rom_directories_configured": False,
    }
    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            data = {}
        folders = data.get("rom_directories", [])
        if not isinstance(folders, list):
            folders = []
        defaults["rom_directories"] = [
            str(Path(item).expanduser()) for item in folders if isinstance(item, str)
        ]
        defaults["theme"] = "light" if data.get("theme") == "light" else "dark"
        defaults["rom_directories_configured"] = bool(
            data.get("rom_directories_configured", False)
        )
    except (OSError, json.JSONDecodeError):
        # A first run has no settings file. The bundled project ROMs folder
        # becomes the default library location if the user has created it.
        pass

    # Adopt the project's ROMs folder on first run, or when upgrading from an
    # older settings file that never stored an explicit folder choice.
    if not defaults["rom_directories_configured"] and not defaults["rom_directories"]:
        if PROJECT_ROM_DIR.is_dir():
            defaults["rom_directories"] = [str(PROJECT_ROM_DIR)]

    return defaults


def save_settings(settings):
    APP_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    temporary = SETTINGS_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    temporary.replace(SETTINGS_FILE)
