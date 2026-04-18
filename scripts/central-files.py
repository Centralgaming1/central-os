import sys
import os
import shutil
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class CentralFiles(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Central Files")
        self.setMinimumSize(900, 600)
        self.clipboard_path = None
        self.clipboard_mode = None
        self.current_path = os.path.expanduser("~")
        self.setup_ui()
        self.apply_style()
        self.navigate(self.current_path)

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QWidget()
        toolbar.setFixedHeight(48)
        toolbar.setObjectName("toolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 0, 12, 0)
        toolbar_layout.setSpacing(8)

        self.back_btn = QPushButton("←")
        self.back_btn.setFixedSize(32, 32)
        self.back_btn.clicked.connect(self.go_back)

        self.forward_btn = QPushButton("→")
        self.forward_btn.setFixedSize(32, 32)

        self.up_btn = QPushButton("↑")
        self.up_btn.setFixedSize(32, 32)
        self.up_btn.clicked.connect(self.go_up)

        self.path_bar = QLineEdit()
        self.path_bar.setObjectName("pathbar")
        self.path_bar.returnPressed.connect(lambda: self.navigate(self.path_bar.text()))

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("search")
        self.search_bar.setFixedWidth(200)
        self.search_bar.setObjectName("searchbar")
        self.search_bar.textChanged.connect(self.filter_files)

        toolbar_layout.addWidget(self.back_btn)
        toolbar_layout.addWidget(self.forward_btn)
        toolbar_layout.addWidget(self.up_btn)
        toolbar_layout.addWidget(self.path_bar)
        toolbar_layout.addWidget(self.search_bar)
        layout.addWidget(toolbar)

        # Main area
        splitter = QSplitter()
        splitter.setObjectName("splitter")

        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(180)
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(8, 16, 8, 16)
        sidebar_layout.setSpacing(4)

        places = [
            ("Home", os.path.expanduser("~")),
            ("Documents", os.path.expanduser("~/Documents")),
            ("Downloads", os.path.expanduser("~/Downloads")),
            ("Pictures", os.path.expanduser("~/Pictures")),
            ("Music", os.path.expanduser("~/Music")),
            ("Videos", os.path.expanduser("~/Videos")),
            ("Root", "/"),
        ]

        for name, path in places:
            btn = QPushButton(name)
            btn.setObjectName("sidebar_btn")
            btn.setProperty("path", path)
            btn.clicked.connect(lambda checked, p=path: self.navigate(p))
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        splitter.addWidget(sidebar)

        # File view
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("")

        self.list_view = QListView()
        self.list_view.setModel(self.file_model)
        self.list_view.setViewMode(QListView.ViewMode.IconMode)
        self.list_view.setIconSize(QSize(48, 48))
        self.list_view.setGridSize(QSize(90, 80))
        self.list_view.setSpacing(4)
        self.list_view.setObjectName("fileview")
        self.list_view.doubleClicked.connect(self.on_double_click)
        self.list_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_view.customContextMenuRequested.connect(self.show_context_menu)

        splitter.addWidget(self.list_view)
        layout.addWidget(splitter)

        # Status bar
        self.status = QStatusBar()
        self.status.setObjectName("statusbar")
        self.setStatusBar(self.status)

        self.history = []
        self.history_index = -1

    def apply_style(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #0a0a0a;
                color: #e8e8e8;
                font-family: 'Space Grotesk', sans-serif;
                font-size: 13px;
            }
            #toolbar {
                background-color: #111111;
                border-bottom: 1px solid #222222;
            }
            QPushButton {
                background-color: #1a1a1a;
                color: #e8e8e8;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #222222;
                border-color: #e8272a;
            }
            QPushButton:pressed {
                background-color: #e8272a;
                color: #ffffff;
            }
            #sidebar {
                background-color: #0d0d0d;
                border-right: 1px solid #1a1a1a;
            }
            #sidebar_btn {
                background-color: transparent;
                border: none;
                color: #888888;
                text-align: left;
                padding: 8px 12px;
                border-radius: 4px;
            }
            #sidebar_btn:hover {
                background-color: #1a1a1a;
                color: #e8e8e8;
            }
            #pathbar, #searchbar {
                background-color: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                color: #e8e8e8;
                padding: 4px 8px;
            }
            #pathbar:focus, #searchbar:focus {
                border-color: #e8272a;
            }
            #fileview {
                background-color: #0a0a0a;
                border: none;
                color: #e8e8e8;
            }
            #fileview::item:hover {
                background-color: #1a1a1a;
                border-radius: 4px;
            }
            #fileview::item:selected {
                background-color: #e8272a;
                border-radius: 4px;
            }
            QScrollBar:vertical {
                background-color: #0a0a0a;
                width: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #2a2a2a;
                border-radius: 3px;
            }
            QSplitter::handle {
                background-color: #1a1a1a;
            }
            QStatusBar {
                background-color: #111111;
                color: #555555;
                border-top: 1px solid #1a1a1a;
            }
            QMenu {
                background-color: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                color: #e8e8e8;
            }
            QMenu::item:selected {
                background-color: #e8272a;
            }
        """)

    def navigate(self, path):
        if os.path.isdir(path):
            self.current_path = path
            self.list_view.setRootIndex(self.file_model.setRootPath(path))
            self.path_bar.setText(path)
            self.status.showMessage(f"{path}")
            self.history.append(path)
            self.history_index = len(self.history) - 1

    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.navigate(self.history[self.history_index])

    def go_up(self):
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            self.navigate(parent)

    def on_double_click(self, index):
        path = self.file_model.filePath(index)
        if os.path.isdir(path):
            self.navigate(path)
        else:
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def filter_files(self, text):
        self.file_model.setNameFilters([f"*{text}*"] if text else [])
        self.file_model.setNameFilterDisables(False)

    def show_context_menu(self, pos):
        index = self.list_view.indexAt(pos)
        menu = QMenu()

        if index.isValid():
            path = self.file_model.filePath(index)
            copy_action = menu.addAction("Copy")
            cut_action = menu.addAction("Cut")
            delete_action = menu.addAction("Delete")
            rename_action = menu.addAction("Rename")
            menu.addSeparator()

            copy_action.triggered.connect(lambda: self.copy_file(path))
            cut_action.triggered.connect(lambda: self.cut_file(path))
            delete_action.triggered.connect(lambda: self.delete_file(path))
            rename_action.triggered.connect(lambda: self.rename_file(path))

        paste_action = menu.addAction("Paste")
        new_folder_action = menu.addAction("New Folder")

        paste_action.triggered.connect(self.paste_file)
        new_folder_action.triggered.connect(self.new_folder)

        menu.exec(self.list_view.mapToGlobal(pos))

    def copy_file(self, path):
        self.clipboard_path = path
        self.clipboard_mode = "copy"
        self.status.showMessage(f"Copied: {path}")

    def cut_file(self, path):
        self.clipboard_path = path
        self.clipboard_mode = "cut"
        self.status.showMessage(f"Cut: {path}")

    def paste_file(self):
        if not self.clipboard_path:
            return
        dest = os.path.join(self.current_path, os.path.basename(self.clipboard_path))
        try:
            if self.clipboard_mode == "copy":
                if os.path.isdir(self.clipboard_path):
                    shutil.copytree(self.clipboard_path, dest)
                else:
                    shutil.copy2(self.clipboard_path, dest)
            elif self.clipboard_mode == "cut":
                shutil.move(self.clipboard_path, dest)
                self.clipboard_path = None
            self.status.showMessage(f"Pasted to: {dest}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_file(self, path):
        reply = QMessageBox.question(self, "Delete", f"Delete {os.path.basename(path)}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self.status.showMessage(f"Deleted: {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def rename_file(self, path):
        name, ok = QInputDialog.getText(self, "Rename", "New name:", text=os.path.basename(path))
        if ok and name:
            new_path = os.path.join(os.path.dirname(path), name)
            try:
                os.rename(path, new_path)
                self.status.showMessage(f"Renamed to: {name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def new_folder(self):
        name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if ok and name:
            try:
                os.makedirs(os.path.join(self.current_path, name))
                self.status.showMessage(f"Created folder: {name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Central Files")
    window = CentralFiles()
    window.show()
    sys.exit(app.exec())
