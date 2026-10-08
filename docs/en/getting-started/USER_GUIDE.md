# User guide: installation, API and integration

[English](USER_GUIDE.md) · [한국어](../../ko/getting-started/USER_GUIDE.md) · [简体中文](../../zh-CN/getting-started/USER_GUIDE.md) · [日本語](../../ja/getting-started/USER_GUIDE.md)

[Dexted DSP](../../../README.md)

## 1. Decide whether the model fits

Use the library for a **fixed, real, normalized biquad** or a serial chain of 1–32 such sections. A deployment check answers whether the supplied denominator is strictly stable and the ideal linear frequency response stays below a chosen limit. It does not automatically inspect FLAMO/PyTorch graphs, parse FAUST/VST/ONNX, or correct coefficients.

Always export the **final deployed coefficients**, including normalization and float32 conversion choices. Test offline, before playback or deployment. No command in this guide plays sound or controls hardware.

## 2. Installation choices

Run every command from the extracted `dexted-dsp/` root, not from `docs/en/`.

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
python -m dexted_dsp --version
```

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install .
python -m dexted_dsp --version
```

Expected version: `0.1.0`. Activation is optional: invoke `.venv/bin/python` on POSIX or `.venv\Scripts\python.exe` on Windows directly. This avoids modifying PowerShell execution policy. Core support is declared for Python >=3.10; hosted OS/version CI must still be run after publication.

### Offline wheel / editable development

```bash
python -m pip install build
python -m build
python -m pip install --no-deps dist/dexted_dsp-0.1.0-py3-none-any.whl
# Alternative for source edits; build backend may need downloading:
python -m pip install -e .
```

Choose **one** installation mode in an environment. Do not assume `pip install dexted-dsp` from an index refers to this unpublished project. The wheel contains the Python runtime, not a compiled native library. Repository documentation, tests, figures and sources are in this ZIP/sdist; keep the source tree for the following examples. Packaging behavior follows the PyPA model [PYPA].

## 3. Input meaning: the most important contract

The filter is

$$H(z)=\frac{b_0+b_1z^{-1}+b_2z^{-2}}{1+a_1z^{-1}+a_2z^{-2}}.$$

| Entry point | Required order |
|---|---|
| `Biquad.from_coefficients()` | `[b0,b1,b2,a1,a2]`, five values |
| `Biquad(b=..., a=...)` | numerator `(b0,b1,b2)` and denominator `(1,a1,a2)` |
| `from_sos()` | SciPy layout `[b0,b1,b2,a0,a1,a2]`, with `a0==1` |
| CLI `type="cascade"` | Each `sections` row has **five** values, not SciPy's six |

No automatic `a0` normalization is performed. Normalize in your actual deployment pipeline, round, then supply those resulting values. Using another tool's sign convention without conversion can describe a different filter.

Python/JSON decimals first become finite binary64 numbers. `precision="float32"` explicitly rounds coefficients again to binary32; `precision="float64"` preserves parsed binary64 values. Those **represented binary rational values** are then certified exactly. It is not exact arithmetic on an intended decimal before parsing. The threshold remains binary64 even for float32 coefficients. NaN, infinity, complex values, booleans, strings and nonpositive limits are rejected. Requested float32 overflow is an error; tiny values can round to zero by that explicit conversion.

## 4. Python single-filter example and result interpretation

```python
from dexted_dsp import Biquad, certify, verify_biquad
f = Biquad.from_coefficients([0.25, 0, 0, -0.5, 0], precision="float32")
report = certify(f, max_gain=1.0)
print(report.status)
print(report.denominator_stable)
print(verify_biquad(report.as_dict(), f, max_gain=1.0))
```

Expected output:

```text
certified
True
True
```

| Single-filter status | Meaning |
|---|---|
| `certified` | Both strict conditions hold for this input |
| `denominator_not_schur` | Denominator failed strict disk stability |
| `gain_limit_not_met` | Stable denominator, but requested strict gain inequality failed |

The report is not an actual maximum-gain solver: `max_gain_limit` stores the **requested limit**. No actual peak frequency, dB headroom, or perceptual score is returned. `certify(Biquad.from_coefficients([1,0,0,0,0]),1.0)` fails because a constant gain exactly 1 does not satisfy `<1`.

Use explicit exceptions and rejection in applications:

```python
from dexted_dsp import Biquad, certify

def accept_exported_filter(values):
    try:
        f = Biquad.from_coefficients(values, precision="float32")
        result = certify(f, max_gain=1.0)
    except (ValueError, TypeError):
        return False
    return result.certified
```

This is a gate for the documented model, not a complete proof of the surrounding feedback system.

## 5. Serial cascades and SciPy

```python
from dexted_dsp import from_sos, certify_cascade, verify_cascade
sections = from_sos([
    [1.0, -0.75, 0.0, 1.0, -0.125, 0.0],
    [0.75, -0.09375, 0.0, 1.0, -0.75, 0.0],
], precision="float32")
proof = certify_cascade(sections, max_gain=1.0)
assert proof["certified"]
assert verify_cascade(proof, sections, max_gain=1.0)
```

The exact cascade transfer here is 0.75. Joint certification preserves frequency compensation; merely multiplying separate peak bounds may lose it. `from_sos` itself needs no SciPy import. `examples/scipy_sos.py` optionally designs a Butterworth SOS with installed SciPy and checks the rounded sections at threshold 1.01.

Cascade statuses are `certified`, `denominator_not_schur`, `condition_failed`, and `unknown`. `condition_failed` has an exact nonpositive strict-gap witness. `unknown` means the resource budget did not produce a proof; it does not mean stable, unstable, or acceptable. Individual unstable sections are rejected even if poles appear algebraically canceled by other sections.

Default budgets: `max_depth=48`, `max_nodes=20000`. Supported maxima: depth 128, nodes 100,000, sections 32. Increasing budgets can help but does not guarantee fast completion on near-zero high-degree cases.

## 6. JSON CLI, saved certificates and expected failures

The normal input example is [safe.json](../../../examples/safe.json):

```json
{
  "type": "biquad",
  "precision": "float32",
  "max_gain": 1.0,
  "coefficients": [0.25, 0, 0, -0.5, 0]
}
```

```bash
python -m dexted_dsp check examples/safe.json --output certificate.json
python -m dexted_dsp verify examples/safe.json certificate.json
```

The check prints full JSON; verification prints `{"verified": true}`. The input path cannot be overwritten by `--output`. Create the parent output directory yourself. JSON objects must be at most 1 MiB. No input file is executed or sent to a service.

Run negative cases separately from a shell that stops on nonzero exit codes:

```bash
python -m dexted_dsp check examples/hidden_peak.json
# Expected: gain_limit_not_met, exit 1.
python -m dexted_dsp check examples/budget_limited.json --max-depth 0
# Expected: unknown, exit 3.
python -m dexted_dsp check examples/budget_limited.json --max-depth 16
# Expected for this included example: certified, exit 0.
```

The last pair demonstrates why `unknown` is not a failure proof. Check status and exit code; do not grep the word “certified”, which could appear in a false-valued JSON field. Only successful certificates can be reverified. Keep original inputs, limit, certificate and package version together. Certificates are not signed; the checker reconstructs the mathematical condition and input binding.

## 7. C++ and C integration

Dependencies: C++20 compiler, CMake >=3.20, Boost >=1.74 headers. Debian/Ubuntu example: `sudo apt-get install g++ cmake libboost-dev`. On macOS, install a compiler/CMake/Boost using your normal package manager; on Windows use a compatible CMake toolchain and Boost installation. The Python core does not need these dependencies.

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
cmake --install build --prefix ./local-install
```

```cpp
#include <dexted_dsp/biquad.hpp>
int main() {
    const float coefficients[5] = {0.25f, 0, 0, -0.5f, 0};
    const int verdict = dexted_dsp::certify_biquad_f32(coefficients, 1.0);
    return verdict == 1 ? 0 : 1;
}
```

Return codes: `1` certified, `0` not certified, `-1` invalid input. The C ABI additionally catches exceptions and returns/stores `-2`. **Never cast these integer codes directly to bool:** negative error codes would become true. The header API can throw allocation exceptions. Do not use fast-math.

A CMake consumer uses `find_package(DextedDSP CONFIG REQUIRED)` and links `DextedDSP::dexted_dsp`; configure it with the installed prefix in `CMAKE_PREFIX_PATH`. C++ coefficients are binary32 only; its threshold is binary64. Native cascades are not implemented.

Optional Python native smoke check, Linux example:

```bash
python tools/native_smoke.py "$PWD/build/libdexted_dsp.so"
```

The wrapper requires an explicit trusted absolute library path and refuses silent coefficient rounding. Library names/directories differ on macOS and Windows. See the [API contract](../../reference/API.md).

## 8. CI integration without unsafe defaults

A deployment gate may run:

```bash
python -m dexted_dsp check examples/safe.json --output certificate.json
python -m dexted_dsp verify examples/safe.json certificate.json
```

Use your real exported coefficients in place of the example. Configure CI to stop on any nonzero exit status, including 3. The supplied GitHub Actions workflow tests Python, native code and builds; its presence is not evidence that hosted checks already ran. Do not publish a green badge until the actual repository workflow succeeds.

## 9. Troubleshooting

| Symptom | Check or remedy |
|---|---|
| `ModuleNotFoundError` or `dexted-dsp` not found | Activate the intended environment; use `python -m pip` and `python -m dexted_dsp` with the same interpreter |
| Float32 overflow / invalid coefficient | Inspect the exported finite real values; do not silently clamp them and reuse the old certificate |
| Unity-gain filter rejected | The limit is strict; choose an explicitly justified limit greater than the actual gain, not a hidden tolerance |
| `unknown` | Inspect node/depth limits and condition margin; increase within public caps or reject deployment |
| Saved proof no longer verifies | Check coefficient order, normalization, rounding, section order and identical threshold |
| Boost not found | Install headers; pass an appropriate CMake prefix for nonstandard installations |
| Native wrapper rejects coefficients | Explicitly convert the export to float32 before certification |
| Headless plotting error | Use `MPLBACKEND=Agg`; set `MPLCONFIGDIR` to a writable directory |
| Benchmark numbers differ | Confirm versions, fixtures, CPU load, flags and thread settings; never replace correctness evidence with faster timings |

For a bug report attach the minimal coefficient JSON, expected condition, actual status, exact version, OS/compiler and logs. Do not attach private audio, credentials, or proprietary models unless authorized.

[OAI-README]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/README.md
[OAI-325]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex
[OAI-DFT]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex
[CP-2017]: https://arxiv.org/abs/1702.00668
[SCIPY-FREQZ]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html
[PYPA]: https://packaging.python.org/en/latest/tutorials/packaging-projects/
