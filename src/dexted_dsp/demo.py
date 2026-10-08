"""Deterministic no-dependency correctness demos for first-time users."""
from __future__ import annotations

import math

from .biquad import certify
from .model import Biquad
from .peak import bound_peak_gain


def hidden_peak_demo(grid_size: int = 1024) -> dict:
    """Compare an inclusive [0,pi] grid against exact full-band checking.

    A known stable biquad has an exact magnitude-2 peak at pi/2, yet grids
    with an even number of inclusive endpoints miss that frequency. Its global
    peak=2 follows algebraically from the numerator/denominator polynomials;
    the peak value is NOT inferred from denser frequency sampling.
    """
    if type(grid_size) is not int or not 2 <= grid_size <= 100000:
        raise ValueError('grid_size must be an integer in [2,100000]')
    alpha = 2.0**-14
    f = Biquad.from_coefficients([alpha,0,-alpha,0,1-alpha],precision='float32')
    peak_sample = 0.0
    for j in range(grid_size):
        omega = math.pi*j/(grid_size-1)
        z2 = complex(math.cos(2*omega),-math.sin(2*omega))
        ratio = abs(alpha*(1-z2))/abs(1+(1-alpha)*z2)
        peak_sample = max(peak_sample,ratio)
    core = certify(f,max_gain=1.0)
    exact = bound_peak_gain(f,precision_bits=24)
    # Global peak is exactly 2 for this specific algebraic example.
    assert exact is not None and exact.lower_bound <= 2 <= exact.upper_bound
    return {
        'demo': 'hidden-peak',
        'model': 'fixed real binary32 biquad; offline ideal response',
        'grid': {'points': grid_size, 'frequencies': 'inclusive 0..pi',
                 'estimated_max_gain': peak_sample,
                 'pass_at_gain_limit_1': peak_sample < 1.0},
        'exact': {'certified_under_limit_1': core.certified,
                  'status': core.status, 'gain_enclosure': exact.as_dict()},
        'analytical': {'peak_gain': 2.0, 'peak_radians': math.pi/2,
                       'method': 'exact rational polynomial extremum; not sampling'},
        'contradiction': peak_sample < 1 and not core.certified,
        'caveat': 'A constructed adversarial filter, not a real-world error-rate estimate',
        'coefficients_hex': f.hex_coefficients(),
    }
