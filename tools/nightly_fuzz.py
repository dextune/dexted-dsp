#!/usr/bin/env python3
"""Reproducible exact-integer/Fraction differential fuzzing (no third party libs)."""
from __future__ import annotations
import argparse
import json
import math
import random
import struct

from dexted_dsp import Biquad,certify
from dexted_dsp.reference import reference_decision


def fuzz(count=50000,seed=20261008):
    rng=random.Random(seed)
    invalid=0
    checked=0
    for i in range(count):
        if i%5:
            v=[struct.unpack('!f',struct.pack('!I',rng.getrandbits(32)))[0] for _ in range(5)]
        else:
            # Adversarial stable near-unit pole family, binary32-rounded.
            radius=1-2**-rng.randint(8,20)
            theta=rng.uniform(.0001,math.pi-.0001)
            v=[rng.uniform(-2,2) for _ in range(3)]+[-2*radius*math.cos(theta),radius**2]
        try:
            f=Biquad.from_coefficients(v,precision='float32')
        except ValueError:
            invalid+=1;continue
        gamma=2**rng.uniform(-6,6)
        expected=reference_decision(f,gamma)
        observed=certify(f,gamma).certified
        if observed!=expected:
            raise AssertionError(f'false agreement case={i} coefficients={f.hex_coefficients()} gamma={gamma.hex()}')
        checked+=1
    return {'status':'passed','seed':seed,'cases':count,'finite_checked':checked,'invalid_rejected':invalid,
            'caveat':'two in-repository exact implementations, not external proof'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--count',type=int,default=50000);p.add_argument('--seed',type=int,default=20261008)
    args=p.parse_args()
    if not 1<=args.count<=1000000:p.error('count must be in [1,1000000]')
    print(json.dumps(fuzz(args.count,args.seed),indent=2))
