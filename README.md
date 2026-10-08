<div align="center">

# Dexted DSP

**Exact-frequency verification for digital filters**

[![CI](https://github.com/dextune/dexted-dsp/actions/workflows/ci.yml/badge.svg)](https://github.com/dextune/dexted-dsp/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](pyproject.toml)
[![C++20](https://img.shields.io/badge/C%2B%2B-20-blue)](CMakeLists.txt)
[![License MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Status](https://img.shields.io/badge/status-research%20alpha-orange)](docs/project/CHANGELOG.md)

[**English**](docs/en/README.md) · [**한국어**](docs/ko/README.md) · [**简体中文**](docs/zh-CN/README.md) · [**日本語**](docs/ja/README.md)

[Documentation](docs/README.md) · [Python/C++ API](docs/reference/API.md) · [Benchmarks](docs/en/benchmarks/BENCHMARKS.md) · [Mathematics](docs/research/README.md)

</div>

---

**Dexted DSP** checks fixed, real digital biquad filters over the **entire frequency interval**, instead of relying on a finite frequency grid. Python also supports certified serial cascades with independently rechecked certificates. A C++20 implementation, command-line interface, tests, and reproducible benchmark data are included.

> **Scope:** Offline mathematical verification of fixed-coefficient models, **not** an audio processor, complete neural-network verifier, real-time audio callback tool, or device-safety certification. OpenAI's Crouzeix manuscript is referenced only for a **conditional research extension** and is not used by the measured runtime. This is an independently maintained, AI-assisted project, not an official OpenAI product.

## Get started

```bash
git clone https://github.com/dextune/dexted-dsp.git
cd dexted-dsp
python -m pip install .
python examples/basic.py
python -m unittest discover -s tests -v
```

```python
from dexted_dsp import Biquad, certify, verify_biquad

f = Biquad.from_coefficients([0.25, 0.0, 0.0, -0.5, 0.0], precision="float32")
proof = certify(f, max_gain=1.0)
assert proof.certified
assert verify_biquad(proof.as_dict(), f, max_gain=1.0)
print(proof.status)  # certified
```

```bash
dexted-dsp check examples/safe.json --output certificate.json
dexted-dsp verify examples/safe.json certificate.json
```

## Benchmarks and evidence

![C++ certificate check latency](benchmarks/figures/native_latency.svg)

Published charts compare a specialized exact integer predicate against sampled grids and a floating-point analytic baseline. The saved synthetic filter set covers **4,096 test filters**; runtime comparisons apply to **offline certification**, not audio throughput. In some cases the exact checker is slower. The source revision, raw timing data, counts of false accept/reject decisions, limitations, and instructions to reproduce the measurements are provided in the [benchmark report](docs/en/benchmarks/BENCHMARKS.md) and [raw benchmark JSON](benchmarks/results/benchmark.json). No sound/image quality advantage is claimed.

## Documentation

| Topic | Documentation |
|---|---|
| Installation, examples, CLI | [Getting started](docs/en/getting-started/USER_GUIDE.md) |
| Python, native C++ and certificate API | [API reference](docs/reference/README.md) |
| Proofs, assumptions, external sources | [Research notes](docs/research/README.md) |
| Benchmarks, datasets, measurements | [Benchmark report](docs/en/benchmarks/BENCHMARKS.md) |
| Tests and reproducibility | [Testing guide](docs/en/guides/TESTING.md) |
| Contributions, security, releases | [Project guide](docs/project/README.md) |
| Chinese, Japanese, Korean, English | [All languages](docs/README.md) |

The full project explanation, mathematical derivations, complete benchmark tables, and methodology are in **[docs/](docs/README.md)**. Original measurement artifacts are preserved; file reorganization does not create new benchmark results.

**License:** [MIT](LICENSE) · **Project stage:** research alpha · **Hosting:** [dextune/dexted-dsp](https://github.com/dextune/dexted-dsp)
