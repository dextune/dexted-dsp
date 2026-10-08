# Testing guide and expected outcomes

[English](TESTING.md) · [한국어](../../ko/guides/TESTING.md) · [简体中文](../../zh-CN/guides/TESTING.md) · [日本語](../../ja/guides/TESTING.md)

[Dexted DSP](../../../README.md)

## 1. Test layers, not one ambiguous “pass” count

| Layer | Command / data | Meaning |
|---|---|---|
| Core regression | 35 unittest methods | API, exact predicate, limits, certificates and CLI |
| Documentation scenarios | 12 checks in `documentation_smoke.py` | The examples and exit-code contract in these guides |
| Native test executable | 1 CTest entry with multiple assertions | C++ header/C ABI agreement on fixed edge cases |
| Native wrapper smoke | 256 seeded filters | Python ctypes integration and rejection of implicit float32 changes |
| Saved full benchmark | 4,096 filters plus 2,048 bit-pattern rows | Recorded algorithm comparisons and native decoding checks |
| Documentation refresh benchmark | 4 × 32 filters, 3 trials | Command-path smoke test only; not the published timing table |

A method can contain many random cases. These are not 35 independent experiments, an external audit, or a Lean verification run. Original logs remain in `validation/`; this refresh writes separate logs under `validation/docs_refresh/`.

## 2. Minimal local test, no benchmark dependencies

Install the package as described in the [user guide](../getting-started/USER_GUIDE.md), then run from the source root:

```bash
python -m unittest discover -s tests -v
python tools/documentation_smoke.py
python examples/basic.py
python examples/cascade.py
```

Expected core summary: `Ran 35 tests ... OK`. The documentation script returns JSON with `"status": "passed"` and `"checks": 12`. `examples/basic.py` prints `certified` and a successful rational recheck. The cascade example reports individual failures but joint `certified`.

Test coverage includes strict equality, a hidden resonance, denominator boundary roots, unstable pole-zero cancellation, explicit float32 conversion, extreme finite values, malformed/complex inputs, randomized integer/Fraction agreement, forged certificate flags, invalid covers, resource exhaustion and CLI input preservation.

The core file contains a 2,500-case seeded exact comparison, up to 1,200 random bit-pattern attempts (nonfinite rows skipped), and 100 candidate compensation cascades. These internal loops are different from the saved benchmark's 4,096/2,048 datasets.

Run a focused regression:

```bash
python -m unittest discover -s tests -p test_dexted_dsp.py -k hidden_peak -v
python -m unittest discover -s tests -p test_dexted_dsp.py -k unknown -v
python -m unittest discover -s tests -p test_dexted_dsp.py -k tampering -v
```

Each focused selection should run one test and succeed. A negative test succeeds because the checker correctly refuses or defers a mathematical claim.

## 3. Check all CLI exit paths

| Input / action | Expected status | Exit |
|---|---|---|
| `safe.json` | `certified` | 0 |
| `hidden_peak.json` | `gain_limit_not_met` | 1 |
| `budget_limited.json --max-depth 0` | `unknown` | 3 |
| Same budget example, `--max-depth 16` | `certified` | 0 |
| Malformed JSON or unsupported type | `invalid_input` | 2 |
| Verify certificate against different coefficients | `verified: false` | 1 |

`python tools/documentation_smoke.py` automates these cases and asserts return codes. For manual inspection on POSIX use `echo $?` immediately after a command; in PowerShell use `$LASTEXITCODE`. Do not place expected-failure commands in an unhandled `set -e` block.

A status of `unknown` must remain rejected in deployment even if the same system passes after a larger budget. A failed gain test is not a general feedback-instability certificate.

## 4. C++ build, C ABI and integration test

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
# Linux shared-library example:
python tools/native_smoke.py "$PWD/build/libdexted_dsp.so"
```

Expected native output includes `native tests: PASS`; CTest reports one passing test. The wrapper prints 256 cases, zero mismatches and `implicit_rounding_rejected: true`. On other platforms locate the built library and pass its actual absolute path. The native benchmark is a separate build path, not a replacement for these interface tests.

Compiler warnings must be preserved. The original GCC/Boost inlining warning and original sanitizer evidence are described in [benchmark details](../benchmarks/BENCHMARKS.md). Re-running a passing CTest is not a proof that every compiler warning is harmless.

## 5. Audit saved benchmark evidence without timing anything

```bash
python tools/audit_benchmark.py
# Needs installed project + NumPy:
python tools/audit_benchmark.py --recheck-fixtures
```

The first command checks the saved NPZ hash, 12 measured source hashes, raw-trial count, medians, paired ratios and count consistency. The second reloads the saved arrays with `allow_pickle=False`, recomputes **all 4,096** exact decisions with the integer and Fraction expressions, and checks family pass counts.

Expected fields include `status: passed`, `fixture_rows: 4096`, and, with rechecking, `exact_recheck_rows: 4096`. This does not independently recompute historical native timing or every baseline's historical confusion count. It verifies archive consistency and the current exact predicates.

A changed measured source hash is a useful failure. Restore the original source to audit that run, or create a new benchmark run for new code. Do not “repair” the audit by editing historical hashes to fit changed code.

## 6. Re-run benchmarks and regenerate charts

```bash
python -m pip install '.[bench]'
python benchmarks/run.py --n 32 --trials 3 --out validation/my-smoke
python benchmarks/run.py --n 1024 --trials 9 --seed 20261007 --out validation/my-run
python benchmarks/plot.py --results validation/my-run/benchmark.json --out validation/my-run/figures
```

Use one thread for OpenBLAS/OMP when reproducing the recorded configuration. For native measurements use a supported C++ compiler and Boost; Windows users should use WSL for this script. Read [BENCHMARKS.md](../benchmarks/BENCHMARKS.md) for exact distributions, timing exclusions and library versions.

Successful reproduction means: no exact-reference discrepancy, valid output artifacts, and an honestly recorded environment. **It does not require a faster timing result.** Do not repeatedly discard slow measurements until a desired headline appears. Keep before/after runs and compare the same fixture values and code revision.

To redraw only the archived graphs without rerunning the experiment:

```bash
python benchmarks/plot.py --results benchmarks/results/benchmark.json --out validation/redrawn-figures
```

## 7. Test the distributable rather than an editable checkout

From the source root, create a separate environment and install a wheel built from this checkout:

```bash
python -m pip install build
python -m build
python -m venv .wheel-test
# POSIX:
.wheel-test/bin/python -m pip install --no-deps dist/dexted_dsp-0.1.0-py3-none-any.whl
.wheel-test/bin/python -m unittest discover -s tests -v
.wheel-test/bin/python tools/documentation_smoke.py
# Windows: replace .wheel-test/bin/python with .wheel-test\Scripts\python.exe
```

Do not set `PYTHONPATH=src` for this test; that would hide an incomplete wheel. To rebuild from source, install the optional development build tools and use `python -m build`, then `python -m twine check dist/*`. Building/checking is not publishing. Rebuild wheels after changing their README metadata.

## 8. Documentation and release checks

```bash
python tools/check_links.py
python tools/check_documentation.py
python tools/audit_benchmark.py
```

These checks validate local links, required documents in all four languages, shared benchmark identity, required result tables, and archived source consistency. They do not evaluate translation nuance or prove the mathematics. No hosted GitHub Actions or independent external audit is implied.

Before publication inspect [validation/docs_refresh/summary.json](../../../validation/docs_refresh/summary.json), retain raw logs, ensure README numbers refer to the intended run, rebuild the distribution metadata, and only then follow the [release guide](../development/RELEASING.md). The ZIP checksum and `MANIFEST.sha256` identify the delivered artifact; hashes detect byte changes, not mathematical correctness.

[OAI-README]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/README.md
[OAI-325]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex
[OAI-DFT]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex
[CP-2017]: https://arxiv.org/abs/1702.00668
[SCIPY-FREQZ]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html
[PYPA]: https://packaging.python.org/en/latest/tutorials/packaging-projects/
