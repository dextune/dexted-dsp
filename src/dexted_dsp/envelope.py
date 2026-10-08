"""Size-capped JSON certificate parsing; duplicate-key and unknown-schema rejection.

This parser checks transport safety. It does NOT prove the mathematical claim:
call verify_serialized_certificate with independent, caller-supplied inputs.
"""
from __future__ import annotations

import json
import math

MAX_PROOF_BYTES = 4_194_304
MAX_INPUT_BYTES = 131_072
MAX_NESTING = 16
KNOWN_SCHEMAS = {
    'dexted-dsp/biquad/v1',
    'dexted-dsp/cascade/v1',
    'dexted-dsp/inspection/v1',
    'dexted-dsp/inspection/v2',
}


def _no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON object key')
        result[key] = value
    return result


def _bounded_integer(token):
    if len(token) > 40:
        raise ValueError('JSON integer token exceeds limit')
    return int(token)


def _finite_decimal(token):
    number = float(token)
    if not math.isfinite(number):
        raise ValueError('non-finite JSON float')
    return number


def _forbid_constant(token):
    raise ValueError('non-standard JSON constant')


def parse_certificate_json(payload: bytes, *, max_bytes: int = MAX_PROOF_BYTES) -> dict:
    """Accept legacy JSON layout, but not duplicates, unknown schemas or overrun."""
    if type(payload) is not bytes:
        raise TypeError('certificate must be a byte string')
    if type(max_bytes) is not int or not 1 <= max_bytes <= MAX_PROOF_BYTES:
        raise ValueError('invalid maximum certificate length')
    if len(payload) > max_bytes:
        raise ValueError('certificate exceeds byte limit')
    document = json.loads(payload.decode('utf-8'), object_pairs_hook=_no_duplicate_keys,
                          parse_int=_bounded_integer, parse_float=_finite_decimal,
                          parse_constant=_forbid_constant)
    if not isinstance(document, dict) or document.get('schema') not in KNOWN_SCHEMAS:
        raise ValueError('unsupported certificate schema')
    stack = [(document, 1)]
    visited = 0
    while stack:
        item, depth = stack.pop()
        visited += 1
        if depth > MAX_NESTING or visited > MAX_PROOF_BYTES:
            raise ValueError('JSON nesting or token count exceeds budget')
        if isinstance(item, dict):
            stack.extend((key, depth+1) for key in item.keys())
            stack.extend((value, depth+1) for value in item.values())
        elif isinstance(item, list):
            stack.extend((value, depth+1) for value in item)
        elif isinstance(item, str) and len(item) > MAX_PROOF_BYTES:
            raise ValueError('oversized JSON token')
    return document


def verify_serialized_certificate(payload: bytes, expected, max_gain: float = 1.0, *,
                                  precision: str = 'float64',
                                  fs: float | None = None) -> bool:
    """Reject malformed or unsupported payload and recheck it against caller data."""
    try:
        report = parse_certificate_json(payload)
        schema = report['schema']
        if schema == 'dexted-dsp/biquad/v1':
            from .verify import verify_biquad
            return verify_biquad(report, expected, max_gain)
        if schema == 'dexted-dsp/cascade/v1':
            from .verify import verify_cascade
            return verify_cascade(report, expected, max_gain)
        from .inspection import verify_inspection
        return verify_inspection(report, expected, precision=precision, max_gain=max_gain, fs=fs)
    except (TypeError, ValueError, KeyError, OverflowError, RecursionError, MemoryError):
        return False
