# RetroDeck

**A custom retro-gaming launcher for Raspberry Pi 5.**

RetroDeck is an in-development desktop application designed to organize and launch a personal retro-game library from one controller-friendly interface. The target platform is Raspberry Pi OS on Raspberry Pi 5.

> **Project status:** Early prototype. The current build is a UI foundation with placeholder game entries. ROM discovery, emulator integration, artwork management, persistence, and controller support are planned, not yet implemented.

## Vision

Create a polished, console-inspired launcher that makes a Raspberry Pi feel like a dedicated retro-gaming system, while remaining a normal Linux desktop application underneath.

## Planned experience

- Home screen with recently played and favorite games
- Library organized by console/system
- Search and filtering
- Game details with cover art and metadata
- Keyboard, mouse, and Xbox-controller navigation
- Configurable emulator commands per system or game
- Automatic discovery of ROM files in user-selected folders
- Dark and light themes
- Local SQLite database for library metadata and settings

## Planned architecture

| Layer | Planned technology |
| --- | --- |
| Desktop UI | Python + PySide6 |
| Local data | SQLite |
| Emulator integration | Launch configured external emulator processes |
| Game discovery | Scanning user-selected ROM directories |
| Target hardware | Raspberry Pi 5 |
| Target OS | Raspberry Pi OS |

RetroDeck is intended to launch standalone emulators directly. It will not require RetroArch as its central runtime. For example, users could configure Mupen64Plus for Nintendo 64 titles and Dolphin for GameCube/Wii titles, provided those emulators are installed and compatible with the device.

## Run the prototype

Install Python 3, then install the dependency:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

If creating a virtual environment fails because the venv package is missing, install it with:

```bash
sudo apt update
sudo apt install python3-venv
```

## Repository layout

```text
RetroDeck/
├── assets/
│   └── covers/
├── docs/
│   └── ROADMAP.md
├── .gitignore
├── CODEX_HANDOFF.md
├── main.py
├── README.md
└── requirements.txt
```

## Development principles

1. Keep the app usable with a controller, keyboard, and mouse.
2. Keep emulator integration modular. The launcher should not depend on one emulator frontend.
3. Do not bundle copyrighted game ROMs, BIOS files, or commercial artwork.
4. Store user data locally and make ROM folders configurable.
5. Build and test for Raspberry Pi OS compatibility, not just Windows development machines.

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for planned milestones.

## Contributing / feedback

This is a personal learning project under active development. Suggestions and bug reports are welcome through GitHub Issues.

## License

No license has been selected yet. Until one is added, all rights are reserved by the author. Please do not assume the code is available for reuse.
