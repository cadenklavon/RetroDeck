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
QMainWindow, QWidget#Root, QWidget#Page { background: #11151d; color: #f5f6f8; }
QWidget#TopBar { background: #1b222d; border: 1px solid #303a49; border-radius: 18px; }
QFrame#NavDivider { background: #3b4656; }
QLabel#Brand { color: #f8f9fb; font-size: 19px; font-weight: 900; letter-spacing: 1px; }
QLabel#Eyebrow { color: #8bc9e8; font-size: 11px; font-weight: 800; letter-spacing: 1.4px; }
QLabel#PageTitle { color: #f8f9fb; font-size: 28px; font-weight: 800; }
QLabel#FeatureTitle { color: #ffffff; font-size: 25px; font-weight: 850; }
QLabel#Muted { color: #aab5c4; font-size: 12px; }
QLabel#SectionTitle { color: #f4f6fa; font-size: 18px; font-weight: 750; }
QPushButton#NavButton { color: #c0c9d5; background: transparent; border: 1px solid transparent; border-radius: 12px; padding: 10px 13px; font-weight: 650; }
QPushButton#NavButton:hover { background: #2a3544; color: white; }
QPushButton#NavButton:checked { color: white; background: #35475c; border: 1px solid #536d89; }
QPushButton#PrimaryButton { color: #101820; background: #a7d9ee; border: 0; border-radius: 13px; padding: 12px 18px; font-weight: 800; }
QPushButton#PrimaryButton:hover { background: #c3e8f6; }
QPushButton#SecondaryButton, QPushButton#ActionTile { color: #f0f3f7; background: #252f3d; border: 1px solid #3c4a5d; border-radius: 14px; padding: 12px 16px; font-weight: 700; }
QPushButton#SecondaryButton:hover, QPushButton#ActionTile:hover { background: #344256; }
QLineEdit { color: #f5f7fa; background: #202a37; border: 1px solid #3b485a; border-radius: 12px; padding: 12px; }
QListWidget { color: #f2f4f7; background: #1a222d; border: 1px solid #303c4d; border-radius: 16px; padding: 8px; }
QListWidget::item { padding: 12px 10px; border-bottom: 1px solid #303c4d; }
QListWidget::item:selected { background: #35475c; border-radius: 8px; }
QListWidget#GameTiles { background: transparent; border: 0; padding: 2px; }
QListWidget#GameTiles::item { background: #273342; border: 1px solid #3a4a5d; border-radius: 14px; padding: 8px; margin: 4px; text-align: center; }
QListWidget#GameTiles::item:hover { background: #35475c; border: 2px solid #a7d9ee; }
QFrame#Panel, QFrame#FeaturePanel { background: #202a37; border: 1px solid #344255; border-radius: 18px; }
QFrame#FeaturePanel { background: #26394c; }
QPushButton:focus, QLineEdit:focus, QListWidget:focus { border: 2px solid #a7d9ee; }
"""

LIGHT_THEME = """
* { font-family: "Inter", "DejaVu Sans", sans-serif; }
QMainWindow, QWidget#Root, QWidget#Page { background: #edf1f5; color: #17212d; }
QWidget#TopBar { background: #ffffff; border: 1px solid #d6dee8; border-radius: 18px; }
QFrame#NavDivider { background: #d5dde7; }
QLabel#Brand { color: #17212d; font-size: 19px; font-weight: 900; letter-spacing: 1px; }
QLabel#Eyebrow { color: #287c9e; font-size: 11px; font-weight: 800; letter-spacing: 1.4px; }
QLabel#PageTitle { color: #17212d; font-size: 28px; font-weight: 800; }
QLabel#FeatureTitle { color: #ffffff; font-size: 25px; font-weight: 850; }
QLabel#Muted { color: #637286; font-size: 12px; }
QLabel#SectionTitle { color: #17212d; font-size: 18px; font-weight: 750; }
QPushButton#NavButton { color: #526174; background: transparent; border: 1px solid transparent; border-radius: 12px; padding: 10px 13px; font-weight: 650; }
QPushButton#NavButton:hover { background: #edf2f7; color: #17212d; }
QPushButton#NavButton:checked { color: #155c78; background: #e0f0f6; border: 1px solid #b8dce9; }
QPushButton#PrimaryButton { color: white; background: #287c9e; border: 0; border-radius: 13px; padding: 12px 18px; font-weight: 800; }
QPushButton#SecondaryButton, QPushButton#ActionTile { color: #233247; background: white; border: 1px solid #ccd6e2; border-radius: 14px; padding: 12px 16px; font-weight: 700; }
QLineEdit { color: #17212d; background: white; border: 1px solid #ccd6e2; border-radius: 12px; padding: 12px; }
QListWidget { color: #17212d; background: white; border: 1px solid #d6dee8; border-radius: 16px; padding: 8px; }
QListWidget::item { padding: 12px 10px; border-bottom: 1px solid #e1e7ee; }
QListWidget::item:selected { background: #e0f0f6; border-radius: 8px; }
QListWidget#GameTiles { background: transparent; border: 0; padding: 2px; }
QListWidget#GameTiles::item { background: white; border: 1px solid #d2dce7; border-radius: 14px; padding: 8px; margin: 4px; }
QListWidget#GameTiles::item:hover { background: #e8f4f8; border: 2px solid #287c9e; }
QFrame#Panel, QFrame#FeaturePanel { background: #ffffff; border: 1px solid #d6dee8; border-radius: 18px; }
QFrame#FeaturePanel { background: #31556b; }
QPushButton:focus, QLineEdit:focus, QListWidget:focus { border: 2px solid #287c9e; }
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
        shell = QVBoxLayout(root)
        shell.setContentsMargins(18, 14, 18, 14)
        shell.setSpacing(14)
        shell.addWidget(self.build_sidebar())

        content = QVBoxLayout()
        content.setContentsMargins(4, 0, 4, 0)
        content.setSpacing(10)
        self.breadcrumb = QLabel("HOME  /  YOUR COLLECTION")
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
        """Console-inspired horizontal navigation."""
        bar = QWidget()
        bar.setObjectName("TopBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(18, 10, 18, 10)
        layout.setSpacing(8)
        brand = QLabel("◈  RETRODECK")
        brand.setObjectName("Brand")
        layout.addWidget(brand)
        divider = QFrame()
        divider.setObjectName("NavDivider")
        divider.setFixedSize(1, 30)
        layout.addWidget(divider)
        for icon, name in [("⌂", "Home"), ("▦", "Library"), ("◈", "Systems"), ("⌕", "Search"), ("⬇", "Emulators")]:
            button = QPushButton(f"{icon}  {name}")
            button.setObjectName("NavButton")
            button.setCheckable(True)
            button.setMinimumHeight(42)
            button.clicked.connect(lambda checked=False, page=name: self.show_page(page))
            self.nav_buttons[name] = button
            layout.addWidget(button)
        layout.addStretch(1)
        settings_button = QPushButton("⚙  Settings")
        settings_button.setObjectName("NavButton")
        settings_button.setCheckable(True)
        settings_button.setMinimumHeight(42)
        settings_button.clicked.connect(lambda: self.show_page("Settings"))
        self.nav_buttons["Settings"] = settings_button
        layout.addWidget(settings_button)
        return bar

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
        self.page_heading(layout, "Good to see you", "Pick up where you left off, or explore your collection.")
        featured = QFrame()
        featured.setObjectName("FeaturePanel")
        featured_layout = QVBoxLayout(featured)
        featured_layout.setContentsMargins(24, 20, 24, 20)
        eyebrow = QLabel("YOUR GAME SPACE")
        eyebrow.setObjectName("Eyebrow")
        title = QLabel("All your games. One place.")
        title.setObjectName("FeatureTitle")
        subtitle = QLabel("Your library is ready whenever you are.")
        subtitle.setObjectName("Muted")
        featured_layout.addWidget(eyebrow)
        featured_layout.addWidget(title)
        featured_layout.addWidget(subtitle)
        layout.addWidget(featured)
        section_row = QHBoxLayout()
        section = QLabel("Recently added")
        section.setObjectName("SectionTitle")
        self.home_count = QLabel("Scanning your folders…")
        self.home_count.setObjectName("Muted")
        section_row.addWidget(section)
        section_row.addStretch()
        section_row.addWidget(self.home_count)
        layout.addLayout(section_row)
        self.home_games = QListWidget()
        self.home_games.setObjectName("GameTiles")
        self.home_games.setViewMode(QListWidget.ViewMode.IconMode)
        self.home_games.setFlow(QListWidget.Flow.LeftToRight)
        self.home_games.setWrapping(False)
        self.home_games.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.home_games.setMovement(QListWidget.Movement.Static)
        self.home_games.setIconSize(__import__("PySide6.QtCore", fromlist=["QSize"]).QSize(112, 112))
        self.home_games.setGridSize(__import__("PySide6.QtCore", fromlist=["QSize"]).QSize(150, 170))
        self.home_games.setFixedHeight(205)
        self.home_games.itemDoubleClicked.connect(self.open_game_from_home)
        layout.addWidget(self.home_games)
        actions = QHBoxLayout()
        for label, page_name in [("Open game library", "Library"), ("Browse systems", "Systems"), ("Manage emulators", "Emulators")]:
            button = QPushButton(label)
            button.setObjectName("ActionTile")
            button.setMinimumHeight(66)
            button.clicked.connect(lambda checked=False, target=page_name: self.show_page(target))
            actions.addWidget(button)
        layout.addLayout(actions)
        scan = QPushButton("↻  Scan game folders")
        scan.setObjectName("PrimaryButton")
        scan.clicked.connect(self.refresh_library)
        layout.addWidget(scan, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addStretch()
        return page

    def open_game_from_home(self, item):
        game_path = item.data(Qt.ItemDataRole.UserRole)
        for index in range(self.library_list.count()):
            candidate = self.library_list.item(index)
            if candidate.data(Qt.ItemDataRole.UserRole) == game_path:
                self.library_list.setCurrentItem(candidate)
                self.show_page("Library")
                self.launch_selected_game()
                return
        self.show_page("Library")

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
        stdout = bytes(process.readAllStandardOutput()).decode("utf-8", errors="replace")
        stderr = bytes(process.readAllStandardError()).decode("utf-8", errors="replace")
        output = stdout + stderr
        if not output:
            return
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
        self.populate_home_games()
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

    def populate_home_games(self):
        if not hasattr(self, "home_games"):
            return
        self.home_games.clear()
        for game in self.games[:30]:
            item = QListWidgetItem(f"{game.title}\n{game.system}")
            item.setData(Qt.ItemDataRole.UserRole, str(game.path))
            self.home_games.addItem(item)
        if not self.games:
            self.home_games.addItem("Your library is empty\nAdd ROM folders in Settings")

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
