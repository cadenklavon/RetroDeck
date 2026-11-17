# RetroDeck Project Handoff

## Mission
Build RetroDeck, a custom retro-gaming launcher for Raspberry Pi 5 running Raspberry Pi OS. It is a standalone desktop launcher, not a web page or replacement operating system.

## Product direction
- 16:9 landscape interface for a TV or monitor.
- Original RetroDeck branding and console-inspired navigation.
- Home screen as the default landing page.
- Dark and light themes.
- Artwork presentation adapts to available media and aspect ratio.
- Xbox controller navigation, with keyboard and mouse fallbacks.
- Develop on Windows, deploy to Raspberry Pi 5.
- Keep dependencies compatible with Raspberry Pi OS.

## Architecture decisions
- Python + PySide6 for the desktop UI prototype.
- SQLite for local library and settings data.
- Launch standalone emulator applications through configurable commands.
- RetroArch is not a required dependency.
- Example targets: Mupen64Plus for N64 and Dolphin for GameCube/Wii, subject to installation and hardware compatibility.
- ROM directories are selected/configured by the user.
- Never bundle ROMs, BIOS files, or copyrighted game artwork.

## Current state
The first prototype includes Home, Library, Consoles, Search, and Settings navigation, a dark/light theme toggle, placeholder game cards, and a keyboard shortcut to return Home.

Not implemented: ROM scanning, emulator detection/launching, gamepad input, SQLite persistence, artwork/metadata loading, functional search/filter, or per-game settings.

## Suggested architecture
```text
retrodeck/
├── app/
│   ├── ui/
│   ├── library/
│   ├── emulators/
│   ├── input/
│   ├── data/
│   └── services/
├── assets/
├── docs/
├── tests/
├── main.py
└── requirements.txt
```

Keep UI code separate from filesystem scanning, database operations, and process launching.

## Milestones
1. Stabilize UI layout and navigation.
2. Define game and emulator data models.
3. Add configurable ROM folders and safe scanning.
4. Add console grouping and search.
5. Add emulator profiles and explicit launch configuration.
6. Add controller navigation and input mapping.
7. Add local artwork/metadata management.
8. Add SQLite persistence, settings, and favorites.
9. Test on Raspberry Pi 5 and document installation.

## Working rules
- Inspect existing code before changing it.
- Preserve working functionality unless there is a clear reason to change it.
- Make small, reviewable commits.
- Explain dependencies and Raspberry Pi OS installation steps.
- Do not claim features work until tested.
- Make emulator executable paths and arguments configurable.
- Do not include copyrighted ROMs, BIOS files, or scraped commercial artwork.

## First next task
Refactor the prototype into a cleaner modular app while preserving its five navigation destinations and theme toggle. Keep it runnable on Raspberry Pi OS and add tests for non-UI logic as it appears.
