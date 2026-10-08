# G3 evidence: W3C Audio EQ design catalog and independent exact oracle

**Status:** reproducible, deterministic, **synthetic design study**. It is NOT a
licensed product coefficient dataset, a user study, a device certification, or
an independent human mathematical review. The main v0.1.0 and 25-case pilot
records remain separate, unchanged datasets with different boundaries.

## Input protocol (predeclared before comparing the shipped certifier)

- **Design reference:** W3C Working Group Note, *Audio EQ Cookbook*, 2021-06-08,
  https://www.w3.org/TR/2021/NOTE-audio-eq-cookbook-20210608/ (selected peaking,
  notch, lowpass and highpass coefficients).
- **Generator:** `benchmarks/suites/eq_catalog.py`. `seed=20261008`,
  `count=1200`; Python `random.Random`, 48 kHz, 1-2 SOS per case, input sample
  types balanced by index, f0/Q ranges explicitly encoded in generator.
- **Represented data:** normalize `a0=1`, then round each coefficient to IEEE-754
  binary32 via `struct.pack('!f')`; the resulting exact binary fractions are
  what the certifier and symbolic oracle evaluate. No automatic rescaling in
  the verifier. Gain thresholds stay binary64.
- **Split:** `SHA256(case ID).first_byte < 64` denotes holdout; the split and
  RNG seed are invariant and do not use observed certification results. The
  exact 64-case audit draws **balanced families** from that holdout with seed
  `20261008` and retains all selected case IDs in the reference record.
- **Whole catalog (UTF-8 canonical JSON):** SHA256
  `873ce092e2fe7fa7e8d16c8fd50b251f377c05c4a02ed267e6917d7599a69120`.
  The hash depends on the Python standard-library libm floating-point results;
  cross-platform differences must be surfaced, not normalized away.
- **Reference holdout file:** `validation/oracle/reference_holdout_64.json`.
  It contains 64 independent expected decisions; exactly 25 satisfy and 39
  violate the requested strict inequality in this deliberately mixed set.
- **Full 1,200-case symbolic *reference-only* run (local Linux, SymPy 1.14.0):**
  476 pass, 724 fail. **These are synthetic design outcomes conditional on
  thresholds, not DSP product bug rates.** This is not a measured runtime
  comparison and does not establish any shipped-implementation agreement.

## Independent mathematical method

`tools/sympy_oracle_audit.py` reconstructs numerator and denominator squared
magnitudes as exact rational polynomials in `c=cos(ω)` using an independent
expression of the Fourier magnitude. It applies strict per-section Schur
conditions; for stable sections it forms

\[P(c)=\gamma^2\prod_j D_j(c)-\prod_j N_j(c)\]

and uses **SymPy's exact closed-interval real-root count** (`Poly.count_roots`)
on `[-1,1]`. If `P` has any root there, strict positivity fails (including
endpoint equality and tangency). If no root exists, exact evaluation at zero
determines the constant sign. It does **not** use the project's Bernstein
subdivision and does not use numerical frequency samples as truth.

This is an independent algorithm and dependency, not independent mathematical
publication, formal proof checking, a security-hardening review, or device-level
floating-point safety certification.

For the shipping certifier, any `certified` verdict MUST match the oracle and
have a reverified certificate. A `condition_failed` must match a strict-gain
failure. A resource-limited `unknown` is recorded, never treated as a pass.
The reference file is not regenerated silently during CI.

## Reproduce (no network during execution except optional installation)

```bash
python -m pip install . 'sympy==1.14.0'
python benchmarks/suites/eq_catalog.py --count 1200 --check-sha256 873ce092e2fe7fa7e8d16c8fd50b251f377c05c4a02ed267e6917d7599a69120
python tools/sympy_oracle_audit.py --count 64 --split holdout --check-reference validation/oracle/reference_holdout_64.json
python tools/sympy_oracle_audit.py --count 1200 --split all --oracle-only
python examples/eq_release_pipeline.py --max-gain 2.0
```

The separate GitHub CI `independent-math-oracle` job additionally tests the
exported coefficients and calls the actual production certificate verifier.
Report mismatches as bugs with exact serialized SOS, threshold, deterministic
case ID and source/fixture digest. Neither script downloads user audio or
performs audio processing.

## Outstanding 9.5 gates

This does NOT close the project plan's requirements for a **third-party**
proof/code audit, 1,000+ **field/appropriately licensed product** exports,
independent hardware performance replication, actual users, or deployment.
Real-life data must only be added with ownership/permission, provenance and
explicit privacy checks. Do not label this generated catalog "real-world".
