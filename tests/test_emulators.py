import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.emulators.catalog import SYSTEM_DEFAULTS
from app.emulators.launcher import EmulatorLaunchError, launch_game
from app.emulators.manager import (
    current_architecture, emulator_candidates, emulator_status, resolve_emulator,
)
from app.library.scanner import Game


class EmulatorManagerTests(unittest.TestCase):
    def test_finds_bundled_linux_executable(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            executable = root / "emulators" / "bin" / "linux" / "arm64" / "mupen64plus"
            executable.parent.mkdir(parents=True)
            executable.write_text("#!/bin/sh\\n", encoding="utf-8")
            with patch("app.emulators.manager.current_platform", return_value="linux"):
                with patch("app.emulators.manager.current_architecture", return_value="arm64"):
                    found = resolve_emulator("mupen64plus", root=root)
            self.assertEqual(found, executable.resolve())

    def test_legacy_bundle_path_still_works(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            executable = root / "emulators" / "bin" / "linux" / "mupen64plus"
            executable.parent.mkdir(parents=True)
            executable.write_text("#!/bin/sh\\n", encoding="utf-8")
            with patch("app.emulators.manager.current_platform", return_value="linux"):
                with patch("app.emulators.manager.current_architecture", return_value="arm64"):
                    found = resolve_emulator("mupen64plus", root=root)
            self.assertEqual(found, executable.resolve())

    def test_debian_game_directory_is_checked(self):
        with patch("app.emulators.manager.current_platform", return_value="linux"):
            with patch("app.emulators.manager.current_architecture", return_value="arm64"):
                candidates = list(emulator_candidates("mgba"))
        self.assertIn(Path("/usr/games/mgba-qt"), candidates)


    def test_finds_retrodeck_managed_install(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "mgba" / "0.10.5"
            root.mkdir(parents=True)
            executable = root / "mgba"
            executable.write_text("test", encoding="utf-8")
            with patch("app.emulators.manager.application_data_dir", return_value=Path(temporary).parent):
                # The managed root is application_data_dir()/emulators/<id>.
                managed_root = Path(temporary).parent / "emulators"
                (managed_root / "mgba").mkdir(parents=True)
                version = managed_root / "mgba" / "0.10.5"
                version.mkdir(parents=True, exist_ok=True)
                managed_executable = version / "mgba"
                managed_executable.write_text("test", encoding="utf-8")
                with patch("app.emulators.manager.current_platform", return_value="linux"):
                    with patch("app.emulators.manager.current_architecture", return_value="arm64"):
                        found = resolve_emulator("mgba", root=Path(temporary) / "empty")
                self.assertEqual(found, managed_executable.resolve())

    def test_unknown_emulator_is_not_available(self):
        self.assertFalse(emulator_status("not-real")["available"])

    def test_n64_has_default_emulator(self):
        self.assertEqual(SYSTEM_DEFAULTS["Nintendo 64"], "mupen64plus")

    def test_mgba_is_default_for_game_boy_color_and_advance(self):
        self.assertEqual(SYSTEM_DEFAULTS["Game Boy Color"], "mgba")
        self.assertEqual(SYSTEM_DEFAULTS["Game Boy Advance"], "mgba")

    def test_launcher_builds_expected_process_command(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            executable = root / "emulators" / "bin" / "linux" / "arm64" / "mupen64plus"
            executable.parent.mkdir(parents=True)
            executable.write_text("#!/bin/sh\\n", encoding="utf-8")
            rom = root / "Ocarina of Time.z64"
            rom.write_bytes(b"test")
            game = Game("Ocarina of Time", "Nintendo 64", rom)
            calls = []

            def fake_popen(command, cwd):
                calls.append((command, cwd))
                return "process"

            with patch("app.emulators.manager.current_platform", return_value="linux"):
                with patch("app.emulators.manager.current_architecture", return_value="arm64"):
                    process = launch_game(game, {}, popen=fake_popen, root=root)
            self.assertEqual(process, "process")
            self.assertEqual(calls[0][0], [str(executable.resolve()), str(rom.resolve())])

    def test_launcher_reports_missing_emulator(self):
        with tempfile.TemporaryDirectory() as temporary:
            rom = Path(temporary) / "game.z64"
            rom.write_bytes(b"test")
            game = Game("Game", "Nintendo 64", rom)
            with patch("app.emulators.manager.current_platform", return_value="linux"):
                with patch("app.emulators.manager.shutil.which", return_value=None):
                    with self.assertRaises(EmulatorLaunchError):
                        launch_game(game, {}, root=temporary)

    def test_pi_os_arm64_package_plan(self):
        plan = supported_package_plan("Linux", "aarch64", True)
        self.assertIn("dolphin", plan)
        self.assertIn("mgba", plan)
        self.assertIn("nestopia", plan)
        self.assertNotIn("mupen64plus", plan)

    def test_package_plan_rejects_unsupported_architecture(self):
        self.assertEqual(supported_package_plan("Linux", "x86_64", True), {})

    def test_package_plan_rejects_non_debian_os(self):
        self.assertEqual(supported_package_plan("Linux", "aarch64", False), {})

    def test_install_command_is_argument_list_and_rejects_bad_names(self):
        self.assertEqual(
            package_install_command(["dolphin-emu", "mgba-qt"]),
            ["pkexec", "apt-get", "install", "-y", "dolphin-emu", "mgba-qt"],
        )
        with self.assertRaises(ValueError):
            package_install_command(["dolphin-emu; rm -rf /"])


if __name__ == "__main__":
    unittest.main()
