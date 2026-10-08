# Candidate OpenAI mathematical result: bounded matrix-polynomial extension

**State:** research hypothesis only; no shipped runtime, formalized theorem import, speed claim or downstream safety claim.

Pinned review source: `openai/math@adc7f1241b42e322a6451854ab7e4b4c146bf78a` and the September 2026 manuscript *A direct proof of the complete Crouzeix inequality* (see [source map](../openai-math/REFERENCES.md)). Manuscript existence does not imply an independent verification of proof validity.

## Proposed bounded-domain research

For a **specified finite-dimensional matrix A** and a **polynomial p**, evaluate whether a rigorously verified inequality of the form `||p(A)|| ≤ C · max_{z in W(A)} |p(z)|` can produce a conservative operational bound on a restricted non-normal state-transition model. C is a *hypothesized/theorem-dependent constant*, not certified by this project's shipped code. The numerical range W(A), its approximation error and stable finite-precision coefficients require separate verified enclosures.

**Do not confuse** general matrix polynomial bounds with the current real SISO biquad/SOS frequency response. Existing integer Jury/Bernstein predicates do not depend on the manuscript and need no matrix theorem.

## Required proof obligations before any code release

1. Independent mathematical reviewer confirms a precise theorem version, constant and conditions; pin text and lemma identifiers rather than trusting a repository title.
2. Restrict A to an explicit admissible family (fixed dimension, coefficient domain, bounded norm); document exclusions such as time-varying coefficients and arbitrary DNNs.
3. Provide independently checked interval enclosure for `max_{z∈W(A)} |p(z)|`; a dense polygon/grid is not a certificate without rounding and covering proofs.
4. Compare the resulting bound with existing SISO and matrix norm upper bounds, with counterexamples and meaningful cases in which it is tighter or materially easier to compute.
5. Build separate `experimental/` code, fail closed on inability to verify assumptions, and write independent checker, tests and measured data before proposing a stable API.

**Stop criterion:** if theorem validation or computable numerical-range enclosures are unachievable, or the resultant bound is uncompetitive on real supported models, do not claim the result is used by Dexted DSP. Exact-DFT candidates should be evaluated separately under the computational model of the manuscript, not presented as a universal faster FFT.
