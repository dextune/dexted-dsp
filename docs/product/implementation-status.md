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
| B-01/B-02 | Historical v0.1.0 dataset frozen; **25-case designed-SOS pilot run with 30 trials**, raw-data auditor and predeclared SHA-based split | >=1,000-case licensed representative holdout, fair norm baseline, 3 machine families, independent reproduction |
| R-01/R-02 | Conditional design note and pinned source documented | New theorem assumptions independently checked; executable research PoC remains absent |
| P-01/P-02 | New native 3-OS CI matrix with clean CMake consumer (pending hosted confirmation), release checklist | All native OS jobs green, trusted publishing and approved GitHub/PyPI release |
| X-01 | External evaluation rubric specified | 5 domain reviewers, 10 new users, >=3 integrations |

**Release restrictions:** repository visibility and PyPI/GitHub Releases are not changed automatically. Public release requires explicit approval, namespace ownership checks and source/binary provenance. No speed or sound-quality improvement is asserted without fair real-world benchmarking.
