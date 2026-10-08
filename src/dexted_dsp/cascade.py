"""Exact SOS positivity certificates with bounded integer work.

No floating-point comparison is used to establish stability, positivity or
proof coverage. Exhausted bit, depth and node resources return UNKNOWN.
"""
from __future__ import annotations

from math import comb, lcm
from .model import Biquad, positive_gamma
from .biquad import integer_coefficients, squared_coefficients
from .request import bounded_take

MAX_SECTIONS = 32
MAX_INTEGER_BITS = 262144
SCHEMA = 'dexted-dsp/cascade/v1'


class ResourceLimitError(ArithmeticError):
    """An exact operation exceeded the integer resource budget."""


def _check_bits(values) -> None:
    for value in values:
        if abs(value).bit_length() > MAX_INTEGER_BITS:
            raise ResourceLimitError('integer bit budget exhausted')


def validate_sections(sections) -> tuple[Biquad, ...]:
    rows = bounded_take(sections, MAX_SECTIONS, 'SOS sections')
    if not 1 <= len(rows) <= MAX_SECTIONS or any(not isinstance(s, Biquad) for s in rows):
        raise ValueError(f'one to {MAX_SECTIONS} Biquad objects are required')
    return rows


def mul(a: list[int], b: list[int]) -> list[int]:
    if not a or not b:
        raise ValueError('polynomial must be nonempty')
    _check_bits(a)
    _check_bits(b)
    if (max(abs(x).bit_length() for x in a)
            + max(abs(x).bit_length() for x in b)
            + min(len(a), len(b)).bit_length() + 1 > MAX_INTEGER_BITS):
        raise ResourceLimitError('multiplication estimate exceeds bit budget')
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    _check_bits(out)
    return out


def gap_polynomial(sections, gamma):
    n, d, stable = [1], [1], True
    for section in sections:
        (b0, b1, b2, a1, a2), scale = integer_coefficients(section.coefficients)
        stable = stable and abs(a2) < scale and scale+a1+a2 > 0 and scale-a1+a2 > 0
        n = mul(n, list(squared_coefficients(b0, b1, b2)))
        d = mul(d, list(squared_coefficients(scale, a1, a2)))
    gn, gd = gamma.as_integer_ratio()
    if (2*max(abs(gn).bit_length(), abs(gd).bit_length())
            + max(max(abs(v).bit_length() for v in n),
                  max(abs(v).bit_length() for v in d)) + 2 > MAX_INTEGER_BITS):
        raise ResourceLimitError('gain polynomial estimate exceeds bit budget')
    p = [gn*gn*y - gd*gd*x for x, y in zip(n, d)]
    _check_bits(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p, bool(stable)


def to_bernstein_scaled(p: list[int]) -> list[int]:
    if not p or len(p) > 65:
        raise ValueError('polynomial degree must be 0..64')
    _check_bits(p)
    n = len(p)-1
    choose = [comb(n, k) for k in range(n+1)]
    positive_lcm = lcm(*choose)
    a = [sum(p[j]*comb(j, k)*2**k*(-1)**(j-k)
             for j in range(k, n+1)) for k in range(n+1)]
    result = [sum(a[k]*comb(i, k)*(positive_lcm//choose[k])
                  for k in range(i+1)) for i in range(n+1)]
    _check_bits(result)
    return result


def split_scaled(b: list[int]) -> tuple[list[int], list[int]]:
    if not b or len(b) > 65:
        raise ValueError('Bernstein degree must be 0..64')
    _check_bits(b)
    n = len(b)-1
    if max(abs(v).bit_length() for v in b) + n + 2 > MAX_INTEGER_BITS:
        raise ResourceLimitError('subdivision growth exceeds bit budget')
    v = b[:]
    left, right = [b[0] << n], [b[-1] << n]
    for r in range(1, n+1):
        v = [x+y for x, y in zip(v[:-1], v[1:])]
        left.append(v[0] << (n-r))
        right.append(v[-1] << (n-r))
    right.reverse()
    _check_bits(left)
    _check_bits(right)
    return left, right


def prove_positive(p: list[int], max_depth: int = 60,
                   max_nodes: int = 20000) -> dict:
    """CERTIFIED iff a complete strictly-positive dyadic cover was visited."""
    if (type(max_depth) is not int or not 0 <= max_depth <= 128
            or type(max_nodes) is not int or not 1 <= max_nodes <= 100000):
        raise ValueError('invalid depth or node budget')
    if not isinstance(p, (tuple, list)) or not p or len(p) > 65 or any(type(v) is not int for v in p):
        raise ValueError('invalid integer polynomial')
    try:
        stack = [(to_bernstein_scaled(list(p)), 0, 0)]
    except ResourceLimitError:
        return dict(verdict='unknown', nodes=0, max_depth=0, reason='integer_bits')
    nodes, leaves, unknown, max_seen = 0, [], False, 0
    while stack:
        if nodes >= max_nodes:
            unknown = True
            break
        b, index, depth = stack.pop()
        nodes += 1
        max_seen = max(max_seen, depth)
        if b[0] <= 0 or b[-1] <= 0:
            k = index if b[0] <= 0 else index+1
            return dict(verdict='condition_failed', nodes=nodes, max_depth=max_seen,
                        witness_t=[k, depth],
                        reason='exact nonpositive gap at dyadic t, c=2t-1')
        if min(b) > 0:
            leaves.append([index, depth])
            continue
        if depth >= max_depth or nodes >= max_nodes:
            unknown = True
            if nodes >= max_nodes:
                break
            continue
        try:
            left, right = split_scaled(b)
        except ResourceLimitError:
            unknown = True
            continue
        stack.append((right, 2*index+1, depth+1))
        stack.append((left, 2*index, depth+1))
    if unknown:
        return dict(verdict='unknown', nodes=nodes, max_depth=max_seen,
                    reason='depth/node/integer budget exhausted')
    return dict(verdict='certified', nodes=nodes, max_depth=max_seen,
                cover=leaves, degree=len(p)-1)


def certify_cascade(sections, max_gain=1.0, *, max_depth=48, max_nodes=20000) -> dict:
    """Exact fail-closed SOS strict-gain result; UNKNOWN is never a PASS.

    All original section denominators must be Schur, even if a pole cancels
    algebraically. Legacy v1 report fields are preserved.
    """
    rows = validate_sections(sections)
    gamma = positive_gamma(max_gain)
    if type(max_depth) is not int or not 0 <= max_depth <= 128:
        raise ValueError('max_depth must be an integer in [0,128]')
    if type(max_nodes) is not int or not 1 <= max_nodes <= 100000:
        raise ValueError('max_nodes must be an integer in [1,100000]')
    try:
        p, stable = gap_polynomial(rows, gamma)
        report = (prove_positive(p, max_depth, max_nodes) if stable else
                  {'verdict': 'denominator_not_schur', 'nodes': 0})
        degree = len(p)-1
    except (ResourceLimitError, MemoryError):
        report = {'verdict': 'unknown', 'nodes': 0, 'max_depth': 0,
                  'reason': 'integer/memory budget exhausted during polynomial preparation'}
        stable, degree = False, 0
    report['status'] = report.pop('verdict')
    report.update(schema=SCHEMA, method='integer-bernstein-subdivision',
                  certified=report['status'] == 'certified', strict=True,
                  denominator_stable=stable, max_gain_hex=gamma.hex(),
                  sections_hex=[s.hex_coefficients() for s in rows],
                  degree=degree,
                  scope='fixed real LTI cascade; all section denominators stable; no runtime-roundoff guarantee')
    return report
