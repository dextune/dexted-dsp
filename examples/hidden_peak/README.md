# One-command hidden-peak demo

```bash
python -m pip install .
dexted-dsp demo hidden-peak
```

The demo depends only on the Python standard library. It checks the binary32 biquad

\[H(z) = \frac{\alpha(1-z^{-2})}{1+(1-\alpha)z^{-2}}, \qquad \alpha = 2^{-14}.\]

An inclusive uniform 1,024-point grid on `[0,π]` misses `π/2` and reports a sampled peak of about `0.0397432122`, below the gain-1 limit. Exact certification returns `gain_limit_not_met`. At `ω=π/2` the ratio is exactly `2`, and writing `c=cos(ω)` shows

\[|H|^2 = \frac{4\alpha^2(1-c^2)}{\alpha^2+4(1-\alpha)c^2}\leq 4,\]

with equality only at `c=0`. Thus **global peak gain 2 is established algebraically**, not guessed from a denser grid. The demo's additional rational enclosure is established by integer sign tests. `grid_size` is configurable, so **not every grid** makes the same false decision (an odd inclusive grid samples `π/2`).

A constructed adversarial example does not establish the prevalence of this failure in actual deployed audio filters. The sampling routine does not purport to provide a mathematical certificate.
