"""RetroDeck desktop launcher prototype.

Stage 1 focuses on the visual interface and navigation. Game entries are
sample data: ROM scanning, artwork loading, emulator launching, persistence,
and controller input are future stages.
"""
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


DARK_THEME = """
* { font-family: "Inter", "Segoe UI", sans-serif; }
QMainWindow, QWidget#Root, QWidget#Page, QScrollArea, QWidget#ScrollContent {
    background: #0b1020; color: #eef2ff;
}
QWidget#Sidebar { background: #10182b; border: 1px solid #202c46; border-radius: 18px; }
QLabel#Brand { color: #f5f7ff; font-size: 21px; font-weight: 900; letter-spacing: 2px; }
QLabel#BrandMark { color: #65d6ff; font-size: 25px; font-weight: 900; }
QLabel#Eyebrow { color: #72d9ff; font-size: 11px; font-weight: 800; letter-spacing: 2px; }
QLabel#PageTitle { color: #f4f6ff; font-size: 29px; font-weight: 800; }
QLabel#Muted { color: #8f9bb6; font-size: 13px; }
QLabel#SectionTitle { color: #f0f3ff; font-size: 18px; font-weight: 750; }
QPushButton#NavButton {
    color: #9eabc6; background: transparent; border: 1px solid transparent;
    border-radius: 10px; padding: 12px 14px; text-align: left; font-size: 14px;
}
QPushButton#NavButton:hover { background: #1b2943; color: #ffffff; }
QPushButton#NavButton:checked {
    color: #ffffff; background: #203754; border: 1px solid #31577b;
}
QPushButton#PrimaryButton {
    color: #071321; background: #72d9ff; border: 0; border-radius: 10px;
    padding: 12px 18px; font-weight: 800;
}
QPushButton#PrimaryButton:hover { background: #a0e7ff; }
QPushButton#SecondaryButton {
    color: #eaf2ff; background: #1b2943; border: 1px solid #344664;
    border-radius: 10px; padding: 11px 16px; font-weight: 650;
}
QPushButton#SecondaryButton:hover { background: #293b5b; }
QPushButton#GameTile {
    color: #f6f8ff; background: #151f35; border: 1px solid #293957;
    border-radius: 14px; text-align: left; padding: 0;
}
QPushButton#GameTile:hover { border: 2px solid #72d9ff; background: #1b2a46; }
QPushButton#GameTile:focus { border: 2px solid #a0e7ff; }
QLineEdit {
    color: #f5f7ff; background: #121c31; border: 1px solid #2b3b59;
    border-radius: 10px; padding: 13px 15px; selection-background-color: #31577b;
}
QFrame#HeroPanel {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #1a3552, stop:0.55 #17314b, stop:1 #29244c);
    border: 1px solid #345574; border-radius: 20px;
}
QFrame#InfoPanel, QFrame#SystemPanel {
    background: #121c31; border: 1px solid #263653; border-radius: 14px;
}
QScrollBar:vertical { background: #0b1020; width: 9px; margin: 0; }
QScrollBar::handle:vertical { background: #344664; border-radius: 4px; min-height: 25px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QPushButton:focus { outline: none; border: 2px solid #72d9ff; }
"""

LIGHT_THEME = """
* { font-family: "Inter", "Segoe UI", sans-serif; }
QMainWindow, QWidget#Root, QWidget#Page, QScrollArea, QWidget#ScrollContent {
    background: #edf2f9; color: #18243a;
}
QWidget#Sidebar { background: #ffffff; border: 1px solid #d8e0ec; border-radius: 18px; }
QLabel#Brand { color: #17243a; font-size: 21px; font-weight: 900; letter-spacing: 2px; }
QLabel#BrandMark { color: #087da9; font-size: 25px; font-weight: 900; }
QLabel#Eyebrow { color: #087da9; font-size: 11px; font-weight: 800; letter-spacing: 2px; }
QLabel#PageTitle { color: #17243a; font-size: 29px; font-weight: 800; }
QLabel#Muted { color: #687791; font-size: 13px; }
QLabel#SectionTitle { color: #17243a; font-size: 18px; font-weight: 750; }
QPushButton#NavButton {
    color: #64728a; background: transparent; border: 1px solid transparent;
    border-radius: 10px; padding: 12px 14px; text-align: left; font-size: 14px;
}
QPushButton#NavButton:hover { background: #edf3fb; color: #17243a; }
QPushButton#NavButton:checked { color: #075d7e; background: #e1f3fb; border: 1px solid #b9e2f1; }
QPushButton#PrimaryButton {
    color: #ffffff; background: #087da9; border: 0; border-radius: 10px;
    padding: 12px 18px; font-weight: 800;
}
QPushButton#PrimaryButton:hover { background: #09658a; }
QPushButton#SecondaryButton {
    color: #1a2a42; background: #ffffff; border: 1px solid #cbd6e5;
    border-radius: 10px; padding: 11px 16px; font-weight: 650;
}
QPushButton#SecondaryButton:hover { background: #e9f1fa; }
QPushButton#GameTile {
    color: #18243a; background: #ffffff; border: 1px solid #d5deeb;
    border-radius: 14px; text-align: left; padding: 0;
}
QPushButton#GameTile:hover, QPushButton#GameTile:focus { border: 2px solid #087da9; }
QLineEdit { color: #18243a; background: #ffffff; border: 1px solid #cbd6e5; border-radius: 10px; padding: 13px 15px; }
QFrame#HeroPanel {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #d3edf8, stop:0.55 #d9e9f7, stop:1 #e9e1fa);
    border: 1px solid #c0d9eb; border-radius: 20px;
}
QFrame#InfoPanel, QFrame#SystemPanel { background: #ffffff; border: 1px solid #d8e0ec; border-radius: 14px; }
QScrollBar:vertical { background: #edf2f9; width: 9px; margin: 0; }
QScrollBar::handle:vertical { background: #b7c6d9; border-radius: 4px; min-height: 25px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""


GAMES = [
    {"title": "Ocarina of Time", "system": "Nintendo 64", "tag": "ADVENTURE", "symbol": "N64", "color": "#315c83"},
    {"title": "The Wind Waker", "system": "GameCube", "tag": "ADVENTURE", "symbol": "GC", "color": "#287b86"},
    {"title": "Super Mario 64", "system": "Nintendo 64", "tag": "PLATFORMER", "symbol": "N64", "color": "#8b563b"},
    {"title": "Metroid Prime", "system": "GameCube", "tag": "ACTION", "symbol": "GC", "color": "#455b83"},
]


class GameTile(QPushButton):
    """Focusable game tile with original text-based placeholder artwork."""

    def __init__(self, game):
        super().__init__()
        self.setObjectName("GameTile")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumSize(190, 190)
        self.setMaximumHeight(210)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.game = game

        layout = QVBoxLayout(self)
        layout.setContentsMargins(13, 13, 13, 13)
        layout.setSpacing(7)

        art = QLabel(game["symbol"])
        art.setAlignment(Qt.AlignmentFlag.AlignCenter)
        art.setMinimumHeight(105)
        art.setStyleSheet(
            "background: " + game["color"] + "; color: white; border-radius: 10px;"
            "font-size: 27px; font-weight: 900; letter-spacing: 2px;"
        )
        title = QLabel(game["title"])
        title.setWordWrap(True)
        title.setStyleSheet("font-size: 14px; font-weight: 800;")
        system = QLabel(game["system"])
        system.setObjectName("Muted")
        layout.addWidget(art)
        layout.addWidget(title)
        layout.addWidget(system)


class RetroDeckWindow(QMainWindow):
    PAGES = ["Home", "Library", "Systems", "Search", "Settings"]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RetroDeck")
        self.resize(1360, 820)
        self.dark_mode = True
        self.nav_buttons = {}

        root = QWidget()
        root.setObjectName("Root")
        shell = QHBoxLayout(root)
        shell.setContentsMargins(18, 18, 18, 18)
        shell.setSpacing(18)

        self.sidebar = self.build_sidebar()
        shell.addWidget(self.sidebar, 0)

        content = QVBoxLayout()
        content.setSpacing(14)
        self.topbar = self.build_topbar()
        content.addWidget(self.topbar)
        self.pages = QStackedWidget()
        self.pages.addWidget(self.build_home_page())
        self.pages.addWidget(self.build_library_page())
        self.pages.addWidget(self.build_systems_page())
        self.pages.addWidget(self.build_search_page())
        self.pages.addWidget(self.build_settings_page())
        content.addWidget(self.pages, 1)
        shell.addLayout(content, 1)

        self.setCentralWidget(root)
        self.apply_theme()
        self.show_page("Home")
        self.install_shortcuts()

    def build_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(205)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(15, 20, 15, 16)
        layout.setSpacing(9)

        brand_row = QHBoxLayout()
        mark = QLabel("R")
        mark.setObjectName("BrandMark")
        brand = QLabel("RETRODECK")
        brand.setObjectName("Brand")
        brand_row.addWidget(mark)
        brand_row.addWidget(brand)
        brand_row.addStretch()
        layout.addLayout(brand_row)

        caption = QLabel("YOUR GAME SPACE")
        caption.setObjectName("Eyebrow")
        caption.setContentsMargins(7, 20, 0, 8)
        layout.addWidget(caption)

        labels = [("⌂", "Home"), ("▦", "Library"), ("◈", "Systems"), ("⌕", "Search")]
        for icon, name in labels:
            button = QPushButton(f"{icon}     {name}")
            button.setObjectName("NavButton")
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, page=name: self.show_page(page))
            self.nav_buttons[name] = button
            layout.addWidget(button)

        layout.addStretch()
        settings = QPushButton("⚙     Settings")
        settings.setObjectName("NavButton")
        settings.setCheckable(True)
        settings.clicked.connect(lambda: self.show_page("Settings"))
        self.nav_buttons["Settings"] = settings
        layout.addWidget(settings)

        footer = QLabel("RETRODECK  •  PREVIEW")
        footer.setObjectName("Muted")
        footer.setContentsMargins(7, 12, 0, 0)
        layout.addWidget(footer)
        return sidebar

    def build_topbar(self):
        bar = QWidget()
        row = QHBoxLayout(bar)
        row.setContentsMargins(2, 0, 2, 0)
        self.breadcrumb = QLabel("HOME")
        self.breadcrumb.setObjectName("Eyebrow")
        status = QLabel("LOCAL LIBRARY  •  PREVIEW DATA")
        status.setObjectName("Muted")
        row.addWidget(self.breadcrumb)
        row.addStretch()
        row.addWidget(status)
        return bar

    def make_page(self):
        page = QWidget()
        page.setObjectName("Page")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(8, 6, 8, 8)
        layout.setSpacing(17)
        return page, layout

    def build_home_page(self):
        page, layout = self.make_page()

        hero = QFrame()
        hero.setObjectName("HeroPanel")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(28, 25, 28, 25)
        hero_layout.setSpacing(20)

        copy = QVBoxLayout()
        eyebrow = QLabel("YOUR NEXT ADVENTURE STARTS HERE")
        eyebrow.setObjectName("Eyebrow")
        headline = QLabel("Press start.\nPlay something great.")
        headline.setStyleSheet("font-size: 31px; font-weight: 900;")
        description = QLabel("One home for the games you love, across every system.")
        description.setWordWrap(True)
        description.setStyleSheet("font-size: 14px;")
        launch_note = QLabel("FEATURED GAME  •  SAMPLE LIBRARY ENTRY")
        launch_note.setObjectName("Muted")
        browse = QPushButton("Explore your library   →")
        browse.setObjectName("PrimaryButton")
        browse.clicked.connect(lambda: self.show_page("Library"))
        copy.addWidget(eyebrow)
        copy.addSpacing(5)
        copy.addWidget(headline)
        copy.addWidget(description)
        copy.addSpacing(8)
        copy.addWidget(launch_note)
        copy.addWidget(browse, 0, Qt.AlignmentFlag.AlignLeft)
        copy.addStretch()

        feature = QFrame()
        feature.setMinimumWidth(220)
        feature.setStyleSheet(
            "background: rgba(5, 14, 30, 0.22); border: 1px solid rgba(255,255,255,0.16);"
            "border-radius: 15px;"
        )
        feature_layout = QVBoxLayout(feature)
        feature_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        feature_icon = QLabel("RD")
        feature_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        feature_icon.setStyleSheet("font-size: 58px; font-weight: 900; color: rgba(255,255,255,0.88);")
        feature_text = QLabel("RETRO\nREIMAGINED")
        feature_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        feature_text.setStyleSheet("font-size: 13px; font-weight: 900; letter-spacing: 3px;")
        feature_layout.addWidget(feature_icon)
        feature_layout.addWidget(feature_text)
        hero_layout.addLayout(copy, 3)
        hero_layout.addWidget(feature, 2)
        layout.addWidget(hero)

        stats = QHBoxLayout()
        for value, label in [("04", "SAMPLE GAMES"), ("02", "SYSTEMS"), ("01", "PLATFORM")]:
            panel = QFrame()
            panel.setObjectName("InfoPanel")
            panel_layout = QVBoxLayout(panel)
            panel_layout.setContentsMargins(16, 12, 16, 12)
            number = QLabel(value)
            number.setStyleSheet("font-size: 21px; font-weight: 900;")
            caption = QLabel(label)
            caption.setObjectName("Muted")
            panel_layout.addWidget(number)
            panel_layout.addWidget(caption)
            stats.addWidget(panel)
        layout.addLayout(stats)

        section_row = QHBoxLayout()
        section = QLabel("Pick up where you left off")
        section.setObjectName("SectionTitle")
        sample = QLabel("SAMPLE TITLES")
        sample.setObjectName("Eyebrow")
        section_row.addWidget(section)
        section_row.addStretch()
        section_row.addWidget(sample)
        layout.addLayout(section_row)

        grid = QGridLayout()
        grid.setSpacing(12)
        for index, game in enumerate(GAMES):
            grid.addWidget(GameTile(game), index // 2, index % 2)
        layout.addLayout(grid)
        layout.addStretch()
        return page

    def build_library_page(self):
        page, layout = self.make_page()
        title = QLabel("Your Library")
        title.setObjectName("PageTitle")
        subtitle = QLabel("All your games, organized in one place.")
        subtitle.setObjectName("Muted")
        search = QLineEdit()
        search.setPlaceholderText("Search your library (sample entries)...")
        grid = QGridLayout()
        for index, game in enumerate(GAMES):
            grid.addWidget(GameTile(game), index // 3, index % 3)
        search.textChanged.connect(lambda text: self.filter_tiles(grid, text))
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(search)
        layout.addLayout(grid)
        layout.addStretch()
        return page

    def filter_tiles(self, grid, query):
        query = query.casefold().strip()
        for index in range(grid.count()):
            widget = grid.itemAt(index).widget()
            if widget is not None:
                game = widget.game
                widget.setVisible(query in game["title"].casefold() or query in game["system"].casefold())

    def build_systems_page(self):
        page, layout = self.make_page()
        title = QLabel("Systems")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Browse your collection by the hardware that runs it.")
        subtitle.setObjectName("Muted")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        for name, description, count in [
            ("Nintendo 64", "Cartridges, 3D worlds, and classic adventures.", "02 SAMPLE GAMES"),
            ("Nintendo GameCube", "A library of disc-based console classics.", "02 SAMPLE GAMES"),
        ]:
            panel = QFrame()
            panel.setObjectName("SystemPanel")
            row = QHBoxLayout(panel)
            details = QVBoxLayout()
            label = QLabel(name)
            label.setStyleSheet("font-size: 18px; font-weight: 800;")
            desc = QLabel(description)
            desc.setObjectName("Muted")
            details.addWidget(label)
            details.addWidget(desc)
            count_label = QLabel(count)
            count_label.setObjectName("Eyebrow")
            row.addLayout(details, 1)
            row.addWidget(count_label)
            layout.addWidget(panel)
        layout.addStretch()
        return page

    def build_search_page(self):
        page, layout = self.make_page()
        title = QLabel("Search")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Find a title or browse by console.")
        subtitle.setObjectName("Muted")
        field = QLineEdit()
        field.setPlaceholderText("Type a game or system name...")
        results = QLabel("Search will use your detected game library in a later stage.")
        results.setObjectName("Muted")
        field.textChanged.connect(
            lambda text: results.setText(
                "Matching sample entries: " + str(sum(
                    text.casefold() in (g["title"] + " " + g["system"]).casefold()
                    for g in GAMES
                )) if text.strip() else "Search will use your detected game library in a later stage."
            )
        )
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(field)
        layout.addWidget(results)
        layout.addStretch()
        return page

    def build_settings_page(self):
        page, layout = self.make_page()
        title = QLabel("Settings")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Make RetroDeck feel right at home on your setup.")
        subtitle.setObjectName("Muted")
        panel = QFrame()
        panel.setObjectName("InfoPanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(20, 18, 20, 18)
        theme_title = QLabel("Appearance")
        theme_title.setStyleSheet("font-size: 17px; font-weight: 800;")
        theme_desc = QLabel("Choose between the dark and light interface themes.")
        theme_desc.setObjectName("Muted")
        self.theme_button = QPushButton("Switch to light theme")
        self.theme_button.setObjectName("SecondaryButton")
        self.theme_button.clicked.connect(self.toggle_theme)
        panel_layout.addWidget(theme_title)
        panel_layout.addWidget(theme_desc)
        panel_layout.addWidget(self.theme_button, 0, Qt.AlignmentFlag.AlignLeft)
        note = QLabel("ROM folders, emulator profiles, controller mapping, and database settings will be added in later stages.")
        note.setObjectName("Muted")
        note.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(panel)
        layout.addWidget(note)
        layout.addStretch()
        return page

    def show_page(self, name):
        index = self.PAGES.index(name)
        self.pages.setCurrentIndex(index)
        self.breadcrumb.setText(name.upper())
        for page_name, button in self.nav_buttons.items():
            button.setChecked(page_name == name)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        QApplication.instance().setStyleSheet(DARK_THEME if self.dark_mode else LIGHT_THEME)
        if hasattr(self, "theme_button"):
            self.theme_button.setText(
                "Switch to light theme" if self.dark_mode else "Switch to dark theme"
            )

    def install_shortcuts(self):
        shortcuts = {
            "Ctrl+1": "Home",
            "Ctrl+2": "Library",
            "Ctrl+3": "Systems",
            "Ctrl+4": "Search",
            "Ctrl+5": "Settings",
        }
        for sequence, page in shortcuts.items():
            shortcut = QShortcut(QKeySequence(sequence), self)
            shortcut.activated.connect(lambda target=page: self.show_page(target))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("RetroDeck")
    window = RetroDeckWindow()
    window.showMaximized()
    sys.exit(app.exec())
