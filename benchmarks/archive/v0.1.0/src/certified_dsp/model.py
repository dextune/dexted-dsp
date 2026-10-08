"""Explicit coefficient semantics: certify the values actually deployed."""
from __future__ import annotations
from dataclasses import dataclass
import math
from numbers import Complex, Real
import struct
from typing import Iterable


def finite_float(value: object) -> float:
    if isinstance(value, Complex) and not isinstance(value, Real):
        raise ValueError("complex coefficients are not supported")
    if isinstance(value, (bool, str, bytes)):
        raise ValueError("coefficients and thresholds must be real numbers, not bool/string")
    try:
        v = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("a finite real number is required") from exc
    if not math.isfinite(v):
        raise ValueError("NaN and infinity are not supported")
    return v


def positive_gamma(value: object) -> float:
    gamma = finite_float(value)
    if gamma <= 0:
        raise ValueError("max_gain must be strictly positive")
    return gamma


@dataclass(frozen=True, slots=True)
class Biquad:
    """H(z)=(b0+b1*z^-1+b2*z^-2)/(1+a1*z^-1+a2*z^-2).

    Finite binary64 values are interpreted exactly. No implicit coefficient
    normalization or float32 rounding is performed by this constructor.
    Use from_coefficients(..., precision='float32') for deployed binary32.
    """
    b: tuple[float, float, float]
    a: tuple[float, float, float]

    def __post_init__(self) -> None:
        try:
            b = tuple(finite_float(x) for x in self.b)
            a = tuple(finite_float(x) for x in self.a)
        except TypeError as exc:
            raise ValueError("b and a must be sequences") from exc
        if len(b) != 3 or len(a) != 3:
            raise ValueError("b and a must each have three values")
        if a[0] != 1.0:
            raise ValueError("a0 must equal 1; normalize and round in your deployment pipeline first")
        object.__setattr__(self, 'b', b)
        object.__setattr__(self, 'a', a)

    @classmethod
    def from_coefficients(cls, values: Iterable[float], *, precision: str = 'float64') -> Biquad:
        """Read [b0,b1,b2,a1,a2]. float32 conversion is explicit and checked."""
        if precision not in ('float32', 'float64'):
            raise ValueError("precision must be float32 or float64")
        try:
            v = tuple(finite_float(x) for x in values)
        except TypeError as exc:
            raise ValueError("five coefficients are required") from exc
        if len(v) != 5:
            raise ValueError("five coefficients are required")
        if precision == 'float32':
            try:
                v = tuple(struct.unpack('!f', struct.pack('!f', x))[0] for x in v)
            except (OverflowError, struct.error) as exc:
                raise ValueError("coefficient exceeds float32 range") from exc
        return cls(v[:3], (1.0, v[3], v[4]))

    @property
    def coefficients(self) -> tuple[float, ...]:
        return self.b + self.a[1:]

    def hex_coefficients(self) -> list[str]:
        return [x.hex() for x in self.coefficients]


def from_sos(sos: Iterable[Iterable[float]], *, precision: str = 'float64') -> tuple[Biquad, ...]:
    """Read SciPy-layout rows [b0,b1,b2,a0,a1,a2], without importing SciPy.

    a0 must already be one. Re-normalizing coefficients here could certify
    values different from those deployed by the caller.
    """
    result = []
    for row in sos:
        values = tuple(finite_float(x) for x in row)
        if len(values) != 6 or values[3] != 1.0:
            raise ValueError("each SOS row must contain six finite values with a0=1")
        result.append(Biquad.from_coefficients(values[:3] + values[4:], precision=precision))
    if not result:
        raise ValueError("at least one SOS row is required")
    return tuple(result)
