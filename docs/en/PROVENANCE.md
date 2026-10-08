# Research provenance and OpenAI attribution

[English](../en/PROVENANCE.md) · [한국어](../ko/PROVENANCE.md) · [简体中文](../zh-CN/PROVENANCE.md) · [日本語](../ja/PROVENANCE.md)

[Dexted DSP](../../README.md)

## 1. Three different meanings of “based on OpenAI”

**Research source:** the investigation began with the [`openai/math` collection][OAI-README]. **Conditional theorem:** a specific OpenAI Crouzeix manuscript supplies an assumption for one research note. **AI-assisted engineering:** this repository was assembled through an interactive research/programming workflow. These are distinct; none implies that the runtime is an OpenAI implementation, that OpenAI audited it, or that the measured optimization is a new OpenAI theorem.

The upstream collection states that its manuscripts have different verification states. A source being in that repository is not sufficient to label a downstream DSP program formally verified [OAI-README].

## 2. Pinned upstream sources

| ID | Exact source and location | How it was used |
|---|---|---|
| OAI-README | `README.md` at commit `adc7f1241b42e322a6451854ab7e4b4c146bf78a` | Collection provenance and verification warning |
| OAI-325 | *A direct proof of the complete Crouzeix inequality*, 2026-09-26; `build/main.tex`, §1, theorem labelled `thm:main`; definitions of `W(A)` and `P[A]` | Assumed complete constant-two bound for matrix-valued polynomials; conditional note only |
| OAI-DFT | *An explicit power saving for the exact discrete Fourier transform*, 2026-09-25; `build/sections/introduction.tex`, computational model and caveat after `cor:decimal` | Scoping decision: not a floating-point FFT implementation or measured speedup |

The full pinned URLs and Git blob hashes are recorded in [sources.json](../provenance/sources.json). Upstream theorem text was checked as LaTeX source; no Lean kernel was run. The dates identify the referenced manuscripts, not a claim about a later upstream revision.

[OpenAI main theorem source][OAI-325] · [OpenAI DFT model and limitations][OAI-DFT]

The Crouzeix assumption is

$$\|P[A]\|_2\le 2\max_{z\in W(A)}\|P(z)\|_2,\qquad P[A]=\sum_k A^k\otimes B_k.$$

The **matrix-valued/complete** statement matters for noncommuting channel coefficient matrices. The reference comparison is the complete constant `1+sqrt(2)` in Crouzeix–Palencia (2017) [CP-2017]. No independent verification of the general OpenAI proof is claimed here.

## 3. What actually depends on that theorem?

| Repository component | Mathematical dependency | Status |
|---|---|---|
| `src/dexted_dsp/biquad.py` and `cpp/include/dexted_dsp/biquad.hpp` | Elementary Schur/Jury conditions; quadratic positivity; exact binary-rational arithmetic | Executable, independent of OpenAI's new theorem |
| `src/dexted_dsp/cascade.py` | Product of magnitude-squared polynomials; Bernstein positivity/subdivision | Executable Python; sufficient, resource-limited certificate |
| `reference.py` and `verify.py` | Separately expressed rational arithmetic and interval-cover checks | Rechecking, not external institutional verification |
| `benchmarks/kernels.cpp` | Integer predicate, sampled-response baseline, float64 algebraic baseline | Benchmarked; no Crouzeix dependency |
| [Conditional research note](../math/crouzeix.md) | Assumes OAI-325 for general base matrices | Documentation only; no production API |

The classical methods are not claimed as new inventions. The engineering contribution is the deployment-value contract, exact integer predicates, inspectable proof objects, independent-expression rechecking, interfaces, and reproducible comparisons.

## 4. Development process and evidence

This is a public account of the work products, not an undocumented claim about unlimited optimization.

| Stage | Decision or implementation | Evidence in this release |
|---|---|---|
| Scope | Explore signal-processing connections in the manuscript collection; distinguish asymptotic theory from deployable algorithms | Pinned source registry; this document |
| Separate assumptions | Keep general Crouzeix extensions conditional and out of the production engine | `docs/math/crouzeix.md`; runtime import graph |
| Choose a tractable contract | Fixed real second-order sections; explicit deployed precision; strict gain threshold | `model.py`; mathematical guides |
| Build exact predicates | Convert binary rationals to integers; test stability, endpoints and any interior quadratic minimum | `biquad.py`; native header |
| Extend to cascades | Prove whole-chain polynomial positivity without discarding frequency compensation | `cascade.py`; `verify.py` |
| Test independently expressed arithmetic | Compare with `Fraction`; bind certificates to expected inputs; reject tampering and unknowns | `tests/test_dexted_dsp.py` |
| Review benchmark fairness | Keep float64 algebraic baseline; cache grids before timing; allow early exits; validate inputs | `benchmarks/run.py`, `kernels.cpp`, `protocol.json` |
| Retain intermediate runs | Keep earlier review and input-validation measurements rather than choosing only favorable timings | `validation/benchmark_before_review*`, `benchmark_before_input_validation*` |
| Package | Python/C++/CLI interfaces, installation tests and local logs | Original `validation/summary.json` and build logs |
| Documentation refresh | Translate core docs, trace attribution, audit saved measurements, rerun command examples and a small benchmark smoke test | `validation/docs_refresh/`; source hashes unchanged |

The historical archive hashes are in [sources.json](../provenance/sources.json). Earlier conversational figures, media experiments, or benchmark revisions are **not** promoted into current benchmark claims. Current README numbers come solely from `benchmarks/results/benchmark.json`.

## 5. Conditional extensions: what they do and do not show

With the OAI-325 assumption, separate tensor axes give a factor `2^r` for `r` nonnormal axes; normal axes cost 1. A common fixed base with changing matrix-polynomial coefficients gives a product bound `2 q^T`, not `(2q)^T`. A relative state perturbation of size `epsilon` yields the sufficient decay condition `q+2 epsilon<1`.

Relative to the same argument using `1+sqrt(2)`, the sufficient perturbation radius increases by `(1+sqrt(2))/2-1`, about **20.71%**. This is an algebraic comparison of two sufficient bounds. It is not measured sound quality, image quality, maximal robustness, or a general certificate for arbitrary time-varying systems. The detailed proof and assumptions remain in the [research note](../math/crouzeix.md).

## 6. Attribution and reuse boundaries

No upstream OpenAI/ADAC implementation, manuscript source, media, weights, or private credentials are vendored. References are links, not software endorsements. The MIT notice of the earlier generated implementation is preserved in [LICENSE](../../LICENSE) and [NOTICE](../../NOTICE.md). Boost is an external native-build dependency; NumPy/SciPy/Matplotlib are optional benchmark tools.

The full general Crouzeix proof, soundness of all compiler optimizations, and physical-device behavior have not been independently audited. Removing the conditional research note leaves the exact biquad/cascade runtime and its benchmark results mathematically unchanged.

[OAI-README]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/README.md
[OAI-325]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex
[OAI-DFT]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex
[CP-2017]: https://arxiv.org/abs/1702.00668
[SCIPY-FREQZ]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html
[PYPA]: https://packaging.python.org/en/latest/tutorials/packaging-projects/
