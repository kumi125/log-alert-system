# monitor.py
import threading
import time


class LogMonitor(threading.Thread):
    """
    A simple tail-like file monitor that calls `on_line(line)` for each new line.
    It runs in its own thread and can be stopped gracefully.
    """

    def __init__(self, file_path, on_line=None, on_error=None, interval=1.0):
        super().__init__(daemon=True)
        self.file_path = file_path
        self.on_line = on_line
        self.on_error = on_error
        self.interval = interval
        self._stop_event = threading.Event()

    def stop(self):
        """Stop the monitoring thread."""
        self._stop_event.set()

    def run(self):
        """Continuously monitor the log file for new lines."""
        try:
            with open(self.file_path, "r") as file:
                # Move to the end of file
                file.seek(0, 2)
                while not self._stop_event.is_set():
                    line = file.readline()
                    if not line:
                        time.sleep(self.interval)
                        continue
                    print("[DEBUG] New line detected:", line.strip())    
                    if self.on_line:
                        self.on_line(line.strip())
        except Exception as e:
            if self.on_error:
                self.on_error(str(e))
