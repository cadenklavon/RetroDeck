"""RetroDeck desktop launcher.

Stage 3 adds the standalone emulator catalog, executable discovery, and game launching.
The ROM scanner only reads filenames and paths. It never modifies game files.
"""
import sys

from PySide6.QtCore import QProcess, Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QFrame, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QMainWindow, QMessageBox, QPushButton, QLineEdit,
    QStackedWidget, QVBoxLayout, QWidget,
)

from app.config.settings import load_settings, save_settings
from app.library.scanner import scan_rom_directories
from app.emulators.catalog import EMULATOR_CATALOG
from app.emulators.installer import package_install_command, supported_package_plan
from app.emulators.launcher import EmulatorLaunchError, launch_game
from app.emulators.manager import emulator_status


DARK_THEME = """
* { font-family: "Inter", "DejaVu Sans", sans-serif; }
QMainWindow, QWidget#Root, QWidget#Page { background: #0b1020; color: #eef2ff; }
QWidget#Sidebar { background: #10182b; border: 1px solid #202c46; border-radius: 16px; }
QLabel#Brand { color: #f5f7ff; font-size: 20px; font-weight: 900; letter-spacing: 2px; }
QLabel#Eyebrow { color: #72d9ff; font-size: 11px; font-weight: 800; letter-spacing: 1px; }
QLabel#PageTitle { color: #f4f6ff; font-size: 27px; font-weight: 800; }
QLabel#Muted { color: #9aa8c2; font-size: 12px; }
QLabel#SectionTitle { color: #f0f3ff; font-size: 18px; font-weight: 750; }
QPushButton#NavButton { color: #9eabc6; background: transparent; border: 1px solid transparent; border-radius: 9px; padding: 11px; text-align: left; }
QPushButton#NavButton:hover { background: #1b2943; color: white; }
QPushButton#NavButton:checked { color: white; background: #203754; border: 1px solid #31577b; }
QPushButton#PrimaryButton { color: #071321; background: #72d9ff; border: 0; border-radius: 9px; padding: 11px 15px; font-weight: 800; }
QPushButton#PrimaryButton:hover { background: #a0e7ff; }
QPushButton#SecondaryButton { color: #eaf2ff; background: #1b2943; border: 1px solid #344664; border-radius: 9px; padding: 10px 14px; }
QPushButton#SecondaryButton:hover { background: #293b5b; }
QLineEdit { color: #f5f7ff; background: #121c31; border: 1px solid #2b3b59; border-radius: 9px; padding: 11px; }
QListWidget { color: #eef2ff; background: #121c31; border: 1px solid #263653; border-radius: 12px; padding: 7px; }
QListWidget::item { padding: 12px 10px; border-bottom: 1px solid #263653; }
QListWidget::item:selected { background: #203754; border-radius: 6px; }
QFrame#Panel { background: #121c31; border: 1px solid #263653; border-radius: 14px; }
QPushButton:focus, QLineEdit:focus, QListWidget:focus { border: 2px solid #72d9ff; }
"""

LIGHT_THEME = """
* { font-family: "Inter", "DejaVu Sans", sans-serif; }
QMainWindow, QWidget#Root, QWidget#Page { background: #edf2f9; color: #18243a; }
QWidget#Sidebar { background: white; border: 1px solid #d8e0ec; border-radius: 16px; }
QLabel#Brand { color: #17243a; font-size: 20px; font-weight: 900; letter-spacing: 2px; }
QLabel#Eyebrow { color: #087da9; font-size: 11px; font-weight: 800; letter-spacing: 1px; }
QLabel#PageTitle { color: #17243a; font-size: 27px; font-weight: 800; }
QLabel#Muted { color: #687791; font-size: 12px; }
QLabel#SectionTitle { color: #17243a; font-size: 18px; font-weight: 750; }
QPushButton#NavButton { color: #64728a; background: transparent; border: 1px solid transparent; border-radius: 9px; padding: 11px; text-align: left; }
QPushButton#NavButton:hover { background: #edf3fb; color: #17243a; }
QPushButton#NavButton:checked { color: #075d7e; background: #e1f3fb; border: 1px solid #b9e2f1; }
QPushButton#PrimaryButton { color: white; background: #087da9; border: 0; border-radius: 9px; padding: 11px 15px; font-weight: 800; }
QPushButton#SecondaryButton { color: #1a2a42; background: white; border: 1px solid #cbd6e5; border-radius: 9px; padding: 10px 14px; }
QLineEdit { color: #18243a; background: white; border: 1px solid #cbd6e5; border-radius: 9px; padding: 11px; }
QListWidget { color: #18243a; background: white; border: 1px solid #d8e0ec; border-radius: 12px; padding: 7px; }
QListWidget::item { padding: 12px 10px; border-bottom: 1px solid #e2e8f0; }
QListWidget::item:selected { background: #e1f3fb; border-radius: 6px; }
QFrame#Panel { background: white; border: 1px solid #d8e0ec; border-radius: 14px; }
QPushButton:focus, QLineEdit:focus, QListWidget:focus { border: 2px solid #087da9; }
"""


class RetroDeckWindow(QMainWindow):
    PAGES = ["Home", "Library", "Systems", "Search", "Emulators", "Settings"]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RetroDeck")
        self.resize(1200, 760)
        self.settings = load_settings()
        self.games = []
        self.dark_mode = self.settings.get("theme", "dark") == "dark"
        self.nav_buttons = {}

        root = QWidget()
        root.setObjectName("Root")
        shell = QHBoxLayout(root)
        shell.setContentsMargins(14, 14, 14, 14)
        shell.setSpacing(14)
        shell.addWidget(self.build_sidebar())

        content = QVBoxLayout()
        self.breadcrumb = QLabel("HOME")
        self.breadcrumb.setObjectName("Eyebrow")
        content.addWidget(self.breadcrumb)

        self.pages = QStackedWidget()
        self.pages.addWidget(self.build_home_page())
        self.pages.addWidget(self.build_library_page())
        self.pages.addWidget(self.build_systems_page())
        self.pages.addWidget(self.build_search_page())
        self.pages.addWidget(self.build_emulators_page())
        self.pages.addWidget(self.build_settings_page())
        content.addWidget(self.pages, 1)
        shell.addLayout(content, 1)
        self.setCentralWidget(root)

        self.apply_theme()
        self.show_page("Home")
        self.install_shortcuts()
        self.refresh_library(show_status=False)

    def build_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(190)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(13, 18, 13, 14)
        layout.setSpacing(8)
        brand = QLabel("◈  RETRODECK")
        brand.setObjectName("Brand")
        layout.addWidget(brand)
        caption = QLabel("YOUR GAME SPACE")
        caption.setObjectName("Eyebrow")
        caption.setContentsMargins(5, 18, 0, 8)
        layout.addWidget(caption)
        for icon, name in [("⌂", "Home"), ("▦", "Library"), ("◈", "Systems"), ("⌕", "Search"), ("⬇", "Emulators")]:
            button = QPushButton(f"{icon}    {name}")
            button.setObjectName("NavButton")
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, page=name: self.show_page(page))
            self.nav_buttons[name] = button
            layout.addWidget(button)
        layout.addStretch()
        settings_button = QPushButton("⚙    Settings")
        settings_button.setObjectName("NavButton")
        settings_button.setCheckable(True)
        settings_button.clicked.connect(lambda: self.show_page("Settings"))
        self.nav_buttons["Settings"] = settings_button
        layout.addWidget(settings_button)
        return sidebar

    def make_page(self):
        page = QWidget()
        page.setObjectName("Page")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(6, 8, 6, 6)
        layout.setSpacing(12)
        return page, layout

    def page_heading(self, layout, title, subtitle):
        heading = QLabel(title)
        heading.setObjectName("PageTitle")
        note = QLabel(subtitle)
        note.setObjectName("Muted")
        note.setWordWrap(True)
        layout.addWidget(heading)
        layout.addWidget(note)

    def build_home_page(self):
        page, layout = self.make_page()
        self.page_heading(layout, "Welcome to RetroDeck", "Your games, from every system, in one place.")
        panel = QFrame()
        panel.setObjectName("Panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(20, 18, 20, 18)
        title = QLabel("Your collection")
        title.setObjectName("SectionTitle")
        self.home_count = QLabel("Scanning your folders…")
        self.home_count.setObjectName("Muted")
        scan = QPushButton("Scan game folders")
        scan.setObjectName("PrimaryButton")
        scan.clicked.connect(self.refresh_library)
        panel_layout.addWidget(title)
        panel_layout.addWidget(self.home_count)
        panel_layout.addWidget(scan, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(panel)
        info = QLabel("Start by adding the folders that contain your legally obtained game files in Settings. RetroDeck scans filenames and organizes matches by system. It does not move or change your files.")
        info.setObjectName("Muted")
        info.setWordWrap(True)
        layout.addWidget(info)
        layout.addStretch()
        return page

    def build_library_page(self):
        page, layout = self.make_page()
        self.page_heading(layout, "Game Library", "Detected games from the folders you selected.")
        row = QHBoxLayout()
        self.library_search = QLineEdit()
        self.library_search.setPlaceholderText("Filter by game title or system…")
        self.library_search.textChanged.connect(self.populate_library)
        scan = QPushButton("Scan folders")
        scan.setObjectName("PrimaryButton")
        scan.clicked.connect(self.refresh_library)
        launch = QPushButton("Launch selected game")
        launch.setObjectName("SecondaryButton")
        launch.clicked.connect(self.launch_selected_game)
        row.addWidget(self.library_search, 1)
        row.addWidget(scan)
        row.addWidget(launch)
        layout.addLayout(row)
        self.library_list = QListWidget()
        self.library_list.setSpacing(2)
        self.library_list.itemDoubleClicked.connect(lambda item: self.launch_selected_game())
        layout.addWidget(self.library_list, 1)
        self.library_status = QLabel("No scan performed yet.")
        self.library_status.setObjectName("Muted")
        layout.addWidget(self.library_status)
        return page

    def build_systems_page(self):
        page, layout = self.make_page()
        self.page_heading(layout, "Systems", "Systems are detected from the file formats in your ROM folders.")
        self.system_list = QListWidget()
        layout.addWidget(self.system_list, 1)
        return page

    def build_search_page(self):
        page, layout = self.make_page()
        self.page_heading(layout, "Search", "Search your detected game collection.")
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search game titles or systems…")
        self.search_field.textChanged.connect(self.populate_search)
        self.search_results = QListWidget()
        layout.addWidget(self.search_field)
        layout.addWidget(self.search_results, 1)
        return page

    def build_settings_page(self):
        page, layout = self.make_page()
        self.page_heading(layout, "Settings", "Configure where RetroDeck looks for your game files.")
        folder_label = QLabel("ROM folders")
        folder_label.setObjectName("SectionTitle")
        layout.addWidget(folder_label)
        self.folder_list = QListWidget()
        layout.addWidget(self.folder_list, 1)
        buttons = QHBoxLayout()
        add = QPushButton("Add folder")
        add.setObjectName("PrimaryButton")
        add.clicked.connect(self.add_rom_folder)
        remove = QPushButton("Remove selected")
        remove.setObjectName("SecondaryButton")
        remove.clicked.connect(self.remove_rom_folder)
        buttons.addWidget(add)
        buttons.addWidget(remove)
        buttons.addStretch()
        layout.addLayout(buttons)
        theme_label = QLabel("Appearance")
        theme_label.setObjectName("SectionTitle")
        layout.addWidget(theme_label)
        self.theme_button = QPushButton("Switch to light theme")
        self.theme_button.setObjectName("SecondaryButton")
        self.theme_button.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_button, 0, Qt.AlignmentFlag.AlignLeft)
        note = QLabel("Supported file types are listed in the project README. Folder settings are saved locally on this Pi.")
        note.setObjectName("Muted")
        note.setWordWrap(True)
        layout.addWidget(note)
        self.populate_folder_list()
        return page

    def build_emulators_page(self):
        page, layout = self.make_page()
        self.page_heading(
            layout, "Emulator Setup",
            "Install supported standalone emulators from your operating system's trusted package repositories.",
        )
        self.emulator_status_list = QListWidget()
        layout.addWidget(self.emulator_status_list, 1)

        self.emulator_setup_status = QLabel(
            "RetroDeck checks for installed emulators and supported packages."
        )
        self.emulator_setup_status.setObjectName("Muted")
        self.emulator_setup_status.setWordWrap(True)
        layout.addWidget(self.emulator_setup_status)

        buttons = QHBoxLayout()
        refresh = QPushButton("Refresh status")
        refresh.setObjectName("SecondaryButton")
        refresh.clicked.connect(self.refresh_emulator_status)
        install = QPushButton("Install supported emulators")
        install.setObjectName("PrimaryButton")
        install.clicked.connect(self.install_supported_emulators)
        buttons.addWidget(refresh)
        buttons.addWidget(install)
        buttons.addStretch()
        layout.addLayout(buttons)
        self.refresh_emulator_status()
        return page

    def refresh_emulator_status(self):
        if not hasattr(self, "emulator_status_list"):
            return
        self.emulator_status_list.clear()
        installed_count = 0
        for emulator_id, profile in EMULATOR_CATALOG.items():
            status = emulator_status(emulator_id)
            if status["available"]:
                installed_count += 1
                detail = f"Installed: {status['path']}"
            else:
                detail = "Not detected on this computer"
            self.emulator_status_list.addItem(
                f"{profile['name']}  |  {', '.join(profile['systems'])}\n{detail}"
            )

        plan = supported_package_plan()
        package_count = len({p for packages in plan.values() for p in packages})
        if plan:
            self.emulator_setup_status.setText(
                f"{installed_count} emulator(s) detected. "
                f"{package_count} supported package(s) can be installed from your system repositories. "
                "Nintendo 64 still needs a validated native ARM64 Mupen64Plus build."
            )
        else:
            self.emulator_setup_status.setText(
                f"{installed_count} emulator(s) detected. Automatic package installation "
                "is currently supported only on Debian-family Linux ARM64 systems."
            )

    def install_supported_emulators(self):
        plan = supported_package_plan()
        packages = sorted({package for group in plan.values() for package in group})
        if not packages:
            QMessageBox.information(
                self, "Not supported on this system",
                "The automatic installer currently supports Raspberry Pi OS / Debian-family Linux ARM64 only.",
            )
            return

        package_text = ", ".join(packages)
        answer = QMessageBox.question(
            self,
            "Install emulators?",
            "RetroDeck will ask your operating system to install these packages:\n\n"
            f"{package_text}\n\n"
            "This changes installed software on this computer. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        self.emulator_install_process = QProcess(self)
        self.emulator_install_process.readyReadStandardOutput.connect(
            self.on_emulator_install_output
        )
        self.emulator_install_process.readyReadStandardError.connect(
            self.on_emulator_install_output
        )
        self.emulator_install_process.finished.connect(self.on_emulator_install_finished)
        self.emulator_install_process.errorOccurred.connect(self.on_emulator_install_error)
        self.emulator_install_log = ""
        self.emulator_install_phase = "update"
        self.emulator_setup_status.setText(
            "Refreshing package lists… This can take a few minutes. "
            "Keep RetroDeck open while it runs."
        )
        self.emulator_install_process.start("pkexec", ["apt-get", "update"])

    def on_emulator_install_output(self):
        process = self.emulator_install_process
        chunks = []
        if process.bytesAvailable():
            chunks.append(bytes(process.readAll()).decode("utf-8", errors="replace"))
        if not chunks:
            return
        output = "".join(chunks)
        self.emulator_install_log = (self.emulator_install_log + output)[-5000:]
        lines = [line.strip() for line in self.emulator_install_log.splitlines() if line.strip()]
        latest = lines[-1] if lines else "Working…"
        phase = "Refreshing package lists" if self.emulator_install_phase == "update" else "Installing emulators"
        self.emulator_setup_status.setText(f"{phase}: {latest[-180:]}")

    def on_emulator_install_finished(self, exit_code, exit_status):
        self.on_emulator_install_output()
        if exit_code != 0:
            details = self.emulator_install_log.strip().splitlines()
            detail = details[-1][-240:] if details else "No output was returned."
            self.emulator_setup_status.setText(
                f"Package operation failed (exit code {exit_code}). {detail}"
            )
            QMessageBox.warning(
                self, "Emulator installation failed",
                "The package manager returned an error. The last reported message was:\n\n"
                f"{detail}\n\n"
                "You can retry after resolving the package-manager issue."
            )
            return

        if self.emulator_install_phase == "update":
            plan = supported_package_plan()
            packages = sorted({package for group in plan.values() for package in group})
            self.emulator_install_phase = "install"
            self.emulator_install_log = ""
            self.emulator_setup_status.setText(
                "Package lists refreshed. Installing Dolphin, mGBA, and Nestopia…"
            )
            self.emulator_install_process.start(
                *package_install_command(packages)
            )
            return

        self.emulator_setup_status.setText(
            "Installation command completed. Checking which emulators are available…"
        )
        self.refresh_emulator_status()

    def on_emulator_install_error(self, process_error):
        detail = self.emulator_install_process.errorString()
        self.emulator_setup_status.setText(f"Could not run the package manager: {detail}")
        QMessageBox.warning(
            self, "Could not start installer",
            "RetroDeck could not start the system package manager.\n\n"
            f"{detail}\n\n"
            "Check that pkexec is installed and that your desktop session supports "
            "the system authorization prompt."
        )

    def show_page(self, name):
        self.pages.setCurrentIndex(self.PAGES.index(name))
        self.breadcrumb.setText(name.upper())
        for page_name, button in self.nav_buttons.items():
            button.setChecked(page_name == name)

    def install_shortcuts(self):
        for sequence, page in {
            "Ctrl+1": "Home", "Ctrl+2": "Library", "Ctrl+3": "Systems",
            "Ctrl+4": "Search", "Ctrl+5": "Settings",
        }.items():
            shortcut = QShortcut(QKeySequence(sequence), self)
            shortcut.activated.connect(lambda target=page: self.show_page(target))
        refresh = QShortcut(QKeySequence("F5"), self)
        refresh.activated.connect(self.refresh_library)

    def persist_settings(self):
        save_settings(self.settings)

    def populate_folder_list(self):
        if not hasattr(self, "folder_list"):
            return
        self.folder_list.clear()
        for folder in self.settings["rom_directories"]:
            self.folder_list.addItem(QListWidgetItem(folder))

    def add_rom_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose a game folder", str(__import__("pathlib").Path.home()))
        if not folder:
            return
        folder = str(__import__("pathlib").Path(folder).expanduser().resolve())
        if folder not in self.settings["rom_directories"]:
            self.settings["rom_directories"].append(folder)
            self.settings["rom_directories_configured"] = True
            self.persist_settings()
            self.populate_folder_list()
            self.refresh_library()

    def remove_rom_folder(self):
        item = self.folder_list.currentItem()
        if item is None:
            QMessageBox.information(self, "Select a folder", "Choose a folder to remove first.")
            return
        folder = item.text()
        self.settings["rom_directories"] = [entry for entry in self.settings["rom_directories"] if entry != folder]
        self.settings["rom_directories_configured"] = True
        self.persist_settings()
        self.populate_folder_list()
        self.refresh_library()

    def refresh_library(self, show_status=True):
        self.games, warnings = scan_rom_directories(self.settings["rom_directories"])
        self.populate_library()
        self.populate_search()
        self.populate_systems()
        if hasattr(self, "home_count"):
            self.home_count.setText(f"{len(self.games)} games detected across {len(self.settings['rom_directories'])} configured folders.")
        if hasattr(self, "library_status"):
            message = f"{len(self.games)} games found."
            if warnings:
                message += f"  {len(warnings)} folder warning(s)."
            self.library_status.setText(message)
        if show_status and warnings:
            QMessageBox.warning(self, "Some folders could not be scanned", "\n".join(warnings[:8]))

    def game_display_text(self, game):
        return f"{game.title}\n{game.system}  •  {game.path}"

    def populate_library(self):
        if not hasattr(self, "library_list"):
            return
        query = self.library_search.text().casefold().strip()
        self.library_list.clear()
        for game in self.games:
            searchable = f"{game.title} {game.system} {game.path}".casefold()
            if query and query not in searchable:
                continue
            item = QListWidgetItem(self.game_display_text(game))
            item.setData(Qt.ItemDataRole.UserRole, str(game.path))
            self.library_list.addItem(item)
        if self.library_list.count() == 0:
            self.library_list.addItem(QListWidgetItem("No games found. Add a ROM folder in Settings, then scan again."))

    def launch_selected_game(self):
        item = self.library_list.currentItem()
        if item is None:
            QMessageBox.information(self, "Choose a game", "Select a game in your library first.")
            return
        game_path = item.data(Qt.ItemDataRole.UserRole)
        game = next((entry for entry in self.games if str(entry.path) == game_path), None)
        if game is None:
            QMessageBox.warning(self, "Game unavailable", "Rescan your library and select the game again.")
            return
        try:
            process = launch_game(game, self.settings)
            self.library_status.setText(f"Started {game.title} in its configured emulator.")
            self.last_emulator_process = process
        except EmulatorLaunchError as exc:
            QMessageBox.warning(self, "Could not launch game", str(exc))

    def populate_search(self):
        if not hasattr(self, "search_results"):
            return
        query = self.search_field.text().casefold().strip()
        self.search_results.clear()
        for game in self.games:
            if query in f"{game.title} {game.system} {game.path}".casefold():
                self.search_results.addItem(QListWidgetItem(self.game_display_text(game)))
        if not self.games:
            self.search_results.addItem(QListWidgetItem("Your library is empty. Add folders in Settings."))

    def populate_systems(self):
        if not hasattr(self, "system_list"):
            return
        counts = {}
        for game in self.games:
            counts[game.system] = counts.get(game.system, 0) + 1
        self.system_list.clear()
        if not counts:
            self.system_list.addItem("No systems detected yet. Add a game folder in Settings.")
            return
        for system, count in sorted(counts.items()):
            self.system_list.addItem(f"{system}  •  {count} game(s)")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.settings["theme"] = "dark" if self.dark_mode else "light"
        self.persist_settings()
        self.apply_theme()

    def apply_theme(self):
        QApplication.instance().setStyleSheet(DARK_THEME if self.dark_mode else LIGHT_THEME)
        if hasattr(self, "theme_button"):
            self.theme_button.setText("Switch to light theme" if self.dark_mode else "Switch to dark theme")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("RetroDeck")
    window = RetroDeckWindow()
    window.showMaximized()
    sys.exit(app.exec())
