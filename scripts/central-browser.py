#!/usr/bin/env python3
"""
Central Browser — Part of Central OS
Dark red/black theme | AI assistant | Ad blocker | Password manager | Email | News
"""

import sys
import os
import json
import re
import hashlib
import threading
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtWebEngineCore import *

# ── Config paths ─────────────────────────────────────────────────────────────
CONFIG_DIR = Path.home() / ".config" / "central-browser"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
PASSWORDS_FILE = CONFIG_DIR / "passwords.json"
ACCOUNT_FILE   = CONFIG_DIR / "account.json"
HISTORY_FILE   = CONFIG_DIR / "history.json"
BOOKMARKS_FILE = CONFIG_DIR / "bookmarks.json"

def load_json(path, default):
    try:
        return json.loads(path.read_text())
    except:
        return default

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2))

# ── Ad block list ─────────────────────────────────────────────────────────────
AD_DOMAINS = {
    "doubleclick.net", "googlesyndication.com", "googleadservices.com",
    "adservice.google.com", "amazon-adsystem.com", "ads.twitter.com",
    "facebook.com/tr", "connect.facebook.net", "analytics.google.com",
    "google-analytics.com", "hotjar.com", "optimizely.com",
    "scorecardresearch.com", "quantserve.com", "outbrain.com",
    "taboola.com", "pubmatic.com", "rubiconproject.com", "openx.net",
    "adnxs.com", "advertising.com", "moatads.com", "criteo.com",
    "adroll.com", "chartbeat.com", "newrelic.com", "mixpanel.com",
}

class AdBlocker(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        host = info.requestUrl().host()
        for domain in AD_DOMAINS:
            if domain in host or domain in url:
                info.block(True)
                return

# ── Search engines ────────────────────────────────────────────────────────────
SEARCH_ENGINES = {
    "DuckDuckGo": "https://duckduckgo.com/?q={}",
    "Google":     "https://www.google.com/search?q={}",
    "Bing":       "https://www.bing.com/search?q={}",
    "Brave":      "https://search.brave.com/search?q={}",
    "Ecosia":     "https://www.ecosia.org/search?q={}",
    "Startpage":  "https://www.startpage.com/search?q={}",
}

# ── News sources (RSS) ────────────────────────────────────────────────────────
NEWS_FEEDS = {
    "BBC News":       "http://feeds.bbci.co.uk/news/rss.xml",
    "Hull Live":      "https://www.hulldailymail.co.uk/news/?service=rss",
    "Sky News":       "https://feeds.skynews.com/feeds/rss/home.xml",
    "The Guardian":   "https://www.theguardian.com/uk/rss",
    "Yorkshire Post": "https://www.yorkshirepost.co.uk/news/rss.xml",
}

# ── Stylesheet ────────────────────────────────────────────────────────────────
QSS = """
* {
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    color: #f0f0f0;
}
QMainWindow, QWidget {
    background-color: #0a0a0a;
}
QToolBar {
    background: #0f0f0f;
    border-bottom: 2px solid #cc0000;
    padding: 4px;
    spacing: 4px;
}
QLineEdit {
    background: #1a1a1a;
    border: 1px solid #333;
    border-radius: 6px;
    padding: 6px 12px;
    color: #f0f0f0;
    font-size: 13px;
    selection-background-color: #cc0000;
}
QLineEdit:focus {
    border-color: #cc0000;
}
QPushButton {
    background: #1a1a1a;
    border: 1px solid #333;
    border-radius: 6px;
    padding: 6px 14px;
    color: #f0f0f0;
    font-size: 12px;
}
QPushButton:hover {
    background: #cc0000;
    border-color: #cc0000;
}
QPushButton:pressed {
    background: #990000;
}
QTabWidget::pane {
    border: none;
    background: #0a0a0a;
}
QTabBar::tab {
    background: #111;
    color: #888;
    border: none;
    padding: 8px 18px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    min-width: 120px;
}
QTabBar::tab:selected {
    background: #1a1a1a;
    color: #f0f0f0;
    border-bottom: 2px solid #cc0000;
}
QTabBar::tab:hover {
    background: #1e1e1e;
    color: #f0f0f0;
}
QComboBox {
    background: #1a1a1a;
    border: 1px solid #333;
    border-radius: 6px;
    padding: 5px 10px;
    color: #f0f0f0;
}
QComboBox:hover { border-color: #cc0000; }
QComboBox QAbstractItemView {
    background: #1a1a1a;
    border: 1px solid #cc0000;
    selection-background-color: #cc0000;
}
QScrollBar:vertical {
    background: #111;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #cc0000;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QListWidget {
    background: #111;
    border: 1px solid #222;
    border-radius: 6px;
}
QListWidget::item { padding: 8px; }
QListWidget::item:selected { background: #cc0000; }
QListWidget::item:hover { background: #1e1e1e; }
QTextEdit {
    background: #111;
    border: 1px solid #222;
    border-radius: 6px;
    padding: 8px;
    color: #f0f0f0;
}
QLabel { color: #f0f0f0; }
QGroupBox {
    border: 1px solid #333;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 8px;
    color: #cc0000;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}
QMenuBar {
    background: #0f0f0f;
    border-bottom: 1px solid #222;
}
QMenuBar::item:selected { background: #cc0000; }
QMenu {
    background: #1a1a1a;
    border: 1px solid #333;
}
QMenu::item:selected { background: #cc0000; }
QSplitter::handle { background: #222; }
QDialog {
    background: #0a0a0a;
}
QInputDialog {
    background: #0a0a0a;
}
"""

# ── Password Manager ──────────────────────────────────────────────────────────
class PasswordManager:
    def __init__(self):
        self.data = load_json(PASSWORDS_FILE, {})

    def save_password(self, site, username, password):
        self.data[site] = {"username": username, "password": password}
        save_json(PASSWORDS_FILE, self.data)

    def get_password(self, site):
        return self.data.get(site)

    def all_entries(self):
        return self.data

    def delete(self, site):
        self.data.pop(site, None)
        save_json(PASSWORDS_FILE, self.data)

class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Password Manager")
        self.setMinimumSize(600, 400)
        layout = QVBoxLayout(self)

        self.pm = parent.password_manager if parent else PasswordManager()

        top = QHBoxLayout()
        self.search = QLineEdit(placeholderText="Search sites...")
        self.search.textChanged.connect(self.refresh)
        top.addWidget(self.search)
        add_btn = QPushButton("+ Add")
        add_btn.clicked.connect(self.add_entry)
        top.addWidget(add_btn)
        layout.addLayout(top)

        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self.copy_password)
        layout.addWidget(self.list)

        del_btn = QPushButton("Delete Selected")
        del_btn.clicked.connect(self.delete_entry)
        layout.addWidget(del_btn)

        self.refresh()

    def refresh(self):
        self.list.clear()
        q = self.search.text().lower()
        for site, creds in self.pm.all_entries().items():
            if q in site.lower() or q in creds["username"].lower():
                item = QListWidgetItem(f"🔐  {site}  —  {creds['username']}")
                item.setData(Qt.ItemDataRole.UserRole, site)
                self.list.addItem(item)

    def add_entry(self):
        site, ok = QInputDialog.getText(self, "Site", "Website:")
        if not ok or not site: return
        user, ok = QInputDialog.getText(self, "Username", "Username/Email:")
        if not ok: return
        pwd, ok = QInputDialog.getText(self, "Password", "Password:", QLineEdit.EchoMode.Password)
        if not ok: return
        self.pm.save_password(site, user, pwd)
        self.refresh()

    def copy_password(self, item):
        site = item.data(Qt.ItemDataRole.UserRole)
        creds = self.pm.get_password(site)
        if creds:
            QApplication.clipboard().setText(creds["password"])
            QMessageBox.information(self, "Copied", f"Password for {site} copied to clipboard.")

    def delete_entry(self):
        item = self.list.currentItem()
        if item:
            site = item.data(Qt.ItemDataRole.UserRole)
            self.pm.delete(site)
            self.refresh()

# ── Account Manager ───────────────────────────────────────────────────────────
class AccountDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Central Browser Account")
        self.setMinimumSize(400, 300)
        layout = QVBoxLayout(self)

        self.data = load_json(ACCOUNT_FILE, {})

        grp = QGroupBox("Your Account")
        form = QFormLayout(grp)

        self.name_edit = QLineEdit(self.data.get("name", ""))
        self.email_edit = QLineEdit(self.data.get("email", ""))
        self.avatar_label = QLabel(self.data.get("email", "No account linked"))
        self.avatar_label.setStyleSheet("color: #cc0000; font-size: 14px;")

        form.addRow("Display Name:", self.name_edit)
        form.addRow("Email:", self.email_edit)
        form.addRow("Linked:", self.avatar_label)
        layout.addWidget(grp)

        save_btn = QPushButton("Save Account")
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

        info = QLabel("Linking your email enables syncing bookmarks and passwords across devices (coming soon).")
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(info)

    def save(self):
        self.data["name"] = self.name_edit.text()
        self.data["email"] = self.email_edit.text()
        save_json(ACCOUNT_FILE, self.data)
        self.avatar_label.setText(self.data["email"] or "No account linked")
        QMessageBox.information(self, "Saved", "Account saved.")

# ── News Page ─────────────────────────────────────────────────────────────────
class NewsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("📰  Central News")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #cc0000; margin-bottom: 10px;")
        layout.addWidget(header)

        # Source selector
        src_bar = QHBoxLayout()
        src_bar.addWidget(QLabel("Source:"))
        self.src_combo = QComboBox()
        for name in NEWS_FEEDS:
            self.src_combo.addItem(name)
        src_bar.addWidget(self.src_combo)
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_news)
        src_bar.addWidget(refresh_btn)
        src_bar.addStretch()
        layout.addLayout(src_bar)

        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self.open_article)
        layout.addWidget(self.list)

        self.articles = []
        self.load_news()

    def load_news(self):
        self.list.clear()
        self.list.addItem("Loading...")
        source = self.src_combo.currentText()
        url = NEWS_FEEDS[source]
        threading.Thread(target=self._fetch, args=(url,), daemon=True).start()

    def _fetch(self, url):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "CentralBrowser/1.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = r.read()
            root = ET.fromstring(data)
            items = root.findall(".//item")
            self.articles = []
            for item in items[:20]:
                title = item.findtext("title", "No title")
                link  = item.findtext("link", "")
                desc  = item.findtext("description", "")
                desc  = re.sub('<[^>]+>', '', desc)[:120]
                pub   = item.findtext("pubDate", "")
                self.articles.append((title, link, desc, pub))
            QMetaObject.invokeMethod(self, "_update_list", Qt.ConnectionType.QueuedConnection)
        except Exception as e:
            self.articles = [(f"Failed to load: {e}", "", "", "")]
            QMetaObject.invokeMethod(self, "_update_list", Qt.ConnectionType.QueuedConnection)

    @pyqtSlot()
    def _update_list(self):
        self.list.clear()
        for title, link, desc, pub in self.articles:
            item = QListWidgetItem(f"  {title}\n  {desc}")
            item.setData(Qt.ItemDataRole.UserRole, link)
            item.setSizeHint(QSize(0, 56))
            self.list.addItem(item)

    def open_article(self, item):
        url = item.data(Qt.ItemDataRole.UserRole)
        if url and hasattr(self.parent(), 'open_url'):
            self.parent().open_url(url)

# ── Email Client ──────────────────────────────────────────────────────────────
class EmailPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("✉️  Central Mail")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #cc0000; margin-bottom: 10px;")
        layout.addWidget(header)

        info = QLabel(
            "Central Mail connects to your Gmail or Yahoo account via webmail.\n"
            "Select your provider below to open your inbox."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #888; margin-bottom: 16px;")
        layout.addWidget(info)

        btn_row = QHBoxLayout()

        gmail_btn = QPushButton("📧  Open Gmail")
        gmail_btn.setMinimumHeight(48)
        gmail_btn.clicked.connect(lambda: self._open("https://mail.google.com"))
        btn_row.addWidget(gmail_btn)

        yahoo_btn = QPushButton("📧  Open Yahoo Mail")
        yahoo_btn.setMinimumHeight(48)
        yahoo_btn.clicked.connect(lambda: self._open("https://mail.yahoo.com"))
        btn_row.addWidget(yahoo_btn)

        outlook_btn = QPushButton("📧  Open Outlook")
        outlook_btn.setMinimumHeight(48)
        outlook_btn.clicked.connect(lambda: self._open("https://outlook.live.com"))
        btn_row.addWidget(outlook_btn)

        layout.addLayout(btn_row)

        compose_grp = QGroupBox("Quick Compose")
        compose_form = QFormLayout(compose_grp)
        self.to_edit      = QLineEdit(placeholderText="To:")
        self.subject_edit = QLineEdit(placeholderText="Subject:")
        self.body_edit    = QTextEdit()
        self.body_edit.setMaximumHeight(120)
        self.body_edit.setPlaceholderText("Message...")
        compose_form.addRow("To:", self.to_edit)
        compose_form.addRow("Subject:", self.subject_edit)
        compose_form.addRow("Body:", self.body_edit)

        send_row = QHBoxLayout()
        gmail_send = QPushButton("Send via Gmail")
        gmail_send.clicked.connect(lambda: self._compose_mailto("gmail"))
        yahoo_send = QPushButton("Send via Yahoo")
        yahoo_send.clicked.connect(lambda: self._compose_mailto("yahoo"))
        send_row.addWidget(gmail_send)
        send_row.addWidget(yahoo_send)
        compose_form.addRow("", send_row)
        layout.addWidget(compose_grp)
        layout.addStretch()

    def _open(self, url):
        main = self.window()
        if hasattr(main, 'open_url'):
            main.open_url(url)

    def _compose_mailto(self, provider):
        to      = urllib.parse.quote(self.to_edit.text())
        subject = urllib.parse.quote(self.subject_edit.text())
        body    = urllib.parse.quote(self.body_edit.toPlainText())
        if provider == "gmail":
            url = f"https://mail.google.com/mail/?view=cm&to={to}&su={subject}&body={body}"
        else:
            url = f"https://compose.mail.yahoo.com/?to={to}&subject={subject}&body={body}"
        self._open(url)

# ── AI Assistant Panel ────────────────────────────────────────────────────────
class AiPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(340)
        self.setMinimumWidth(280)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        header = QLabel("🤖  Central AI  (Mistral)")
        header.setStyleSheet("font-size: 14px; font-weight: bold; color: #cc0000; padding: 4px;")
        layout.addWidget(header)

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setStyleSheet("font-size: 12px; line-height: 1.5;")
        layout.addWidget(self.chat)

        input_row = QHBoxLayout()
        self.input = QLineEdit(placeholderText="Ask Mistral anything...")
        self.input.returnPressed.connect(self.send)
        input_row.addWidget(self.input)
        send_btn = QPushButton("▶")
        send_btn.setFixedWidth(36)
        send_btn.clicked.connect(self.send)
        input_row.addWidget(send_btn)
        layout.addLayout(input_row)

        context_btn = QPushButton("📄 Send Page Context")
        context_btn.clicked.connect(self.send_page_context)
        layout.addWidget(context_btn)

        self.messages = []
        self._append("system", "Central AI ready. Using Mistral via Ollama.\nMake sure Ollama is running: ollama serve")

    def _append(self, role, text):
        color = "#cc0000" if role == "user" else "#aaa" if role == "system" else "#f0f0f0"
        label = "You" if role == "user" else "AI" if role == "assistant" else "System"
        self.chat.append(f'<span style="color:{color};font-weight:bold;">{label}:</span> {text}<br>')

    def send(self, extra=""):
        prompt = self.input.text().strip()
        if extra:
            prompt = f"{prompt}\n\n[Page context]: {extra}" if prompt else extra
        if not prompt:
            return
        self.input.clear()
        self._append("user", prompt)
        self.messages.append({"role": "user", "content": prompt})
        threading.Thread(target=self._query, args=(list(self.messages),), daemon=True).start()

    def send_page_context(self):
        main = self.window()
        if hasattr(main, 'current_tab'):
            tab = main.current_tab()
            if tab and hasattr(tab, 'page'):
                tab.page().toPlainText(lambda text: self.send(text[:2000]))

    def _query(self, messages):
        try:
            payload = json.dumps({
                "model": "mistral",
                "messages": messages,
                "stream": False
            }).encode()
            req = urllib.request.Request(
                "http://localhost:11434/api/chat",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=60) as r:
                resp = json.loads(r.read())
            reply = resp["message"]["content"]
            self.messages.append({"role": "assistant", "content": reply})
            QMetaObject.invokeMethod(self, "_ai_reply",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, reply))
        except Exception as e:
            QMetaObject.invokeMethod(self, "_ai_reply",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, f"[Error: {e}]\nIs Ollama running? Try: ollama serve"))

    @pyqtSlot(str)
    def _ai_reply(self, text):
        self._append("assistant", text)

# ── Browser Tab ───────────────────────────────────────────────────────────────
class BrowserTab(QWebEngineView):
    def __init__(self, profile, parent=None):
        super().__init__(parent)
        page = QWebEnginePage(profile, self)
        self.setPage(page)
        self.setUrl(QUrl("https://duckduckgo.com"))

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        menu.exec(event.globalPos())

# ── Main Window ───────────────────────────────────────────────────────────────
class CentralBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Central Browser")
        self.setMinimumSize(1100, 700)
        self.password_manager = PasswordManager()
        self.search_engine = "DuckDuckGo"
        self.ai_visible = False

        # Web profile + ad blocker
        self.profile = QWebEngineProfile("central", self)
        self.interceptor = AdBlocker()
        self.profile.setUrlRequestInterceptor(self.interceptor)

        self._build_ui()
        self._build_menubar()
        self.setStyleSheet(QSS)

        # Load account
        acc = load_json(ACCOUNT_FILE, {})
        if acc.get("name"):
            self.statusBar().showMessage(f"Welcome, {acc['name']}", 3000)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left: browser area
        browser_area = QWidget()
        browser_layout = QVBoxLayout(browser_area)
        browser_layout.setContentsMargins(0, 0, 0, 0)
        browser_layout.setSpacing(0)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))

        back_btn = QPushButton("◀")
        back_btn.setFixedWidth(36)
        back_btn.clicked.connect(lambda: self._current_web().back())
        fwd_btn = QPushButton("▶")
        fwd_btn.setFixedWidth(36)
        fwd_btn.clicked.connect(lambda: self._current_web().forward())
        reload_btn = QPushButton("↻")
        reload_btn.setFixedWidth(36)
        reload_btn.clicked.connect(lambda: self._current_web().reload())
        home_btn = QPushButton("⌂")
        home_btn.setFixedWidth(36)
        home_btn.clicked.connect(lambda: self._current_web().setUrl(QUrl("https://duckduckgo.com")))

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter URL...")
        self.url_bar.returnPressed.connect(self._navigate)

        self.engine_combo = QComboBox()
        for name in SEARCH_ENGINES:
            self.engine_combo.addItem(name)
        self.engine_combo.currentTextChanged.connect(lambda t: setattr(self, 'search_engine', t))

        new_tab_btn = QPushButton("+")
        new_tab_btn.setFixedWidth(36)
        new_tab_btn.clicked.connect(self.new_tab)

        ai_btn = QPushButton("🤖 AI")
        ai_btn.clicked.connect(self.toggle_ai)

        for w in [back_btn, fwd_btn, reload_btn, home_btn]:
            toolbar.addWidget(w)
        toolbar.addWidget(self.url_bar)
        toolbar.addWidget(self.engine_combo)
        toolbar.addWidget(new_tab_btn)
        toolbar.addWidget(ai_btn)
        browser_layout.addWidget(toolbar)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self._tab_changed)
        browser_layout.addWidget(self.tabs)

        main_layout.addWidget(browser_area)

        # Right: AI panel
        self.ai_panel = AiPanel(self)
        self.ai_panel.hide()
        main_layout.addWidget(self.ai_panel)

        # Status bar
        self.setStatusBar(QStatusBar())

        # Special pages in tabs
        self._add_special_tab("🏠 Home", self._make_home())
        self.new_tab()

    def _make_home(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo = QLabel("⬛  CENTRAL BROWSER")
        logo.setStyleSheet("font-size: 36px; font-weight: bold; color: #cc0000; letter-spacing: 4px;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        sub = QLabel("Part of Central OS")
        sub.setStyleSheet("color: #444; font-size: 14px; margin-bottom: 30px;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        quick_links = [
            ("📰 News",    self._open_news),
            ("✉️ Mail",    self._open_email),
            ("🔐 Passwords", self._open_passwords),
            ("🤖 AI Chat", self.toggle_ai),
        ]
        btn_row = QHBoxLayout()
        for label, fn in quick_links:
            btn = QPushButton(label)
            btn.setMinimumSize(130, 50)
            btn.clicked.connect(fn)
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)
        return w

    def _add_special_tab(self, title, widget):
        idx = self.tabs.addTab(widget, title)
        self.tabs.setCurrentIndex(idx)

    def _open_news(self):
        self._add_special_tab("📰 News", NewsPage(self))

    def _open_email(self):
        self._add_special_tab("✉️ Mail", EmailPage(self))

    def _open_passwords(self):
        dlg = PasswordDialog(self)
        dlg.exec()

    def _build_menubar(self):
        mb = self.menuBar()

        file_menu = mb.addMenu("File")
        file_menu.addAction("New Tab", self.new_tab, "Ctrl+T")
        file_menu.addAction("Close Tab", lambda: self.close_tab(self.tabs.currentIndex()), "Ctrl+W")
        file_menu.addSeparator()
        file_menu.addAction("Quit", self.close, "Ctrl+Q")

        view_menu = mb.addMenu("View")
        view_menu.addAction("News", self._open_news)
        view_menu.addAction("Mail", self._open_email)
        view_menu.addAction("Toggle AI Panel", self.toggle_ai, "Ctrl+Shift+A")

        tools_menu = mb.addMenu("Tools")
        tools_menu.addAction("Password Manager", self._open_passwords)
        tools_menu.addAction("Account Settings", lambda: AccountDialog(self).exec())
        tools_menu.addAction("History", self._show_history)

    def new_tab(self, url="https://duckduckgo.com"):
        tab = BrowserTab(self.profile, self)
        tab.setUrl(QUrl(url))
        tab.urlChanged.connect(lambda u, t=tab: self._url_changed(u, t))
        tab.titleChanged.connect(lambda title, t=tab: self._title_changed(title, t))
        idx = self.tabs.addTab(tab, "New Tab")
        self.tabs.setCurrentIndex(idx)
        self.url_bar.setFocus()

    def close_tab(self, idx):
        if self.tabs.count() > 1:
            self.tabs.removeTab(idx)

    def _current_web(self):
        w = self.tabs.currentWidget()
        if isinstance(w, BrowserTab):
            return w
        return None

    def current_tab(self):
        return self._current_web()

    def _navigate(self):
        text = self.url_bar.text().strip()
        if not text:
            return
        if text.startswith("http://") or text.startswith("https://") or "." in text.split("/")[0]:
            if not text.startswith("http"):
                text = "https://" + text
            url = QUrl(text)
        else:
            template = SEARCH_ENGINES[self.search_engine]
            url = QUrl(template.format(urllib.parse.quote(text)))
        w = self._current_web()
        if w:
            w.setUrl(url)
        else:
            self.new_tab(url.toString())

    def open_url(self, url):
        self.new_tab(url)

    def _url_changed(self, url, tab):
        if self.tabs.currentWidget() == tab:
            self.url_bar.setText(url.toString())
        # Save history
        history = load_json(HISTORY_FILE, [])
        history.insert(0, {"url": url.toString(), "time": datetime.now().isoformat()})
        save_json(HISTORY_FILE, history[:500])

    def _title_changed(self, title, tab):
        idx = self.tabs.indexOf(tab)
        if idx >= 0:
            self.tabs.setTabText(idx, title[:24] if title else "Loading...")

    def _tab_changed(self, idx):
        w = self.tabs.widget(idx)
        if isinstance(w, BrowserTab):
            self.url_bar.setText(w.url().toString())

    def toggle_ai(self):
        self.ai_visible = not self.ai_visible
        self.ai_panel.setVisible(self.ai_visible)

    def _show_history(self):
        history = load_json(HISTORY_FILE, [])
        dlg = QDialog(self)
        dlg.setWindowTitle("History")
        dlg.setMinimumSize(500, 400)
        layout = QVBoxLayout(dlg)
        lst = QListWidget()
        for entry in history[:100]:
            item = QListWidgetItem(f"  {entry['time'][:16]}  —  {entry['url']}")
            item.setData(Qt.ItemDataRole.UserRole, entry["url"])
            lst.addItem(item)
        lst.itemDoubleClicked.connect(lambda i: (self.open_url(i.data(Qt.ItemDataRole.UserRole)), dlg.close()))
        layout.addWidget(lst)
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(lambda: (save_json(HISTORY_FILE, []), lst.clear()))
        layout.addWidget(clear_btn)
        dlg.exec()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Central Browser")
    app.setStyleSheet(QSS)
    window = CentralBrowser()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
