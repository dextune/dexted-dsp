# Exact biquad gain test — derivation and implementation contract

**Status:** elementary mathematical derivation plus executable exact-arithmetic tests.
Not a new theorem, not Lean-verified, not an independent external audit.
The production predicate does not depend on Crouzeix's inequality.

## 1. Object being certified

For real, fixed coefficients and a positive real threshold gamma,

$$H(z)=\frac{b_0+b_1z^{-1}+b_2z^{-2}}{1+a_1z^{-1}+a_2z^{-2}}.$$

We decide the conjunction of:

1. all roots of `z² + a1 z + a2` lie strictly inside the unit disk;
2. `sup_{omega in [0,pi]} |H(exp(i omega))| < gamma`.

Real coefficients give conjugate symmetry, so `[0,pi]` covers the whole circle.
A canceled unstable section is deliberately rejected: this is not a minimal-transfer-function
stability classifier. The supplied denominator represents the intended internal section.

A finite Python float is its exact binary rational value, not the intended decimal
number before conversion. Explicit float32 conversion occurs before any certification.
The C++ predicate accepts binary32 coefficients and binary64 gamma. `a0` must already be one.

## 2. Second-order stability

For a real monic quadratic the strict Schur/Jury conditions are

$$|a_2|<1,\qquad 1+a_1+a_2>0,\qquad 1-a_1+a_2>0.$$

A direct justification uses `z=(1+s)/(1-s)`, which maps the open left half-plane
to the open unit disk. After multiplying by `(1-s)^2`, the polynomial becomes

$$(1-a_1+a_2)s^2+2(1-a_2)s+(1+a_1+a_2).$$

Under the listed inequalities all three coefficients are positive. A real quadratic
with positive leading, linear and constant coefficients has both roots in the open
left half-plane (negative real roots, or a conjugate pair with negative real part).
Conversely, a real stable monic disk polynomial has `|a2|<1`; its values at +1 and -1
are positive by factoring over real roots or conjugate pairs. This proves necessity.
Strict endpoints exclude roots at +1 and -1 and avoid the bilinear transform's boundary case.

## 3. Frequency response becomes a quadratic

Let `c=cos(omega)`. For any real x,y,z,

$$|x+ye^{-i\omega}+ze^{-2i\omega}|^2
=(x-z)^2+y^2+2y(x+z)c+4xz c^2.$$

This follows by expanding the squared modulus and using `cos(2 omega)=2c²-1`.
Let N(c) and D(c) be the respective numerator and denominator squared-magnitude polynomials.
Strict Schur stability ensures D(c)>0 for every c in [-1,1]. Therefore

$$\sup_\omega |H(e^{i\omega})|<\gamma
\iff Q(c)=\gamma^2D(c)-N(c)>0\quad\forall c\in[-1,1].$$

The equivalence between pointwise strict positivity and a strict supremum follows
from continuity and compactness. Set `Q(c)=A c²+B c+C`.

Its minimum is among the two endpoints and, only when `A>0` and `|B|<2A`, the interior vertex.
Thus the exact conditions are

$$A-B+C>0,\quad A+B+C>0,$$

and, when that vertex is internal,

$$4AC-B^2>0.$$

At a boundary vertex, the endpoint test already covers it. Concave/linear/constant
cases require only endpoint checks. No division by a nearly zero floating number
and no trigonometric sampling appear in the decision.

## 4. Integer implementation

Every finite binary float equals an integer divided by a power of two. Choose the
largest denominator S across the five coefficients, so each coefficient has an exact
integer numerator over S. Gamma is independently represented as `gn/gd`.

Compute the squared-magnitude polynomials on these integer numerators, then use

$$Q_{\rm int}(c)=g_n^2D_{\rm int}(c)-g_d^2N_{\rm int}(c).$$

This is `gd² S²` times Q(c), a positive scaling, so all signs are unchanged.
Jury uses `S-|a2_int|`, `S+a1_int+a2_int`, `S-a1_int+a2_int`.
Quadratic signs use arbitrary-precision integers. JSON integers are emitted as decimal
strings to avoid JavaScript's binary64 integer limit.

This has a fixed number of arithmetic operations for a biquad, but **not constant bit
complexity**: arithmetic cost depends on operand bit length. It is an offline method.

## 5. Counterexample to naive sampling

Let alpha=2^-14 and

$$H(z)=\frac{\alpha(1-z^{-2})}{1+(1-\alpha)z^{-2}}.$$

The section is strictly stable. At `omega=pi/2`, `z^-2=-1`, hence `|H|=2` exactly.
A 1,024-point inclusive uniform grid does not contain pi/2 and may substantially
underestimate the peak. This is a weakness of using sampling as a certificate,
not a defect in a library whose stated task is only response sampling.

The accompanying plot is illustrative; the exact evaluation above is the proof.

## 6. Meaning of results

`certified`: both strict properties hold in the stated mathematical model.
`gain_limit_not_met`: stable denominator, but the requested gain limit fails or is met with equality.
`denominator_not_schur`: the supplied section does not have all strict stable poles.
None of these outputs by itself proves safety of a device or an arbitrary feedback network.

`verify_biquad` binds the report to caller-supplied coefficients/gamma, then independently
recomputes the exact-rational minimum. It does not trust the reported flags or integer witness.
This verifier is another implementation within the project, not an external reviewer.

## 7. Traceability

- Algorithm: `src/dexted_dsp/biquad.py`, `cpp/include/dexted_dsp/biquad.hpp`.
- Independent arithmetic: `src/dexted_dsp/reference.py`.
- Input semantics: `src/dexted_dsp/model.py`.
- Proof recheck: `src/dexted_dsp/verify.py`.
- Regression: `tests/test_dexted_dsp.py`, C++ tests, benchmark IEEE fixtures.
- Context and related full-order numerical methods: [references](../REFERENCES.md).
