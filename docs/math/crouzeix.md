# Crouzeix connection — conditional research notes, NOT a production API

**Status: conditional derivation.** None of the executable biquad/cascade benchmarks
uses the new theorem below. We did not independently re-prove the source's general
constant-two theorem. It is not a runtime feature of Dexted DSP v0.1.0.

## Source assumption

Crouzeix–Palencia's 2017 paper establishes that the numerical range is a complete
`(1+sqrt(2))` spectral set [R1]. The OpenAI preprint at frozen commit
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`, result family 325, states the complete
constant-two inequality [R2]:

$$\|P[A]\|_2\le2\max_{z\in W(A)}\|P(z)\|_2,$$

where `P(z)=sum B_k z^k` is matrix-valued and `P[A]=sum A^k ⊗ B_k`.
The adjective **complete** matters: channel coefficient matrices need not commute.

[R1: primary paper](https://arxiv.org/abs/1702.00668)

[R2: pinned source theorem](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex)

## 1. Several independent axes

For separate tensor axes A_1,...,A_r and a matrix-valued polynomial symbol E,
apply the complete bound one axis at a time. This gives

$$\|E[\mathbf A]\|_2\le 2^r
\sup_{z_j\in W(A_j)}\|E(z_1,\ldots,z_r)\|_2.$$

Each normal axis has constant 1 by unitary diagonalization, so r need count only
the nonnormal axes. The tensor-axis hypothesis is essential; arbitrary noncommuting
base matrices cannot be substituted. With a proved symbol error <=epsilon, this yields
`||(P[A]-Q[A])x|| <= 2^r epsilon ||x||`.

Sharpness of the universal factor is illustrated by
`J=[[0,2],[0,0]]`. For a unit vector, `u*Ju` fills the unit disk, while `||J||=2`.
The symbol `z1*...*zr` has supremum 1 on the product disks, and `||J⊗...⊗J||=2^r`.
This lower-bound example is an elementary illustration, not a newly discovered construction.
The complete constant 2 for 2-by-2 base matrices predates the source's general result.

## 2. Fixed base, changing channel polynomials

Fix A and let H_t=P_t[A], with all symbols bounded by q<1 on the SAME W(A).
Because Kronecker multiplication preserves the order of coefficient matrices,

$$H_{T-1}\cdots H_0=(P_{T-1}\cdots P_0)[A].$$

Applying the complete bound ONCE gives `||H_{T-1}...H_0|| <= K q^T`, not `(Kq)^T`,
where K=2 under R2 and K=1+sqrt(2) under R1. This works with noncommuting channel
matrices, but it requires a common fixed A and a verified uniform symbol bound.

## 3. Relative additive perturbation

Let `x_{t+1}=H_t x_t + e_t(x_t)` with `||e_t(x)|| <= epsilon ||x||`.
Variation of constants and the bound above give

$$u_T\le Kq^T u_0+K\epsilon\sum_{j=0}^{T-1}q^{T-1-j}u_j,
\qquad u_t=\|x_t\|.$$

Induction (or the finite geometric identity) yields

$$u_T\le K(q+K\epsilon)^T u_0.$$

Thus a sufficient zero-input decay condition is `epsilon < (1-q)/K`.
Replacing K=1+sqrt(2) by K=2 enlarges this sufficient perturbation radius by
`(1+sqrt(2))/2 - 1`, approximately 20.71%.
This is a comparison of two sufficient bounds, NOT proof of the true maximal
robustness radius, better perceptual quality, or a new stability region for all filters.

## 4. What is still needed for an executable general certifier?

A rigorous enclosure for W(A), a provable supremum bound for the symbol on it,
validated coefficient uncertainty and applicable state-space/temporal assumptions.
A dense numerical sample of W(A) is NOT such a proof. Generic learned filters may
not share a fixed base, and ordinary FFT axes are already normal (constant 1).

No `crouzeix_certify()` function is shipped. The exact-gain APIs in this release
are valid independently of the status of R2. No theorem-prover kernel was run here.
