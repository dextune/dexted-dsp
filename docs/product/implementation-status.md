# Implementation progress against the 9.5/10 plan

**Reference:** `DEXTED_DSP_95_MASTER_PLAN.md` (user-approved local planning artifact). **Date:** 2026-10-08. This status describes implemented source, not an achieved numerical score.

A green CI or finished README does **not** imply 9.5/10. Expert review, public distribution and external adoption are separate prerequisites.

| Work package | Present source-state | Remaining exit gate |
|---|---|---|
| H-01/H-02 | Root hook, executable hidden-peak demo, archived evidence connected | Blind-user tests (9/10) and independent UX review |
| U-01/U-02 | SOS inspection, failure reasons, JSON/Markdown CLI, SciPy and release-gate examples | 3 real partner projects; clean external install |
| U-03 | Provable gain intervals and **rational cosine peak-location intervals for biquads** | Certified Hz conversion, SOS peak-location solver, external mathematical review |
| U-04 | Native C++20 binary32 SOS predicate and error-aware C ABI | 3-OS native CI, serializable native proof, hardened resource budgets |
| Q-01 | Deterministic property/tamper tests and source-level fuzz runner | 50,000 nightly cases running in GitHub Actions; external audit |
| B-01/B-02 | Historical v0.1.0 dataset frozen; **25-case designed-SOS pilot** and **9-case SciPy + python-control competitive run** (30 time + 30 heap trials per case/method), raw-data auditor and SHA-based split | >=1,000-case licensed representative holdout, fair norm baseline, 3 machine families, independent reproduction |
| R-01/R-02 | Conditional design note and pinned source documented | New theorem assumptions independently checked; executable research PoC remains absent |
| P-01/P-02 | Native 3-OS GitHub Actions matrix and clean CMake consumers passed on 2026-10-08, release checklist | Independent cross-host replication, trusted publishing and approved GitHub/PyPI release |
| X-01 | External evaluation rubric specified | 5 domain reviewers, 10 new users, >=3 integrations |

**Release restrictions:** repository visibility and PyPI/GitHub Releases are not changed automatically. Public release requires explicit approval, namespace ownership checks and source/binary provenance. No speed or sound-quality improvement is asserted without fair real-world benchmarking.

## G3 — next executed validation gate: independent exact algorithm

The [W3C Audio EQ cookbook integration](eq-workflow.md) and
[synthetic design catalog](../../benchmarks/suites/EQ_CATALOG_PROTOCOL.md)
cover 1,200 generated EQ/notch/lowpass/highpass designs with a fixed seed and
SHA-256 contract. An exact symbolic rational-polynomial root-count method,
implemented with SymPy and distinct from the shipped integer Bernstein
subdivision, has a frozen 64-case holdout reference with 25 passes and 39
strict-limit failures. CI runs the oracle alone on all 1,200 and compares
the actual Dexted producer + rechecked certificates on those 64 cases.
The 1,200-case reference-only calculation is NOT a measurement of shipped-code
correctness. Any failure blocks CI; an 'unknown' is retained, not counted as
certified. [External reviewer packet](../research/review/INDEPENDENT_REVIEW_PACKET.md).

**Still not complete:** no field-collected or appropriately licensed production
SOS exports; no independent third-party mathematical proof audit; no user
interviews; no independent third-party benchmark reproduction or OpenAI theorem runtime implementation.
Scores remain unverified and the 9.5/10 gates stay open.

## Competitive pilot: measured, but not product validation (2026-10-08)

The [current-source competitive benchmark](../../benchmarks/competitive/README.md)
uses actual SciPy `signal.freqz_sos` and python-control
`frequency_response` on nine preselected synthetic float32 SOS filters.
Both sampling gates falsely pass **the same** constructed hidden-peak case;
adding verified Dexted proof rejects it. Wall p50 rises from 0.230 to
1.258 ms (SciPy) and from 0.217 to 1.142 ms (control). A whole-band proof
is extra validation, not a speedup of sampled frequency response.

The original frozen 30-time/30-Python-allocation trial archive and SymPy
independent rational-polynomial oracle are preserved. CI on the final
2026-10-08 release-candidate code passed on Linux, macOS and Windows,
including the native consumer. Memory data concern Python-traced peaks,
not native allocation/RSS. No unmeasured production improvement claims.

**Remaining required work before describing the library as complete:**
representative licensed real filter exports and independent hardware runs;
mathematical review outside the project; packaging/release automation and
API stabilization; production integration testing and UX assessment; true
native memory/RSS evidence; and optional certified cascade peak locations
or device-roundoff models as separate product tracks.
