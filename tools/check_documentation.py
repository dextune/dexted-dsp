#!/usr/bin/env python3
"""Offline checks for four-language documentation and archived result tables.

Checks files, shared numeric evidence and Python snippet syntax. It does not judge
translation quality, execute arbitrary snippets, check external URLs or prove math.
"""
from __future__ import annotations
import ast
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ("en", "ko", "zh-CN", "ja")
SECTIONS = {"BENCHMARKS":"benchmarks", "MATHEMATICS":"mathematics", "PROVENANCE":"development", "RELEASING":"development", "TESTING":"guides", "USER_GUIDE":"getting-started"}
KINDS = ("PROVENANCE", "BENCHMARKS", "USER_GUIDE", "TESTING", "MATHEMATICS", "RELEASING")
METHODS = ("integer", "grid1024", "grid16384", "float64_algebraic")


def check() -> dict:
    result_path = ROOT / "benchmarks/results/benchmark.json"
    data = json.loads(result_path.read_text(encoding="utf-8"))
    digest = hashlib.sha256(result_path.read_bytes()).hexdigest()
    marker = f"<!-- benchmark-sha256: {digest} -->"
    failures = []
    snippets = 0
    documents = 0
    numeric_rows = 0
    for locale in LOCALES:
        files = [ROOT/f"docs/{locale}/README.md"] + [ROOT/f"docs/{locale}/{SECTIONS[kind]}/{kind}.md" for kind in KINDS]
        for file in files:
            if not file.is_file():
                failures.append(f"Missing {file.relative_to(ROOT)}")
                continue
            documents += 1
            text = file.read_text(encoding="utf-8")
            if "@@" in text:
                failures.append(f"Unexpanded template: {file.relative_to(ROOT)}")
            if file.name == "BENCHMARKS.md" or file.name.startswith("README"):
                if marker not in text:
                    failures.append(f"Benchmark identity: {file.relative_to(ROOT)}")
                for family in data["families"].values():
                    m = family["median_us"]
                    cells = [f"{m[k]:.6f}" for k in METHODS]
                    cells.append(f"{m['grid1024']/m['integer']:.3f}×")
                    if " | ".join(cells) not in text:
                        failures.append(f"Latency row missing: {file.relative_to(ROOT)}")
                    numeric_rows += 1
                for c in data["families"]["high_q"]["correctness"].values():
                    if f"| {c['false_accepts']} | {c['false_rejects']} |" not in text:
                        failures.append(f"Correctness row: {file.relative_to(ROOT)}")
            for match in re.finditer(r"^```python\s*\n(.*?)^```", text, re.M | re.S):
                snippets += 1
                try:
                    ast.parse(match.group(1), filename=str(file))
                except SyntaxError as exc:
                    failures.append(f"Snippet syntax {file.relative_to(ROOT)}: {exc}")
            if "adc7f1241b42e322a6451854ab7e4b4c146bf78a" not in text:
                failures.append(f"Missing pinned reference: {file.relative_to(ROOT)}")
    # README.md is deliberately a short landing page. Full documentation lives under docs/.
    if not (ROOT/"README.md").is_file():
        failures.append("Missing GitHub landing README")
    with (ROOT/"benchmarks/results/summary.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != len(data["families"])*len(METHODS):
        failures.append("CSV row count")
    for row in rows:
        family = data["families"][row["family"]]
        method = row["method"]
        values = {
            "n": family["n"], "exact_pass": family["exact_pass"],
            "median_us_per_filter": family["median_us"][method],
            "min_us_per_filter": min(family["raw_us_per_filter"][method]),
            "max_us_per_filter": max(family["raw_us_per_filter"][method]),
            "false_accepts": family["correctness"][method]["false_accepts"],
            "false_rejects": family["correctness"][method]["false_rejects"],
        }
        for key, value in values.items():
            if float(row[key]) != value:
                failures.append(f"CSV {row['family']}/{method}/{key}")
    if failures:
        raise ValueError("; ".join(failures))
    return {"status":"passed", "languages":list(LOCALES), "primary_documents":documents,
            "checked_python_snippets":snippets, "latency_rows_checked":numeric_rows,
            "csv_rows_checked":len(rows), "benchmark_sha256":digest,
            "note":"Document structure/data consistency only; not a translation review or mathematical proof."}

if __name__ == "__main__":
    try:
        print(json.dumps(check(), indent=2, ensure_ascii=False))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status":"failed", "error":str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
