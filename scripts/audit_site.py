"""Verify all local asset references in HTML resolve to existing files."""
import re
from pathlib import Path
from urllib.parse import unquote

from _paths import SITE_ROOT

html_files = list(SITE_ROOT.rglob("*.html"))
missing = []

for hf in html_files:
    text = hf.read_text(encoding="utf-8", errors="ignore")
    for m in re.findall(r'(?:src|href)="([^"]+)"', text):
        if m.startswith(("http://", "https://", "mailto:", "tel:", "javascript:", "data:")):
            continue
        if m.startswith("#"):
            continue

        ref = unquote(m.split("#", 1)[0].split("?", 1)[0])
        if not ref or ref.endswith(".html"):
            continue

        fp = (hf.parent / ref).resolve()
        if not fp.exists():
            fp = (SITE_ROOT / ref.lstrip("./")).resolve()

        if not fp.exists():
            missing.append((hf.relative_to(SITE_ROOT).as_posix(), m))

print("BROKEN_REFS", len(missing))
for row in missing[:30]:
    print(row)
