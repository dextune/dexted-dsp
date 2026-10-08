"""Certified gain enclosures for fixed real biquads and SOS cascades.

Only exact rational signs establish upper bounds. Numeric display values are
rounded outwards and are never used to decide certification. This is offline
analysis, not a real-time norm or an audio-processing engine.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isfinite, isqrt, nextafter
from typing import Sequence

from .biquad import integer_coefficients, squared_coefficients
from .cascade import gap_polynomial, prove_positive, validate_sections, ResourceLimitError
from .model import Biquad


def _fraction_text(q: Fraction) -> str:
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"


def _outward_float(q: Fraction, *, upper: bool) -> float | None:
    try:
        x = float(q)
    except OverflowError:
        return None
    if not isfinite(x):
        return None
    if q == 0:
        return 0.0
    return nextafter(x, float('inf') if upper else float('-inf'))


@dataclass(frozen=True, slots=True)
class GainBounds:
    """Provable closed interval [lower, upper] for ideal peak magnitude.

    Rational endpoints are authoritative. Floating-point fields are only
    conservative outward-rounded conveniences and may be null on overflow.
    A `budget_limited` result still has *valid* bounds, just not target width.
    """
    lower_ratio: str
    upper_ratio: str
    lower_bound: float | None
    upper_bound: float | None
    status: str
    method: str
    refinements: int
    relative_width_target_bits: int

    def as_dict(self) -> dict:
        return {
            'lower_ratio': self.lower_ratio,
            'upper_ratio': self.upper_ratio,
            'lower_bound': self.lower_bound,
            'upper_bound': self.upper_bound,
            'status': self.status,
            'method': self.method,
            'refinements': self.refinements,
            'relative_width_target_bits': self.relative_width_target_bits,
            'frequency_region_hz': None,
            'scope': 'ideal exact represented coefficients; no runtime-roundoff guarantee',
        }


def _make_bounds(lo: Fraction, hi: Fraction, status: str, method: str,
                 refinements: int, bits: int) -> GainBounds:
    if lo < 0 or hi < lo:
        raise AssertionError('invalid rational gain enclosure')
    return GainBounds(_fraction_text(lo), _fraction_text(hi),
                      _outward_float(lo, upper=False),
                      _outward_float(hi, upper=True), status, method,
                      refinements, bits)


def _biquad_gap_sign(f: Biquad, gamma: Fraction) -> bool:
    """TRUE iff strict gain < positive rational gamma, using integer signs."""
    if gamma <= 0:
        return False
    (b0,b1,b2,a1,a2), scale = integer_coefficients(f.coefficients)
    if not (abs(a2) < scale and scale+a1+a2 > 0 and scale-a1+a2 > 0):
        return False
    num = squared_coefficients(b0,b1,b2)
    den = squared_coefficients(scale,a1,a2)
    gn,gd = gamma.numerator,gamma.denominator
    c,b,a = (gn*gn*d-gd*gd*n for n,d in zip(num,den))
    if a-b+c <= 0 or a+b+c <= 0:
        return False
    return not (a > 0 and -2*a < b < 2*a) or 4*a*c-b*b > 0


def bound_peak_gain(f: Biquad, *, precision_bits: int = 24) -> GainBounds | None:
    """Certified rational interval for max_omega |H(exp(i omega))|.

    `precision_bits` halves an initial factor-of-two bracket that contains the
    true peak. Exact zero numerator yields [0,0]. Unstable denominators return
    None rather than implying a finite gain bound.
    """
    if not isinstance(f, Biquad):
        raise TypeError('bound_peak_gain expects a Biquad')
    if type(precision_bits) is not int or not 0 <= precision_bits <= 64:
        raise ValueError('precision_bits must be an integer in [0,64]')
    (_,_,_,a1,a2), scale = integer_coefficients(f.coefficients)
    if not (abs(a2)<scale and scale+a1+a2>0 and scale-a1+a2>0):
        return None
    if all(v == 0 for v in f.b):
        return _make_bounds(Fraction(0),Fraction(0),'bounded','exact-zero',0,precision_bits)
    hi = Fraction(1)
    if _biquad_gap_sign(f,hi):
        for _ in range(2200):
            if not _biquad_gap_sign(f,hi/2):
                break
            hi /= 2
        else:
            return None  # defensive limit, not an unproven enclosure
    else:
        for _ in range(2200):
            hi *= 2
            if _biquad_gap_sign(f,hi):
                break
        else:
            return None
    lo = hi / 2
    for _ in range(precision_bits):
        mid = (lo+hi)/2
        if _biquad_gap_sign(f,mid):
            hi = mid
        else:
            lo = mid
    return _make_bounds(lo,hi,'bounded','exact-integer-rational-bisection',precision_bits,precision_bits)


def _sos_sample_lower(rows: Sequence[Biquad], *, bits: int = 24) -> Fraction:
    """Lower bound from three exact frequency witnesses (c=-1,0,1)."""
    peak_squared = Fraction(0)
    for c in (-1,0,1):
        ratio = Fraction(1)
        for f in rows:
            (b0,b1,b2,a1,a2),s = integer_coefficients(f.coefficients)
            n = squared_coefficients(b0,b1,b2)
            d = squared_coefficients(s,a1,a2)
            numerator = n[0]+n[1]*c+n[2]*c*c
            denominator = d[0]+d[1]*c+d[2]*c*c
            if denominator <= 0:
                raise ValueError('SOS denominator must be strictly stable')
            ratio *= Fraction(numerator,denominator)
        peak_squared = max(peak_squared,ratio)
    if peak_squared == 0:
        return Fraction(0)
    # An integer square root gives a *provable* lower rational approximation.
    # Scale adapts to very small witness gains rather than underflowing.
    scale = max(bits, (peak_squared.denominator.bit_length()-peak_squared.numerator.bit_length())//2+bits)
    return Fraction(isqrt((peak_squared.numerator << (2*scale))//peak_squared.denominator), 1<<scale)


def bound_sos_peak_gain(sections: Sequence[Biquad], *, precision_bits: int = 10,
                        max_depth: int = 48, max_nodes: int = 20000,
                        max_bracket_steps: int = 36) -> GainBounds | None:
    """Best-effort certified enclosure; UNKNOWN never becomes an upper bound.

    An exact witness supplies the lower bound. Only a successful Bernstein
    positivity proof supplies an upper bound. Resource exhaustion yields None
    if no upper bound could be established, or `budget_limited` if one exists.
    """
    rows = validate_sections(sections)
    if type(precision_bits) is not int or not 0 <= precision_bits <= 32:
        raise ValueError('precision_bits must be an integer in [0,32]')
    if type(max_depth) is not int or not 0 <= max_depth <= 128:
        raise ValueError('max_depth must be an integer in [0,128]')
    if type(max_nodes) is not int or not 1 <= max_nodes <= 100000:
        raise ValueError('max_nodes must be an integer in [1,100000]')
    if type(max_bracket_steps) is not int or not 1 <= max_bracket_steps <= 128:
        raise ValueError('max_bracket_steps must be an integer in [1,128]')
    try:
        _, stable = gap_polynomial(rows,Fraction(1))
    except ResourceLimitError:
        return None
    if not stable:
        return None
    lo = _sos_sample_lower(rows)
    def verdict(gamma: Fraction) -> str:
        try:
            p,_ = gap_polynomial(rows,gamma)
        except ResourceLimitError:
            return 'unknown'
        return prove_positive(p,max_depth,max_nodes)['verdict']
    # Start with a known lower witness; do not mistake UNKNOWN for failure.
    hi = max(Fraction(1),lo*2)
    for _ in range(max_bracket_steps):
        v = verdict(hi)
        if v == 'certified':
            break
        hi *= 2
    else:
        return None
    completed = 0
    for _ in range(precision_bits):
        mid = (lo+hi)/2
        if mid <= 0:
            break
        v = verdict(mid)
        if v == 'certified':
            hi = mid
        elif v == 'condition_failed':
            lo = mid
        else:
            return _make_bounds(lo,hi,'budget_limited','integer-bernstein-plus-point-witness',
                                completed,precision_bits)
        completed += 1
    return _make_bounds(lo,hi,'bounded','integer-bernstein-plus-point-witness',completed,precision_bits)
