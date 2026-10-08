# Architecture

| Folder | Responsibility |
|---|---|
| [`src/dexted_dsp/`](../../src/dexted_dsp/) | Python exact biquad decision, cascade cover, certificate verification and CLI |
| [`cpp/`](../../cpp/) | C++20 exact biquad predicate, C ABI, CMake exports |
| [`tests/`](../../tests/) | Unit and boundary regression tests |
| [`examples/`](../../examples/) | Installable API demonstrations and JSON fixtures |
| [`docs/`](../README.md) | Translated usage, mathematical research, development and API documentation |
| [`benchmarks/`](../../benchmarks/) | Frozen synthetic measurements, plotting source, historical implementation |
| [`validation/`](../../validation/) | Historical local test evidence and generated-command summaries |
| [`tools/`](../../tools/) | Documentation checks, benchmark auditing, fixture regeneration |

**Trust boundary:** `certify` checks precise mathematical conditions for fixed real digital filters. An `unknown` result is not a pass; a failing sufficient condition need not imply full application-level instability. Crouzeix extensions are kept in notes, outside the executable engine.
