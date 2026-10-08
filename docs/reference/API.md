# API reference / integration contract

## Python

`Biquad(b=(b0,b1,b2), a=(1,a1,a2))`: immutable, finite binary64 values, a0 exactly one.
`Biquad.from_coefficients(values, precision="float32"|"float64")`: five coefficients;
explicit round-to-binary32 conversion when requested; overflow is an error.
`from_sos(rows, precision=...)`: six-column SciPy layout; a0 must be one.

`certify(biquad, max_gain=1.0) -> BiquadCertificate` returns `status`, `certified`,
`denominator_stable`, the threshold, exact integer sign witnesses and `as_dict()`.
The actual H-infinity maximum, critical frequency and headroom margin are NOT returned.
All comparisons are strict. Input errors raise `ValueError` (wrong object type: `TypeError`).

`certify_cascade(sections, max_gain=1.0, max_depth=48, max_nodes=20000) -> dict`:
status is `certified`, `condition_failed`, `unknown`, or `denominator_not_schur`.
Maximum public budgets: depth 128, nodes 100,000; maximum 32 sections.
`condition_failed` identifies an exact nonpositive value of the strict-gain gap.
`unknown` is a resource-limited lack of proof. Neither is a general instability claim.

`verify_biquad(report, expected_biquad, max_gain=1.0) -> bool` independently redoes the
exact-rational decision. It checks input/threshold binding; informative integer witness
strings are not used as a trust anchor.
`verify_cascade(report, expected_sections, max_gain=1.0) -> bool` rebuilds and verifies
the dyadic cover with rational arithmetic. Only a claimed PASS can be verified.

### Input semantics

Decimal source literals are first converted to binary64 by Python/JSON parsing.
That resulting value is certified exactly. `precision="float32"` explicitly rounds
it again before certification. Tiny nonzero values may become zero during that
requested deployment conversion. Signed zero has the same mathematical value, but
hex bindings retain its sign to detect serialization changes.
The threshold stays binary64, even for binary32 coefficients.
No automatic gain correction, normalization or double-to-float32 conversion is hidden.

For PyTorch or FLAMO, export the final constant coefficients and construct Biquad
objects yourself. No autograd/graph adapter is shipped. For SciPy, `from_sos` needs
no SciPy import. JSON is the only input format supported by the CLI.

## CLI

```bash
dexted-dsp check input.json --output proof.json
dexted-dsp check cascade.json --max-depth 48 --max-nodes 20000
dexted-dsp verify input.json proof.json
```

`--output` never overwrites the input path. JSON inputs are limited to 1 MiB.
No file is executed, compiled or sent over the network by the CLI.
Exit 0: certified/verified; 1: not certified/invalid certificate;
2: malformed input/error; 3: unknown. Shell/CI must accept ONLY zero.

## C++

`dexted_dsp::certify_biquad_f32(const float*, double gamma) -> int`
is a header API for binary32 coefficients, gamma binary64.
Returns 1 (both conditions hold), 0 (one or both conditions fail), -1 (invalid input).
It does not provide a detailed failure classification or proof metadata.
The C++ header may throw allocation exceptions. Do not compile with fast-math,
which can invalidate finite-value checks.

`dexted_dsp_biquad_f32`, `dexted_dsp_batch_f32` are the C ABI; they catch internal exceptions
and return/store -2. Batch callers own adequately sized buffers. Check errors explicitly;
**never convert the raw int to bool** because negative error codes are truthy in C/C++.

### CMake consumer

```bash
cmake --install build --prefix "$PWD/local-install"
```

```cmake
find_package(DextedDSP CONFIG REQUIRED)
add_executable(my_check main.cpp)
target_link_libraries(my_check PRIVATE DextedDSP::dexted_dsp)
```

Pass `-DCMAKE_PREFIX_PATH=/path/to/local-install` when configuring the consumer.
Boost headers must be available to the consuming build.

### Optional Python native loading

```python
from pathlib import Path
from dexted_dsp import Biquad
from dexted_dsp.native import NativeBiquad
engine = NativeBiquad(Path("build/libdexted_dsp.so").resolve())  # Linux example
f = Biquad.from_coefficients([.25, 0, 0, -.5, 0], precision="float32")
assert engine.certify(f, 1.0)
```

Library filename differs on macOS/Windows and multi-configuration generators.
The loader requires an explicit existing absolute trusted path and never downloads
binaries. It refuses coefficients that would require implicit float32 conversion.

## Resource and safety boundaries

Arbitrary-precision code can allocate significant memory for adversarial values.
Certificate checks are not a hardened network sandbox. No sound is played and no
hardware is controlled. `CERTIFIED` applies only to the documented mathematical model.

## High-level inspection and peak intervals (unreleased)

See [the detailed inspection contract](../product/inspection.md). New functions `inspect_biquad`, `inspect_sos`, `inspect_cascade`, `verify_inspection`, `bound_peak_gain`, `bound_sos_peak_gain` preserve existing `certify`/`verify_biquad`/v1 semantics. `GainBounds.lower_ratio` and `.upper_ratio` are proven rational enclosures; `frequency_region_hz` is currently null. New `dexted-dsp inspect ... --report report.md` and `demo hidden-peak` commands are available in source. New native `dexted_dsp_cascade_f32` has error-aware integer returns and **does not** serialize a proof object.
