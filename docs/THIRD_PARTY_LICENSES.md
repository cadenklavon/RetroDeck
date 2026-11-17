# Third-party emulator notices

RetroDeck's emulator catalog currently lists candidate projects only. No
third-party emulator binary is included in this repository yet.

Before redistributing a binary, add a directory for that exact release with:
- The upstream license text.
- Copyright and attribution notices.
- Required notices for bundled libraries and assets.
- Exact upstream version or commit.
- Source-code location and any RetroDeck patches/build scripts required by
  the applicable license.
- Target operating system and CPU architecture.

## Candidate project references

| Project | Upstream source | Review status |
| --- | --- | --- |
| Mupen64Plus | https://github.com/mupen64plus | Verify exact selected component and release |
| Dolphin | https://github.com/dolphin-emu/dolphin | Verify current release notices and dependencies |
| Nestopia | https://github.com/libretro/nestopia | Verify standalone build and component licensing |
| bsnes | https://github.com/bsnes-emu/bsnes | Verify selected release and dependencies |
| Gambatte | https://github.com/libretro/gambatte | Verify standalone build and component licensing |
| mGBA | https://github.com/mgba-emu/mgba | Upstream states MPL-2.0 |
| melonDS | https://github.com/melonDS-emu/melonDS | Upstream states GPL-3.0-or-later |
| PPSSPP | https://github.com/hrydgard/ppsspp | Verify selected release and bundled dependencies |

This is a tracking document, not legal advice or a completed redistribution
review. The exact source revision and build configuration determine which
notices and source obligations apply.
