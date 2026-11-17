# Emulator packaging and installation

## Raspberry Pi OS 64-bit first

RetroDeck's first supported automatic system-package installation target is
Raspberry Pi OS / Debian-family Linux on ARM64. The app uses the system's
configured APT repositories and asks the desktop authorization service before
installing anything. It does not silently elevate privileges.

The first verified Debian ARM64 package set is:

| Emulator | Systems | Debian package | Status |
| --- | --- | --- | --- |
| Dolphin | GameCube and Wii | `dolphin-emu` | Package available for Debian 13 ARM64 |
| mGBA | Game Boy, Game Boy Color, GBA | `mgba-qt` | Package available for Debian 13 ARM64 |
| Nestopia | NES | `nestopia` | Package available for Debian 13 ARM64 |
| Mupen64Plus | Nintendo 64 | None in Debian 13 ARM64 | Requires a separately validated ARM64 build |
| bsnes | SNES | Not yet selected | Package/build verification required |
| melonDS | Nintendo DS | Not yet selected | Standalone ARM64 package verification required |
| PPSSPP | PSP | Not yet selected | Package/build verification required |

The APT package names above are fixed in code. RetroDeck runs
`pkexec apt-get install` only after the user confirms the install action.
The package manager handles dependencies and system updates. RetroDeck does
not download arbitrary binaries or run downloaded scripts.

## Executable discovery

Bundled builds use this layout:

```text
emulators/bin/<platform>/<architecture>/<executable>
```

The resolver also checks the older `emulators/bin/<platform>/` location for
backwards compatibility, Debian's `/usr/games`, `/usr/bin`, and
`/usr/local/bin`, then checks the system PATH. This permits distro
packages to work without copying their files into the RetroDeck repository.

## Important limitations

- Installing a package does not prove that every game runs at full speed.
  Each emulator still needs launch and controller testing on a Pi 5.
- Debian 13's Mupen64Plus console package is not built for ARM64. Do not offer
  it as an APT install on the Pi. A dedicated ARM64 build and its plugins must
  be validated before N64 is marked installed.
- Dolphin's package is a distro-maintained build. Its version can differ from
  the upstream release.
- Do not bundle commercial game files, console firmware, BIOS images, keys,
  or copyrighted artwork. Users must provide any required files themselves.
- Third-party license and notice obligations still apply to any binaries
  redistributed directly by RetroDeck.

## Current implementation

- Architecture-aware executable discovery.
- Fixed Debian ARM64 package plan for Dolphin, mGBA, and Nestopia.
- Explicit privileged APT install command, only after UI confirmation.
- Unit tests for platform filtering, package names, and launch discovery.

Still required:
- Run the installer on a real Raspberry Pi 5.
- Confirm the actual installed executable paths and launch arguments.
- Test representative games and controller mappings.
- Build and validate a native ARM64 Mupen64Plus package.
