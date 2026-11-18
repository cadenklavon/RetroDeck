import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.emulators.catalog import SYSTEM_DEFAULTS
from app.emulators.launcher import EmulatorLaunchError, launch_game
from app.emulators.manager import emulator_candidates, emulator_status, resolve_emulator
from app.library.scanner import Game


class EmulatorManagerTests(unittest.TestCase):
    def test_finds_bundled_linux_executable(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            executable = root / "emulators" / "bin" / "linux" / "arm64" / "mupen64plus"
            executable.parent.mkdir(parents=True)
            executable.write_text("test", encoding="utf-8")
            with patch("app.emulators.manager.current_platform", return_value="linux"):
                with patch("app.emulators.manager.current_architecture", return_value="arm64"):
                    found = resolve_emulator("mupen64plus", root=root)
            self.assertEqual(found, executable.resolve())

    def test_legacy_bundle_path_still_works(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            executable = root / "emulators" / "bin" / "linux" / "mupen64plus"
            executable.parent.mkdir(parents=True)
            executable.write_text("test", encoding="utf-8")
            with patch("app.emulators.manager.current_platform", return_value="linux"):
                with patch("app.emulators.manager.current_architecture", return_value="arm64"):
                    found = resolve_emulator("mupen64plus", root=root)
            self.assertEqual(found, executable.resolve())

    def test_finds_retrodeck_managed_install(self):
        with tempfile.TemporaryDirectory() as temporary:
            data_root = Path(temporary) / "user-data"
            executable = data_root / "emulators" / "mgba" / "0.10.5" / "mgba"
            executable.parent.mkdir(parents=True)
            executable.write_text("test", encoding="utf-8")
            with patch("app.emulators.manager.application_data_dir", return_value=data_root):
                with patch("app.emulators.manager.current_platform", return_value="linux"):
                    with patch("app.emulators.manager.current_architecture", return_value="arm64"):
                        found = resolve_emulator("mgba", root=Path(temporary) / "empty")
            self.assertEqual(found, executable.resolve())

    def test_debian_game_directory_is_checked(self):
        with patch("app.emulators.manager.current_platform", return_value="linux"):
            with patch("app.emulators.manager.current_architecture", return_value="arm64"):
                candidates = list(emulator_candidates("mgba"))
        self.assertIn(Path("/usr/games/mgba-qt"), candidates)

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
            executable.write_text("test", encoding="utf-8")
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


if __name__ == "__main__":
    unittest.main()
