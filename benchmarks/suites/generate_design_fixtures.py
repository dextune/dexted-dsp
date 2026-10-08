#!/usr/bin/env python3
"""Generate a frozen *designed synthetic* SOS pilot dataset, not real product data.

This utility is an explicit opt-in regeneration tool. The checked-in JSON is the
benchmark input contract; routine benchmark executions NEVER regenerate it.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import scipy
from scipy import signal

ROOT=Path(__file__).resolve().parent


def make() -> dict:
    cases=[]
    def add(name, family, sos, limit=1.01):
        arr=np.asarray(sos,dtype=np.float32)
        cases.append({'id':name,'family':family,'precision':'float32',
                      'max_gain':limit,'sos':arr.astype(np.float64).tolist(),
                      'split':'holdout' if hashlib.sha256(name.encode()).digest()[0]%4==0 else 'development'})
    for order in (2,4,8,12):
        for cutoff in (.02,.12,.3):
            add(f'butter-lowpass-{order}-{cutoff}', 'designed-butter',
                signal.butter(order,cutoff,output='sos'))
    for order in (4,8):
        for cutoff in (.05,.2):
            add(f'cheby1-lowpass-{order}-{cutoff}','designed-cheby1',
                signal.cheby1(order,.5,cutoff,output='sos'))
    for order in (4,8):
        add(f'ellip-lowpass-{order}','designed-ellip',
            signal.ellip(order,.5,50,.12,output='sos'))
    for q in (100.,10000.):
        for f in (.01,.49):
            b,a=signal.iirpeak(f,q)
            add(f'iirpeak-{f}-{int(q)}','designed-high-q',[[*b,*a]])
    a=2.**-14
    add('hidden-peak-adversarial','constructed-adversarial',
        [[a,0,-a,1,0,1-a]],1.0)
    add('compensating-two-sections','constructed-adversarial',
        [[1,-.75,0,1,-.125,0],[.75,-.09375,0,1,-.75,0]],1.0)
    add('strict-unity-boundary','constructed-adversarial',[[1,0,0,1,0,0]],1.0)
    return {
        'schema':'dexted-dsp/designed-sos-pilot/v1',
        'description':'Deterministically designed filters; NOT field recordings or product-failure prevalence',
        'generator':'benchmarks/suites/generate_design_fixtures.py',
        'scipy_version_at_generation':scipy.__version__,
        'numpy_version_at_generation':np.__version__,
        'input_contract':'fixed represented binary32 SOS, per-case strict binary64 max_gain',
        'split_rule':'sha256(case_id).first_byte % 4 == 0 => holdout; fixed before results',
        'cases':cases,
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=ROOT/'fixtures/designed_sos_pilot_v1.json')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    content=json.dumps(make(),sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n'
    if args.check:
        if not args.out.is_file() or args.out.read_text()!=content:
            raise SystemExit('Generated fixture differs from pinned archive; inspect dependency versions')
        print('Pinned designed SOS fixture: PASS')
    else:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(content)
        print('Written:',args.out,'sha256',hashlib.sha256(content.encode()).hexdigest())

if __name__=='__main__':
    main()
