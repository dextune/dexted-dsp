# Python interface

Install with `python -m pip install .` at repository root. The public import is `dexted_dsp`.

```python
from dexted_dsp import Biquad, certify, verify_biquad, from_sos, certify_cascade, verify_cascade
b = Biquad.from_coefficients([0.25, 0., 0., -0.5, 0.], precision='float32')
r = certify(b, max_gain=1.0)
assert r.certified and verify_biquad(r.as_dict(), b, max_gain=1.0)
```

- `Biquad` supports finite binary64 inputs. `from_coefficients(..., precision='float32')` rounds coefficients explicitly before analysis.
- `certify(biquad, max_gain=...)` tests strict denominator stability and strict peak-gain limit.
- `certify_cascade(sections, ..., max_depth=48, max_nodes=20000)` uses a resource-bounded dyadic positivity cover and may report `unknown`.
- `verify_biquad` and `verify_cascade` independently validate a claimed successful certificate against the given input.
- The API does **not** return an exact peak-gain value or audio signal; the `max_gain` argument is a user-supplied threshold.

[Full API semantics](API.md) · [Usage guide](../en/getting-started/USER_GUIDE.md) · [Tests](../en/guides/TESTING.md)

## New offline user-facing inspection

[Precise API semantics, strict thresholds, gain enclosures, certificate verification and examples](../product/inspection.md).


## Peak-localization API

`from dexted_dsp import localize_peak, PeakRegion`. Certified output is `PeakRegion.cosine_intervals` as rational strings. Optional `frequency_hz_approx` must never be treated as an outward-rounded certified Hz interval. [Exact derivation](../research/proofs/peak-localization.md).
