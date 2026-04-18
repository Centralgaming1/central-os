import sys
import os
import subprocess
import math
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

CATEGORIES = {
    "All": [],
    "Internet": ["firefox", "chromium", "thunderbird", "transmission", "filezilla", "wget", "curl", "openssh"],
    "Media": ["vlc", "mpv", "rhythmbox", "kdenlive", "obs-studio", "gimp", "inkscape", "audacity", "ffmpeg", "handbrake"],
    "Development": ["git", "vim", "code", "python3", "gcc", "nodejs", "docker", "golang", "rust", "java-17-openjdk", "cmake", "make"],
    "Games": ["steam", "lutris", "retroarch", "hedgewars", "supertuxkart", "openarena"],
    "System": ["htop", "gparted", "timeshift", "bleachbit", "neofetch", "fastfetch", "btop", "lm_sensors", "smartmontools"],
    "Office": ["libreoffice", "libreoffice-writer", "libreoffice-calc", "okular", "evince", "calibre"],
    "Utilities": ["ark", "filelight", "kcalc", "spectacle", "kdeconnect", "rsync", "unzip", "p7zip", "fuse"],
}

class LoadingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("loading")
        self.angle = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_angle)
        self.timer.start(16)
        self.status_text = "Loading packages..."

    def update_angle(self):
        self.angle = (self.angle + 3) % 360
        self.update()

    def set_status(self, text):
        self.status_text = text
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2

        painter.fillRect(0, 0, w, h, QColor("#0a0a0a"))

        # Draw CENTRAL text
        painter.setPen(QColor("#e8e8e8"))
        font = QFont("Space Grotesk", 22, QFont.Weight.Light)
        painter.setFont(font)
        fm = painter.fontMetrics()
        text = "CENTRAL"
        text_w = fm.horizontalAdvance(text)
        painter.drawText(cx - text_w // 2, cy + 130, text)

        # Draw infinity track (faint)
        track_pen = QPen(QColor("#1a1a1a"), 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        self.draw_infinity(painter, cx, cy, 120, 55)

        # Draw infinity white outline
        white_pen = QPen(QColor("#2a2a2a"), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(white_pen)
        self.draw_infinity(painter, cx, cy, 120, 55)

        # Draw dot on track
        t = math.radians(self.angle)
        r = 120
        scale_y = 55
        x = cx + (r * math.cos(t)) / (1 + math.sin(t) ** 2)
        y = cy + (scale_y * math.sin(t) * math.cos(t)) / (1 + math.sin(t) ** 2)

        # Glow effect
        for radius, alpha in [(14, 30), (10, 60), (7, 120), (5, 255)]:
            color = QColor(232, 39, 42, alpha)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            painter.drawEllipse(QPointF(x, y), radius, radius)

        # Status text
        painter.setPen(QColor("#555555"))
        font2 = QFont("Space Grotesk", 10)
        painter.setFont(font2)
        fm2 = painter.fontMetrics()
        sw = fm2.horizontalAdvance(self.status_text)
        painter.drawText(cx - sw // 2, cy + 180, self.status_text)

    def draw_infinity(self, painter, cx, cy, r, scale_y):
        steps = 200
        points = []
        for i in range(steps + 1):
            t = (i / steps) * 2 * math.pi
            x = cx + (r * math.cos(t)) / (1 + math.sin(t) ** 2)
            y = cy + (scale_y * math.sin(t) * math.cos(t)) / (1 + math.sin(t) ** 2)
            points.append(QPointF(x, y))
        path = QPainterPath()
        path.moveTo(points[0])
        for p in points[1:]:
            path.lineTo(p)
        painter.drawPath(path)


class AppCard(QFrame):
    install_requested = pyqtSignal(str)
    remove_requested = pyqtSignal(str)

    def __init__(self, name, installed=False):
        super().__init__()
        self.name = name
        self.installed = installed
        self.setObjectName("appcard")
        self.setFixedSize(200, 120)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        icon = QIcon.fromTheme(name, QIcon.fromTheme("application-x-executable"))
        icon_label.setPixmap(icon.pixmap(32, 32))

        name_label = QLabel(name)
        name_label.setObjectName("appname")
        name_label.setWordWrap(True)

        self.btn = QPushButton("Remove" if installed else "Install")
        self.btn.setObjectName("removebtn" if installed else "installbtn")
        self.btn.clicked.connect(self.on_btn_click)

        layout.addWidget(icon_label)
        layout.addWidget(name_label)
        layout.addStretch()
        layout.addWidget(self.btn)

    def on_btn_click(self):
        if self.installed:
            self.remove_requested.emit(self.name)
        else:
            self.install_requested.emit(self.name)


class PackageLoader(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(list, set)

    def run(self):
        all_packages = []
        installed = set()

        self.progress.emit("Loading installed packages...")
        try:
            proc = subprocess.run(
                ["dnf", "list", "installed", "--quiet"],
                capture_output=True, text=True, timeout=30
            )
            for line in proc.stdout.split("\n"):
                if line:
                    name = line.split(".")[0].strip()
                    if name:
                        installed.add(name)
        except:
            pass

        self.progress.emit("Loading available packages...")
        try:
            proc = subprocess.run(
                ["dnf", "list", "available", "--quiet"],
                capture_output=True, text=True, timeout=60
            )
            for line in proc.stdout.split("\n"):
                if line and not line.startswith("Available"):
                    name = line.split(".")[0].strip()
                    if name and not name.startswith("lib") and len(name) > 1:
                        all_packages.append(name)
        except:
            pass

        self.progress.emit("Ready!")
        self.finished.emit(all_packages, installed)


class InstallWorker(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, package, action):
        super().__init__()
        self.package = package
        self.action = action

    def run(self):
        try:
            cmd = ["sudo", "dnf", self.action, self.package, "-y"]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            self.finished.emit(proc.returncode == 0, self.package)
        except Exception as e:
            self.finished.emit(False, str(e))


class CentralStore(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Central Store")
        self.setMinimumSize(1000, 650)
        self.installed_packages = set()
        self.all_packages = []
        self.current_category = "All"

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.loading_screen = LoadingScreen()
        self.stack.addWidget(self.loading_screen)

        self.main_widget = QWidget()
        self.setup_main_ui()
        self.stack.addWidget(self.main_widget)

        self.apply_style()
        self.load_packages()

    def load_packages(self):
        self.loader = PackageLoader()
        self.loader.progress.connect(self.loading_screen.set_status)
        self.loader.finished.connect(self.on_packages_loaded)
        self.loader.start()

    def on_packages_loaded(self, packages, installed):
        self.all_packages = packages
        self.installed_packages = installed
        self.stack.setCurrentWidget(self.main_widget)
        self.show_category("All")

    def setup_main_ui(self):
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setObjectName("header")
        header.setFixedHeight(60)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        title = QLabel("Central Store")
        title.setObjectName("title")

        self.search = QLineEdit()
        self.search.setPlaceholderText("search apps...")
        self.search.setFixedWidth(300)
        self.search.setObjectName("searchbar")
        self.search.textChanged.connect(self.do_search)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.search)
        main_layout.addWidget(header)

        # Body
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(180)
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(8, 16, 8, 16)
        sidebar_layout.setSpacing(4)

        cat_label = QLabel("CATEGORIES")
        cat_label.setObjectName("catlabel")
        sidebar_layout.addWidget(cat_label)
        sidebar_layout.addSpacing(8)

        self.cat_buttons = {}
        for cat in CATEGORIES:
            btn = QPushButton(cat)
            btn.setObjectName("catbtn")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, c=cat: self.show_category(c))
            sidebar_layout.addWidget(btn)
            self.cat_buttons[cat] = btn

        self.cat_buttons["All"].setChecked(True)
        sidebar_layout.addStretch()

        installed_btn = QPushButton("Installed")
        installed_btn.setObjectName("installedbtn")
        installed_btn.clicked.connect(self.show_installed)
        sidebar_layout.addWidget(installed_btn)

        body_layout.addWidget(sidebar)

        # Content
        content = QWidget()
        content.setObjectName("content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(12)

        self.page_title = QLabel("All Apps")
        self.page_title.setObjectName("pagetitle")
        content_layout.addWidget(self.page_title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("scroll")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.grid_widget = QWidget()
        self.grid = QGridLayout(self.grid_widget)
        self.grid.setSpacing(12)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(self.grid_widget)
        content_layout.addWidget(scroll)

        body_layout.addWidget(content)
        main_layout.addWidget(body)

        # Status bar
        self.status_bar = QWidget()
        self.status_bar.setObjectName("statusbar")
        self.status_bar.setFixedHeight(36)
        self.status_bar.hide()
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(16, 0, 16, 0)

        self.status_label = QLabel("")
        self.status_label.setObjectName("statuslabel")
        self.progress = QProgressBar()
        self.progress.setObjectName("progress")
        self.progress.setRange(0, 0)
        self.progress.setFixedWidth(200)

        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.progress)
        main_layout.addWidget(self.status_bar)

    def show_category(self, category):
        self.current_category = category
        for cat, btn in self.cat_buttons.items():
            btn.setChecked(cat == category)

        if category == "All":
            packages = self.all_packages[:200]
        else:
            packages = CATEGORIES.get(category, [])

        self.page_title.setText(category)
        self.populate_grid(packages)

    def show_installed(self):
        for btn in self.cat_buttons.values():
            btn.setChecked(False)
        self.page_title.setText("Installed")
        installed_list = sorted([p for p in self.installed_packages if not p.startswith("lib")])[:100]
        self.populate_grid(installed_list)

    def do_search(self, text):
        if not text:
            self.show_category(self.current_category)
            return
        results = [p for p in self.all_packages if text.lower() in p.lower()][:100]
        self.page_title.setText(f"Results for '{text}'")
        self.populate_grid(results)

    def populate_grid(self, packages):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        row, col = 0, 0
        for pkg in packages:
            card = AppCard(pkg, pkg in self.installed_packages)
            card.install_requested.connect(self.install_package)
            card.remove_requested.connect(self.remove_package)
            self.grid.addWidget(card, row, col)
            col += 1
            if col >= 4:
                col = 0
                row += 1

    def install_package(self, package):
        self.status_bar.show()
        self.status_label.setText(f"Installing {package}...")
        self.worker = InstallWorker(package, "install")
        self.worker.finished.connect(self.on_action_finished)
        self.worker.start()

    def remove_package(self, package):
        self.status_bar.show()
        self.status_label.setText(f"Removing {package}...")
        self.worker = InstallWorker(package, "remove")
        self.worker.finished.connect(self.on_action_finished)
        self.worker.start()

    def on_action_finished(self, success, package):
        self.status_bar.hide()
        if success:
            if "Installing" in self.status_label.text():
                self.installed_packages.add(package)
            else:
                self.installed_packages.discard(package)
            self.show_category(self.current_category)
            QMessageBox.information(self, "Done", f"{package} completed successfully.")
        else:
            QMessageBox.critical(self, "Error", f"Failed to complete action on {package}.")

    def apply_style(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #0a0a0a;
                color: #e8e8e8;
                font-family: 'Space Grotesk', sans-serif;
                font-size: 13px;
            }
            #header {
                background-color: #111111;
                border-bottom: 1px solid #1a1a1a;
            }
            #title {
                font-size: 18px;
                font-weight: bold;
                color: #e8e8e8;
                letter-spacing: 2px;
            }
            #searchbar {
                background-color: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                color: #e8e8e8;
                padding: 6px 12px;
            }
            #searchbar:focus {
                border-color: #e8272a;
            }
            #sidebar {
                background-color: #0d0d0d;
                border-right: 1px solid #1a1a1a;
            }
            #catlabel {
                color: #555555;
                font-size: 11px;
                letter-spacing: 2px;
                padding-left: 12px;
            }
            #catbtn {
                background-color: transparent;
                border: none;
                color: #888888;
                text-align: left;
                padding: 8px 12px;
                border-radius: 4px;
            }
            #catbtn:hover {
                background-color: #1a1a1a;
                color: #e8e8e8;
            }
            #catbtn:checked {
                background-color: #1a1a1a;
                color: #e8272a;
                border-left: 2px solid #e8272a;
            }
            #installedbtn {
                background-color: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                color: #e8e8e8;
                padding: 8px 12px;
            }
            #installedbtn:hover {
                border-color: #e8272a;
                color: #e8272a;
            }
            #content {
                background-color: #0a0a0a;
            }
            #pagetitle {
                font-size: 16px;
                font-weight: bold;
                color: #e8e8e8;
                padding-bottom: 8px;
            }
            #scroll {
                border: none;
                background-color: #0a0a0a;
            }
            #appcard {
                background-color: #111111;
                border: 1px solid #1a1a1a;
                border-radius: 8px;
            }
            #appcard:hover {
                border-color: #333333;
            }
            #appname {
                color: #e8e8e8;
                font-size: 12px;
            }
            #installbtn {
                background-color: #e8272a;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }
            #installbtn:hover {
                background-color: #cc2020;
            }
            #removebtn {
                background-color: transparent;
                color: #888888;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }
            #removebtn:hover {
                border-color: #e8272a;
                color: #e8272a;
            }
            #statusbar {
                background-color: #111111;
                border-top: 1px solid #1a1a1a;
            }
            #statuslabel {
                color: #888888;
                font-size: 12px;
            }
            #progress::chunk {
                background-color: #e8272a;
                border-radius: 2px;
            }
            QScrollBar:vertical {
                background-color: #0a0a0a;
                width: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #2a2a2a;
                border-radius: 3px;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Central Store")
    window = CentralStore()
    window.show()
    sys.exit(app.exec())
