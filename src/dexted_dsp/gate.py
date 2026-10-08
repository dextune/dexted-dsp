"""Typed, decision-only producer/consumer interface (not a deployment gate).

Proof generation and independent verification are required for 'verified'.
The caller must separately attest deployment bytes, policy, worker time/RSS,
and runtime DSP behavior; a mathematically valid proof alone cannot deploy.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from .model import Biquad, positive_gamma
from .cascade import certify_cascade, validate_sections
from .verify import verify_cascade


@dataclass(frozen=True, slots=True)
class CheckResult:
    math_status: str
    execution_status: str
    proof_status: str
    input_digest: str
    proof: dict | None
    reason: str

    @property
    def verified(self) -> bool:
        return (self.math_status == 'certified' and
                self.execution_status == 'completed' and
                self.proof_status == 'valid')

    @property
    def deployment_allowed(self) -> bool:
        # No unverified caller-policy, runtime model or artifact byte binding.
        return False

    def __bool__(self):
        raise TypeError('CheckResult cannot be used as a truth value; check .verified explicitly')


def check_sos(sections, max_gain=1.0, *, max_depth=48, max_nodes=20000,
              max_proof_bytes=4_194_304) -> CheckResult:
    """Return exact proof status, keeping rejection and unknown separate.

    This synchronous in-process entrypoint has node/bit/serialization bounds,
    but NOT a hard wall-clock or RSS guarantee. Untrusted jobs must execute in
    a supervised process with an independently enforced timeout.
    """
    if type(max_proof_bytes) is not int or not 1 <= max_proof_bytes <= 4_194_304:
        raise ValueError('max_proof_bytes must be 1..4194304')
    rows = validate_sections(sections)
    gamma = positive_gamma(max_gain)
    raw = json.dumps({'sections_hex':[s.hex_coefficients() for s in rows],
                      'gamma_hex':gamma.hex()},sort_keys=True,separators=(',',':')).encode()
    digest = hashlib.sha256(raw).hexdigest()
    result = certify_cascade(rows, gamma, max_depth=max_depth, max_nodes=max_nodes)
    status = result['status']
    if status != 'certified':
        return CheckResult(status, 'completed', 'not_run', digest,
                           result, result.get('reason',status))
    try:
        proof_bytes = json.dumps(result,sort_keys=True,separators=(',',':'),
                                 allow_nan=False).encode('utf-8')
    except (ValueError, TypeError, OverflowError, MemoryError):
        return CheckResult('certified', 'resource_limited', 'not_run', digest,
                           None, 'proof serialization failed')
    if len(proof_bytes) > max_proof_bytes:
        return CheckResult('certified', 'resource_limited', 'not_run', digest,
                           None, 'proof exceeds byte budget')
    try:
        valid = verify_cascade(result, rows, gamma)
    except (ValueError, TypeError, ArithmeticError, MemoryError):
        valid = False
    return CheckResult('certified','completed','valid' if valid else 'invalid',
                       digest,result,'certified' if valid else 'proof verification failed')
