# Emulator packaging plan

## Goal

A person installing a RetroDeck release should not have to find, download, or
configure each emulator manually. RetroDeck should provide a first-run setup
flow and install approved builds into its own application data directory.

Compiled emulator binaries should not be committed to the source repository.
They belong in platform-specific RetroDeck release assets, or should be
downloaded by the app from a versioned manifest published with an official
RetroDeck release. This keeps Git history small and permits separate ARM64
and Windows packages.

## Target order

1. Raspberry Pi OS 64-bit on Raspberry Pi 5 (Linux ARM64 / aarch64).
2. Windows x64 development package.
3. Other Linux architectures only after testing.

A Linux ARM64 build must not be assumed compatible with Windows or x86-64.
Each package needs its own build, dependency, and runtime validation.

## Initial standalone emulator candidates

| System | Candidate | Upstream project | Status |
| --- | --- | --- | --- |
| Nintendo 64 | Mupen64Plus | https://github.com/mupen64plus | Build and license review required |
| GameCube / Wii | Dolphin | https://github.com/dolphin-emu/dolphin | Build and license review required |
| NES | Nestopia | https://github.com/libretro/nestopia | Verify standalone app/build choice |
| SNES | bsnes | https://github.com/bsnes-emu/bsnes | Verify standalone ARM64 build |
| Game Boy / Color | Gambatte | https://github.com/libretro/gambatte | Verify standalone app/build choice |
| Game Boy Advance | mGBA | https://github.com/mgba-emu/mgba | Build and license review required |
| Nintendo DS | melonDS | https://github.com/melonDS-emu/melonDS | Build and license review required |
| PSP | PPSSPP | https://github.com/hrydgard/ppsspp | Build and license review required |

These are candidates, not a claim that every emulator is currently bundled or
tested. Some upstream projects expose libretro cores as well as standalone
applications. RetroDeck intends to launch standalone applications and will
not depend on RetroArch.

## Proposed release layout

~~~text
RetroDeck/
├── app/emulators/
│   ├── catalog.py
│   ├── manager.py
│   └── launcher.py
├── emulators/bin/
│   ├── linux/
│   │   └── arm64/
│   └── windows/
├── licenses/third_party/
├── packaging/manifests/
├── packaging/scripts/
└── docs/
~~~

The current resolver uses emulators/bin/<platform> as its initial lookup path.
The final release layout can add architecture folders once the first ARM64
build pipeline is validated. Never put local game files, firmware, or BIOS
images in this directory.

## Planned first-run installation

1. Detect the operating system and CPU architecture.
2. Read a versioned manifest from a trusted RetroDeck release.
3. Show compatible emulator packages and offer install-selected or install-all.
4. Download only approved packages.
5. Verify each archive's SHA-256 checksum before extraction.
6. Extract into RetroDeck's application data directory, never over user files.
7. Record installed version, source URL, checksum, and license details.
8. Recheck installed files on later launches and offer safe updates.

Downloads must use HTTPS and pinned checksums from a trusted RetroDeck release.
The app must not execute a downloaded file until checksum validation succeeds.
An interrupted install must leave any previous working version intact.

## Redistribution and firmware

- Every emulator retains its own upstream license and copyright notices.
- Review the exact release, dependencies, build options, and license obligations
  before redistributing any binary.
- For GPL-covered binaries, publish corresponding source and required
  build/patch information as required by the applicable license.
- Include required license texts and third-party notices with each package.
- Add a third-party notices screen in RetroDeck.
- Do not bundle commercial game files, console firmware, BIOS images, keys, or
  copyrighted artwork. If an emulator requires firmware, users must supply a
  legally obtained copy.
- Free download does not automatically mean permission to redistribute.
- Snes9x is not selected at this stage because its licensing terms need a
  separate review. bsnes is the current SNES candidate, subject to verification.

## Current implementation

Implemented in the source repository:
- Central emulator candidate catalog with upstream links and review status.
- Resolver checks a configured executable, a RetroDeck-bundled executable,
  then the system PATH.
- Default emulator mappings for the detected systems.
- Process launcher with argument-list handling and clear errors.
- Unit tests for discovery and launch-command construction.

Not implemented:
- Emulator binaries or source trees.
- Automatic downloads, checksum verification, extraction, or updates.
- ARM64 build scripts and reproducible builds.
- A graphical emulator manager.
- End-to-end tests with real emulator builds and games.

Do not mark an emulator as bundled until its exact build, architecture, notices,
and Raspberry Pi 5 launch test have been recorded.
