# Emulator packaging and installation

## Product requirement

RetroDeck should feel like a console setup. Users should not need a terminal,
package manager, administrator password, or manual emulator paths.

Managed emulator files belong in the user's application-data directory:

- Linux: `~/.local/share/RetroDeck/emulators/` (or `$XDG_DATA_HOME`)
- Windows: `%LOCALAPPDATA%/RetroDeck/emulators/`
- macOS: `~/Library/Application Support/RetroDeck/emulators/`

The ROM library remains separate and is never modified by emulator installation.

## Implemented setup flow

- At startup, RetroDeck checks the manifest for packages matching the current
  operating system and CPU architecture.
- Missing compatible packages are downloaded automatically in a background
  QThread. The app remains responsive.
- The Emulators page also has an install button for manual retry.
- A progress bar reports the active package and overall download percentage.
- Downloads are HTTPS-only, size-limited, SHA-256 checked, and installed into
  versioned per-user directories.
- ZIP and tar extraction rejects traversal paths, links, special files, and
  oversized expanded archives.
- AppImage-in-ZIP packages are accepted only when the archive contains exactly
  one AppImage. The file is renamed to the manifest's stable executable name.
- The game launcher searches RetroDeck-managed installs.

## Currently published Raspberry Pi package

The manifest currently includes one package:

| Emulator | Version | Platform | Download | Verification |
|---|---:|---|---:|---|
| melonDS | 1.1 | Linux ARM64 | 33.4 MB | SHA-256 pinned from official GitHub release metadata |

Official asset:
`https://github.com/melonDS-emu/melonDS/releases/download/1.1/melonDS-1.1-appimage-aarch64.zip`

The official release asset publishes SHA-256
`c537ae018d6dcedfe9da0317a1d5c0163e69201e23abfa163fa2a63e437ace09`.
The installer checks the downloaded bytes against this value before extracting.

This confirms package provenance and download integrity, not successful runtime
compatibility on every Raspberry Pi OS image. The AppImage must still be
launched and tested on the user's Pi 5, including its runtime/FUSE requirements,
ROM launch, audio, and controller behavior.

## Package approval policy

A package is not eligible for automatic installation merely because an upstream
download exists. Before enabling additional packages, RetroDeck must verify:

1. The exact official upstream asset and release version.
2. A trustworthy SHA-256 value or publisher signature.
3. CPU architecture and operating-system compatibility.
4. Runtime dependencies on the target Raspberry Pi OS release.
5. Executable path and launch arguments.
6. License, notices, and source-code obligations.
7. A real launch smoke test on Raspberry Pi 5.

mGBA publishes an ARM64 AppImage, but the current release asset does not expose
a publisher SHA-256 digest through GitHub release metadata. It is therefore
not yet enabled in the automatic manifest. Dolphin, Mupen64Plus, Nestopia,
bsnes, Gambatte, and PPSSPP need the same platform-specific review and testing
before they are automatically installed.

## Remaining work

- Validate melonDS launch on Raspberry Pi 5 and confirm AppImage runtime
  dependencies are satisfied without asking the user to install packages.
- Add checksum-pinned mGBA and additional standalone emulators.
- Add update, repair, rollback, and removal controls.
- Validate each emulator with actual games and controller input on Pi 5.
- Add Windows x64 packages after the Pi experience is reliable.

No ROMs, BIOS images, firmware, encryption keys, or copyrighted artwork are
downloaded or bundled by RetroDeck. Users provide any legally required game
files and firmware themselves.
