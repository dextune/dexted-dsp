# Inspection API and proof envelope — developer contract

**Status:** implemented in source; independent audit and public package distribution remain pending.

## Minimal use

```python
from scipy.signal import butter
from dexted_dsp import inspect_sos, verify_inspection
sos = butter(8, .2, output='sos')
report = inspect_sos(sos, precision='float32', max_gain=1.01, fs=48000)
print(report.status, report.reason)
print(report.gain_bounds.as_dict() if report.gain_bounds else None)
report.save('proof.json')
assert verify_inspection(report.as_dict(), sos, precision='float32', fs=48000, max_gain=1.01)
```

`inspect_biquad` accepts a `Biquad` or exactly five coefficients. `inspect_sos` accepts standard SciPy six-column rows `[b0,b1,b2,1,a1,a2]` and converts only when explicitly requested (`precision='float32'` by default). `inspect_cascade` accepts previously deployed `Biquad` objects, without implicit rounding. All denominator sections must be strictly Schur-stable. A nonunit `a0` is rejected, never silently normalized.

### Result model

`InspectionReport.status` is `certified`, `rejected` or `unknown`; `.reason` retains the core status (`gain_limit_not_met`, `denominator_not_schur`, `condition_failed`, `unknown`, `certified`). `.certified` is true *only* for `certified`. `.gain_bounds` is `None` for unstable cases or when the SOS refiner cannot establish an upper bound within its budgets.

`GainBounds` includes `lower_ratio` and `upper_ratio` as authoritative **exact rational** closed enclosures of the *ideal* peak magnitude. `lower_bound` / `upper_bound` are **conservatively outward-rounded** float display conveniences, or `None` if not representable. `status='bounded'` means the requested number of bisections completed, **not** that a particular absolute accuracy was achieved. `status='budget_limited'` means an already established valid interval is returned without full refinement. The `GainBounds.frequency_region_hz` field remains `null`: a **certified Hz interval** is not implemented. For **single biquads**, `localize_peak()` now provides `PeakRegion.cosine_intervals` as authoritative rational intervals in `c=cos(omega)` guaranteed to contain every global maximum. Optional `frequency_hz_approx` is a display-only transformation, explicitly tagged `frequency_hz_certified=false`. Cascades have no peak-frequency region yet.

For a single biquad, `bound_peak_gain` brackets a peak by exact-integer tests at rational thresholds and halves the bracket `precision_bits` times (default 24). For SOS, `bound_sos_peak_gain` uses an exactly evaluated frequency witness for its lower bound and accepts an upper bound **only when a Bernstein proof succeeds**. `unknown` and arbitrary finite grids are never interpreted as an upper bound. The SOS default is 8 bisections; runtime depends on degree and proximity to strict equality.

### Versioning and verification

Existing `dexted-dsp/biquad/v1` and `dexted-dsp/cascade/v1` proofs remain supported. New inspections serialize `dexted-dsp/inspection/v2` (and still **verify** existing `inspection/v1` proofs), a wrapper with an SHA-256 binding of hex-encoded coefficients, threshold, precision and optional sample rate, together with the core proof. A digest is not a digital signature. `verify_inspection()` only verifies claimed PASS records and recomputes the exact predicate; it also checks the single-biquad witness and exported bound values for tampering. SOS cover checks use the independently expressed `Fraction` verifier in the existing core. These are **two in-repository** implementations, not third-party validation or a formal proof assistant. A v2 single-biquad proof additionally carries a rational `peak_region` with `region_bits` and rejects altered exact intervals; v1 reports lack this new claim.

### CLI

```bash
dexted-dsp demo hidden-peak
dexted-dsp inspect examples/safe.json --output proof.json --report inspection.md
dexted-dsp verify examples/safe.json proof.json
```

CLI `inspect` reads the existing JSON schema (`type=biquad` or `type=cascade` containing five-element sections). `--peak-bits` controls gain-enclosure effort; `--region-bits` (biquad only) controls exact stationary-point isolation. JSON may supply `sample_rate_hz`, bound to the proof; `--max-depth` and `--max-nodes` control the SOS proof budget. Only `0` is a deployment PASS; reject `1`, invalid `2` and resource-limited `3` fail closed. `--report` writes human-readable Markdown in addition to full JSON. No network action is performed.

### Native C++20

`dexted_dsp::certify_cascade_f32(rows, count, gamma, max_depth=48, max_nodes=20000)` is now a C++ exact-integer Bern­stein **predicate** for 1–32 binary32 sections, each `[b0,b1,b2,a1,a2]`. It returns `1` certified, `0` condition failed, `-1` invalid, or `-3` budget-limited unknown; it may throw allocation exceptions. The `extern "C"` wrapper `dexted_dsp_cascade_f32` catches exceptions and returns `-2`. Neither native entry point generates a serialized certificate; the Python certificate/independent rational checker is still required for portable inspectable proof objects. Never convert negative return codes to bool.

### Scope and security

Only fixed real coefficient LTI transfer functions are covered. No rounding error accumulated by runtime filter processing, nonlinear saturation, graph/device safety, audio-quality effect or Crouzeix theorem is certified. This offline arbitrary-precision code is **not hardened against untrusted remote proof-object DoS**. Place application-specific execution and memory limits around external inputs.

### Exact single-biquad peak-location contract

```python
from dexted_dsp import Biquad, localize_peak, inspect_biquad
f = Biquad.from_coefficients([2**-14, 0, -2**-14, 0, 1-2**-14], precision='float32')
region = localize_peak(f, isolation_bits=32, fs=48000)
assert region.cosine_intervals == (('0', '0'),)
report = inspect_biquad(f, precision='float32', fs=48000)
assert report.peak_region is not None
```

The exact guarantee is in `c=cos(omega)`; the displayed 12,000 Hz value is not a rigorously outward-rounded frequency enclosure. Read the [full mathematical derivation](../research/proofs/peak-localization.md).

### Installed native CMake consumer

Use `python tools/native_consumer_smoke.py --build-dir build` after a Release CMake build. It installs the library to a temporary prefix, configures a *separate* project with `find_package(DextedDSP CONFIG REQUIRED)`, links the shared C ABI and runs biquad and compensated SOS checks. CI tests this consumer on Linux, macOS and Windows (subject to actual hosted build results).
