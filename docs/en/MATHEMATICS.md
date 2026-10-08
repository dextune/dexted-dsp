# Mathematical guide and implementation boundaries

[English](../en/MATHEMATICS.md) · [한국어](../ko/MATHEMATICS.md) · [简体中文](../zh-CN/MATHEMATICS.md) · [日本語](../ja/MATHEMATICS.md)

[Dexted DSP](../../README.md)

## 1. Statement actually decided by the runtime

For fixed real coefficients,

$$H(z)=\frac{b_0+b_1z^{-1}+b_2z^{-2}}{1+a_1z^{-1}+a_2z^{-2}},\quad \gamma>0,$$

the runtime checks both strict stability of the supplied section denominator and `sup |H| < gamma`. Real coefficients give conjugate symmetry, so `[0,pi]` suffices. A nonminimal transfer representation with a canceled unstable denominator is still rejected.

The exact values are the finite binary rationals after the explicitly requested deployment conversion. This is not a proof about an ideal decimal, an unknown coefficient interval, or all rounding during sample processing.

## 2. Denominator stability

The real monic quadratic `z²+a1 z+a2` has its roots strictly inside the unit disk exactly when

$$|a_2|<1,\qquad 1+a_1+a_2>0,\qquad 1-a_1+a_2>0.$$

For sufficiency, use `z=(1+s)/(1-s)`. Multiplication by `(1-s)²` yields

$$(1-a_1+a_2)s^2+2(1-a_2)s+(1+a_1+a_2).$$

The listed conditions make these three coefficients positive, placing both roots in the open left half-plane, hence the original roots in the disk. Necessity follows from the product of the roots and the positive polynomial values at `z=±1`. Strict inequalities exclude boundary roots. This is classical second-order Schur/Jury reasoning, not an OpenAI theorem.

## 3. Gain becomes a quadratic sign test

For real `x,y,z` and `c=cos(omega)`, expansion gives

$$|x+ye^{-i\omega}+ze^{-2i\omega}|^2=(x-z)^2+y^2+2y(x+z)c+4xz c^2.$$

Call the numerator and denominator versions `N(c)` and `D(c)`. Stable denominator implies `D(c)>0`, so the gain condition is equivalent to

$$Q(c)=\gamma^2D(c)-N(c)>0\quad\text{for all }c\in[-1,1].$$

Continuity on a compact interval makes pointwise strict positivity equivalent to a strict global supremum bound here. Write `Q(c)=Ac²+Bc+C`. Check `A-B+C>0` and `A+B+C>0`. Only when `A>0` and `-2A<B<2A` must the interior vertex also be checked; its sign reduces to

$$4AC-B^2>0.$$

Every finite binary float is an integer divided by a power of two. Multiplying by a common **positive** denominator clears fractions without changing signs. Python integers and Boost `cpp_int` evaluate these predicates without cancellation error. This does not make the runtime constant-time in input bit length.

Full derivation and boundary treatment: [biquad.md](../math/biquad.md). Implementation: `biquad.py`, native header; separately expressed reference: `reference.py`.

## 4. Cascades and why UNKNOWN is necessary

For stable sections, whole-chain gain is equivalent to

$$Q(c)=\gamma^2\prod_j D_j(c)-\prod_j N_j(c)>0,\quad c\in[-1,1].$$

This preserves compensation between frequencies. It differs from the generally looser product of separate supremum bounds. A grid that multiplies responses at matching frequencies also preserves compensation, but still only samples the interval.

With `t=(c+1)/2`, write the polynomial in Bernstein form:

$$Q(2t-1)=\sum_{i=0}^n\beta_i {n\choose i}t^i(1-t)^{n-i}.$$

The basis is nonnegative and sums to one. All `beta_i>0` therefore prove positivity on that interval. A nonpositive coefficient alone does **not** prove failure; subdivide exactly at the midpoint. A nonpositive endpoint value gives a valid strict-positivity failure witness. When limits prevent further subdivision, return `unknown`.

A successful proof is a dyadic interval cover. `verify_cascade()` rebuilds the rational polynomial, binds original inputs and threshold, checks a gap-free/nonoverlapping cover and positive Bernstein coefficients on every interval. The producer flag is not trusted. This is a sufficient, resource-bounded procedure, not a complete arbitrary-degree real-root solver. Full details: [cascade.md](../math/cascade.md).

## 5. Conditional OpenAI connection, not runtime mathematics

The OpenAI source [OAI-325] states the complete inequality

$$\|P[A]\|_2\le2\sup_{z\in W(A)}\|P(z)\|_2,$$

for matrix-valued coefficients. Assuming this general theorem, repeated use on independent tensor axes gives `2^r` for `r` nonnormal axes; normal axes have cost 1. A fixed common base with changing channel polynomials gives `||H_(T-1)...H_0|| <= 2 q^T` if every symbol is bounded by `q<1` on the same numerical range.

For relative additive state perturbations `||e_t(x)||<=epsilon||x||`, variation of constants and induction yield

$$\|x_T\|\le2(q+2\epsilon)^T\|x_0\|.$$

Replacing the established complete constant `1+sqrt(2)` [CP-2017] by 2 increases the sufficient perturbation-radius bound by about 20.71%. It does not identify the true maximal radius or prove a universal audio/video quality gain. Arbitrarily changing base matrices or arbitrary feedback graphs do not satisfy the common-base hypothesis automatically.

The general OpenAI theorem remains an external assumption here. The exact biquad/cascade runtime and all published benchmark bars **do not use it**. See [provenance](PROVENANCE.md) and the [full conditional note](../math/crouzeix.md) for source version and missing steps toward a general executable certifier.

## 6. What “verified” means in this repository

Exact arithmetic verifies signs for the stated finite-input model. Test agreement checks implementation consistency. A rational proof checker checks a claimed certificate against expected inputs. These are distinct from proof-assistant verification, an independent security audit, all-runtime numerical correctness, and physical safety certification. None of the latter is implied.

[OAI-README]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/README.md
[OAI-325]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex
[OAI-DFT]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex
[CP-2017]: https://arxiv.org/abs/1702.00668
[SCIPY-FREQZ]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html
[PYPA]: https://packaging.python.org/en/latest/tutorials/packaging-projects/
