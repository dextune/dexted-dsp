# Unreleased 9.5-plan implementation track

**2026-10-08 — implemented source changes, no public release**

- Reposition README toward proof-carrying offline IIR gain verification and reproducible hidden-peak contrast.
- Add exact-rational peak enclosures for biquads and proof-supported SOS bounds with fail-closed budget semantics.
- Add Python `inspect_biquad`, `inspect_sos`, `inspect_cascade`, `verify_inspection`, and JSON/Markdown inspection CLI.
- Add `dexted-dsp demo hidden-peak` with mathematically proven global peak and sampled-grid contrast.
- Add native C++20 SOS cascade predicate, C ABI and explicit optional ctypes bridge; distinguish unknown/error from rejection.
- Add property, tamper, round-trip and cross-language tests, nightly deterministic fuzz plan, and evidence auditing.
- Freeze v0.1.0 historical benchmark values; do not present them as timings of changed source.

**Not implemented/approved:** certified Hz peak region (rational cos(omega) peak location is implemented for biquads), native proof serialization, externally peer-reviewed novel mathematical runtime, production filter dataset, public visibility/PyPI/GitHub release, independent third-party replication, blind onboarding study and three external adoption integrations. The research alpha label remains appropriate.

## Next-step milestone — single-biquad peak location and consumer CI

- Add [exact cosine-domain peak isolation](../research/proofs/peak-localization.md), explicit tie/flat response semantics, approximate-only Hz display.
- Upgrade new inspection wrappers to `inspection/v2` with backward verification of `inspection/v1` and exact location rechecking.
- Extend CLI with `--region-bits` and `sample_rate_hz` JSON metadata binding.
- Fix installed CMake package to load Boost dependency and add a standalone native consumer smoke test.
- Add macOS/Windows native CI in addition to existing Linux native CI. These statuses are **not** asserted green until the corresponding GitHub jobs finish.

The external review, 3-partner integrations, independently reproduced current-code benchmark, public package release and experimental OpenAI-math runtime still require separate gates.

## Designed SOS benchmark pilot — NOT a public performance guarantee

- Record 25 frozen f32 SciPy-designed/constructed SOS cases with SHA-based split and clear synthetic provenance.
- Introduce per-case 30-trial timing of three **different** tasks: core exact gate, whole inspection+bounds and inclusive 1,024-point sampled response.
- Save all raw timings, p50/p95, fixture/source SHA256, host details and method semantics.
- Audit stored statistics and fixed-fixture identity; preserve the original v0.1.0 results separately.
- One adversarial hidden-peak case deliberately causes the sampler to accept a rejected filter; never generalize its incidence.

## Benchmark provenance correction (CI discovered)

The first local designed-SOS timing artifact was made against formatting-different biquad/cascade source files. The CI source-hash audit rejected it, correctly. Instead of replacing the historical timing evidence or editing its hashes, preserve it as an explicitly source-drifted archive and **remeasure with the exact current GitHub source bytes**, storing a second independent 30-trial run. Use [the main-matched result](../../validation/pilot_v2/designed_sos_20261008_main_matched.json) for this branch's pilot audit.
