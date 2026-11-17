import tempfile
import unittest
from pathlib import Path

from app.library.scanner import scan_rom_directories


class ScannerTests(unittest.TestCase):
    def test_discovers_supported_files_recursively_and_ignores_unknown_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            nested = root / "Nintendo 64"
            nested.mkdir()
            (nested / "Ocarina of Time.z64").write_bytes(b"test")
            (nested / "notes.txt").write_text("not a game", encoding="utf-8")
            games, warnings = scan_rom_directories([root])
            self.assertEqual(warnings, [])
            self.assertEqual(len(games), 1)
            self.assertEqual(games[0].title, "Ocarina of Time")
            self.assertEqual(games[0].system, "Nintendo 64")

    def test_deduplicates_same_folder(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "game.gba").write_bytes(b"test")
            games, _ = scan_rom_directories([root, root])
            self.assertEqual(len(games), 1)

    def test_reports_missing_folder(self):
        with tempfile.TemporaryDirectory() as temporary:
            missing = Path(temporary) / "missing"
            games, warnings = scan_rom_directories([missing])
            self.assertEqual(games, [])
            self.assertEqual(len(warnings), 1)


if __name__ == "__main__":
    unittest.main()
