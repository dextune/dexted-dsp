# Deploy an actual EQ workflow, not a marketing-only demo

This is an executable, application-shaped **three-band parametric EQ design**
using the documented W3C Audio EQ Cookbook equations. Its chosen parameters
are synthetic; it has **not** been installed in a commercial audio device or
independently audited.

Reference: https://www.w3.org/TR/2021/NOTE-audio-eq-cookbook-20210608/

## One command

```bash
python -m pip install .
python examples/eq_release_pipeline.py --max-gain 2.0 \
  --proof /tmp/dexted-eq-proof.json --report /tmp/dexted-eq-report.md
```

The example constructs 180 Hz (-3 dB), 1600 Hz (+4 dB), and 8400 Hz (-2 dB)
peaking bands at 48 kHz; these are **design labels**, not certified peaks.
It normalizes coefficients, explicitly rounds the five coefficients per
section to binary32, sends the final SOS to `inspect_sos`, and independently
rechecks any successful `inspection/v2` certificate using `verify_inspection`.

The strict limit is a *linear amplitude gain*, not dB. `--max-gain 2.0` means
a bound strictly less than two. The output JSON includes source scope and a
rational peak-gain interval where the proof procedure obtains one; Hz display
is illustrative, not a certified frequency interval. Nothing is processed or
rendered as audio.

A rejected filter exits nonzero; `unknown` also exits nonzero. No serialized
PASS may be trusted unless its exact input is rechecked. Optional proof/report
paths are never silently overwritten.

## Evidence and limitations

- The W3C formulas are *design* formulas, not guarantees that an arbitrary
  quantized implementation is safe. Dexted checks the final represented
  coefficients in an ideal fixed linear transfer function.
- [Audit against independent exact rational polynomial real-root counting](../../benchmarks/suites/EQ_CATALOG_PROTOCOL.md).
- [Mathematical proof obligations and external reviewer checklist](../research/review/INDEPENDENT_REVIEW_PACKET.md).
- The framework does not certify limit cycles, coefficient updates,
  rounding in runtime accumulators, audio quality or hardware safety.
