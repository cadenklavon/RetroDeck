# RetroDeck

**A custom retro-gaming launcher for Raspberry Pi 5.**

RetroDeck is an in-development desktop application designed to organize and launch a personal retro-game library from one controller-friendly interface. The first deployment target is 64-bit Raspberry Pi OS on Raspberry Pi 5.

> **Current status: Stage 3 foundation.** RetroDeck has a working PySide6 interface, configurable ROM folders, recursive game discovery, system grouping, search/filtering, local settings, an emulator candidate catalog, executable discovery, and a tested process-launching module. Real emulator packages, automatic installation, controller input, and end-to-end emulator testing are still outstanding.

## Current features

- Home, Library, Systems, Search, and Settings pages
- Dark and light themes, with the selected theme saved locally
- Add and remove ROM folders from Settings
- Recursively scan configured folders without moving or modifying game files
- Detect supported file extensions and group games by system
- Search/filter the detected library by title, system, or path
- Folder settings saved locally in the user's RetroDeck configuration directory
- Keyboard shortcuts: Ctrl+1 Home, Ctrl+2 Library, Ctrl+3 Systems, Ctrl+4 Search, Ctrl+5 Settings, F5 rescan
- Emulator candidate catalog with upstream project references
- Executable discovery for configured, RetroDeck-bundled, and system-installed emulators
- Modular process launcher with configurable argument templates and readable errors
- Launch selected games from the Library page when a compatible emulator is available

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

This is a file-discovery list, not a guarantee that an emulator is installed or can launch every format. Generic .bin files are excluded because they are often companion files rather than standalone games.

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

## Emulator packaging direction

RetroDeck is designed to launch standalone emulators directly. It will not require RetroArch as its central runtime.

The goal is for users to install RetroDeck and then install compatible emulator packages through a first-run setup screen, without manually finding each emulator. Compiled binaries will be delivered as platform-specific RetroDeck release assets or installed from a versioned, checksum-verified manifest. They will not be committed to the Git source history.

The first packaging target is Raspberry Pi OS 64-bit / ARM64. Windows and other platforms need their own builds. No emulator binaries are bundled yet. Each emulator's license, dependencies, source-code obligations, and redistribution permissions must be checked before packaging.

Candidate standalone emulators include Mupen64Plus (N64), Dolphin (GameCube/Wii), Nestopia (NES), bsnes (SNES), Gambatte (Game Boy/Color), mGBA (GBA), melonDS (DS), and PPSSPP (PSP). These are candidates, not a claim of completed support.

See:
- docs/EMULATOR_PACKAGING.md for the packaging and first-run installation plan.
- docs/THIRD_PARTY_LICENSES.md for third-party license tracking.

## Planned experience

- First-run emulator installation and update manager
- Per-system emulator selection and per-game overrides
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
| Emulator catalog and discovery | Python modules under app/emulators |
| Emulator integration | Standalone emulator processes |
| First release target | Raspberry Pi OS 64-bit on Raspberry Pi 5 |

## Repository layout

~~~text
RetroDeck/
├── app/
│   ├── config/
│   │   └── settings.py
│   ├── emulators/
│   │   ├── catalog.py
│   │   ├── manager.py
│   │   └── launcher.py
│   └── library/
│       └── scanner.py
├── docs/
│   ├── EMULATOR_PACKAGING.md
│   ├── THIRD_PARTY_LICENSES.md
│   └── ROADMAP.md
├── tests/
│   ├── test_emulators.py
│   └── test_scanner.py
├── ROMs/
├── main.py
├── requirements.txt
└── README.md
~~~

## Development principles

1. Keep the app usable with a controller, keyboard, and mouse.
2. Keep emulator integration modular and independent of one frontend.
3. Do not bundle copyrighted game ROMs, BIOS files, firmware, keys, or commercial artwork.
4. Store user data locally and make ROM folders configurable.
5. Build and test for Raspberry Pi OS compatibility.
6. Clearly distinguish working features from planned features.
7. Preserve each third-party emulator's license and required notices when packaging.

## Roadmap

See docs/ROADMAP.md for planned milestones.

## License

No license has been selected for RetroDeck's own code yet. Until one is added, all rights are reserved by the author. Third-party emulator projects retain their own licenses.
