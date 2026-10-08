"""Dexted DSP: exact, offline gain verification for fixed real filters."""
from .model import Biquad, from_sos
from .biquad import BiquadCertificate, certify
from .cascade import certify_cascade
from .verify import verify_biquad, verify_cascade
from .peak import GainBounds, bound_peak_gain, bound_sos_peak_gain
from .peak_region import PeakRegion, localize_peak
from .inspection import InspectionReport, inspect_biquad, inspect_sos, inspect_cascade, verify_inspection
__version__ = '0.1.0'
__all__ = ['Biquad','BiquadCertificate','certify','from_sos','certify_cascade','verify_biquad','verify_cascade',
           'GainBounds','bound_peak_gain','bound_sos_peak_gain','InspectionReport','inspect_biquad','inspect_sos',
           'inspect_cascade','verify_inspection','PeakRegion','localize_peak']
