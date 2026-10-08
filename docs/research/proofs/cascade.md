# Cascades: exact polynomial positivity with an inspectable certificate

**Status:** sufficient certification procedure with exact integer arithmetic.
A finite budget may return UNKNOWN. Not a complete real-root/positivity decision algorithm.

## Statement

For fixed real biquads H_j whose individual denominators are strictly Schur stable,
write N_j(c), D_j(c) for the squared-magnitude polynomials in c=cos(omega).
Then the strict gain bound for the cascade is equivalent to positivity of

$$Q(c)=\gamma^2\prod_jD_j(c)-\prod_jN_j(c),\qquad c\in[-1,1].$$

Every denominator factor is positive on this interval. Multiplication by the
common positive binary denominator preserves all signs. This constructs an integer
polynomial of degree at most twice the number of sections.

The difference from multiplying individual suprema is substantive:
`sup |H1 H2|` may be much smaller than `sup |H1| * sup |H2|`.
A frequency-sampled method that multiplies responses at the SAME frequencies already
preserves compensation; do not misdescribe it as the product-of-suprema baseline.

## Bernstein certificate

Set t=(c+1)/2. Represent Q(2t-1) in degree-n Bernstein form:

$$Q(2t-1)=\sum_{i=0}^n\beta_i {n\choose i}t^i(1-t)^{n-i}.$$

The basis functions are nonnegative and sum to one. Consequently all beta_i>0
is sufficient to prove Q>0 on that interval. Some beta_i<=0 is NOT itself a failure.

Power coefficients alpha_k are converted using

$$\beta_i=\sum_{k=0}^i\alpha_k\frac{{i\choose k}}{{n\choose k}}.$$

Multiplying by the least common multiple of the binomial denominators keeps the
producer entirely integral. De Casteljau subdivision at 1/2 creates exact child
coefficients; each child is multiplied by a positive power of two instead of dividing.

The producer recursively accepts intervals with all-positive coefficients.
A nonpositive endpoint value supplies an exact witness of failure of strict positivity.
Otherwise it subdivides. On an exhausted node/depth budget it returns UNKNOWN,
never CERTIFIED. Strictly positive polynomials can be resolved with sufficiently
fine subdivisions; exact tangencies may remain UNKNOWN unless encountered as an endpoint.

## Proof object and checker

A successful proof contains a dyadic cover `[[index,depth], ...]` of t in [0,1], where
an interval is `[index/2^depth,(index+1)/2^depth]`. The checker:

1. Binds to the CALLER's exact deployed coefficients and requested threshold.
2. Rebuilds the polynomial with independent Fraction expressions and checks denominators.
3. Checks that intervals form a gap-free, overlap-free cover of [0,1].
4. Affinely transforms the polynomial on each interval and checks all rational Bernstein coefficients.

For `[lo,hi]` in t, local u in [-1,1] maps to c=(hi-lo)u+(hi+lo-1).
All checker calculations are exact rational calculations.
The producer's status flag, cover and stored bound are not trusted on their own.
There are explicit resource limits, but this checker is not a hostile-input sandbox.

## Scope and complexity

The current interface accepts one to 32 sections. Defaults are depth 48 and 20,000 nodes.
Certification time can grow rapidly with degree, coefficient size and proximity to zero.
The lack of a proof is NOT evidence of an unstable network. Runtime arithmetic,
nonlinearities, changing coefficients and cancellations of unstable internal sections are excluded.

`examples/compensating_cascade.json` has total transfer function exactly 0.75 and provides
an easily audited demonstration, not a perceptual-quality benchmark.

Implementation: `cascade.py`; checker: `verify.py`; rational algebra: `reference.py`.
