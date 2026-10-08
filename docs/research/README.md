# Mathematics and research provenance

The executable **exact-frequency** filter predicate and cascade verification are classical, locally derived techniques. OpenAI's manuscript collection is a **research reference** for a conditional generalization, not a runtime dependency or a third-party audit.

## Proof notes

- [Exact biquad stability and gain decision](proofs/biquad.md)
- [Cascaded filters and finite interval covers](proofs/cascade.md)
- [Conditional Crouzeix matrix-polynomial extension](proofs/crouzeix.md)

## External sources and review trail

- [Literature references](openai-math/REFERENCES.md)
- [Machine-readable upstream source revision and attribution](provenance/sources.json)
- [English research provenance and engineering process](../en/development/PROVENANCE.md)
- [한국어 연구 출처](../ko/development/PROVENANCE.md)

The research notes do not constitute a proof-assistant or independent safety audit. The runtime benchmark uses neither a faster FFT from OpenAI nor the general Crouzeix result.

## New bounded-gain mathematics and future research

- [Exact rational peak-gain enclosures](proofs/peak-enclosure.md) — implemented offline for fixed real filters
- [Pinned OpenAI matrix-theorem applicability research](design-notes/openai-math-adapter.md) — hypothesis only, not runtime


- [New: exact biquad peak-location region derivation](proofs/peak-localization.md) — integer/rational stationary-point isolation, no certified Hz interval

## Independent-algorithm review path

The [SymPy rational real-root auditor](../../tools/sympy_oracle_audit.py) is a separate algorithm from the shipped Bernstein certifier. [Review packet](review/INDEPENDENT_REVIEW_PACKET.md). It is **not** independent external human mathematical validation or formal verification.
