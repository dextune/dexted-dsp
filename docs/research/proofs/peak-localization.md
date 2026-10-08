# Exact biquad peak localization (cosine coordinate)

**Implementation:** [`src/dexted_dsp/peak_region.py`](../../../src/dexted_dsp/peak_region.py) · **State:** in-repository mathematical derivation with executable tests, **not external peer review**.

## Model and guarantee

For a fixed real biquad with strictly Schur-stable denominator, let `c = cos(omega)` and

\[
 R(c) = |H(e^{i\omega})|^2 = N(c)/D(c), \qquad c\in[-1,1].
\]

Both numerator `N` and denominator `D` are quadratic polynomials with exact integer coefficients after a common positive scaling. Schur stability implies **D(c) > 0** on `[-1,1]`. `R` is continuous, so its global maxima occur at endpoints or at stationary points.

The function `localize_peak()` returns a union of **closed rational intervals in c** guaranteed to contain **every** global maximizer. Its intervals may conservatively contain extra stationary points when their exact gain ranges overlap. It does not output a falsely precise single floating-point peak frequency.

## Exact stationary-point isolation

Write `N(c) = n0+n1*c+n2*c²`, `D(c) = d0+d1*c+d2*c²`. Then

\[
R'(c) = T(c)/D(c)^2,
\]

\[
T(c) = (n_1d_0-n_0d_1) + 2(n_2d_0-n_0d_2)c + (n_2d_1-n_1d_2)c^2.
\]

The cubic terms cancel. Therefore **at most two distinct interior stationary points** exist unless `T ≡ 0`. To isolate all roots without floating-point rounding:

1. Start with rational knots `-1` and `1`. If `T` is quadratic and its rational vertex lies in `(-1,1)`, include it as an additional knot.
2. On each knot interval `T` is monotone. Evaluate endpoint signs exactly as `Fraction`. Include any exact endpoint zeros; opposite signs indicate exactly one interior zero.
3. For each bracket, bisect with rational midpoints `isolation_bits + 3` times or stop when a midpoint is exactly zero. No approximate quadratic formula is used.
4. Add the global domain endpoints as candidates. If `T ≡ 0`, `R` is constant throughout `[-1,1]` and every frequency is a maximizer; return the complete interval.

Each retained root bracket is closed and still contains its exact root (including an irrational algebraic root). On this degree-two derivative, no distinct stationary root is omitted.

## Safe exclusion of lower candidates

For every candidate interval `I=[a,b]`, evaluate the exact min and max of `N` and `D` over `I`. A quadratic's extrema occur at its two endpoints and possibly its rational vertex. Thus all such extrema have exact rational values. Denote them `Nmin,Nmax,Dmin,Dmax`, where `Dmin>0` and `Nmin>=0`. For any `c∈I`,

\[
\frac{N_{min}}{D_{max}} \leq R(c) \leq \frac{N_{max}}{D_{min}}.
\]

Let `L` be the maximum of these per-candidate lower bounds. Since at least one actual endpoint or stationary point lies in every candidate interval, `L` is no greater than the true global maximum. Any candidate interval with its certified `upper < L` is consequently impossible as a global maximizer and is discarded. Tied peaks remain included.

These are rational inequalities, *not* sampled-frequency guesses. Reporting a union rather than a single winning root preserves ties and honest uncertainty.

## What is and is not certified

- **Certified:** Each `cosine_intervals` member consists of exact rational strings. The union contains **every** ideal global peak location for the supplied stable fixed-coefficient biquad, subject to this implementation's mathematical correctness.
- **Informational only:** `frequency_hz_approx` transforms rational endpoints through ordinary `math.acos` and the represented sample rate. It is **not** a certified interval in Hz. `frequency_hz_certified=false` is mandatory in the proof payload. Cross-platform verifier compares this display hint with a small tolerance, while strictly comparing all exact proof fields.
- **Unavailable:** A denominator that fails strict Schur stability receives no peak region; this does not assert any stability of a larger feedback system.
- **Out of scope:** General high-degree SOS peak location, finite-precision runtime rounding, unknown coefficient disturbances, saturation/nonlinearity, or device-safety certification.

The new inspection wrapper is versioned `dexted-dsp/inspection/v2`. The verifier rechecks its rational region and previous gain/stability proof against **caller-supplied coefficients and threshold**. Legacy `inspection/v1` remains supported without a peak-region claim. Since the verifier and producer share this repository, it is not a third-party independent audit or a proof-assistant formalization.

## Reproduce

```bash
python -m unittest discover -s tests -v
python -m dexted_dsp inspect examples/hidden_peak.json --region-bits 32
```

The supplied hidden-peak example has global peak `c=0` exactly (`omega=pi/2`); normalized sample rate 48,000 Hz displays 12,000 Hz. The exact cosine certificate is `[0,0]`. Examples with equal peaks at `omega=0` and `omega=pi` correctly return two disjoint point intervals; constant-ratio filters return the entire frequency band.
