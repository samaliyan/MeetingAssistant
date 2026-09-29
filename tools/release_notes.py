"""Prints the CHANGELOG.md section of one version (the text of its GitHub Release)."""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
version = sys.argv[1] if len(sys.argv) > 1 else ""
text = open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8").read()
m = re.search(rf"^## \[?{re.escape(version)}\]?(?![\w.])[^\n]*$(.*?)(?=^## |\Z)", text, re.M | re.S)
if not m or not m.group(1).strip():
    sys.exit(f"CHANGELOG.md has no section for version {version} - add it before releasing")
body = m.group(1).strip()
sys.stdout.reconfigure(encoding="utf-8")
print(body + "\n\nDownload **MeetingAssistant.exe**, put it in its own folder and run it. "
      "Full guide: Guide-EN.md (English) or Guide-FA.md (Persian).")
