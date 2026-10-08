# Sources and related work

Source access checked on 2026-10-07. Links identify context; none implies endorsement.

## Mathematical context

1. Michel Crouzeix and César Palencia, **The numerical range as a spectral set** (2017).
   Primary paper: https://arxiv.org/abs/1702.00668 . Establishes complete constant `1+sqrt(2)`.
2. OpenAI, **A direct proof of the complete Crouzeix inequality** (2026-09-26).
   The source theorem was read at a fixed repository commit:
   https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex .
   Used only as an explicitly conditional assumption in `math/crouzeix.md`.
   No general independent proof verification is claimed.
3. The elementary second-order stability/quadratic and Bernstein arguments needed
   by executable code are derived in full in `math/biquad.md` and `math/cascade.md`.
   They are classical methods, not results invented in this project.

## Existing numerical tools: avoid overclaiming novelty

4. SciPy `signal.freqz`, official documentation:
   https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html .
   Computes response values at requested frequencies; it is not advertised as an exact
   continuum proof. The optional Python benchmark calls the installed version directly.
5. Python Control `linfnorm`, official documentation:
   https://python-control.readthedocs.io/en/latest/generated/control.linfnorm.html .
   A general linear-system L-infinity norm estimate with a numerical tolerance; related
   Slycot routine `ab13dd`. This release does not benchmark it or claim superiority to it.

## Implementation and distribution

6. Boost.Multiprecision `cpp_int`, official documentation:
   https://www.boost.org/doc/libs/latest/libs/multiprecision/doc/html/boost_multiprecision/tut/ints/cpp_int.html .
   Arbitrary-precision integer backend, not a fixed-width integer.
7. Python Packaging User Guide:
   https://packaging.python.org/en/latest/tutorials/packaging-projects/ and
   https://packaging.python.org/en/latest/guides/writing-pyproject-toml/ .
   Used for `pyproject.toml`, wheel/sdist build and local installation layout.

## Artifact lineage

8. Earlier MIT-licensed generated research archive `av_certified_research_v2.zip`.
   Integer biquad decoding/predicate and Bernstein subdivision were adapted into a
   public API. Earlier benchmarks and media studies are not copied as current results.
   See `NOTICE.md`. No private Project data, third-party media or credentials are bundled.
