import sys
import time
import threading
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QFileDialog, QLabel, QMessageBox, QLineEdit, QHBoxLayout
)
from PyQt5.QtCore import pyqtSignal, QObject, QTimer
import winsound
from datetime import datetime
from collections import deque


class AlertHandler(QObject):
    trigger_alert = pyqtSignal(str)


class LogAlertApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛡️ Log Alert System")
        self.setGeometry(200, 200, 500, 220)

        self.log_file = ""
        self.alert_log_file = ""
        self.keywords = []
        self.last_position = 0
        self.monitoring = False

        self.alert_handler = AlertHandler()
        self.alert_handler.trigger_alert.connect(self.queue_alert)

        self.alert_queue = deque()
        self.alert_showing = False

        # UI Elements
        self.label = QLabel("No log file selected.")
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Enter keywords, separated by commas")

        self.set_keywords_btn = QPushButton("Set Keywords")
        self.select_file_btn = QPushButton("Select Log File")
        self.start_btn = QPushButton("Start Monitoring")

        self.set_keywords_btn.clicked.connect(self.set_keywords)
        self.select_file_btn.clicked.connect(self.select_file)
        self.start_btn.clicked.connect(self.start_monitoring)

        layout = QVBoxLayout()
        layout.addWidget(self.label)

        keyword_layout = QHBoxLayout()
        keyword_layout.addWidget(self.keyword_input)
        keyword_layout.addWidget(self.set_keywords_btn)

        layout.addLayout(keyword_layout)
        layout.addWidget(self.select_file_btn)
        layout.addWidget(self.start_btn)
        self.setLayout(layout)

    def set_keywords(self):
        user_input = self.keyword_input.text()
        if user_input.strip():
            self.keywords = [k.strip().lower() for k in user_input.split(",")]
            QMessageBox.information(self, "Keywords Set",
                                    f"Monitoring for: {', '.join(self.keywords)}")

    def select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Log File", "", "Log Files (*.log *.txt)")
        if file_name:
            self.log_file = file_name
            self.alert_log_file = os.path.join(os.path.dirname(file_name), "alerts.txt")
            self.label.setText(f"Selected: {os.path.basename(file_name)}")
            self.last_position = 0

    def start_monitoring(self):
        if not self.log_file:
            QMessageBox.warning(self, "Error", "Please select a log file first.")
            return
        if not self.keywords:
            QMessageBox.warning(self, "Error", "Please enter keywords to monitor.")
            return
        if not self.monitoring:
            self.monitoring = True
            threading.Thread(target=self.monitor_log, daemon=True).start()
            self.start_btn.setText("Monitoring...")

    def monitor_log(self):
        while self.monitoring:
            try:
                with open(self.log_file, "r") as f:
                    f.seek(self.last_position)
                    new_lines = f.readlines()
                    self.last_position = f.tell()

                    for line in new_lines:
                        for keyword in self.keywords:
                            if keyword in line.lower():
                                self.save_alert(line.strip())
                                self.alert_handler.trigger_alert.emit(line.strip())
                                break
            except Exception as e:
                print(f"[ERROR] {e}")
            time.sleep(1)

    def queue_alert(self, message):
        self.alert_queue.append(message)
        if not self.alert_showing:
            self.show_next_alert()

    def show_next_alert(self):
        if self.alert_queue:
            self.alert_showing = True
            message = self.alert_queue.popleft()
            winsound.Beep(1000, 500)
            alert = QMessageBox(QMessageBox.Warning, "Suspicious Log Detected", message)
            alert.setStandardButtons(QMessageBox.Ok)
            alert.buttonClicked.connect(self.alert_closed)
            alert.exec_()

    def alert_closed(self):
        self.alert_showing = False
        QTimer.singleShot(100, self.show_next_alert)  # Delay before showing next popup

    def save_alert(self, line):
        if self.alert_log_file:
            with open(self.alert_log_file, "a") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {line}\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LogAlertApp()
    window.show()
    sys.exit(app.exec_())
