# utils.py
import re
import json
import os

ALERTS_FILE = "alerts.json"


def is_match(line, keywords, use_regex=False):
    """
    Check if a line matches any of the provided keywords.
    Returns (True, keyword) if a match is found, else (False, None).
    """
    for kw in keywords:
        if use_regex:
            if re.search(kw, line):
                return True, kw
        else:
            if kw.lower() in line.lower():
                return True, kw
    return False, None


def record_alert(alert):
    """
    Save the alert into alerts.json (simple persistent log).
    """
    alerts = []

    if os.path.exists(ALERTS_FILE):
        try:
            with open(ALERTS_FILE, "r") as f:
                alerts = json.load(f)
        except Exception:
            alerts = []

    alerts.append(alert)

    with open(ALERTS_FILE, "w") as f:
        json.dump(alerts, f, indent=2)
