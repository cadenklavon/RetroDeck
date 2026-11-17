"""Small JSON settings store for local RetroDeck preferences."""
import json
from pathlib import Path

APP_CONFIG_DIR = Path.home() / ".config" / "retrodeck"
SETTINGS_FILE = APP_CONFIG_DIR / "settings.json"


def load_settings():
    defaults = {"rom_directories": [], "theme": "dark"}
    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return defaults
        folders = data.get("rom_directories", [])
        if not isinstance(folders, list):
            folders = []
        defaults["rom_directories"] = [str(Path(item).expanduser()) for item in folders if isinstance(item, str)]
        defaults["theme"] = "light" if data.get("theme") == "light" else "dark"
    except (OSError, json.JSONDecodeError):
        pass
    return defaults


def save_settings(settings):
    APP_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    temporary = SETTINGS_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    temporary.replace(SETTINGS_FILE)
