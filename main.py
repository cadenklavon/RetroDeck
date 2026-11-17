"""RetroDeck: early PySide6 desktop UI prototype.

This prototype intentionally uses placeholder game entries. It does not yet
scan ROM folders, launch emulators, load artwork, or save a game database.
"""
import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QApplication, QFrame, QGridLayout, QHBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget, QVBoxLayout, QWidget

DARK_STYLE = """
QWidget { background: #10131b; color: #f3f5fa; font-family: sans-serif; }
QPushButton { background: #252b39; border: 1px solid #3b4559; border-radius: 9px; padding: 10px 16px; text-align: left; }
QPushButton:hover { background: #354057; }
QPushButton:checked { background: #405b86; }
QFrame#GameCard { background: #1b2230; border: 1px solid #30394b; border-radius: 14px; }
"""
LIGHT_STYLE = """
QWidget { background: #f2f4f8; color: #182033; font-family: sans-serif; }
QPushButton { background: #ffffff; border: 1px solid #cbd2df; border-radius: 9px; padding: 10px 16px; text-align: left; }
QPushButton:hover { background: #e3eaf5; }
QPushButton:checked { background: #c9daf5; }
QFrame#GameCard { background: #ffffff; border: 1px solid #d5dbe6; border-radius: 14px; }
"""

class GameCard(QFrame):
    def __init__(self, title: str, system: str):
        super().__init__()
        self.setObjectName("GameCard")
        self.setMinimumSize(170, 150)
        layout = QVBoxLayout(self)
        artwork = QLabel("GAME ART")
        artwork.setAlignment(Qt.AlignmentFlag.AlignCenter)
        artwork.setMinimumHeight(82)
        artwork.setStyleSheet("background: rgba(120,140,170,0.16); border-radius: 8px;")
        name = QLabel(title)
        name.setStyleSheet("font-size: 15px; font-weight: 700;")
        platform = QLabel(system)
        layout.addWidget(artwork)
        layout.addWidget(name)
        layout.addWidget(platform)

class RetroDeckWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RetroDeck")
        self.resize(1280, 720)
        self.dark_mode = True
        root = QWidget()
        outer = QHBoxLayout(root)
        outer.setContentsMargins(18, 18, 18, 18)
        outer.setSpacing(18)
        sidebar = QVBoxLayout()
        brand = QLabel("RETRODECK")
        brand.setStyleSheet("font-size: 22px; font-weight: 900; padding: 12px;")
        sidebar.addWidget(brand)
        self.pages = QStackedWidget()
        self.nav_buttons = []
        for label in ["Home", "Library", "Consoles", "Search", "Settings"]:
            button = QPushButton(label)
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, name=label: self.show_page(name))
            sidebar.addWidget(button)
            self.nav_buttons.append(button)
        sidebar.addStretch()
        theme_button = QPushButton("Toggle light / dark theme")
        theme_button.clicked.connect(self.toggle_theme)
        sidebar.addWidget(theme_button)
        outer.addLayout(sidebar, 1)
        outer.addWidget(self.pages, 5)
        self.setCentralWidget(root)
        self.add_home_page()
        self.add_placeholder_page("Library", "Your complete game library will appear here.")
        self.add_placeholder_page("Consoles", "Browse games by console or emulator.")
        self.add_placeholder_page("Search", "Search your installed game library.")
        self.add_placeholder_page("Settings", "Configure ROM folders, emulators, controls, and appearance.")
        self.show_page("Home")
        self.apply_theme()
        home_action = QAction(self)
        home_action.setShortcut(QKeySequence("H"))
        home_action.triggered.connect(lambda: self.show_page("Home"))
        self.addAction(home_action)

    def add_home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        heading = QLabel("Welcome back")
        heading.setStyleSheet("font-size: 30px; font-weight: 800;")
        layout.addWidget(heading)
        layout.addWidget(QLabel("Your games, all in one place."))
        section = QLabel("Recently played")
        section.setStyleSheet("font-size: 20px; font-weight: 700; margin-top: 20px;")
        layout.addWidget(section)
        grid = QGridLayout()
        samples = [
            ("The Legend of Zelda: Ocarina of Time", "Nintendo 64"),
            ("The Legend of Zelda: The Wind Waker", "GameCube"),
            ("Example Game", "Arcade"),
        ]
        for index, (title, system) in enumerate(samples):
            grid.addWidget(GameCard(title, system), index // 3, index % 3)
        layout.addLayout(grid)
        layout.addStretch()
        note = QLabel("Prototype content only. Game scanning and launching are not implemented yet.")
        note.setWordWrap(True)
        layout.addWidget(note)
        self.pages.addWidget(page)

    def add_placeholder_page(self, title: str, description: str):
        page = QWidget()
        layout = QVBoxLayout(page)
        heading = QLabel(title)
        heading.setStyleSheet("font-size: 30px; font-weight: 800;")
        body = QLabel(description)
        body.setWordWrap(True)
        layout.addWidget(heading)
        layout.addWidget(body)
        layout.addStretch()
        self.pages.addWidget(page)

    def show_page(self, name: str):
        names = ["Home", "Library", "Consoles", "Search", "Settings"]
        self.pages.setCurrentIndex(names.index(name))
        for button in self.nav_buttons:
            button.setChecked(button.text() == name)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        QApplication.instance().setStyleSheet(DARK_STYLE if self.dark_mode else LIGHT_STYLE)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RetroDeckWindow()
    window.showMaximized()
    sys.exit(app.exec())
