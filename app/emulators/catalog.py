"""Metadata for standalone emulator integrations.

The catalog distinguishes emulator candidates from packages verified for a
specific operating system. A system package is not a RetroDeck-bundled binary.
"""
EMULATOR_CATALOG = {
    "mupen64plus": {
        "name": "Mupen64Plus", "systems": ["Nintendo 64"],
        "project_url": "https://github.com/mupen64plus",
        "license": "GPL-2.0-or-later; verify exact component/build",
        "license_status": "review-required",
        "executables": {"linux": ["mupen64plus"], "windows": ["mupen64plus.exe"]},
        "arguments": ["{rom}"],
    },
    "dolphin": {
        "name": "Dolphin", "systems": ["Nintendo GameCube", "Nintendo Wii", "GameCube / Wii"],
        "project_url": "https://github.com/dolphin-emu/dolphin",
        "license": "GPL-2.0-or-later",
        "license_status": "source-and-notice-review-required",
        "executables": {"linux": ["dolphin-emu", "dolphin"], "windows": ["Dolphin.exe"]},
        "arguments": ["-e", "{rom}"],
    },
    "nestopia": {
        "name": "Nestopia", "systems": ["Nintendo Entertainment System"],
        "project_url": "https://github.com/libretro/nestopia",
        "license": "GPL-2.0 core lineage; standalone build must be verified",
        "license_status": "review-required",
        "executables": {"linux": ["nestopia"], "windows": ["nestopia.exe"]},
        "arguments": ["{rom}"],
    },
    "bsnes": {
        "name": "bsnes", "systems": ["Super Nintendo"],
        "project_url": "https://github.com/bsnes-emu/bsnes",
        "license": "GPL-3.0-or-later; verify selected release",
        "license_status": "review-required",
        "executables": {"linux": ["bsnes"], "windows": ["bsnes.exe"]},
        "arguments": ["{rom}"],
    },
    "gambatte": {
        "name": "Gambatte", "systems": ["Game Boy", "Game Boy Color"],
        "project_url": "https://github.com/libretro/gambatte",
        "license": "GPL-2.0 core lineage; standalone packaging not selected",
        "license_status": "review-required",
        "executables": {"linux": ["gambatte"], "windows": ["gambatte.exe"]},
        "arguments": ["{rom}"],
    },
    "mgba": {
        "name": "mGBA", "systems": ["Game Boy", "Game Boy Color", "Game Boy Advance"],
        "project_url": "https://github.com/mgba-emu/mgba",
        "license": "MPL-2.0",
        "license_status": "source-and-notice-review-required",
        "executables": {"linux": ["mgba", "mgba-qt"], "windows": ["mGBA.exe"]},
        "arguments": ["{rom}"],
    },
    "melonds": {
        "name": "melonDS", "systems": ["Nintendo DS"],
        "project_url": "https://github.com/melonDS-emu/melonDS",
        "license": "GPL-3.0-or-later",
        "license_status": "review-required",
        "executables": {"linux": ["melonDS.AppImage", "melonDS"], "windows": ["melonDS.exe"]},
        "arguments": ["{rom}"],
    },
    "ppsspp": {
        "name": "PPSSPP", "systems": ["PlayStation Portable"],
        "project_url": "https://github.com/hrydgard/ppsspp",
        "license": "GPL-2.0-or-later",
        "license_status": "review-required",
        "executables": {"linux": ["PPSSPP"], "windows": ["PPSSPPWindows64.exe", "PPSSPPWindows.exe"]},
        "arguments": ["{rom}"],
    },
}
SYSTEM_DEFAULTS = {
    system: emulator_id
    for emulator_id, profile in EMULATOR_CATALOG.items()
    for system in profile["systems"]
}
