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
