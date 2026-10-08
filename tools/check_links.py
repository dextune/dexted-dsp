#!/usr/bin/env python3
"""Check local Markdown links and image targets; no network calls.

Anchors and external URLs are not fetched or semantically validated.
Code-fenced example links are not part of this check.
"""
from pathlib import Path
import re
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
SKIP = {'build','dist','.venv','.wheel-test','local-install','.git','__pycache__','archive'}
missing = []
checked = 0
for file in ROOT.rglob('*.md'):
    rel = file.relative_to(ROOT)
    if any(p in SKIP or p.endswith('.egg-info') for p in rel.parts):
        continue
    text = file.read_text(encoding='utf-8')
    text = re.sub(r'^```[^\n]*\n.*?^```[^\n]*$', '', text, flags=re.M|re.S)
    targets = re.findall(r'\]\(([^)]+)\)', text)
    targets += re.findall(r'^\[[^\]]+\]:\s*(\S+)', text, flags=re.M)
    for raw in targets:
        link = raw.split()[0].strip('<>')
        if '://' in link or link.startswith(('#', 'mailto:')):
            continue
        path = unquote(link.split('#',1)[0])
        if not path:
            continue
        checked += 1
        if not (file.parent/path).exists():
            missing.append((str(rel),link))
for file, link in missing:
    print(f'MISSING {file}: {link}')
print(f'{checked} local links checked; {len(missing)} missing; external URLs/anchors not tested')
raise SystemExit(bool(missing))
