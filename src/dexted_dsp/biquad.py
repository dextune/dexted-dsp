"""Exact strict-gain decision, using integer Jury and quadratic tests."""
from __future__ import annotations
from dataclasses import dataclass
from .model import Biquad, positive_gamma

SCHEMA = 'dexted-dsp/biquad/v1'


def integer_coefficients(values: tuple[float, ...]) -> tuple[tuple[int, ...], int]:
    ratios = tuple(v.as_integer_ratio() for v in values)
    scale = max(d for _, d in ratios)  # binary denominators: lcm = maximum
    return tuple(n * (scale // d) for n, d in ratios), scale


def squared_coefficients(x: int, y: int, z: int) -> tuple[int, int, int]:
    # Constant, linear, quadratic coefficients of |x+y*e^-iw+z*e^-2iw|^2.
    return (x-z)**2 + y*y, 2*y*(x+z), 4*x*z


@dataclass(frozen=True)
class BiquadCertificate:
    status: str
    denominator_stable: bool
    max_gain_limit: float
    coefficients_hex: tuple[str, ...]
    jury: tuple[int, int, int]
    polynomial: tuple[int, int, int]
    endpoints: tuple[int, int]
    interior_required: bool
    vertex_gap: int | None

    @property
    def certified(self) -> bool:
        return self.status == 'certified'

    def as_dict(self) -> dict:
        return {
            'schema': SCHEMA, 'method': 'integer-jury-quadratic',
            'status': self.status, 'certified': self.certified,
            'denominator_stable': self.denominator_stable,
            'coefficients_hex': list(self.coefficients_hex),
            'max_gain_hex': self.max_gain_limit.hex(),
            'strict': True,
            'witness': {
                'jury': list(map(str, self.jury)),
                'polynomial_c0_c1_c2': list(map(str, self.polynomial)),
                'endpoints_minus_plus': list(map(str, self.endpoints)),
                'interior_required': self.interior_required,
                'vertex_gap': None if self.vertex_gap is None else str(self.vertex_gap),
            },
            'scope': 'fixed real LTI biquad; exact supplied coefficients; no runtime-roundoff guarantee',
        }


def certify(biquad: Biquad, max_gain: float = 1.0) -> BiquadCertificate:
    """Decide strict Schur stability AND sup_w |H(e^iw)| < max_gain.

    Failure of a gain limit does NOT establish closed-loop instability.
    An equality is rejected: this is a strict inequality. max_gain is a
    threshold, not an estimate of the actual maximum frequency response.
    """
    if not isinstance(biquad, Biquad):
        raise TypeError("certify expects a Biquad")
    gamma = positive_gamma(max_gain)
    (b0, b1, b2, a1, a2), s = integer_coefficients(biquad.coefficients)
    jury = (s-abs(a2), s+a1+a2, s-a1+a2)
    stable = all(v > 0 for v in jury)
    num = squared_coefficients(b0, b1, b2)
    den = squared_coefficients(s, a1, a2)
    gn, gd = gamma.as_integer_ratio()
    c, b, a = (gn*gn*d - gd*gd*n for n, d in zip(num, den))
    endpoints = (a-b+c, a+b+c)
    interior = a > 0 and -2*a < b < 2*a
    vertex_gap = 4*a*c-b*b if interior else None
    gain = min(endpoints) > 0 and (not interior or vertex_gap > 0)
    status = ('denominator_not_schur' if not stable else
              'certified' if gain else 'gain_limit_not_met')
    return BiquadCertificate(status, stable, gamma, tuple(biquad.hex_coefficients()),
                             jury, (c, b, a), endpoints, interior, vertex_gap)
