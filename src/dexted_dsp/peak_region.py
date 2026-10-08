"""Exact cosine-domain localization of global peaks of stable real biquads.

The certificate is a *union of closed rational intervals in c=cos(omega)*.
There is no floating-point root finding in the proof path. The optional Hz
coordinates are display-only approximations, not an interval certificate in Hz.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from math import acos, pi

from .biquad import integer_coefficients, squared_coefficients
from .model import Biquad, positive_gamma


def _text(q: Q) -> str:
    return str(q.numerator) if q.denominator == 1 else f'{q.numerator}/{q.denominator}'


def _eval(p: tuple[int, int, int], x: Q) -> Q:
    return p[0] + x * (p[1] + x*p[2])


def _quadratic_range(p: tuple[int, int, int], lo: Q, hi: Q) -> tuple[Q,Q]:
    values = [_eval(p,lo), _eval(p,hi)]
    if p[2]:
        vertex = Q(-p[1],2*p[2])
        if lo < vertex < hi:
            values.append(_eval(p,vertex))
    return min(values), max(values)


def _candidate_intervals(n: tuple[int,int,int],d: tuple[int,int,int],bits:int) -> list[tuple[Q,Q]]:
    """All extrema in [-1,1] via exact derivative roots and endpoints.

    Since N,D are quadratic, the cubic coefficient of N'D-ND' cancels.
    Splitting at the quadratic derivative vertex gives monotonic segments,
    each of which contains at most one distinct non-endpoint root.
    """
    t = (n[1]*d[0]-n[0]*d[1], 2*(n[2]*d[0]-n[0]*d[2]),
         n[2]*d[1]-n[1]*d[2])
    if t == (0,0,0):
        return [(Q(-1),Q(1))]  # flat response: EVERY frequency is a maximizer
    knots = [Q(-1),Q(1)]
    if t[2]:
        vertex = Q(-t[1], 2*t[2])
        if -1 < vertex < 1:
            knots.append(vertex)
    knots.sort()
    candidates = {(Q(-1),Q(-1)),(Q(1),Q(1))}
    for lo,hi in zip(knots,knots[1:]):
        f_lo,f_hi = _eval(t,lo),_eval(t,hi)
        if f_lo == 0:
            candidates.add((lo,lo))
        if f_hi == 0:
            candidates.add((hi,hi))
        if f_lo*f_hi >= 0:
            continue
        # Exactly one root on this monotone branch; dyadic bisection
        # does not assume a correctly-rounded floating-point sqrt.
        for _ in range(bits+3):
            mid = (lo+hi)/2
            f_mid = _eval(t,mid)
            if f_mid == 0:
                lo=hi=mid
                break
            if f_lo*f_mid < 0:
                hi,f_hi = mid,f_mid
            else:
                lo,f_lo = mid,f_mid
        candidates.add((lo,hi))
    return sorted(candidates)


@dataclass(frozen=True,slots=True)
class PeakRegion:
    """Set guaranteed to contain ALL global maximizers in cos(omega).

    Any spurious stationary candidates can remain, but true maximizers cannot
    be dropped. Each rational endpoint is mathematically authoritative.
    """
    cosine_intervals: tuple[tuple[str,str], ...]
    status: str
    isolation_bits: int
    method: str
    frequency_hz_approx: tuple[tuple[float,float], ...] | None

    def as_dict(self) -> dict:
        return {
            'cosine_intervals': [list(pair) for pair in self.cosine_intervals],
            'status': self.status,
            'isolation_bits': self.isolation_bits,
            'method': self.method,
            'frequency_hz_approx': ([list(p) for p in self.frequency_hz_approx]
                                   if self.frequency_hz_approx is not None else None),
            'frequency_hz_certified': False,
            'scope': 'closed rational c=cos(omega) intervals; every ideal global maximizer included',
        }


def localize_peak(f: Biquad, *, isolation_bits: int = 24,
                  fs: float | None = None) -> PeakRegion | None:
    """Locate the global biquad response maximizer to rational cos intervals.

    One or more rational intervals are returned, including tied peaks. If
    numerator and denominator responses have a constant ratio, the whole
    band is returned. A non-Schur denominator returns None, not a proof.
    Hz values are non-rigorous display approximations to rational boundaries.
    """
    if not isinstance(f,Biquad):
        raise TypeError('localize_peak expects a Biquad')
    if type(isolation_bits) is not int or not 0 <= isolation_bits <= 64:
        raise ValueError('isolation_bits must be an integer in [0,64]')
    if fs is not None:
        fs = positive_gamma(fs)
    (b0,b1,b2,a1,a2),scale = integer_coefficients(f.coefficients)
    if not (abs(a2)<scale and scale+a1+a2>0 and scale-a1+a2>0):
        return None
    n = squared_coefficients(b0,b1,b2)
    d = squared_coefficients(scale,a1,a2)
    candidates = _candidate_intervals(n,d,isolation_bits)
    if candidates == [(Q(-1),Q(1))]:
        survivors = candidates
        status='flat'
    else:
        # Exact bounding of the squared response on each candidate interval.
        # The global maximizer must occur at an endpoint or stationary point.
        # Eliminating an interval requires a strict, independently valid bound:
        # candidate_upper < max(other candidate_lower).
        ratios=[]
        for lo,hi in candidates:
            nlo,nhi=_quadratic_range(n,lo,hi)
            dlo,dhi=_quadratic_range(d,lo,hi)
            if dlo <= 0 or nlo < 0:
                raise AssertionError('invalid exact response polynomial range')
            ratios.append((nlo/dhi,nhi/dlo))
        global_lower=max(x[0] for x in ratios)
        survivors=[interval for interval,(_,upper) in zip(candidates,ratios)
                   if upper>=global_lower]
        status='isolated'
    approx = None
    if fs is not None:
        approx = tuple((fs*acos(float(hi))/(2*pi),fs*acos(float(lo))/(2*pi))
                       for lo,hi in survivors)
    return PeakRegion(tuple((_text(lo),_text(hi)) for lo,hi in survivors),
                      status,isolation_bits,'exact-rational-stationary-isolation',approx)
