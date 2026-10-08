#!/usr/bin/env python3
"""Fail closed if competitive results conceal trials, truth, scope or provenance."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks/competitive"))
from run import CASE_IDS, METHODS, VERSION, q


def audit(path, archived=False, oracle_recheck=False):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data["schema"] != VERSION:
        raise AssertionError("schema mismatch")
    inputs = data["inputs"]
    if inputs["case_ids_in_order"] != list(CASE_IDS):
        raise AssertionError("predeclared fixture membership changed")
    if inputs["trials"] < 30 or inputs["memory_trials"] < 30:
        raise AssertionError("fewer than 30 repeats")
    if inputs["sampling_is_certificate"] is not False or data["environment"]["native_memory_captured"] is not False:
        raise AssertionError("misleading claim of proof or complete RSS")
    for key, file in (
        ("fixture_sha256", ROOT / inputs["fixture"]),
        ("run_source_sha256", ROOT / "benchmarks/competitive/run.py"),
        ("oracle_source_sha256", ROOT / "tools/sympy_oracle_audit.py"),
    ):
        if inputs[key] != hashlib.sha256(file.read_bytes()).hexdigest():
            raise AssertionError("hash drift: " + key)
    ids = [c["id"] for c in data["cases"]]
    if ids != list(CASE_IDS) or len(set(ids)) != len(CASE_IDS):
        raise AssertionError("case removed, added or reordered")
    for case in data["cases"]:
        fixture = {c["id"]: c for c in json.loads((ROOT / inputs["fixture"]).read_text())["cases"]}[case["id"]]
        if case["sos"] != fixture["sos"] or case["gain_limit"] != fixture["max_gain"] or case["fixture_split"] != fixture["split"]:
            raise AssertionError("case coefficients, threshold or split differ from frozen fixture")
        if case["oracle_pass"] != (case["oracle_verdict"] == "certified"):
            raise AssertionError("oracle truth mismatch")
        if archived and oracle_recheck:
            sys.path.insert(0, str(ROOT / "tools"))
            from sympy_oracle_audit import oracle_verdict
            if oracle_verdict(case["sos"], case["gain_limit"]) != case["oracle_verdict"]:
                raise AssertionError("published oracle truth does not match independent root counter")
        d = case["decisions"]
        if set(d) != set(METHODS):
            raise AssertionError("missing method")
        if d["dexted_certification_only"] != case["oracle_pass"]:
            raise AssertionError("Dexted disagrees with exact oracle")
        for backend in ("scipy", "control"):
            if d[backend + "_after"] != (d[backend + "_before"] and case["oracle_pass"]):
                raise AssertionError("After must preserve the baseline decision AND add exact proof")
        for m in METHODS:
            for field, n in (("raw_ms", inputs["trials"]), ("raw_python_peak_kib", inputs["memory_trials"])):
                values = case[field][m]
                if len(values) != n or not all(type(x) in (int, float) and math.isfinite(x) and x >= 0 for x in values):
                    raise AssertionError("missing, negative or nonfinite measurements")
    for m in METHODS:
        s = data["summary"][m]
        values = [v for c in data["cases"] for v in c["raw_ms"][m]]
        mem = [v for c in data["cases"] for v in c["raw_python_peak_kib"][m]]
        expected = {
            "p50_ms": round(q(values, 50), 6),
            "p95_ms": round(q(values, 95), 6),
            "peak_python_kib_p50": round(q(mem, 50), 6),
            "false_accepts": sum(c["decisions"][m] and not c["oracle_pass"] for c in data["cases"]),
            "false_rejects": sum(not c["decisions"][m] and c["oracle_pass"] for c in data["cases"]),
            "pass": sum(c["decisions"][m] for c in data["cases"]),
            "observations_time": len(values),
            "observations_memory": len(mem),
        }
        if s != expected:
            raise AssertionError("summary != raw measurements for " + m)
    if archived and inputs["trials"] != 30:
        raise AssertionError("published evidence requires the predeclared 30-trial protocol")
    return {"result": "PASS", "cases": len(ids), "trials_per_method": inputs["trials"],
            "memory_repeats_per_method": inputs["memory_trials"],
            "false_accepts": {m: data["summary"][m]["false_accepts"] for m in METHODS},
            "published": archived}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("result", type=Path)
    p.add_argument("--archived", action="store_true")
    p.add_argument("--recheck-oracle", action="store_true")
    a = p.parse_args()
    print(json.dumps(audit(a.result, a.archived, a.recheck_oracle), indent=2))
