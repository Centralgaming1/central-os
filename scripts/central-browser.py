import sys
import os
import subprocess
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtWebEngineCore import *
from PyQt6.QtNetwork import *

TOR_PROXY_HOST = "127.0.0.1"
TOR_PROXY_PORT = 9050
HOME_URL = "https://duckduckgo.com/?kad=en_GB&kp=-2&k1=-1"

def start_tor():
    try:
        result = subprocess.run(["pgrep", "tor"], capture_output=True)
        if result.returncode != 0:
            subprocess.Popen(["tor"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass


class CentralBrowserTab(QWebEngineView):
    def __init__(self, profile):
        super().__init__()
        self.setPage(QWebEnginePage(profile, self))
        self.load(QUrl(HOME_URL))


class CentralBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Central Browser")
        self.setMinimumSize(1200, 700)
        self.tor_enabled = False

        self.profile = QWebEngineProfile("central", self)
        self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.NoCache)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
        QNetworkProxy.setApplicationProxy(QNetworkProxy(QNetworkProxy.ProxyType.NoProxy))

        self.setup_ui()
        self.apply_style()

    def setup_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setCentralWidget(container)

        toolbar = QWidget()
        toolbar.setObjectName("toolbar")
        toolbar.setFixedHeight(48)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(8, 0, 8, 0)
        tb_layout.setSpacing(6)

        self.back_btn = QPushButton("←")
        self.back_btn.setFixedSize(32, 32)
        self.back_btn.setObjectName("navbtn")
        self.back_btn.clicked.connect(self.go_back)

        self.forward_btn = QPushButton("→")
        self.forward_btn.setFixedSize(32, 32)
        self.forward_btn.setObjectName("navbtn")
        self.forward_btn.clicked.connect(self.go_forward)

        self.reload_btn = QPushButton("↺")
        self.reload_btn.setFixedSize(32, 32)
        self.reload_btn.setObjectName("navbtn")
        self.reload_btn.clicked.connect(self.reload_page)

        self.home_btn = QPushButton("⌂")
        self.home_btn.setFixedSize(32, 32)
        self.home_btn.setObjectName("navbtn")
        self.home_btn.clicked.connect(self.go_home)

        self.url_bar = QLineEdit()
        self.url_bar.setObjectName("urlbar")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setPlaceholderText("search or enter address...")

        self.tor_btn = QPushButton("● TOR OFF")
        self.tor_btn.setObjectName("torbtnoff")
        self.tor_btn.setCheckable(True)
        self.tor_btn.clicked.connect(self.toggle_tor)

        new_tab_btn = QPushButton("+ tab")
        new_tab_btn.setObjectName("newtabbtn")
        new_tab_btn.clicked.connect(self.new_tab)

        tb_layout.addWidget(self.back_btn)
        tb_layout.addWidget(self.forward_btn)
        tb_layout.addWidget(self.reload_btn)
        tb_layout.addWidget(self.home_btn)
        tb_layout.addWidget(self.url_bar)
        tb_layout.addWidget(self.tor_btn)
        tb_layout.addWidget(new_tab_btn)
        layout.addWidget(toolbar)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setObjectName("tabs")
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        layout.addWidget(self.tabs)

        self.status = QStatusBar()
        self.status.setObjectName("statusbar")
        self.setStatusBar(self.status)

        self.new_tab()

    def toggle_tor(self):
        if self.tor_btn.isChecked():
            proxy = QNetworkProxy()
            proxy.setType(QNetworkProxy.ProxyType.Socks5Proxy)
            proxy.setHostName(TOR_PROXY_HOST)
            proxy.setPort(TOR_PROXY_PORT)
            QNetworkProxy.setApplicationProxy(proxy)
            self.tor_btn.setText("● TOR ON")
            self.tor_btn.setStyleSheet("color: #50fa7b; font-weight: bold; border-color: #50fa7b;")
            self.status.showMessage("Tor enabled")
        else:
            QNetworkProxy.setApplicationProxy(QNetworkProxy(QNetworkProxy.ProxyType.NoProxy))
            self.tor_btn.setText("● TOR OFF")
            self.tor_btn.setStyleSheet("")
            self.status.showMessage("Tor disabled")

    def new_tab(self, url=None):
        view = CentralBrowserTab(self.profile)
        if url:
            view.load(QUrl(url))
        view.titleChanged.connect(lambda title, v=view: self.update_tab_title(v, title))
        view.urlChanged.connect(lambda qurl, v=view: self.on_url_changed(v, qurl))
        view.loadStarted.connect(lambda v=view: self.on_load_started(v))
        view.loadFinished.connect(lambda ok, v=view: self.on_load_finished(v, ok))
        index = self.tabs.addTab(view, "New Tab")
        self.tabs.setCurrentIndex(index)
        return view

    def current_view(self):
        return self.tabs.currentWidget()

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def on_tab_changed(self, index):
        view = self.tabs.widget(index)
        if view:
            self.url_bar.setText(view.url().toString())

    def update_tab_title(self, view, title):
        index = self.tabs.indexOf(view)
        if index >= 0:
            self.tabs.setTabText(index, title[:20] + "..." if len(title) > 20 else title)

    def on_url_changed(self, view, qurl):
        if view == self.current_view():
            self.url_bar.setText(qurl.toString())

    def on_load_started(self, view):
        if view == self.current_view():
            self.reload_btn.setText("✕")
            self.status.showMessage("Loading...")

    def on_load_finished(self, view, ok):
        if view == self.current_view():
            self.reload_btn.setText("↺")
            self.status.showMessage("Done" if ok else "Failed to load")

    def navigate_to_url(self):
        text = self.url_bar.text().strip()
        if not text:
            return
        if "." in text and " " not in text:
            if not text.startswith("http"):
                text = "https://" + text
            self.current_view().load(QUrl(text))
        else:
            query = text.replace(" ", "+")
            self.current_view().load(QUrl(f"https://duckduckgo.com/?q={query}&kad=en_GB&kp=-2&k1=-1"))

    def go_back(self):
        self.current_view().back()

    def go_forward(self):
        self.current_view().forward()

    def reload_page(self):
        view = self.current_view()
        if self.reload_btn.text() == "✕":
            view.stop()
        else:
            view.reload()

    def go_home(self):
        self.current_view().load(QUrl(HOME_URL))

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
                border-bottom: 1px solid #1a1a1a;
            }
            #navbtn {
                background-color: transparent;
                border: none;
                color: #888888;
                font-size: 16px;
                border-radius: 4px;
            }
            #navbtn:hover {
                background-color: #1a1a1a;
                color: #e8e8e8;
            }
            #urlbar {
                background-color: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 20px;
                color: #e8e8e8;
                padding: 6px 16px;
            }
            #urlbar:focus {
                border-color: #e8272a;
            }
            #torbtnoff {
                background-color: transparent;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                color: #e8272a;
                font-size: 11px;
                font-weight: bold;
                padding: 4px 10px;
            }
            #torbtnoff:hover {
                border-color: #e8272a;
            }
            #newtabbtn {
                background-color: transparent;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                color: #888888;
                padding: 4px 10px;
            }
            #newtabbtn:hover {
                border-color: #e8272a;
                color: #e8e8e8;
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
                max-width: 180px;
            }
            QTabBar::tab:selected {
                color: #e8e8e8;
                border-bottom: 2px solid #e8272a;
            }
            QTabBar::tab:hover {
                color: #e8e8e8;
            }
            QStatusBar {
                background-color: #111111;
                color: #555555;
                font-size: 11px;
                border-top: 1px solid #1a1a1a;
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
    start_tor()
    app = QApplication(sys.argv)
    app.setApplicationName("Central Browser")
    window = CentralBrowser()
    window.show()
    sys.exit(app.exec())
