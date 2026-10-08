"""User-oriented offline filter inspections with checkable proof envelopes.

An inspection binds the *actual represented coefficients* and requested gain
limit to the core proof. This API does not normalize a0, redesign filters,
certify finite-precision runtime arithmetic, or process audio.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isclose, isfinite
import hashlib
import json
from pathlib import Path
from typing import Iterable

from .biquad import certify
from .cascade import certify_cascade, validate_sections
from .model import Biquad, finite_float, from_sos, positive_gamma
from .peak import GainBounds, bound_peak_gain, bound_sos_peak_gain
from .peak_region import PeakRegion, localize_peak
from .verify import verify_biquad, verify_cascade

SCHEMA = 'dexted-dsp/inspection/v2'
LEGACY_SCHEMA = 'dexted-dsp/inspection/v1'


def _sample_rate(fs: float | None) -> float | None:
    if fs is None:
        return None
    rate = finite_float(fs)
    if rate <= 0:
        raise ValueError('fs must be a positive finite sample rate in Hz')
    return rate


def _digest(rows: tuple[Biquad, ...], gamma: float, fs: float | None,
            precision: str, kind: str) -> str:
    binding = {
        'kind': kind, 'precision': precision,
        'coefficients_hex': [s.hex_coefficients() for s in rows],
        'max_gain_hex': gamma.hex(),
        'sample_rate_hex': fs.hex() if fs is not None else None,
    }
    raw = json.dumps(binding,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')
    return hashlib.sha256(raw).hexdigest()


def _validate_precision(rows: tuple[Biquad, ...], precision: str) -> None:
    """A prebuilt Biquad labeled float32 must really hold binary32 values."""
    if precision == 'float32':
        for section in rows:
            f32 = Biquad.from_coefficients(section.coefficients, precision='float32')
            if f32.coefficients != section.coefficients:
                raise ValueError('float32 inspection requires already deployed binary32 coefficients')


@dataclass(frozen=True, slots=True)
class InspectionReport:
    kind: str
    status: str
    reason: str
    input_digest: str
    precision: str
    max_gain: float
    fs: float | None
    proof: dict
    gain_bounds: GainBounds | None
    peak_bits: int
    max_depth: int
    max_nodes: int
    peak_region: PeakRegion | None = None
    region_bits: int | None = None

    @property
    def certified(self) -> bool:
        return self.status == 'certified'

    def as_dict(self) -> dict:
        return {
            'schema': SCHEMA,
            'kind': self.kind, 'status': self.status, 'reason': self.reason,
            'certified': self.certified, 'input_digest': self.input_digest,
            'precision': self.precision,
            'max_gain_hex': self.max_gain.hex(), 'sample_rate_hex': self.fs.hex() if self.fs is not None else None,
            'peak_bits': self.peak_bits, 'max_depth': self.max_depth, 'max_nodes': self.max_nodes,
            'gain_bounds': self.gain_bounds.as_dict() if self.gain_bounds is not None else None,
            **({'peak_region':self.peak_region.as_dict(), 'region_bits':self.region_bits}
               if self.region_bits is not None else {}),
            'proof': self.proof,
            'scope': 'offline ideal real fixed-coefficient LTI response only',
            'note': 'hash binds inputs but is not a digital signature or external safety audit',
        }

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.as_dict(),indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')

    def markdown(self) -> str:
        bounds = ('Unavailable (unstable denominator or resource limit)' if self.gain_bounds is None else
                  f'[{self.gain_bounds.lower_ratio}, {self.gain_bounds.upper_ratio}] (exact rational endpoints; {self.gain_bounds.status})')
        region = ('Not computed (SOS cascade or unstable biquad)' if self.peak_region is None else
                  str(self.peak_region.cosine_intervals))
        return (f'# Dexted DSP filter inspection\n\n'
                f'- **Status:** {self.status}\n- **Reason:** `{self.reason}`\n'
                f'- **Model:** {self.kind}, {self.precision}, ideal fixed-coefficient\n'
                f'- **Gain condition:** strict peak < {self.max_gain!r}\n'
                f'- **Provable peak gain interval:** {bounds}\n'
                f'- **Certified cos(omega) peak region:** {region}\n'
                f'- **SHA-256 input binding:** `{self.input_digest}`\n\n'
                'The interval concerns the ideal transfer function; no hardware or runtime-roundoff guarantee.\n'
                'Inspect the paired JSON certificate for the complete proof payload.\n')


def inspect_biquad(biquad: Biquad | Iterable[float], *, max_gain: float = 1.0,
                   precision: str = 'float64', fs: float | None = None,
                   peak_bits: int = 24, region_bits: int = 24) -> InspectionReport:
    """Inspect a Biquad or an explicitly rounded five-coefficient row."""
    if precision not in ('float32','float64'):
        raise ValueError('precision must be float32 or float64')
    f = biquad if isinstance(biquad,Biquad) else Biquad.from_coefficients(biquad,precision=precision)
    gamma,rate = positive_gamma(max_gain),_sample_rate(fs)
    _validate_precision((f,),precision)
    result = certify(f,gamma)
    bounds = bound_peak_gain(f,precision_bits=peak_bits)
    region = localize_peak(f,isolation_bits=region_bits,fs=rate)
    status = 'certified' if result.certified else 'rejected'
    return InspectionReport('biquad',status,result.status,_digest((f,),gamma,rate,precision,'biquad'),
                            precision,gamma,rate,result.as_dict(),bounds,peak_bits,48,20000,region,region_bits)


def inspect_cascade(sections: Iterable[Biquad], *, max_gain: float = 1.0,
                    precision: str = 'float64', fs: float | None = None,
                    peak_bits: int = 8, max_depth: int = 48,
                    max_nodes: int = 20000) -> InspectionReport:
    """Inspect existing deployed Biquad objects without re-rounding them."""
    if precision not in ('float32','float64'):
        raise ValueError('precision must be float32 or float64')
    if type(peak_bits) is not int or not 0 <= peak_bits <= 32:
        raise ValueError('peak_bits must be an integer in [0,32]')
    rows = validate_sections(sections)
    _validate_precision(rows,precision)
    gamma,rate = positive_gamma(max_gain),_sample_rate(fs)
    core = certify_cascade(rows,gamma,max_depth=max_depth,max_nodes=max_nodes)
    if core['certified']:
        status = 'certified'
    elif core['status']=='unknown':
        status = 'unknown'
    else:
        status = 'rejected'
    bounds = None
    if core['denominator_stable']:
        bounds = bound_sos_peak_gain(rows,precision_bits=peak_bits,max_depth=max_depth,max_nodes=max_nodes)
    return InspectionReport('sos',status,core['status'],_digest(rows,gamma,rate,precision,'sos'),
                            precision,gamma,rate,core,bounds,peak_bits,max_depth,max_nodes)


def inspect_sos(sos: Iterable[Iterable[float]], *, max_gain: float = 1.0,
                precision: str = 'float32', fs: float | None = None,
                peak_bits: int = 8, max_depth: int = 48,
                max_nodes: int = 20000) -> InspectionReport:
    """Accept SciPy six-column SOS rows [b0,b1,b2,1,a1,a2].

    Float32 rounding is explicit and precedes all verification. No dependency
    on SciPy exists in the runtime. Reject a0 != 1 rather than changing it.
    """
    rows = from_sos(sos,precision=precision)
    return inspect_cascade(rows,max_gain=max_gain,precision=precision,fs=fs,
                           peak_bits=peak_bits,max_depth=max_depth,max_nodes=max_nodes)



def _region_matches(candidate: dict | None, expected: dict | None, fs: float | None) -> bool:
    """Compare exact proof fields exactly; tolerate only libm-display rounding.

    Approximate Hz endpoints do not participate in any acceptance decision.
    Nevertheless they are sanity-checked to avoid maliciously misleading UI.
    """
    if expected is None:
        return candidate is None
    if not isinstance(candidate,dict):
        return False
    a=dict(candidate)
    b=dict(expected)
    approx_a=a.pop('frequency_hz_approx',None)
    approx_b=b.pop('frequency_hz_approx',None)
    if a!=b:
        return False
    if approx_b is None:
        return approx_a is None
    if (not isinstance(approx_a,list) or len(approx_a)!=len(approx_b)):
        return False
    for actual, reference in zip(approx_a,approx_b):
        if not isinstance(actual,list) or len(actual)!=2:
            return False
        for value,truth in zip(actual,reference):
            if type(value) not in (float,int) or not isfinite(value):
                return False
            if not isclose(value,truth,rel_tol=1e-12,abs_tol=(fs or 1.0)*1e-12):
                return False
    return True


def verify_inspection(report: dict, expected, *, precision: str = 'float64',
                      max_gain: float = 1.0, fs: float | None = None) -> bool:
    """Recheck claimed PASS against caller-supplied inputs, never report flags.

    v1 biquad proofs are additionally compared with a fresh integer witness.
    SOS proofs use the independent exact-rational dyadic-cover checker.
    Limits on accepted proof/refinement sizes are applied before recomputation.
    """
    try:
        if not isinstance(report,dict) or report.get('schema') not in (SCHEMA,LEGACY_SCHEMA) or report.get('status')!='certified':
            return False
        if report.get('certified') is not True or report.get('reason')!='certified' or precision not in ('float32','float64'):
            return False
        gamma,rate=positive_gamma(max_gain),_sample_rate(fs)
        if report.get('precision')!=precision or report.get('max_gain_hex')!=gamma.hex():
            return False
        if report.get('sample_rate_hex')!=(rate.hex() if rate is not None else None):
            return False
        peak_bits=report.get('peak_bits')
        if type(peak_bits) is not int or not 0<=peak_bits<=64:
            return False
        kind=report.get('kind')
        if kind=='biquad':
            f=expected if isinstance(expected,Biquad) else Biquad.from_coefficients(expected,precision=precision)
            rows=(f,)
            _validate_precision(rows,precision)
            if _digest(rows,gamma,rate,precision,kind)!=report.get('input_digest'):
                return False
            proof=report.get('proof')
            if report.get('max_depth')!=48 or report.get('max_nodes')!=20000:
                return False
            if not verify_biquad(proof,f,gamma) or proof != certify(f,gamma).as_dict():
                return False
            expected_bounds=bound_peak_gain(f,precision_bits=peak_bits)
            if report['schema']==SCHEMA and ('peak_region' not in report or 'region_bits' not in report):
                return False
            if report['schema']==LEGACY_SCHEMA and ('peak_region' in report or 'region_bits' in report):
                return False
            if 'peak_region' in report or 'region_bits' in report:
                region_bits=report.get('region_bits')
                if type(region_bits) is not int or not 0<=region_bits<=64:
                    return False
                region=localize_peak(f,isolation_bits=region_bits,fs=rate)
                expected_region = region.as_dict() if region else None
                candidate_region = report.get('peak_region')
                if not _region_matches(candidate_region,expected_region,rate):
                    return False
        elif kind=='sos':
            if 'peak_region' in report or 'region_bits' in report:
                return False
            if peak_bits>32:
                return False
            rows=(validate_sections(expected) if isinstance(expected,(tuple,list)) and expected
                  and all(isinstance(f,Biquad) for f in expected) else from_sos(expected,precision=precision))
            _validate_precision(rows,precision)
            if _digest(rows,gamma,rate,precision,kind)!=report.get('input_digest'):
                return False
            depth,nodes=report.get('max_depth'),report.get('max_nodes')
            if type(depth) is not int or type(nodes) is not int or not 0<=depth<=128 or not 1<=nodes<=100000:
                return False
            if not verify_cascade(report.get('proof'),rows,gamma):
                return False
            expected_bounds=bound_sos_peak_gain(rows,precision_bits=peak_bits,max_depth=depth,max_nodes=nodes)
        else:
            return False
        candidate=report.get('gain_bounds')
        return candidate == (expected_bounds.as_dict() if expected_bounds is not None else None)
    except (ValueError,TypeError,OverflowError,KeyError,ZeroDivisionError,MemoryError):
        return False
