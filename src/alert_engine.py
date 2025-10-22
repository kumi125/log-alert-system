# alert_engine.py
import re
from pathlib import Path
from datetime import datetime




def is_match(line, keywords, use_regex=False):
"""Return (matched: bool, matched_keyword_or_pattern: str|None).


- If use_regex==False: keywords are treated as plain substrings (case-insensitive).
- If use_regex==True: keywords are treated as regex patterns and tested with IGNORECASE.
"""
if line is None:
return False, None
if use_regex:
for pat in keywords:
try:
if re.search(pat, line, re.IGNORECASE):
return True, pat
except re.error:
# skip invalid regex
continue
return False, None


# plain substring, case-insensitive
lower = line.lower()
for kw in keywords:
if kw.lower() in lower:
return True, kw
return False, None




def record_alert(alert, alerts_file="alerts.txt"):
"""Append an alert dict to the alerts file.


alert should contain at least: {"time": str, "keyword": str, "line": str}
"""
p = Path(alerts_file)
line = f"[{alert.get('time')}] {alert.get('keyword')} - {alert.get('line')}\n"
with p.open("a", encoding="utf-8") as fh:
fh.write(line)