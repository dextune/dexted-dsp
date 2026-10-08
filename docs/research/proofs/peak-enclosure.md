# Exact gain enclosure — proof sketch and implementation contract

`src/dexted_dsp/peak.py` provides **mathematically valid rational enclosures**, not a floating estimate mislabeled as a certificate.

## Single real biquad

For a strictly Schur-stable denominator and `c=cos(ω)`, write `N(c)=|B(e^{iω})|²` and `D(c)=|A(e^{iω})|²`. Each is a quadratic in c and `D(c)>0` over `[-1,1]`. For any *rational* candidate `g>0`,

\[\sup_\omega |H(e^{i\omega})|<g\quad\iff\quad g^2D(c)-N(c)>0\ \forall c\in[-1,1].\]

The right-hand polynomial is quadratic; checking its two endpoints and an interior minimum (if any) with **exact integers** decides the proposition. Strictly positive `g` eventually succeeds, while any `g` at or below the true maximum fails. Find neighboring powers of two, then bisect exactly `precision_bits` times. At each step `lower` is known **not** to exceed the actual maximum, and `upper` is known **strictly above** it. A constant-zero numerator returns `[0,0]`. No Schur stability ⇒ no finite certified response bound is emitted.

The JSON stores those rational endpoints as decimal integer fractions. Any float display values use `math.nextafter` outward, so they cannot appear tighter than the underlying rational interval. A returned `frequency_region_hz=null` is intentional: the position of the maximum is not certified yet.

## Serial SOS cascade

Each section's N and D factors are multiplied to form the *exact* polynomial `P_g(c)=g²∏D_j(c)−∏N_j(c)`. A lower bound is obtained by evaluating the actual cascade at three exact frequencies, `c∈{-1,0,1}`, and rounding its gain magnitude **downward** using integer square root. This is a point witness, not a sampled estimate asserted to be a global peak.

A rational `g` is admitted as a **global upper bound only** when the integer Bernstein subdivision algorithm proves `P_g(c)>0` on the full interval. `unknown` produces **no new upper bound**, and an exact nonpositive witness may raise the lower bound. The algorithm returns either a provable enclosure with the achieved refinement status, or None if it cannot establish an upper bound within the requested budget.

All results concern **exact represented coefficients and the ideal transfer function**. No hardware arithmetic safety, nonlinear systems, changing coefficients, DNNs or general matrix operator results are inferred. The verifier remains independently expressed rational arithmetic **within this repository**, not external audit or formal proof certification.
