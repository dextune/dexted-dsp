#!/usr/bin/env python3
"""Native-vs-Python cascade predicates and Python proof verifier regression."""
from __future__ import annotations
import json
import math
import random
import sys
from pathlib import Path

from dexted_dsp import Biquad,certify_cascade,verify_cascade
from dexted_dsp.native import NativeCascade


def check(path, count=300,seed=95128):
    native=NativeCascade(Path(path).resolve())
    rng=random.Random(seed)
    tested=passed=0
    for i in range(count):
        rows=[]
        for j in range(rng.randint(1,5)):
            pole=rng.uniform(.05,1.12);theta=rng.uniform(.03,math.pi-.03)
            coeffs=[rng.uniform(-.5,.5) for _ in range(3)]+[-2*pole*math.cos(theta),pole*pole]
            rows.append(Biquad.from_coefficients(coeffs,precision='float32'))
        native_status=native.check(rows)
        proof=certify_cascade(rows)
        if (native_status=='certified')!=proof['certified']:
            raise AssertionError(f'case {i}: native={native_status}, python={proof["status"]}')
        if proof['certified']:
            assert verify_cascade(proof,rows)
            passed+=1
        tested+=1
    return {'status':'passed','cases':tested,'certified_and_reverified':passed,'seed':seed,
            'scope':'float32 binary coefficient exact predicates; not native proof serialization'}

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: python tools/native_cascade_differential.py /absolute/path/libdexted_dsp.so')
    print(json.dumps(check(sys.argv[1]),indent=2))
