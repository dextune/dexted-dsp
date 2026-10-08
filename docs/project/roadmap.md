# Roadmap

Dexted DSP v0.1.0 is a **research alpha**, not a complete safety certification suite.

1. Preserve rigorous fixed real biquad and serial-cascade predicates, independently verified certificates, and reproducible benchmark methodology.
2. Improve end-user errors, integration examples, package metadata and cross-platform CI reliability.
3. Consider matrix/MIMO and graph-level certificates with explicit assumptions and a distinct performance evaluation.
4. Consider real-world audio/video applications only with independent datasets and quality measurements, without treating numerical bounds as perceptual improvements.

The Crouzeix `openai/math` result is a **conditional theoretical reference**; implementers must not label it as an audited runtime algorithm before a separate implementation and independent validation.

## Current product track (not a release claim)

See [implementation status and unmet external gates](../product/implementation-status.md) and the [prospective benchmark protocol](../../benchmarks/suites/PROTOCOL_V2.md). Actual external adoption and independently audited `openai/math` integration remain uncompleted.


### Next validation gates

Hosted native cross-platform jobs, independent math review, certified Hz conversion, SOS peak localization, licensed representative holdout, independent current-code timing replication and approved public packaging remain open. [Current implementation status](../product/implementation-status.md).

### Executed G3 evidence — synthetic W3C Cookbook model collection

See [deterministic EQ catalog, exact real-root oracle and 64-case holdout](../../benchmarks/suites/EQ_CATALOG_PROTOCOL.md). This does not close the explicit **field-data, outside reviewer, third-party reproducibility or public release** gates. Actual deployed filter exports require permission and provenance, not manufactured substitutes.
