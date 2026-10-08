"""Usage: python tools/native_smoke.py /absolute/path/to/shared/library"""
from pathlib import Path
import json
import math
import random
import sys
from dexted_dsp import Biquad
from dexted_dsp.native import NativeBiquad
from dexted_dsp.reference import reference_decision

engine=NativeBiquad(Path(sys.argv[1]).resolve())
rng=random.Random(951671)
count=256
for _ in range(count):
    radius=rng.uniform(.01,1.2);angle=rng.uniform(0,math.pi)
    f=Biquad.from_coefficients([rng.uniform(-.5,.5) for _ in range(3)]+
                              [-2*radius*math.cos(angle),radius*radius],precision='float32')
    assert engine.certify(f)==reference_decision(f)
try:
    engine.certify(Biquad.from_coefficients([.1,0,0,0,0]))
except ValueError:
    pass
else:
    raise AssertionError('native loader silently changed deployment precision')
print(json.dumps({'native_wrapper_cases':count,'mismatches':0,'implicit_rounding_rejected':True}))
