#!/usr/bin/env python3
"""Reproducible, honest *pilot* comparison for current Dexted DSP APIs.

Three DIFFERENT tasks are timed and labeled individually: an offline SOS
exact decision, a full inspect+gain-bounds workflow, and a finite SciPy grid
response check (NOT a certificate). Never market cross-task time ratios.
The fixed designed SOS cases are synthetic, not real-production prevalence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import random
import statistics
import sys
import time
from datetime import datetime, timezone

import numpy as np
import scipy
from scipy import signal

from dexted_dsp import certify_cascade, from_sos, inspect_sos, verify_cascade

ROOT=Path(__file__).resolve().parents[2]
FIXTURE=Path(__file__).resolve().parent/'fixtures/designed_sos_pilot_v1.json'
SOURCES=['src/dexted_dsp/biquad.py','src/dexted_dsp/cascade.py',
         'src/dexted_dsp/peak.py','src/dexted_dsp/peak_region.py',
         'src/dexted_dsp/inspection.py','benchmarks/suites/run_pilot_v2.py']


def digest(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def percentile(samples, percent):
    ordered=sorted(samples)
    x=(len(ordered)-1)*percent/100
    l=math.floor(x);r=math.ceil(x)
    return float(ordered[l]+(ordered[r]-ordered[l])*(x-l))


def grid_gate(sos, limit:float, omega)->bool:
    # Response sampler; all checks refer to exact represented input values.
    for b0,b1,b2,a0,a1,a2 in sos:
        if a0!=1 or not (abs(a2)<1 and 1+a1+a2>0 and 1-a1+a2>0):
            return False
    _,response=signal.freqz_sos(sos,worN=omega)
    return bool(np.max(np.abs(response))<limit)


def run(fixture:Path, trials:int, limit:int|None, seed:int)->dict:
    archive=json.loads(fixture.read_text())
    if archive['schema']!='dexted-dsp/designed-sos-pilot/v1':
        raise ValueError('unexpected fixture schema')
    cases=archive['cases'] if limit is None else archive['cases'][:limit]
    rng=random.Random(seed)
    omega=np.linspace(0,np.pi,1024)  # inclusive [0,pi], no adaptive frequency refinement
    measurements=[]
    for case in cases:
        sos=np.asarray(case['sos'],dtype=np.float64)
        threshold=case['max_gain']
        rows=from_sos(sos,precision='float32')
        exact=certify_cascade(rows,threshold,max_depth=32,max_nodes=5000)
        if exact['certified'] and not verify_cascade(exact,rows,threshold):
            raise AssertionError('producer certificate did not verify: '+case['id'])
        grid=grid_gate(sos,threshold,omega)
        inspect=inspect_sos(sos,max_gain=threshold,precision='float32',
                            peak_bits=4,max_depth=32,max_nodes=5000)
        if inspect.reason!=exact['status']:
            raise AssertionError('inspection changes decision: '+case['id'])
        methods={
            'exact_gate_predicate':lambda:certify_cascade(rows,threshold,max_depth=32,max_nodes=5000)['status'],
            'full_inspection_with_bounds':lambda:inspect_sos(sos,max_gain=threshold,precision='float32',peak_bits=4,max_depth=32,max_nodes=5000).status,
            'scipy_inclusive_grid1024':lambda:grid_gate(sos,threshold,omega),
        }
        raw={k:[] for k in methods}
        # Warm each path once before timing, shuffled call order per trial.
        for call in methods.values():call()
        for _ in range(trials):
            order=list(methods);rng.shuffle(order)
            for name in order:
                start=time.perf_counter_ns()
                methods[name]()
                raw[name].append((time.perf_counter_ns()-start)/1_000_000)
        measurements.append({
            'id':case['id'],'family':case['family'],'split':case['split'],
            'sections':len(rows),'exact_status':exact['status'],
            'sampling_pass':grid,'inspection_status':inspect.status,
            'gain_enclosure_status':inspect.gain_bounds.status if inspect.gain_bounds else None,
            'exact_certificate_verified':bool(exact['certified']),
            'raw_ms':raw,
            'median_ms':{k:statistics.median(v) for k,v in raw.items()},
            'p95_ms':{k:percentile(v,95) for k,v in raw.items()},
        })
    assessed=[m for m in measurements if m['exact_status']!='unknown']
    if any(m['exact_status']=='certified' and not m['exact_certificate_verified'] for m in measurements):
        raise AssertionError('verified certificate missing')
    return {
        'schema':'dexted-dsp/pilot-v2/v1','type':'DESIGNED-SYNTHETIC pilot only',
        'notice':'not real-world prevalence; no outside reproduction; timing methods perform DIFFERENT tasks',
        'fixture_sha256':digest(fixture),
        'source_sha256':{p:digest(ROOT/p) for p in SOURCES},
        'protocol':{'trials':trials,'shuffle_seed':seed,'grid_points':1024,'grid_includes_endpoints':True,
                    'peak_bits':4,'max_depth':32,'max_nodes':5000,'precision':'binary32','threshold':'per fixture',
                    'warmup_each_method':1,'timer':'perf_counter_ns','sampling_is_not_a_certificate':True},
        'environment':{'timestamp_utc':datetime.now(timezone.utc).isoformat(),
                       'platform':platform.platform(),'cpu_count':os.cpu_count(),
                       'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,
                       'cpu_pinning':False,'virtualized_host_not_controlled':True},
        'totals':{'cases':len(measurements),'assessed_exact':len(assessed),
                  'unknown':sum(m['exact_status']=='unknown' for m in measurements),
                  'false_accepts_grid':sum(m['sampling_pass'] and m['exact_status'] not in ('certified','unknown') for m in assessed),
                  'false_rejects_grid':sum(not m['sampling_pass'] and m['exact_status']=='certified' for m in assessed)},
        'cases':measurements,
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture',type=Path,default=FIXTURE)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--trials',type=int,default=30)
    parser.add_argument('--limit',type=int)
    parser.add_argument('--seed',type=int,default=20261008)
    args=parser.parse_args()
    if not 3<=args.trials<=1000 or (args.limit is not None and args.limit<1):
        parser.error('trials 3-1000; limit must be positive')
    if args.out.exists():
        parser.error('refusing to overwrite an existing result; choose new --out')
    result=run(args.fixture.resolve(),args.trials,args.limit,args.seed)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':'pilot complete','path':str(args.out),
                      'totals':result['totals'],'trials':args.trials},indent=2))

if __name__=='__main__':
    main()
