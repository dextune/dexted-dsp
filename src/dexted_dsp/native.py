"""Optional explicit ctypes loaders; native return codes are fail-closed."""
import ctypes
from pathlib import Path

from .model import Biquad, positive_gamma
from .cascade import validate_sections


class NativeBiquad:
    """Caller-provided native library, exact deployed float32 semantics."""
    def __init__(self, library_path):
        path = Path(library_path)
        if not path.is_absolute() or not path.is_file():
            raise ValueError("an existing absolute library path is required")
        self._library = ctypes.CDLL(str(path))
        self._call = self._library.dexted_dsp_biquad_f32
        self._call.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.c_double]
        self._call.restype = ctypes.c_int

    def certify(self, biquad: Biquad, max_gain=1.0) -> bool:
        if not isinstance(biquad, Biquad):
            raise TypeError('native API expects a Biquad')
        gamma = positive_gamma(max_gain)
        rounded = Biquad.from_coefficients(biquad.coefficients, precision='float32')
        if rounded.coefficients != biquad.coefficients:
            raise ValueError("native API requires explicitly deployed float32 coefficients")
        array = (ctypes.c_float*5)(*rounded.coefficients)
        code = self._call(array, gamma)
        if code == 1:
            return True
        if code == 0:
            return False
        raise RuntimeError(f"native biquad returned error or unsupported code {code}")


class NativeCascade:
    """Optional C ABI, preserving 1/0/-1/-2/-3 integer status semantics."""
    def __init__(self, library_path):
        path = Path(library_path)
        if not path.is_absolute() or not path.is_file():
            raise ValueError('an existing absolute library path is required')
        self._library = ctypes.CDLL(str(path))
        self._call = self._library.dexted_dsp_cascade_f32
        self._call.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.c_size_t,
                              ctypes.c_double, ctypes.c_uint, ctypes.c_size_t]
        self._call.restype = ctypes.c_int

    def check(self, sections, max_gain=1.0, *, max_depth=48, max_nodes=20000) -> str:
        rows = validate_sections(sections)
        if type(max_depth) is not int or not 0 <= max_depth <= 128:
            raise ValueError('max_depth must be in [0,128]')
        if type(max_nodes) is not int or not 1 <= max_nodes <= 100000:
            raise ValueError('max_nodes must be in [1,100000]')
        packed = []
        for section in rows:
            rounded = Biquad.from_coefficients(section.coefficients, precision='float32')
            if rounded.coefficients != section.coefficients:
                raise ValueError('every section must have deployed float32 coefficients')
            packed.extend(rounded.coefficients)
        array = (ctypes.c_float*len(packed))(*packed)
        code = self._call(array, len(rows), positive_gamma(max_gain), max_depth, max_nodes)
        if code == 1:
            return 'certified'
        if code == 0:
            return 'condition_failed'
        if code == -3:
            return 'unknown'
        if code == -1:
            raise ValueError('native cascade rejected invalid input')
        raise RuntimeError(f'native cascade returned error or unsupported code {code}')
