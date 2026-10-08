# Adversarial review — SciPy/python-control competitive evidence

Date: 2026-10-08. Scope: a **small synthetic comparison**, not product-grade
field efficacy or an external mathematical safety audit. Raw measurement:
[run-20261008.json](../../../benchmarks/competitive/results/run-20261008.json).
Published toolchain: actual SciPy 1.17.0, actual python-control 0.10.2,
independent SymPy 1.14.0, official GitHub Actions Linux host.

## Red-team objections and changes

| Objection (hostile) | Evidence / disposition |
|---|---|
| Numerical samplers don't even claim certificates; equivalence would be dishonest | Explicitly label estimated grid checking versus strict mathematically verified whole-band gain; never claim faster DSP |
| Case choice overstates prevalence, only one failure | Freeze nine IDs and entire original SOS coefficients, display both baselines missing the **same** constructed case; no production prevalence claims |
| Threshold or float32 rounding differs between engines | Exact binary32 input asserted, losslessly represented as f64; identical 1,024-point inclusive grid, per-case threshold and numeric stability precheck |
| python-control overhead includes costly TF setup and distorts results | Prepare control TF once outside timed functions (and disclose excluded setup); compare each Before/After with the *same* preconstructed system |
| Proof return could be forged or incomplete | Full production `certify_cascade` plus `verify_cascade` for PASS and an independent SymPy exact-rational root-count oracle for every case |
| Failing/unknown results hidden | Store every status and 30 untrimmed timed observations + 30 separate peak-allocation repeats for **all five methods**, including negative cases |
| Unfair acceleration claim from different tasks | Show actual **higher** p50 and p95 for both After workflows; proof-only separate; no general speed claims |
| Memory looks unchanged, but native buffers missing | Label `tracemalloc` as Python allocations only; explicitly exclude native NumPy/C memory and RSS |
| GitHub hook not backed by figures | Commit deterministic SVGs generated from archived JSON; source code and pixel-source audit exercised in CI |
| Someone edits or selectively drops a bad trial | CI rejects missing/reordered cases, raw-count changes, altered summaries, source/fixture drift and coefficient tampering |
| Exact oracle result in archive could be fabricated | Benchmark itself recomputes SymPy truth; competitor CI additionally reruns exact oracle on the archived coefficients |
| Cross-hardware repeatability proven? | **Not yet**. One Azure GitHub runner, unpinned shared vCPUs, no independent organization-run replication. This is a release-level limitation, not a reason to suppress the benchmark |

## Review iterations, checkable acceptance

- **Pass 1:** the first staging revision failed the repository link gate
  because the planned archival JSON had not been committed yet. The final
  branch includes the actual measured archive, so the link is resolved.
- **Pass 2:** raw-data integrity alone did not recompute stored oracle truth.
  Added strict coefficient/threshold/split comparison to the immutable
  fixture and optional independent SymPy truth recheck in the competitive CI.
- **Pass 3:** the landing dashboard now shows detection **and** measured
  increased time, separately measured allocation peaks, an executable
  reproduction protocol, and the constructed-case disclaimer.

Internal pilot-scope scoring (0..10) after these fixes, conditional on CI green:

| Internal criterion | Score / 10 | Basis |
|---|---:|---|
| Genuine two-library baseline / matched inputs | 9.5 | Exact APIs and pinned versions; TF construction explicitly excluded |
| Mathematical correctness crosscheck | 9.5 | Exact SymPy QQ root counting and certificate verification, not external human proof |
| Statistical/raw-record completeness | 9.5 | 30 untrimmed time and 30 allocation observations per method and case; no confidence interval |
| README and responsive evidence usability | 9.5 | Three regenerated semantic SVGs, hooks and copy-paste reproduction |
| Automatic regression/adversarial checks | 9.5 | Archive SHA checks, oracle rerun, mutation tests, CI |
| Transparency about negatives / scope | 10.0 | Slower After and bounded synthetic host findings shown upfront |

**Internal pilot bar: >=9.5 in every scoped category, subject to successful
test execution.** This self-review is NOT independent external validation.
For unrestricted production/externally reproduced evidence, the gate remains
**OPEN/NOT MET** until unrelated hardware/organization repetition, coverage
beyond nine selected designs, end-to-end RSS/native-memory profiling, confidence
intervals and public release approval are completed.
