import hashlib
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from app.emulators.managed_installer import (
    _safe_member_path, application_data_dir, install_package,
    load_manifest, sha256_file, validate_package,
)


class ManagedInstallerTests(unittest.TestCase):
    def test_app_data_is_per_user(self):
        with patch("app.emulators.managed_installer.os.name", "posix"):
            with patch("app.emulators.managed_installer.platform.system", return_value="Linux"):
                with patch.dict("os.environ", {"XDG_DATA_HOME": "/tmp/rd-data"}):
                    self.assertEqual(application_data_dir(), Path("/tmp/rd-data/RetroDeck"))

    def test_rejects_non_https_or_unapproved_host(self):
        package = {"id":"mgba","version":"1","platform":"linux","architecture":"arm64",
                   "url":"http://example.com/file","sha256":"a"*64,"archive":"appimage",
                   "executable":"mgba.AppImage"}
        with self.assertRaises(ValueError):
            validate_package(package, {"example.com"})

    def test_rejects_bad_digest(self):
        package = {"id":"mgba","version":"1","platform":"linux","architecture":"arm64",
                   "url":"https://example.com/file","sha256":"bad","archive":"appimage",
                   "executable":"mgba.AppImage"}
        with self.assertRaises(ValueError):
            validate_package(package, {"example.com"})

    def test_blocks_archive_path_traversal(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                _safe_member_path(Path(temp), "../outside")

    def test_loads_empty_reviewed_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "manifest.json"
            path.write_text(json.dumps({"schema_version":1,"packages":[]}), encoding="utf-8")
            self.assertEqual(load_manifest(path)["packages"], [])

    def test_download_verifies_hash_and_installs_appimage(self):
        payload = b"fake appimage for unit test"
        digest = hashlib.sha256(payload).hexdigest()
        package = {"id":"testemu","version":"1.0","platform":"linux","architecture":"arm64",
                   "url":"https://downloads.example.test/test.AppImage","sha256":digest,
                   "archive":"appimage","executable":"test.AppImage"}
        class Response(io.BytesIO):
            def __enter__(self): return self
            def __exit__(self, *args): self.close()
        with tempfile.TemporaryDirectory() as temp:
            result = install_package(package, Path(temp), {"downloads.example.test"},
                                     opener=lambda *args, **kwargs: Response(payload))
            self.assertEqual(result.read_bytes(), payload)
            self.assertTrue(result.stat().st_mode & 0o111)

    def test_bad_hash_never_installs(self):
        package = {"id":"testemu","version":"1.0","platform":"linux","architecture":"arm64",
                   "url":"https://downloads.example.test/test.AppImage","sha256":"0"*64,
                   "archive":"appimage","executable":"test.AppImage"}
        class Response(io.BytesIO):
            def __enter__(self): return self
            def __exit__(self, *args): self.close()
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                install_package(package, Path(temp), {"downloads.example.test"},
                                opener=lambda *args, **kwargs: Response(b"not matching"))
            self.assertFalse((Path(temp) / "testemu").exists())



    def test_installs_official_appimage_zip_and_reports_progress(self):
        archive_buffer = io.BytesIO()
        with zipfile.ZipFile(archive_buffer, "w") as archive:
            archive.writestr("package/melonDS-aarch64.AppImage", b"fake appimage")
        payload = archive_buffer.getvalue()
        digest = hashlib.sha256(payload).hexdigest()
        package = {
            "id": "melonds", "version": "1.1", "platform": "linux",
            "architecture": "arm64",
            "url": "https://github.com.example.test/melonds.zip",
            "sha256": digest, "size": len(payload),
            "archive": "appimage_zip", "executable": "melonDS.AppImage",
        }

        class Response(io.BytesIO):
            def __enter__(self): return self
            def __exit__(self, *args): self.close()

        progress = []
        with tempfile.TemporaryDirectory() as temp:
            result = install_package(
                package, Path(temp), {"github.com.example.test"},
                opener=lambda *args, **kwargs: Response(payload),
                progress_callback=lambda downloaded, total: progress.append((downloaded, total)),
            )
            self.assertEqual(result.read_bytes(), b"fake appimage")
            self.assertTrue(result.stat().st_mode & 0o111)
            self.assertTrue(progress)
            self.assertEqual(progress[-1], (len(payload), len(payload)))

    def test_manifest_contains_checksum_pinned_pi_arm64_package(self):
        manifest = load_manifest()
        packages = [
            package for package in manifest["packages"]
            if package.get("id") == "melonds"
            and package.get("platform") == "linux"
            and package.get("architecture") == "arm64"
        ]
        self.assertTrue(packages)
        self.assertEqual(len(packages[0]["sha256"]), 64)
        self.assertEqual(packages[0]["archive"], "appimage_zip")

if __name__ == "__main__":
    unittest.main()
