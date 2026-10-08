#!/usr/bin/env python3
"""SciPy/python-control BEFORE vs the same sampler PLUS verified Dexted proof.

Numerical sampling is an estimate, never a certificate. Fixed, predeclared
synthetic fixtures; no inference about prevalence in production deployments.
"""
from __future__ import annotations

import argparse
import base64
import gc
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import random
import statistics
import sys
import time
import tracemalloc
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "benchmarks/suites/fixtures/designed_sos_pilot_v1.json"
# All IDs chosen before inspecting outcomes. Keep both favorable/unfavorable.
CASE_IDS = (
    "butter-lowpass-2-0.02", "butter-lowpass-4-0.12",
    "cheby1-lowpass-4-0.2", "ellip-lowpass-4",
    "iirpeak-0.01-100", "iirpeak-0.49-10000",
    "hidden-peak-adversarial", "compensating-two-sections",
    "strict-unity-boundary",
)
METHODS = ("scipy_before", "scipy_after", "control_before",
           "control_after", "dexted_certification_only")
FAMILIES = ("ordinary-iir", "high-q", "critical-gain", "designed-case")
VERSION = "dexted-dsp/competitive-benchmark/v1"


def q(values, percentage):
    values = sorted(values)
    point = (len(values) - 1) * percentage / 100
    low = int(math.floor(point))
    high = int(math.ceil(point))
    return float(values[low] + (values[high] - values[low]) * (point - low))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def family_of(case):
    name = case["id"]
    if name.startswith("butter") or name.startswith("cheby"):
        return "ordinary-iir"
    if name.startswith("iirpeak") or name == "hidden-peak-adversarial":
        return "high-q"
    if name in ("strict-unity-boundary", "compensating-two-sections"):
        return "critical-gain"
    return "designed-case"


def stability_numerical(sos):
    # A numeric precondition shared by BOTH existing-grid workflows.
    # This is NOT an independent exact stability certificate.
    for b0, b1, b2, a0, a1, a2 in sos:
        if a0 != 1.0 or not (abs(a2) < 1.0 and
                              1 + a1 + a2 > 0 and 1 - a1 + a2 > 0):
            return False
    return True


def discrete_tf(sos, np, ct):
    # SOS H(z)=B(z^-1)/A(z^-1); multiply by z^(2N) for ct.tf(...,dt=1).
    # Prebuilt as a one-time reusable TF, NOT charged to either control path.
    numerator = np.array([1.0])
    denominator = np.array([1.0])
    for row in sos:
        numerator = np.convolve(numerator, row[:3])
        denominator = np.convolve(denominator, row[3:])
    return ct.tf(numerator, denominator, 1)


def run(*, trials=30, memory_trials=30, seed=20261008, case_ids=CASE_IDS):
    import numpy as np
    import scipy
    from scipy import signal
    import control as ct
    import sympy
    from dexted_dsp import from_sos, certify_cascade, verify_cascade
    sys.path.insert(0, str(ROOT / "tools"))
    from sympy_oracle_audit import oracle_verdict

    if trials < 30 or memory_trials < 30:
        raise ValueError("published measurements require >=30 trials for time AND memory")
    archive = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert archive["schema"] == "dexted-dsp/designed-sos-pilot/v1"
    by_id = {c["id"]: c for c in archive["cases"]}
    if len(case_ids) != len(set(case_ids)) or any(x not in by_id for x in case_ids):
        raise ValueError("unrecognized or duplicate case ID")
    rng = random.Random(seed)
    omega = np.linspace(0.0, np.pi, 1024, dtype=np.float64)  # inclusive
    records = []
    for name in case_ids:
        c = by_id[name]
        sos = np.asarray(c["sos"], dtype=np.float64)
        if not np.array_equal(sos, sos.astype(np.float32).astype(np.float64)):
            raise AssertionError("input not already represented binary32: " + name)
        rows = from_sos(sos, precision="float32")
        limit = float(c["max_gain"])
        truth = oracle_verdict(c["sos"], limit)  # SymPy exact QQ, closed root interval
        system = discrete_tf(sos, np, ct)
        valid = stability_numerical(sos)

        def numeric(backend):
            if not valid:
                return False
            if backend == "scipy":
                magnitude = np.abs(signal.freqz_sos(sos, worN=omega)[1])
            else:
                magnitude = np.asarray(ct.frequency_response(system, omega).magnitude)
            return bool(np.all(np.isfinite(magnitude)) and
                        np.max(magnitude) < limit)

        def proof_gate():
            cert = certify_cascade(rows, limit, max_depth=32, max_nodes=5000)
            if cert["status"] == "unknown":
                return False
            if cert["certified"]:
                if not verify_cascade(cert, rows, limit):
                    raise AssertionError("Dexted certificate failed independent verifier: " + name)
                return True
            return False

        functions = {
            "scipy_before": lambda: numeric("scipy"),
            "scipy_after": lambda: (numeric("scipy"), proof_gate()),
            "control_before": lambda: numeric("control"),
            "control_after": lambda: (numeric("control"), proof_gate()),
            "dexted_certification_only": proof_gate,
        }

        def verdict(method):
            answer = functions[method]()
            return (bool(answer[0] and answer[1])
                    if isinstance(answer, tuple) else bool(answer))

        expected = truth == "certified"
        decisions = {m: verdict(m) for m in METHODS}
        if decisions["dexted_certification_only"] != expected:
            raise AssertionError("exact oracle vs Dexted mismatch " + name)
        for backend in ("scipy", "control"):
            if decisions[backend + "_after"] != (
                decisions[backend + "_before"] and expected):
                raise AssertionError("After is not conjunction of baseline and proof")
        for func in functions.values():
            func()  # warm up, never time imports or fixture construction
        timings = {m: [] for m in METHODS}
        for _ in range(trials):
            order = list(METHODS)
            rng.shuffle(order)
            for method in order:
                begin = time.perf_counter_ns()
                verdict(method)
                timings[method].append((time.perf_counter_ns() - begin) / 1e6)
        # Tracemalloc measures Python allocations only; native buffers omitted.
        # Do not mix instrumented calls into wall-time samples.
        memory = {m: [] for m in METHODS}
        for _ in range(memory_trials):
            order = list(METHODS)
            rng.shuffle(order)
            for method in order:
                gc.collect()
                tracemalloc.start()
                tracemalloc.reset_peak()
                verdict(method)
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                memory[method].append(round(peak / 1024, 6))
        records.append({
            "id": name, "family": family_of(c), "original_family": c["family"],
            "fixture_split": c["split"], "sections": len(sos), "gain_limit": limit,
            "sos": c["sos"], "oracle_verdict": truth, "oracle_pass": expected,
            "decisions": decisions, "raw_ms": timings, "raw_python_peak_kib": memory,
        })
        print("CASE_COMPLETE " + name + " " + json.dumps(decisions), flush=True)

    sums = {}
    for method in METHODS:
        values = [x for c in records for x in c["raw_ms"][method]]
        mem = [x for c in records for x in c["raw_python_peak_kib"][method]]
        sums[method] = {
            "p50_ms": round(q(values, 50), 6),
            "p95_ms": round(q(values, 95), 6),
            "peak_python_kib_p50": round(q(mem, 50), 6),
            "false_accepts": sum(c["decisions"][method] and not c["oracle_pass"] for c in records),
            "false_rejects": sum(not c["decisions"][method] and c["oracle_pass"] for c in records),
            "pass": sum(c["decisions"][method] for c in records),
            "observations_time": len(values),
            "observations_memory": len(mem),
        }
    cpu = ""
    if Path("/proc/cpuinfo").exists():
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                cpu = line.split(":", 1)[1].strip()
                break
    env = {
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(), "cpu_model": cpu,
        "logical_cpu_count": os.cpu_count(), "python": sys.version,
        "numpy": np.__version__, "scipy": scipy.__version__,
        "python_control": ct.__version__, "sympy": sympy.__version__,
        "github_sha": os.getenv("GITHUB_SHA"), "github_run_id": os.getenv("GITHUB_RUN_ID"),
        "openblas_num_threads": os.getenv("OPENBLAS_NUM_THREADS"),
        "omp_num_threads": os.getenv("OMP_NUM_THREADS"),
        "machine_pinning": "not configured, CI shared runner", "native_memory_captured": False,
    }
    return {
        "schema": VERSION, "population": "9 PRESELECTED SYNTHETIC cases, not field prevalence",
        "environment": env,
        "inputs": {
            "fixture": str(FIXTURE.relative_to(ROOT)), "fixture_sha256": sha(FIXTURE),
            "run_source_sha256": sha(__file__),
            "oracle_source_sha256": sha(ROOT / "tools/sympy_oracle_audit.py"),
            "case_ids_in_order": list(case_ids), "precision": "IEEE754 binary32 stored exactly in float64",
            "frequency_grid_rad_per_sample": "numpy.linspace(0, pi, 1024) inclusive",
            "gain_test": "strict < threshold", "stability_precheck": "numeric Jury, both samplers",
            "oracle": "independent SymPy exact rational root counting on closed [-1,1]",
            "sampling_is_certificate": False, "control_tf_preconstructed": True,
            "control_tf_note": "convolution to z-domain transfer-function polynomial; conversion excluded from timing",
            "warmup_per_method": 2, "timer": "perf_counter_ns",
            "trials": trials, "memory_trials": memory_trials, "seed": seed,
            "proof": "certify_cascade plus verify_cascade on certified PASS; UNKNOWN is fail-closed",
            "memory_scope": "Python-traced peak KiB per invocation, omits NumPy/C native allocations",
        },
        "summary": sums, "cases": records,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--trials", type=int, default=30)
    parser.add_argument("--memory-trials", type=int, default=30)
    parser.add_argument("--seed", type=int, default=20261008)
    parser.add_argument("--emit", action="store_true",
                        help="Print base64 JSON for lossless capture in CI logs")
    args = parser.parse_args()
    if args.out.exists():
        parser.error("refusing to overwrite " + str(args.out))
    data = run(trials=args.trials, memory_trials=args.memory_trials, seed=args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(data, indent=2, ensure_ascii=True, allow_nan=False) + "\n").encode()
    args.out.write_bytes(raw)
    print("BENCHMARK_SUMMARY_JSON=" + json.dumps(data["summary"], separators=(",", ":")))
    print("BENCHMARK_ENV_JSON=" + json.dumps(data["environment"], separators=(",", ":")))
    if args.emit:
        print("BENCHMARK_PAYLOAD_BASE64=" + base64.b64encode(raw).decode("ascii"))


if __name__ == "__main__":
    main()
