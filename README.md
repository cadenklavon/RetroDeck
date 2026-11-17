# RetroDeck

**A custom retro-gaming launcher for Raspberry Pi 5.**

RetroDeck is an in-development desktop application designed to organize and launch a personal retro-game library from one controller-friendly interface. The target platform is Raspberry Pi OS on Raspberry Pi 5.

> **Current status: Stage 2 library foundation.** RetroDeck now has a working PySide6 desktop interface, configurable ROM folders, recursive game-file discovery, system grouping, search/filtering, and locally saved settings. Emulator launching, controller input, cover artwork, favorites, and play history are not implemented yet.

## Current features

- Home, Library, Systems, Search, and Settings pages
- Dark and light themes, with the selected theme saved locally
- Add and remove ROM folders from Settings
- Recursively scan configured folders without moving or modifying game files
- Detect supported file extensions and group games by system
- Search/filter the detected library by title, system, or path
- Folder settings saved locally in the user's RetroDeck configuration directory
- Keyboard shortcuts: Ctrl+1 Home, Ctrl+2 Library, Ctrl+3 Systems, Ctrl+4 Search, Ctrl+5 Settings, F5 rescan

## Supported file extensions

| System | Extensions |
| --- | --- |
| Nintendo 64 | .z64, .n64, .v64 |
| Nintendo GameCube | .gcm, .gcz, .iso |
| Nintendo Wii | .wbfs |
| GameCube / Wii disc images | .rvz, .wia |
| Nintendo Entertainment System | .nes |
| Super Nintendo | .sfc, .smc |
| Game Boy | .gb, .gbc |
| Game Boy Advance | .gba |
| Nintendo DS | .nds |
| PlayStation Portable | .cso |

This is a file-discovery list, not a guarantee that an emulator is installed or can launch every format. More formats and per-folder system overrides can be added later. Generic .bin files are deliberately excluded because they are often companion files rather than standalone games.

## Run on Raspberry Pi OS

On a Debian 13 / Raspberry Pi OS installation where the PySide6 system package is available:

~~~bash
sudo apt update
sudo apt install python3-pyside6.qtwidgets
cd ~/RetroDeck
python3 main.py
~~~

If you have not cloned the repository yet:

~~~bash
git clone https://github.com/cadenklavon/RetroDeck.git
cd RetroDeck
~~~

## Planned experience

- Configurable emulator profiles and launch commands
- Keyboard, mouse, and Xbox-controller navigation
- Local cover art and game metadata
- Favorites and recently played history
- SQLite persistence for library metadata and play history
- Backup/export of settings

## Architecture

| Layer | Technology |
| --- | --- |
| Desktop UI | Python + PySide6 |
| ROM discovery | Python pathlib |
| Local preferences | JSON in the user's config directory |
| Planned library database | SQLite |
| Emulator integration | Launch configured external emulator processes |
| Target hardware | Raspberry Pi 5 |
| Target OS | Raspberry Pi OS |

RetroDeck is intended to launch standalone emulators directly. It will not require RetroArch as its central runtime. Example targets include Mupen64Plus for Nintendo 64 and Dolphin for GameCube/Wii, subject to installation and hardware compatibility.

## Repository layout

~~~text
RetroDeck/
├── app/
│   ├── config/
│   │   └── settings.py
│   └── library/
│       └── scanner.py
├── docs/
│   └── ROADMAP.md
├── tests/
│   └── test_scanner.py
├── main.py
├── requirements.txt
└── README.md
~~~

## Development principles

1. Keep the app usable with a controller, keyboard, and mouse.
2. Keep emulator integration modular and independent of one frontend.
3. Do not bundle copyrighted game ROMs, BIOS files, or commercial artwork.
4. Store user data locally and make ROM folders configurable.
5. Build and test for Raspberry Pi OS compatibility.
6. Clearly distinguish working features from planned features.

## Roadmap

See docs/ROADMAP.md for planned milestones.

## License

No license has been selected yet. Until one is added, all rights are reserved by the author. Please do not assume the code is available for reuse.
