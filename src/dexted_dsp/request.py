"""Bounded, owning iterable adapter for input-cardinality safety.

At most limit+1 next() calls; a blocking next() or malicious __float__
requires an isolated process supervisor for an elapsed-time bound.
"""
from typing import Iterable, TypeVar

T = TypeVar('T')


def bounded_take(values: Iterable[T], limit: int, field: str) -> tuple[T, ...]:
    if type(limit) is not int or not 0 <= limit <= 100000:
        raise ValueError('invalid iterable limit')
    try:
        it = iter(values)
    except TypeError as exc:
        raise ValueError(f'{field} must be iterable') from exc
    result = []
    for _ in range(limit):
        try:
            result.append(next(it))
        except StopIteration:
            return tuple(result)
    try:
        next(it)
    except StopIteration:
        return tuple(result)
    raise ValueError(f'{field} exceeds maximum of {limit} elements')
