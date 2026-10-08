<div align="center">

# Dexted DSP

**Exact filter checks. Inspectable evidence.**

Offline verification for fixed digital filters · Python & C++20

[![CI](https://github.com/dextune/dexted-dsp/actions/workflows/ci.yml/badge.svg)](https://github.com/dextune/dexted-dsp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](../../LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](../../pyproject.toml)
[![C++20](https://img.shields.io/badge/C%2B%2B-20-blue.svg)](../../CMakeLists.txt)
[![Research alpha](https://img.shields.io/badge/status-research%20alpha-orange.svg)](../project/CHANGELOG.md)

[English](../../README.md) · [한국어](../ko/README.md) · [简体中文](../zh-CN/README.md) · [日本語](../ja/README.md)

[Get started](#install-and-run) · [Benchmarks](#benchmarks-what-was-measured) · [Documentation](../README.md) · [Contributing](../../.github/CONTRIBUTING.md)

</div>

---

**Check a fixed digital filter over the entire frequency range, rather than hoping a sampling grid catches its largest peak.**

Python · C++20 · CLI · exact arithmetic · inspectable certificates · reproducible measurements

**v0.1.0 · research alpha.** An independent, AI-assisted project maintained in [dextune/dexted-dsp](https://github.com/dextune/dexted-dsp). Not an OpenAI product, endorsed integration, or externally audited safety tool. Install from this repository; a PyPI release is not implied.

## What you can use today

The executable library checks **fixed real biquads** and, in Python, **serial cascades**. It checks both strict denominator stability and a requested strict frequency-gain limit. Use it offline, after rounding the coefficients to the precision that will actually be deployed. It does not process audio, optimize filters, inspect arbitrary neural networks, or certify physical device safety.

A fixed temporal filter applied independently to video pixels can fit this model. A complete video-restoration network generally does not. Arbitrary-precision arithmetic and allocation make the certifier unsuitable for an audio callback.

## Install and run

Clone the repository (GitHub access is required while it is private), then install from source:

```bash
git clone https://github.com/dextune/dexted-dsp.git
cd dexted-dsp
python -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows PowerShell instead: .venv\Scripts\Activate.ps1
python -m pip install .
python examples/basic.py
python tools/documentation_smoke.py
```

Python 3.10 or newer; no third-party **core runtime** dependency. The source build backend may be downloaded during installation. For offline use, first build a wheel using [the release guide](development/RELEASING.md); generated `dist/` files are not tracked in Git.

```python
from dexted_dsp import Biquad, certify, verify_biquad

f = Biquad.from_coefficients(
    [0.25, 0.0, 0.0, -0.5, 0.0],  # b0, b1, b2, a1, a2; a0 is 1
    precision="float32",
)
report = certify(f, max_gain=1.0)
assert report.certified
assert verify_biquad(report.as_dict(), f, max_gain=1.0)
print(report.status)  # certified
```

`max_gain` is an input **threshold**, not a returned peak estimate. The condition is `<`, not `<=`. Changing the coefficients or threshold invalidates the input binding of a saved certificate.

```bash
python -m dexted_dsp check examples/safe.json --output certificate.json
python -m dexted_dsp verify examples/safe.json certificate.json
python -m dexted_dsp check examples/hidden_peak.json
# The last command intentionally exits 1; it is a successful negative test.
```

CLI exit codes: `0` certified/verified; `1` condition not met or invalid certificate; `2` invalid input; `3` resource-limited **unknown**. Only exit zero may pass a deployment gate. `dexted-dsp` is an equivalent installed command.

## Precisely what came from OpenAI?

The research started from the mathematical manuscript collection in [`openai/math`][OAI-README]. We pin the research source to commit **`adc7f1241b42e322a6451854ab7e4b4c146bf78a`**, rather than silently tracking revisions. Its README warns that verification status varies across manuscripts.

| Source or method | Role here | Executed in the benchmark? |
|---|---|---|
| OpenAI result family 325, *A direct proof of the complete Crouzeix inequality*, §1 main theorem [OAI-325] | Conditional extensions for matrix-polynomial error and restricted time-varying systems; see the research note | **No** |
| OpenAI exact-DFT paper, introduction and computational-model caveats [OAI-DFT] | Exploratory scoping; its asymptotic exact-arithmetic result is not a practical FFT speed claim | **No** |
| Classical second-order Schur/Jury test and a quadratic in `cos(omega)` | Executable exact biquad predicate | **Yes** |
| Classical Bernstein positivity and exact subdivision | Python cascade certificate and rational rechecker | Cascade demonstration only; **not native latency bars** |

**The measured speedups do not come from the Crouzeix theorem.** No OpenAI proof code or DSP source is copied into the runtime. The general constant-two theorem has not been independently verified here, and no `crouzeix_certify()` API is shipped. OpenAI's original manuscript generation is separate from the AI-assisted engineering work in this project.

The development sequence was: inspect candidate mathematics → separate theoretical assumptions from runnable methods → implement exact predicates → compare against separately expressed rational arithmetic → port to C++ → measure stronger numerical baselines → retain review failures → package and document. Each stage and its evidence is mapped in [Research provenance](development/PROVENANCE.md).

## Benchmarks: what was measured

These are the **saved v0.1.0 measurements**, not newly selected timings for this translation. The documentation refresh checks their hashes and decisions; its separate small smoke run does not replace them.

| Protocol field | Recorded value |
|---|---|
| Data | 4 synthetic families × 1,024 binary32 filters = **4,096** |
| Threshold / randomness | Binary64 `max_gain=0.9999`; fixture seed `20261007`; method-order seed `932851` |
| Timing | 9 trials; 4 native batch repetitions per timed trial; `perf_counter_ns` |
| Native build | GCC 14.2.0; `-O3 -std=c++20 -ffp-contract=off`; no fast-math |
| Host | AMD EPYC 9V74 reported by a shared Linux x86-64 host; 5 visible logical CPUs; no affinity pinning |
| Python environment | Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0; benchmark requirements record Matplotlib 3.10.8 |

Native timings are **µs/filter, medians of 9 trials**. All four implementations include validity and denominator checks. The grids have prewarmed trigonometric caches, use early rejection, and do not pay for cache construction inside the timed interval.

| Family | Exact integer | Grid 1,024 | Grid 16,384 | Float64 algebraic | Grid 1,024 / exact¹ |
| --- | --- | --- | --- | --- | --- |
| Ordinary filters | 0.564106 | 1.686392 | 27.877729 | 0.011137 | 2.989× |
| High-Q stress | 0.599275 | 2.161358 | 33.816509 | 0.012064 | 3.607× |
| Near gain threshold | 0.377707 | 0.932293 | 16.152820 | 0.011086 | 2.468× |
| Unstable denominators | 0.008509 | 0.006741 | 0.007093 | 0.006717 | 0.792× |

¹ This column is **ratio of the two medians**, not the median of paired trial ratios. Both statistics, observed min/max, and the exact timing boundary are documented in [Benchmark details](benchmarks/BENCHMARKS.md).

![Native latency: four methods and four filter families](../../benchmarks/figures/native_latency.svg)

The integer predicate is faster than the 1,024-point grid on the first three recorded families, but slower on immediate unstable-denominator rejection. **Float64 algebra is much faster**, and remains in the comparison despite its rounding-sensitive decisions. These are certification latencies, not audio-processing throughput or improved perceptual quality.

### Accuracy and Python overhead are separate questions

On the high-Q family, exact rational arithmetic accepts 539 filters and rejects 485. The following are counts, not population failure-rate estimates:

| Method | False accepts / 485 reference failures | False rejects / 539 reference passes |
| --- | --- | --- |
| Exact integer | 0 | 0 |
| Grid 1,024 | 356 | 0 |
| Grid 16,384 | 213 | 0 |
| Float64 algebraic | 2 | 5 |

The other three families have zero recorded disagreements for all four native methods. A false accept means a failed **mathematical condition** was accepted; it is not automatically proof that an arbitrary feedback network explodes.

![High-Q correctness against the rational reference](../../benchmarks/figures/high_q_correctness.svg)

![Python API comparison, with per-call overhead](../../benchmarks/figures/python_latency.svg)

The Python graph uses 128 high-Q filters and calls the installed SciPy `signal.freqz` directly. That function evaluates a response at requested frequencies; it is not sold as an exact certificate [SCIPY-FREQZ]. Do not combine its per-filter API timings with native batch-kernel timings.

![An analytically established peak between grid points](../../benchmarks/figures/hidden_peak.svg)

The hidden-peak example has an exact magnitude of 2 at `omega=pi/2`. The curve illustrates that algebraic fact; a dense graph is not the proof.

### Evidence and reproduction

[Raw JSON and repeated timings](../../benchmarks/results/benchmark.json) · [CSV summary](../../benchmarks/results/summary.csv) · [Coefficient arrays](../../tools/restore_fixtures.py) · [Protocol and source hashes](../../benchmarks/results/protocol.json) · [Environment](../../benchmarks/results/environment.json) · [Recorded run log](../../validation/runs/v0.1.0/benchmark_run.log)

```bash
python -m pip install '.[bench]'
python -m pip install -r benchmarks/requirements-bench-tested.txt
python tools/restore_fixtures.py
python tools/audit_benchmark.py --recheck-fixtures
# Quick command-path check; not the published dataset:
python benchmarks/run.py --n 32 --trials 3 --out validation/my-smoke
# Full new measurement, leaving the published artifacts intact:
python benchmarks/run.py --n 1024 --trials 9 --seed 20261007 --out validation/my-run
python benchmarks/plot.py --results validation/my-run/benchmark.json --out validation/my-run/figures
```

Native benchmark reproduction currently targets Linux/macOS with GNU/Clang tooling; use WSL on Windows. Historical charts use shared English labels; the linked guides provide localized legends and interpretation.

## Tests and integration

```bash
python -m unittest discover -s tests -v
python tools/documentation_smoke.py
python examples/cascade.py
# Optional C++ build: C++20, CMake >=3.20 and Boost >=1.74 headers
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
```

The core suite has **35 unittest methods**, with randomized checks inside several methods. The documentation smoke script adds **12 scenario checks**. Historical benchmarks contain 4,096 deployed fixtures and a separate 2,048-row native bit-pattern check. These counts are different layers, not independent external audits. Read [Testing](guides/TESTING.md) for negative tests, budget exhaustion, installed-wheel tests, and troubleshooting.

## Documentation and limitations

| Document | What it explains |
|---|---|
| [User guide](getting-started/USER_GUIDE.md) | Installation, input semantics, Python/SOS/CLI, budgets, C++, CI, troubleshooting |
| [Testing guide](guides/TESTING.md) | Expected outputs, pass/fail/unknown, regression and benchmark reproduction |
| [Benchmark report](benchmarks/BENCHMARKS.md) | Distributions, all methods, timing boundaries, raw fields, limitations |
| [Research provenance](development/PROVENANCE.md) | OpenAI source locations, dependency boundaries, development evidence |
| [Mathematical guide](mathematics/MATHEMATICS.md) | Derivations, certificate semantics, and conditional extensions |
| [API reference](../reference/API.md) / [Publication guide](development/RELEASING.md) | Low-level contracts and repository/package release procedure |

A certificate describes the ideal fixed linear system with the supplied deployed coefficients. It does **not** prove all runtime roundoff, overflow, limit cycles, arbitrary modulation, feedback topology, AI behavior, hearing protection, PSNR, STOI or PESQ. `unknown` must fail closed. A JSON certificate is not a digital signature or a hardened untrusted-input sandbox.

[MIT license](../../LICENSE) · [NOTICE](../legal/NOTICE.md) · [Security](../../.github/SECURITY.md) · [Issues](https://github.com/dextune/dexted-dsp/issues). Mathematical methods are classical unless explicitly marked as an external conditional theorem. No claim of novel mathematics, independent audit, or physical-device safety certification is made. The CI badge reflects GitHub Actions dynamically; [local validation records](../../validation/rebrand/) are a separate evidence source.

[OAI-README]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/README.md
[OAI-325]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex
[OAI-DFT]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex
[CP-2017]: https://arxiv.org/abs/1702.00668
[SCIPY-FREQZ]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html
[PYPA]: https://packaging.python.org/en/latest/tutorials/packaging-projects/

**Measurement provenance.** These numbers were recorded under the former research name **CertifiedDSP**. The Dexted DSP rename changes names, namespaces, CLI and certificate schemas—not the algebraic predicates. The original measurements and benchmarked source snapshots are retained. [Migration and reproducibility](../project/REBRANDING.md) · [Source mapping](../../benchmarks/results/rebrand-map.json).

**Source checkout data:** the NPZ is generated on demand, not stored in Git. Install the pinned benchmark requirements and run `python tools/restore_fixtures.py`. Reconstruction must match the original SHA-256; no measurement is replaced.

<!-- benchmark-sha256: 0332cbc6a22ebf2da482a043b3f206ae175bcab5d71f640417c96c46c7ac99a0 -->

## What's new in source (unreleased)

[Try the exact-grid hidden-peak demo](../../examples/hidden_peak/README.md), [inspect SciPy SOS and bound peak gain](../product/inspection.md), or view [current implementation gates](../product/implementation-status.md). New API benchmarks have **not** been run; existing tables are historical v0.1.0 measurements.


## Current source: exact peak-location region

For a single stable fixed real biquad, `localize_peak` now certifies rational intervals in `cos(ω)` that cover every global peak, including ties. Ordinary Hz values are **approximations, not certified Hz bounds**. See the [derivation](../research/proofs/peak-localization.md) and the [25-case designed-SOS pilot](../../benchmarks/suites/PROTOCOL_V2.md); neither supplies an external audit.
