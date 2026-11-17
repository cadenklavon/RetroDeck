"""Discover supported game files in user-selected folders.

The scanner never moves, renames, edits, or deletes ROM files.
"""
from dataclasses import dataclass
from pathlib import Path


# Extensions are intentionally explicit. Generic formats such as .bin are
# omitted because they are often companion files rather than standalone games.
SYSTEM_EXTENSIONS = {
    "Nintendo 64": {".z64", ".n64", ".v64"},
    "Nintendo GameCube": {".gcm", ".gcz", ".rvz", ".wia", ".iso"},
    "Nintendo Wii": {".wbfs", ".wia", ".rvz"},
    "Nintendo Entertainment System": {".nes"},
    "Super Nintendo": {".sfc", ".smc"},
    "Game Boy": {".gb", ".gbc"},
    "Game Boy Advance": {".gba"},
    "Nintendo DS": {".nds"},
    "PlayStation Portable": {".cso"},
}

EXTENSION_TO_SYSTEM = {}
for _system, _extensions in SYSTEM_EXTENSIONS.items():
    for _extension in _extensions:
        # Shared Wii/GameCube disc formats are classified as GameCube unless
        # the user later adds a per-folder or per-game system override.
        EXTENSION_TO_SYSTEM.setdefault(_extension, _system)

# These disc-image formats can contain either GameCube or Wii games.
EXTENSION_TO_SYSTEM[".rvz"] = "GameCube / Wii"
EXTENSION_TO_SYSTEM[".wia"] = "GameCube / Wii"


@dataclass(frozen=True)
class Game:
    title: str
    system: str
    path: Path

    @property
    def extension(self) -> str:
        return self.path.suffix.lower()


def scan_rom_directories(directories):
    """Return (games, warnings) for files found under directories.

    Directory traversal is recursive. Paths are deduplicated, sorted, and
    returned as absolute paths. Missing/unreadable folders become warnings.
    """
    games = []
    warnings = []
    seen = set()

    for directory in directories:
        root = Path(directory).expanduser()
        if not root.exists():
            warnings.append(f"Folder does not exist: {root}")
            continue
        if not root.is_dir():
            warnings.append(f"Not a folder: {root}")
            continue

        try:
            candidates = root.rglob("*")
            for candidate in candidates:
                try:
                    if not candidate.is_file() or candidate.name.startswith("."):
                        continue
                    system = EXTENSION_TO_SYSTEM.get(candidate.suffix.lower())
                    if system is None:
                        continue
                    resolved = candidate.resolve()
                    key = str(resolved)
                    if key in seen:
                        continue
                    seen.add(key)
                    games.append(Game(candidate.stem, system, resolved))
                except (OSError, PermissionError):
                    continue
        except (OSError, PermissionError) as exc:
            warnings.append(f"Could not scan {root}: {exc}")

    games.sort(key=lambda game: (game.system.casefold(), game.title.casefold(), str(game.path).casefold()))
    return games, warnings
