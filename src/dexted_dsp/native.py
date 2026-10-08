"""Optional explicit ctypes loader; no automatic native code download/build."""
import ctypes
from pathlib import Path
from .model import Biquad, positive_gamma


class NativeBiquad:
    """Load a library that YOU built, from an explicit trusted absolute path.

    This native predicate takes binary32 coefficients. The caller must already
    have a Biquad whose values are exactly representable as float32. Python's
    certify() supplies full proof metadata; this class returns only a predicate.
    """
    def __init__(self, library_path):
        path = Path(library_path)
        if not path.is_absolute() or not path.is_file():
            raise ValueError("an existing absolute library path is required")
        self._library = ctypes.CDLL(str(path))
        self._call = self._library.dexted_dsp_biquad_f32
        self._call.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.c_double]
        self._call.restype = ctypes.c_int

    def certify(self, biquad: Biquad, max_gain=1.0) -> bool:
        gamma = positive_gamma(max_gain)
        rounded = Biquad.from_coefficients(biquad.coefficients, precision='float32')
        if rounded.coefficients != biquad.coefficients:
            raise ValueError("native API requires explicitly deployed float32 coefficients")
        array = (ctypes.c_float*5)(*rounded.coefficients)
        code = self._call(array, gamma)
        if code < 0:
            raise RuntimeError(f"native predicate returned error code {code}")
        return code == 1
