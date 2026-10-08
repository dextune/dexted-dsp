# Unreleased 9.5-plan implementation track

**2026-10-08 — implemented source changes, no public release**

- Reposition README toward proof-carrying offline IIR gain verification and reproducible hidden-peak contrast.
- Add exact-rational peak enclosures for biquads and proof-supported SOS bounds with fail-closed budget semantics.
- Add Python `inspect_biquad`, `inspect_sos`, `inspect_cascade`, `verify_inspection`, and JSON/Markdown inspection CLI.
- Add `dexted-dsp demo hidden-peak` with mathematically proven global peak and sampled-grid contrast.
- Add native C++20 SOS cascade predicate, C ABI and explicit optional ctypes bridge; distinguish unknown/error from rejection.
- Add property, tamper, round-trip and cross-language tests, nightly deterministic fuzz plan, and evidence auditing.
- Freeze v0.1.0 historical benchmark values; do not present them as timings of changed source.

**Not implemented/approved:** exact peak-frequency region, native proof serialization, externally peer-reviewed novel mathematical runtime, production filter dataset, public visibility/PyPI/GitHub release, independent third-party replication, blind onboarding study and three external adoption integrations. The research alpha label remains appropriate.
