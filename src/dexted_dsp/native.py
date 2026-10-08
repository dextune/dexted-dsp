"""Optional explicit ctypes native loaders; never download or build automatically."""
import ctypes
from pathlib import Path
from .model import Biquad, positive_gamma


class NativeBiquad:
    """Caller-provided library, with explicitly representable float32 values."""
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


class NativeCascade:
    """Native SOS exact-gain predicate, with explicit resource-limit status.

    Return values are strings rather than bool, so negative native errors
    cannot silently be treated as accepted filters. This API does NOT return
    a serializable proof; use Python's certify_cascade for that.
    """
    def __init__(self, library_path):
        path = Path(library_path)
        if not path.is_absolute() or not path.is_file():
            raise ValueError('an existing absolute library path is required')
        lib = ctypes.CDLL(str(path))
        self._call = lib.dexted_dsp_cascade_f32
        self._call.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.c_size_t,
                              ctypes.c_double, ctypes.c_uint, ctypes.c_size_t]
        self._call.restype = ctypes.c_int
        self._library = lib

    def check(self, sections, max_gain=1.0, *, max_depth=48, max_nodes=20000) -> str:
        rows = tuple(sections)
        if not 1 <= len(rows) <= 32 or not all(isinstance(s,Biquad) for s in rows):
            raise ValueError('1..32 Biquad objects required')
        if type(max_depth) is not int or not 0<=max_depth<=128:
            raise ValueError('max_depth must be in [0,128]')
        if type(max_nodes) is not int or not 1<=max_nodes<=100000:
            raise ValueError('max_nodes must be in [1,100000]')
        packed=[]
        for section in rows:
            rounded=Biquad.from_coefficients(section.coefficients,precision='float32')
            if rounded.coefficients != section.coefficients:
                raise ValueError('every section must have deployed float32 coefficients')
            packed.extend(rounded.coefficients)
        array=(ctypes.c_float*len(packed))(*packed)
        code=self._call(array,len(rows),positive_gamma(max_gain),max_depth,max_nodes)
        if code==-2:raise RuntimeError('native cascade hit an internal/resource error')
        if code==-1:raise ValueError('native cascade rejected invalid input')
        return {1:'certified',0:'condition_failed',-3:'unknown'}[code]
