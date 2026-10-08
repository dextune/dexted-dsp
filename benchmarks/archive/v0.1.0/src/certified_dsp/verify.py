"""Certificate checking with a separately expressed exact-rational path."""
from fractions import Fraction as F
from math import comb
from .model import Biquad, positive_gamma
from . import reference


def verify_biquad(report: dict, expected: Biquad, max_gain=1.0) -> bool:
    """Recheck a claimed PASS for the CALLER's filter and threshold.

    The integer witness is informative; trust is established by re-evaluating
    the original exact-rational decision, not by trusting a serialized flag.
    """
    try:
        return bool(
            isinstance(report, dict) and isinstance(expected, Biquad)
            and report.get('schema') == 'certified-dsp/biquad/v1'
            and report.get('status') == 'certified'
            and report.get('certified') is True and report.get('strict') is True
            and report.get('coefficients_hex') == expected.hex_coefficients()
            and report.get('max_gain_hex') == positive_gamma(max_gain).hex()
            and reference.reference_decision(expected, max_gain)
        )
    except (ValueError, TypeError, OverflowError):
        return False


def verify_cascade(report: dict, expected_sections, max_gain=1.0) -> bool:
    """Verify an exact dyadic interval cover bound to expected inputs.

    Explicit size/depth limits reduce accidental resource exhaustion. This is
    not a hardened sandbox for hostile remote proof objects.
    """
    try:
        rows = tuple(expected_sections)
        if not 1 <= len(rows) <= 32 or any(not isinstance(s, Biquad) for s in rows):
            return False
        if (not isinstance(report, dict)
            or report.get('schema') != 'certified-dsp/cascade/v1'
            or report.get('status') != 'certified'
            or report.get('certified') is not True or report.get('strict') is not True
            or report.get('sections_hex') != [s.hex_coefficients() for s in rows]
            or report.get('max_gain_hex') != positive_gamma(max_gain).hex()):
            return False
        cover = report.get('cover')
        if not isinstance(cover, list) or not 1 <= len(cover) <= 100000:
            return False
        p, stable = reference.polynomial(rows, max_gain)
        if not stable:
            return False
        intervals = []
        for item in cover:
            if not isinstance(item, list) or len(item) != 2:
                return False
            index, depth = item
            if type(index) is not int or type(depth) is not int or not 0 <= depth <= 128:
                return False
            if not 0 <= index < 2**depth:
                return False
            intervals.append((F(index,2**depth), F(index+1,2**depth)))
        intervals.sort()
        last = F(0)
        for lo, hi in intervals:
            if lo != last:
                return False
            # Local u in [-1,1] -> c=(hi-lo)*u+(hi+lo-1).
            h, m, n = hi-lo, hi+lo-1, len(p)-1
            transformed = [sum((p[j]*comb(j,k)*h**k*m**(j-k)
                                for j in range(k,n+1)), F(0)) for k in range(n+1)]
            if min(reference.bernstein(transformed)) <= 0:
                return False
            last = hi
        return last == 1
    except (KeyError, TypeError, ValueError, OverflowError, ZeroDivisionError):
        return False
