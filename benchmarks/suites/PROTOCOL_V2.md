# Prospective benchmark protocol v2 — not yet measured

**Predeclared for future execution; these are requirements, not results.** Historical v0.1.0 synthetic data and source SHA hashes are immutable and must never be silently overwritten. Store new measurements under a versioned directory.

1. **Questions:** (A) frequency-sampling false acceptance on constructed peak stress; (B) exact-integer vs numerical analytic comparators; (C) end-to-end SOS design/export/inspection/verification; (D) native C++ batch/one-shot and Python public API, always separate.
2. **Populations:** synthetic high-Q and boundary fixtures, open-license real filter-design coefficients with provenance, deliberately adversarial bit-pattern inputs. Never pool their false-accept rates into a general production prevalence.
3. **Proposed size:** >=1000 holdout rows/group; >=30 distinct timing observations per method. Before execution, publish seed, held-out split IDs and fixture digest; no cherry-picked family elimination.
4. **Scoring:** exact PASS/FAIL/UNKNOWN against independent rational or interval oracle; false accepts, false rejects, resource exhaustion, certified bound width, p50/p95 time, peak RSS, cold-start and installation time. Distinguish whole-system gain vs individual SOS section gain.
5. **Fairness:** equal deployment precision, threshold, validity checks and inputs; disclose warm/cold caches and early-exit behavior. Compare against both fast float64 algebra and at least one credible interval/rational reference. Numeric-only solvers provide estimates, not the same proof contract.
6. **Environments:** one controlled Linux x86-64 host, ARM macOS, Windows, plus an independently reproduced run; retain CPU/flags/versions/threads, source SHA, raw repetitions. Do not generalize from cloud microbenchmarks.
7. **Statistics:** report untrimmed raw trials, median, p95, and the interval estimation method; do not compare unrelated Python and C++ timing boundaries with one speedup ratio.
8. **Integrity:** generator records a protocol version and archive SHA. The audit fails on mismatched source/fixture/correctness. No speed regression may be hidden; recorded v0.1.0 baseline is a historical comparator, not a target.

**Hard publication gate:** at least one third-party run reproduces correctness; headline acceleration must survive all relevant baselines and disclose slow/unknown outcomes. Existing v0.1.0 source revisions and static plots remain historical evidence only.

## Executed *pilot*, not the protocol's full release gate (2026-10-08)

A 25-case **synthetic designed-SOS pilot** is implemented in `run_pilot_v2.py`. Its immutable input file is [designed_sos_pilot_v1.json](fixtures/designed_sos_pilot_v1.json); [generator](generate_design_fixtures.py) records design methods and f32 export. This is *not* a real product fixture and is too small to satisfy the above >=1,000-row holdout or third-party reproduction requirements. The holdout split is assigned via case-id SHA-256 before execution.

The first local Linux shared-host run is in [main-source-matched 30-trial run](../../validation/pilot_v2/designed_sos_20261008_main_matched.json): 25 cases, 30 timed trials per function and filter, 0 `unknown`, with 1 false grid acceptance **only in the deliberately constructed hidden-peak family**. It does not show a production false-accept frequency. An explicit exact-core check, full certificate+bounds inspection and SciPy inclusive-grid response evaluation are **different work contracts**; never market cross-task timing differences as speedups. Current source hashes, environment, fixture sha256 and untrimmed timings are stored alongside p50 and p95; auditable with:

```bash
python -m pip install '.[bench]'
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python benchmarks/suites/run_pilot_v2.py --trials 30 --out validation/my-new-pilot.json
python benchmarks/suites/audit_pilot_v2.py validation/my-new-pilot.json
```

**Remaining:** independent quantitative baseline, held-out >=1,000 real/publicly licensed coefficient exports, ≥3 different host families, portable confidence intervals, partner replication and explicit measured release targets. None are supplied by the 25-case pilot.

### Pilot source-revision traceability

The earliest private [local formatting-variant run](../../validation/pilot_v2/designed_sos_20261008_linux_shared.json) predates a bit-for-bit sync of `biquad.py` and `cascade.py` from the actual GitHub `main` checkout. **Its current-source hash check correctly fails**; it is retained rather than silently overwritten. The [corrected main-matched run](../../validation/pilot_v2/designed_sos_20261008_main_matched.json) was performed afresh using the verified GitHub blob contents and passes strict source-hash auditing. See the [provenance note](../../validation/pilot_v2/README.md).
