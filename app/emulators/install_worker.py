"""Background worker for installing reviewed emulator packages."""
from PySide6.QtCore import QThread, Signal

from app.emulators.managed_installer import install_package


class EmulatorInstallWorker(QThread):
    progress_changed = Signal(str, int, int)
    package_started = Signal(str)
    package_finished = Signal(str, str)
    setup_finished = Signal(bool, str)

    def __init__(self, packages, allowed_hosts, parent=None):
        super().__init__(parent)
        self.packages = list(packages)
        self.allowed_hosts = set(allowed_hosts)

    def run(self):
        completed = []
        failures = []
        total_packages = max(1, len(self.packages))
        for index, package in enumerate(self.packages):
            emulator_id = package["id"]
            self.package_started.emit(emulator_id)

            def report(downloaded, total, package_id=emulator_id, package_index=index):
                if total > 0:
                    package_percent = min(100, int(downloaded * 100 / total))
                else:
                    package_percent = 0
                overall = int((package_index * 100 + package_percent) / total_packages)
                self.progress_changed.emit(package_id, overall, package_percent)

            try:
                executable = install_package(
                    package,
                    allowed_hosts=self.allowed_hosts,
                    progress_callback=report,
                )
                completed.append(f"{emulator_id}: {executable}")
                self.package_finished.emit(emulator_id, "installed")
            except Exception as exc:
                failures.append(f"{emulator_id}: {exc}")
                self.package_finished.emit(emulator_id, "failed")

        if failures:
            message = "Installed: " + str(len(completed)) + ". Failed: " + " | ".join(failures)
            self.setup_finished.emit(False, message)
        else:
            self.setup_finished.emit(True, f"Installed {len(completed)} emulator package(s).")
