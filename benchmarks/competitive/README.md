# Competitive benchmark protocol v1

**Different contracts:** SciPy `signal.freqz_sos` and python-control
`control.frequency_response` numerically evaluate a fixed frequency grid;
Dexted DSP additionally verifies a strict, ideal fixed-coefficient, whole-band
gain condition. The latter is a correctness check, **not a faster FFT/response
engine or a proof of implementation/device runtime roundoff**.

Population is **nine predeclared, synthetic** cases from
[`designed_sos_pilot_v1.json`](../suites/fixtures/designed_sos_pilot_v1.json):
ordinary Butterworth/Chebyshev; high-Q and purposely hidden peak; threshold
unity and two-section compensation; and an elliptic design. These are not
production defect rates. The complete original fixture IDs are declared in
`run.py`, and an audit fails if cases are dropped. At least one negative and
one positive case must be retained even when the results are unfavorable.

## Reproduction

Use Python 3.13 on Linux with actual installed competitors. On a fresh checkout:

```bash
python -m pip install . 'numpy==2.3.5' 'scipy==1.17.0' 'control==0.10.2' 'sympy==1.14.0'
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python benchmarks/competitive/run.py --out validation/competitive-local.json --trials 30 --memory-trials 30
python tools/audit_competitive.py validation/competitive-local.json
```

The script refuses to overwrite earlier evidence. CI runs this protocol with
30 untrimmed wall-time and 30 separate Python allocation observations **for
each case/method**; it independently computes the exact mathematical oracle
via SymPy QQ polynomial real-root counting. Performance is measured using
`perf_counter_ns`; Python-traced peaks are measured with `tracemalloc`
outside the timing loop and **exclude native NumPy/C buffers and full RSS**.
Both samplers evaluate the identical **1024-point inclusive grid** in radians,
with represented binary32 SOS rows carried losslessly in binary64; control's
preconstructed z-transfer polynomial excludes model-conversion time. Both
Before and After use the same frequency-response function and float Jury
precheck; After *always* adds `certify_cascade` and PASS verifier
`verify_cascade`. Unknown is fail-closed. Functionality is **not equivalent**
because no finite numeric sample establishes the full-band claim.

Combined wall times can vary with shared-host noise, CPU, versions and input
order, so **no general-purpose speedup is inferred**. All raw time and peak
allocation samples, direct decisions, environment, immutable fixture digest,
benchmark source/oracle hashes, selected IDs and summary are retained in
[`results/run-20261008.json`](results/run-20261008.json) in this versioned evidence release.
Results correspond to ONE GitHub Actions host, not independent external
reproduction; separate hardware and 1,000+ holdout production-grade filters
remain outside this pilot. Archived v0.1.0 results are not overwritten.

[Python-traced allocation chart](figures/memory.svg) · [Mobile allocation chart](figures/memory-mobile.svg) · [Verified timing chart](figures/runtime.svg)

## Observed run: 2026-10-08 (single shared runner)

Actual tested versions: SciPy 1.17.0, python-control 0.10.2, NumPy 2.3.5,
SymPy 1.14.0, Python 3.13.15, AMD EPYC 7763 Linux (2 logical vCPUs exposed).
Time and Python-heap allocation are each recorded **30 times per case/method**;
9 filters × 30 repetitions = 270 observations per method per type.

| Same coefficients, 1024 samples, strict limit | False PASS | False FAIL | Wall p50 / p95 (ms) | Python peak KiB p50 |
|---|---:|---:|---:|---:|
| SciPy `freqz_sos` BEFORE | 1 | 0 | 0.230 / 0.387 | 91.22 |
| SciPy + verified Dexted AFTER | **0** | 0 | 1.258 / 3.399 | 91.22 |
| python-control `frequency_response` BEFORE | 1 | 0 | 0.217 / 0.266 | 122.45 |
| control + verified Dexted AFTER | **0** | 0 | 1.142 / 3.277 | 122.45 |
| Verified Dexted-only certificate | 0 | 0 | 0.897 / 3.034 | 8.09 |

**Cost:** the median total Before→After wall-time rises by **1.028 ms**
for SciPy and **0.925 ms** for control (difference of medians, NOT paired
mean overhead). The two numerical false PASS counts concern **the same single
constructed hidden-peak case**, not two distinct defective filters. At an exact
unity boundary all methods correctly reject; there were no false FAIL cases
in this small selected population. Memory is `tracemalloc` peak *per call*:
absence of increase in a peak statistic does not mean zero added allocations
or constant RSS. Numeric samplers do **not** promise mathematical proof.

The frozen source commit identified inside the archive is
`0a2cf2865261795683cca8529056a40831b0ef63` (run ID `37728771239`).
Subsequent documentation-only commits do not alter that benchmark source hash.
Reproduction on different hardware will have different latency distributions.
