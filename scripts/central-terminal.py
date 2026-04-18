import sys
import os
import platform
import subprocess
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

def get_system_info():
    info = {}
    info["user"] = os.getenv("USER", "user")
    info["hostname"] = "central"
    try:
        info["os"] = "Central OS (Fedora 41)"
        info["kernel"] = platform.release()
        info["shell"] = os.getenv("SHELL", "bash").split("/")[-1]
        result = subprocess.run(["uptime", "-p"], capture_output=True, text=True)
        info["uptime"] = result.stdout.strip().replace("up ", "")
        result = subprocess.run(["nproc"], capture_output=True, text=True)
        info["cpu_cores"] = result.stdout.strip()
        with open("/proc/cpuinfo") as f:
            for line in f:
                if "model name" in line:
                    info["cpu"] = line.split(":")[1].strip()
                    break
        result = subprocess.run(["free", "-h"], capture_output=True, text=True)
        lines = result.stdout.strip().split("\n")
        parts = lines[1].split()
        info["ram"] = f"{parts[2]} / {parts[1]}"
        result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True)
        parts = result.stdout.strip().split("\n")[1].split()
        info["disk"] = f"{parts[2]} / {parts[1]}"
        result = subprocess.run(["bash", "-c", "echo $XDG_SESSION_TYPE"], capture_output=True, text=True)
        info["session"] = result.stdout.strip()
    except:
        pass
    return info

CENTRAL_ASCII = [
    "   ██████╗███████╗███╗  ██╗████████╗██████╗  █████╗ ██╗",
    "  ██╔════╝██╔════╝████╗ ██║╚══██╔══╝██╔══██╗██╔══██╗██║",
    "  ██║     █████╗  ██╔██╗██║   ██║   ██████╔╝███████║██║",
    "  ██║     ██╔══╝  ██║╚████║   ██║   ██╔══██╗██╔══██║██║",
    "  ╚██████╗███████╗██║ ╚███║   ██║   ██║  ██║██║  ██║███████╗",
    "   ╚═════╝╚══════╝╚═╝  ╚══╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝",
    "                      ∞  O P E R A T I N G  S Y S T E M  ∞",
]

class TerminalWidget(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setObjectName("terminal")
        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.read_output)

        env = QProcessEnvironment.systemEnvironment()
        env.insert("TERM", "xterm-256color")
        env.insert("FORCE_COLOR", "1")
        self.process.setProcessEnvironment(env)
        self.process.start("bash", ["--norc"])

        self.username = os.getenv("USER", "user")
        self.hostname = "central"
        self.cwd = os.path.expanduser("~")
        self.input_buffer = ""
        self.history = []
        self.history_index = -1
        self.input_start = 0

        self.ansi_colors = {
            "30": "#1a1a1a", "31": "#e8272a", "32": "#50fa7b",
            "33": "#f1fa8c", "34": "#6272a4", "35": "#ff79c6",
            "36": "#8be9fd", "37": "#e8e8e8", "90": "#555555",
            "91": "#e8272a", "92": "#50fa7b", "93": "#f1fa8c",
            "94": "#6272a4", "95": "#ff79c6", "96": "#8be9fd",
            "97": "#ffffff",
        }

        self.installEventFilter(self)
        self.show_prompt()

    def show_central_fetch(self):
        info = get_system_info()
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)

        red = QTextCharFormat()
        red.setForeground(QColor("#e8272a"))
        red.setFontWeight(QFont.Weight.Bold)

        white = QTextCharFormat()
        white.setForeground(QColor("#e8e8e8"))
        white.setFontWeight(QFont.Weight.Bold)

        muted = QTextCharFormat()
        muted.setForeground(QColor("#555555"))

        label = QTextCharFormat()
        label.setForeground(QColor("#e8272a"))
        label.setFontWeight(QFont.Weight.Bold)

        value = QTextCharFormat()
        value.setForeground(QColor("#e8e8e8"))

        cursor.insertText("\n", muted)

        for line in CENTRAL_ASCII:
            cursor.insertText(line + "\n", red)

        cursor.insertText("\n", muted)

        fields = [
            ("OS", info.get("os", "Central OS")),
            ("Kernel", info.get("kernel", "unknown")),
            ("Shell", info.get("shell", "bash")),
            ("Uptime", info.get("uptime", "unknown")),
            ("CPU", info.get("cpu", "unknown")),
            ("Cores", info.get("cpu_cores", "unknown")),
            ("RAM", info.get("ram", "unknown")),
            ("Disk", info.get("disk", "unknown")),
            ("Session", info.get("session", "wayland")),
        ]

        for key, val in fields:
            cursor.insertText(f"  {key:<10}", label)
            cursor.insertText(f"  {val}\n", value)

        cursor.insertText("\n", muted)

        colors = ["#e8272a", "#50fa7b", "#f1fa8c", "#6272a4", "#ff79c6", "#8be9fd", "#e8e8e8", "#555555"]
        for col in colors:
            fmt = QTextCharFormat()
            fmt.setBackground(QColor(col))
            cursor.insertText("   ", fmt)
        cursor.insertText("\n\n", muted)

        self.setTextCursor(cursor)
        self.input_start = cursor.position()
        self.ensureCursorVisible()

    def show_prompt(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        fmt_user = QTextCharFormat()
        fmt_user.setForeground(QColor("#e8272a"))
        fmt_user.setFontWeight(QFont.Weight.Bold)

        fmt_at = QTextCharFormat()
        fmt_at.setForeground(QColor("#888888"))
        fmt_at.setFontWeight(QFont.Weight.Normal)

        fmt_host = QTextCharFormat()
        fmt_host.setForeground(QColor("#50fa7b"))
        fmt_host.setFontWeight(QFont.Weight.Bold)

        fmt_colon = QTextCharFormat()
        fmt_colon.setForeground(QColor("#888888"))

        fmt_path = QTextCharFormat()
        fmt_path.setForeground(QColor("#8be9fd"))
        fmt_path.setFontWeight(QFont.Weight.Bold)

        fmt_dollar = QTextCharFormat()
        fmt_dollar.setForeground(QColor("#e8e8e8"))
        fmt_dollar.setFontWeight(QFont.Weight.Normal)

        display_path = self.cwd.replace(os.path.expanduser("~"), "~")

        cursor.insertText(self.username, fmt_user)
        cursor.insertText("@", fmt_at)
        cursor.insertText(self.hostname, fmt_host)
        cursor.insertText(":", fmt_colon)
        cursor.insertText(display_path, fmt_path)
        cursor.insertText("$ ", fmt_dollar)

        self.setTextCursor(cursor)
        self.input_start = cursor.position()
        self.ensureCursorVisible()

    def read_output(self):
        raw = self.process.readAllStandardOutput().data().decode(errors="replace")
        self.insert_ansi_text(raw)
        self.input_start = self.textCursor().position()
        self.ensureCursorVisible()

    def insert_ansi_text(self, text):
        import re
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        current_fmt = QTextCharFormat()
        current_fmt.setForeground(QColor("#e8e8e8"))
        parts = re.split(r'(\x1b\[[0-9;]*m)', text)
        for part in parts:
            if part.startswith('\x1b['):
                codes = part[2:-1].split(';')
                for code in codes:
                    if code in ('0', ''):
                        current_fmt = QTextCharFormat()
                        current_fmt.setForeground(QColor("#e8e8e8"))
                    elif code == '1':
                        current_fmt.setFontWeight(QFont.Weight.Bold)
                    elif code in self.ansi_colors:
                        current_fmt.setForeground(QColor(self.ansi_colors[code]))
            else:
                if part:
                    cursor.insertText(part, current_fmt)
        self.setTextCursor(cursor)

    def replace_input(self, text):
        cursor = self.textCursor()
        cursor.setPosition(self.input_start)
        cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(text)
        self.input_buffer = text
        self.setTextCursor(cursor)

    def eventFilter(self, obj, event):
        if obj == self and event.type() == QEvent.Type.KeyPress:
            cursor = self.textCursor()

            if event.key() == Qt.Key.Key_Return:
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.setTextCursor(cursor)
                cmd = self.input_buffer.strip()
                self.insertPlainText("\n")
                self.input_buffer = ""

                if cmd:
                    self.history.append(cmd)
                    self.history_index = len(self.history)

                if cmd == "central":
                    self.show_central_fetch()
                    self.show_prompt()
                elif cmd.startswith("cd"):
                    parts = cmd.split(maxsplit=1)
                    path = parts[1] if len(parts) > 1 else os.path.expanduser("~")
                    path = os.path.expanduser(path)
                    path = os.path.abspath(os.path.join(self.cwd, path))
                    if os.path.isdir(path):
                        self.cwd = path
                        self.process.write(f"cd {path}\n".encode())
                    else:
                        fmt = QTextCharFormat()
                        fmt.setForeground(QColor("#e8272a"))
                        c = self.textCursor()
                        c.movePosition(QTextCursor.MoveOperation.End)
                        c.insertText(f"cd: {path}: No such directory\n", fmt)
                        self.setTextCursor(c)
                    self.show_prompt()
                elif cmd == "clear":
                    self.clear()
                    self.input_buffer = ""
                    self.input_start = 0
                    self.show_prompt()
                elif cmd == "exit":
                    self.window().close()
                elif cmd:
                    self.process.write(f"cd {self.cwd} && {cmd}\n".encode())
                else:
                    self.show_prompt()
                return True

            elif event.key() == Qt.Key.Key_Backspace:
                if cursor.position() > self.input_start and self.input_buffer:
                    cursor.deletePreviousChar()
                    self.input_buffer = self.input_buffer[:-1]
                return True

            elif event.key() == Qt.Key.Key_Up:
                if self.history and self.history_index > 0:
                    self.history_index -= 1
                    self.replace_input(self.history[self.history_index])
                return True

            elif event.key() == Qt.Key.Key_Down:
                if self.history_index < len(self.history) - 1:
                    self.history_index += 1
                    self.replace_input(self.history[self.history_index])
                else:
                    self.replace_input("")
                return True

            elif event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                self.process.write(b"\x03")
                self.input_buffer = ""
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.insertPlainText("\n")
                self.show_prompt()
                return True

            elif event.key() == Qt.Key.Key_L and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                self.clear()
                self.input_buffer = ""
                self.input_start = 0
                self.show_prompt()
                return True

            else:
                if cursor.position() < self.input_start:
                    cursor.movePosition(QTextCursor.MoveOperation.End)
                    self.setTextCursor(cursor)
                char = event.text()
                if char:
                    self.input_buffer += char
                return False

        return False


class CentralTerminal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Central Terminal")
        self.setMinimumSize(900, 550)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setObjectName("tabs")

        toolbar = QWidget()
        toolbar.setObjectName("toolbar")
        toolbar.setFixedHeight(40)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(8, 0, 8, 0)

        new_tab_btn = QPushButton("+ new tab")
        new_tab_btn.setObjectName("newtab")
        new_tab_btn.clicked.connect(self.new_tab)
        tb_layout.addWidget(new_tab_btn)
        tb_layout.addStretch()

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(toolbar)
        layout.addWidget(self.tabs)
        self.setCentralWidget(container)

        self.apply_style()
        self.new_tab()

    def new_tab(self):
        term = TerminalWidget()
        index = self.tabs.addTab(term, f"terminal {self.tabs.count() + 1}")
        self.tabs.setCurrentIndex(index)
        term.setFocus()

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def apply_style(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #0a0a0a;
                color: #e8e8e8;
            }
            #toolbar {
                background-color: #111111;
                border-bottom: 1px solid #1a1a1a;
            }
            #newtab {
                background-color: transparent;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                color: #888888;
                padding: 4px 10px;
                font-size: 12px;
            }
            #newtab:hover {
                color: #e8e8e8;
                border-color: #e8272a;
            }
            QTabWidget::pane {
                border: none;
                background-color: #0a0a0a;
            }
            QTabBar::tab {
                background-color: #111111;
                color: #555555;
                padding: 6px 16px;
                border: none;
                border-right: 1px solid #1a1a1a;
            }
            QTabBar::tab:selected {
                color: #e8e8e8;
                border-bottom: 2px solid #e8272a;
            }
            QTabBar::tab:hover {
                color: #e8e8e8;
            }
            #terminal {
                background-color: #0a0a0a;
                color: #e8e8e8;
                font-family: 'Courier New', monospace;
                font-size: 13px;
                border: none;
                padding: 8px;
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
    app.setApplicationName("Central Terminal")
    window = CentralTerminal()
    window.show()
    sys.exit(app.exec())
