# gui.py
import datetime
import time
import json
import os
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon
from monitor import LogMonitor
from utils import is_match, record_alert


class LogSignal(QObject):
    new_line = pyqtSignal(str)


class MainWindow(QtWidgets.QMainWindow):
    new_alert = QtCore.pyqtSignal(dict)
    monitor_error = QtCore.pyqtSignal(str)

    # store keywords file next to this script
    KEYWORD_FILE = os.path.join(os.path.dirname(__file__), "keywords.json")

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Log Alert System")
        self.setGeometry(200, 200, 800, 500)

        # --- System Tray Setup ---
        self.tray = QtWidgets.QSystemTrayIcon(self)
        self.tray.setIcon(QIcon.fromTheme("dialog-information"))
        self.tray.setVisible(True)
        # optional: clicking a tray message will also act as a 'closed' notifier
        self.tray.messageClicked.connect(self._on_tray_message_closed)

        # --- Tray queue management ---
        self.tray_queue = []
        self.active_trays = 0
        self.max_active_trays = 2  # up to 2 popups visible at once

        self.file_path = None
        self.monitor = None
        self.keywords = []
        self.use_regex = False

        # (not currently used, kept for extensibility)
        self.signal = LogSignal()
        self.signal.new_line.connect(self.on_new_line)

        self.last_popup_time = 0

        self._build_ui()

        # Connect signals
        self.new_alert.connect(self.on_new_alert)
        self.monitor_error.connect(self.on_monitor_error)

        # Load saved keywords (if any)
        self.load_keywords()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout()

        # --- File selection ---
        file_layout = QtWidgets.QHBoxLayout()
        self.file_label = QtWidgets.QLabel("No file selected")
        select_btn = QtWidgets.QPushButton("Select File")
        select_btn.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(select_btn)

        # --- Keyword input ---
        self.kw_input = QtWidgets.QLineEdit()
        self.kw_input.setPlaceholderText("Enter keywords (comma separated)")
        self.regex_checkbox = QtWidgets.QCheckBox("Use regex")

        # --- Buttons ---
        btn_layout = QtWidgets.QHBoxLayout()
        self.start_btn = QtWidgets.QPushButton("Start")
        self.stop_btn = QtWidgets.QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.start_monitor)
        self.stop_btn.clicked.connect(self.stop_monitor)
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)

        # --- Table for alerts ---
        self.table = QtWidgets.QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Time", "Matched Line"])
        self.table.horizontalHeader().setStretchLastSection(True)

        # --- Add everything ---
        layout.addLayout(file_layout)
        layout.addWidget(self.kw_input)
        layout.addWidget(self.regex_checkbox)
        layout.addLayout(btn_layout)
        layout.addWidget(self.table)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    # ---------- Keyword persistence ----------
    def load_keywords(self):
        """Load last used keywords from KEYWORD_FILE into the input box."""
        try:
            if os.path.exists(self.KEYWORD_FILE):
                with open(self.KEYWORD_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                last_keywords = data.get("keywords")
                if isinstance(last_keywords, list) and last_keywords:
                    # set input as comma-separated text
                    self.kw_input.setText(", ".join(last_keywords))
        except Exception as e:
            # fail silently but print for debugging
            print("Failed to load keywords:", e)

    def save_keywords(self):
        """Save current keywords (self.keywords) to KEYWORD_FILE."""
        try:
            data = {"keywords": self.keywords}
            with open(self.KEYWORD_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print("Failed to save keywords:", e)

    # ---------- File selection & monitor ----------
    def select_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select log file", "", "Log files (*.log *.txt);;All files (*)"
        )
        if path:
            self.file_path = path
            self.file_label.setText(path)

    def start_monitor(self):
        """Scan full log first, then start live monitoring."""
        if not self.file_path:
            QtWidgets.QMessageBox.warning(self, "No file", "You have to select a log file first.")
            return

        kws = [k.strip() for k in self.kw_input.text().split(",") if k.strip()]
        if not kws:
            QtWidgets.QMessageBox.warning(
                self, "No keywords", "Enter at least one keyword (comma separated)."
            )
            return

        self.keywords = kws
        # persist last used keywords
        self.save_keywords()

        self.use_regex = self.regex_checkbox.isChecked()

        # --- Step 1: Scan full existing log file ---
        try:
            with open(self.file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    matched, which = is_match(line, self.keywords, use_regex=self.use_regex)
                    if matched:
                        alert = {
                            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "keyword": which,
                            "line": line.strip(),
                        }
                        record_alert(alert)
                        self.new_alert.emit(alert)
                        # process events so the UI updates during long scans
                        QtWidgets.QApplication.processEvents()
                        # small sleep to avoid spamming too-fast CPU/tray
                        time.sleep(0.1)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Read Error", str(e))
            return

        # --- Step 2: Start live monitoring ---
        self.monitor = LogMonitor(
            self.file_path, on_line=self._on_line, on_error=self._on_error
        )
        self.monitor.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_monitor(self):
        if self.monitor:
            self.monitor.stop()
            self.monitor = None
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

    # ---------- Monitor callbacks ----------
    def _on_line(self, line):
        matched, which = is_match(line, self.keywords, use_regex=self.use_regex)
        if matched:
            alert = {
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "keyword": which,
                "line": line.strip(),
            }
            record_alert(alert)
            self.new_alert.emit(alert)

    def _on_error(self, message):
        self.monitor_error.emit(message)

    # ---------- GUI handlers ----------
    def on_new_line(self, line):
        # kept for future use; currently not used
        pass

    def on_new_alert(self, alert):
        """Handle new alerts (table + tray popup queue)."""
        # audible feedback
        QtWidgets.QApplication.beep()

        # add to table
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(alert["time"]))
        self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(alert["line"]))

        # enqueue alert for tray popups
        self.tray_queue.append(alert)
        self._process_tray_queue()

    def _process_tray_queue(self):
        """Show up to max_active_trays popups at once; queue the rest."""
        while self.active_trays < self.max_active_trays and self.tray_queue:
            alert = self.tray_queue.pop(0)
            self.active_trays += 1
            # show notification
            self.tray.showMessage(
                "⚠️ Log Alert Detected",
                f"Keyword: {alert['keyword']}\n{alert['line']}",
                QtWidgets.QSystemTrayIcon.Information,
                5000,
            )
            # after popup duration + small buffer, mark it closed and process next
            QtCore.QTimer.singleShot(5500, self._on_tray_message_closed)

    def _on_tray_message_closed(self):
        """Called after popup closes — show next in queue."""
        if self.active_trays > 0:
            self.active_trays -= 1
        # process next queued items (if any)
        self._process_tray_queue()

    def on_monitor_error(self, message):
        QtWidgets.QMessageBox.critical(self, "Monitor error", message)
