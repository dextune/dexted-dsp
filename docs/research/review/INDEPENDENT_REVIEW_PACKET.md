# Open technical review request — Dexted DSP

**Status: review REQUEST, no external approval yet.** Engineers, DSP
researchers and formal verification specialists can reproduce these tasks
without access to proprietary coefficients or modifying the repository.

## Exact mathematical claims to examine

1. A finite normalized real biquad has a strictly Schur-stable denominator iff
   its quadratic Jury conditions hold. Check handling of nonminimal sections,
   signed zero, float32 conversion and very small finite values.
2. For each section, Fourier magnitude squared becomes a quadratic rational
   polynomial in `c=cos(ω)`; stable denominators are strictly positive there.
   Therefore the full cascade strict gain condition reduces to positivity of
   a polynomial of degree at most twice the section count on `[-1,1]`.
3. Independently compare integer Bernstein-cover verification (the shipped
   producer/checker), `sympy.Poly.count_roots(-1,1)` (the symbolic audit) and
   any third-party exact/interval implementation on boundary and generated
   cases. Strict equality/tangency must fail; unknown must never pass.
4. Test that altered input coefficients, precision, max gain, sample rate,
   wrong proof envelopes and tampered interval-cover witnesses are rejected.
   Hash binding is not a signature; arbitrary hostile proof objects are NOT
   promised to be safe to deserialize or verify without resource limits.
5. Examine the peak-gain enclosure and `cos(ω)` peak-location union. Hz values
   are NOT currently rigorous bounds. Flag any undocumented branch that drops
   a true global maximizer, admits a false bound, or conflates coefficient
   semantics with actual hardware arithmetic.

## Proposed reviewer exercise

```bash
python -m pip install . 'sympy==1.14.0'
python -m unittest discover -s tests -v
python benchmarks/suites/eq_catalog.py --check-sha256 873ce092e2fe7fa7e8d16c8fd50b251f377c05c4a02ed267e6917d7599a69120
python tools/sympy_oracle_audit.py --count 64 --split holdout --check-reference validation/oracle/reference_holdout_64.json
python examples/eq_release_pipeline.py --max-gain 2.0
```

Submit a report containing: reviewer affiliation only if they consent,
repository SHA, toolchain versions, the exact failing coefficient hex values,
strict binary64 threshold, predicted and observed statuses, reproducible
smallest counterexample, scope of reviewed claims, and explicit limitations.
A confirmed math mismatch blocks release. Do not report benchmark performance
numbers from different contracts as universal speedups.

This packet does **not** request the reviewer's endorsement of the separate
`openai/math` manuscript. That research integration is conditional and not
part of the existing executable gain decision.

**Open work:** licensed field datasets; external reviewers; independent host
benchmark replication; hardened proof-object resource limits; a practical
OpenAI-math research proof-of-concept; user adoption evidence.
