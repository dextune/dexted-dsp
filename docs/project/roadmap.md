# Roadmap

Dexted DSP v0.1.0 is a **research alpha**, not a complete safety certification suite.

1. Preserve rigorous fixed real biquad and serial-cascade predicates, independently verified certificates, and reproducible benchmark methodology.
2. Improve end-user errors, integration examples, package metadata and cross-platform CI reliability.
3. Consider matrix/MIMO and graph-level certificates with explicit assumptions and a distinct performance evaluation.
4. Consider real-world audio/video applications only with independent datasets and quality measurements, without treating numerical bounds as perceptual improvements.

The Crouzeix `openai/math` result is a **conditional theoretical reference**; implementers must not label it as an audited runtime algorithm before a separate implementation and independent validation.

## Current product track (not a release claim)

See [implementation status and unmet external gates](../product/implementation-status.md) and the [prospective benchmark protocol](../../benchmarks/suites/PROTOCOL_V2.md). Actual external adoption and independently audited `openai/math` integration remain uncompleted.
