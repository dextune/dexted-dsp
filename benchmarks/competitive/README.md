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
[`results/run-20261008.json`](results/run-20261008.json) once published.
Results correspond to ONE GitHub Actions host, not independent external
reproduction; separate hardware and 1,000+ holdout production-grade filters
remain outside this pilot. Archived v0.1.0 results are not overwritten.
