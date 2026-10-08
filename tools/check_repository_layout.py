#!/usr/bin/env python3
"""Prevent regression from Dexted DSP's documentation-first repository layout.

This checks *source layout*, not algorithmic proofs or external links.
Temporary build directories are ignored.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = {"README.md", "LICENSE", "CITATION.cff", "pyproject.toml", "CMakeLists.txt", "MANIFEST.in", ".gitignore", ".gitattributes"}
ROOT_DIRS = {".github", "docs", "src", "cpp", "tests", "tools", "examples", "benchmarks", "validation"}
GENERATED_DIRS = {".git", ".venv", ".wheel-test", ".pytest_cache", "build", "dist", "local-install", "_build", "__pycache__"}
LANGS = ("en", "ko", "zh-CN", "ja")
SECTIONS = {"getting-started": "USER_GUIDE.md", "guides": "TESTING.md", "benchmarks": "BENCHMARKS.md", "mathematics": "MATHEMATICS.md", "development": "PROVENANCE.md"}

def check():
    files = {p.name for p in ROOT.iterdir() if p.is_file()}
    folders = {p.name for p in ROOT.iterdir() if p.is_dir() and p.name not in GENERATED_DIRS and not p.name.endswith('.egg-info')}
    failures=[]
    if files!=ROOT_FILES:
        failures.append(f'root files: unexpected={sorted(files-ROOT_FILES)}, missing={sorted(ROOT_FILES-files)}')
    if folders!=ROOT_DIRS:
        failures.append(f'root folders: unexpected={sorted(folders-ROOT_DIRS)}, missing={sorted(ROOT_DIRS-folders)}')
    for lang in LANGS:
        for path in [f'docs/{lang}/README.md', f'docs/{lang}/development/RELEASING.md']+[f'docs/{lang}/{name}/{file}' for name,file in SECTIONS.items()]:
            if not (ROOT/path).is_file(): failures.append('missing: '+path)
    for path in ('docs/README.md','docs/reference/README.md','docs/research/README.md', 'docs/project/README.md', '.github/CONTRIBUTING.md','.github/SECURITY.md', 'docs/legal/NOTICE.md'):
        if not (ROOT/path).is_file(): failures.append('missing: '+path)
    if len((ROOT/'README.md').read_bytes())>8000:
        failures.append('root README should be a concise landing page')
    if failures: raise ValueError('; '.join(failures))
    return {'status':'passed','root_file_count':len(files),'root_folder_count':len(folders),'languages':list(LANGS)}

if __name__=='__main__':
    print(json.dumps(check(), indent=2))
