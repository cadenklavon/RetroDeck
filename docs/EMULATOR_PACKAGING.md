# Emulator packaging and installation

## Product requirement

RetroDeck should feel like a console setup, not a Linux maintenance task.
Users should not need to open a terminal, run package-manager commands, find
emulator downloads, set executable paths, or grant administrator access just
to install an emulator.

Managed emulator files belong in the user's application-data directory:

- Linux: `~/.local/share/RetroDeck/emulators/` (or `$XDG_DATA_HOME`)
- Windows: `%LOCALAPPDATA%/RetroDeck/emulators/`
- macOS: `~/Library/Application Support/RetroDeck/emulators/`

The ROM library remains separate and is never modified by emulator installation.

## Managed package architecture

`app/emulators/managed_installer.py` provides the first implementation of
the package installation engine:

- Reads a versioned JSON package manifest.
- Accepts HTTPS downloads only from explicitly approved hosts.
- Requires a pinned SHA-256 digest before any archive is extracted.
- Streams downloads to a temporary directory.
- Extracts ZIP and tar archives while rejecting path traversal, links, and
  special files.
- Installs into a per-user versioned directory without administrator rights.
- Marks Linux AppImages and executable files as executable.
- Keeps incomplete or checksum-failing downloads out of the installed path.
- Uses atomic directory movement after verification.

The executable resolver checks RetroDeck's per-user managed directory before
legacy project folders and system-installed executables.

## Package approval policy

A package is not eligible for the manifest merely because an upstream download
exists. Before enabling an automatic install, RetroDeck must verify:

1. The exact official upstream asset and release version.
2. A trustworthy SHA-256 value or publisher signature.
3. CPU architecture and operating-system compatibility.
4. Runtime dependencies on the target Raspberry Pi OS release.
5. The executable path and launch arguments.
6. License, notices, and source-code obligations.
7. A real launch smoke test on Raspberry Pi 5.

The current manifest is intentionally empty. This prevents RetroDeck from
silently offering an unverified binary. The official mGBA project publishes
an ARM64 AppImage, and Dolphin publishes ARM64 Linux builds, but their runtime
requirements and package hashes still need to be pinned and tested before
they become one-click installs.

## Current status

Implemented:
- Per-user emulator application-data paths.
- Manifest validation and approved-host checks.
- SHA-256 verification before installation.
- Safe ZIP and tar extraction.
- Atomic versioned installation.
- Managed-install discovery by the game launcher.
- Unit tests for validation, path traversal protection, and verified install.

Not yet complete:
- Populate the manifest with reviewed Pi 5 ARM64 builds.
- Add a background download worker and progress display.
- Add first-run setup that installs the compatible emulator set automatically.
- Add update, repair, rollback, and removal controls.
- Validate each emulator with actual games and controller input on Raspberry Pi 5.
- Add Windows x64 packages after the Pi experience is reliable.

No ROMs, BIOS images, firmware, encryption keys, or copyrighted artwork are
downloaded or bundled by RetroDeck. Users supply any legally required game
files and firmware themselves.
