#!/usr/bin/env python3
"""Reproducible offline benchmarks; all outputs go under --out.

Timing is descriptive for this host, not a universal speed guarantee.
Grid sampling is a response-estimation baseline, NOT an exact certifier.
The float64 predicate uses the same closed-form idea without exact arithmetic.
"""
from __future__ import annotations
import argparse
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import subprocess
import sys
import time
from datetime import datetime, timezone

import numpy as np
import scipy
from scipy import signal
from dexted_dsp import Biquad, certify, certify_cascade, verify_cascade
from dexted_dsp.reference import reference_decision

ROOT = Path(__file__).resolve().parents[1]


def generate(seed, count):
    rng=np.random.default_rng(seed)
    groups={k:[] for k in ['ordinary','high_q','near_threshold','unstable']}
    for _ in range(count):
        r=rng.uniform(.02,.995); theta=rng.uniform(.02,np.pi-.02)
        groups['ordinary'].append([*rng.normal(0,.25,3),-2*r*np.cos(theta),r*r])
        frequency=rng.uniform(.005,.995);q=10**rng.uniform(2,6)
        b,a=signal.iirpeak(frequency,q)
        groups['high_q'].append([*(b*10**rng.uniform(-.4,.4)),a[1],a[2]])
        r=rng.uniform(.02,.99);peak=1+rng.uniform(-.0005,.0005)
        groups['near_threshold'].append([peak*(1-r),0,0,-r,0])
        r=rng.uniform(1.00001,1.3);theta=rng.uniform(.02,np.pi-.02)
        groups['unstable'].append([*rng.normal(0,.1,3),-2*r*np.cos(theta),r*r])
    return {k:np.ascontiguousarray(v,dtype=np.float32) for k,v in groups.items()}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, obj):
    Path(path).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf8')


def errors(out, truth):
    return {'false_accepts':int(np.sum((out==1)&(~truth))),
            'false_rejects':int(np.sum((out==0)&truth)),
            'invalid_or_error':int(np.sum(out<0))}


def cpu_model():
    try:
        for line in Path('/proc/cpuinfo').read_text().splitlines():
            if line.startswith('model name'):
                return line.split(':',1)[1].strip()
    except OSError:pass
    return platform.processor()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=ROOT/'benchmarks/results')
    parser.add_argument('--n',type=int,default=1024)
    parser.add_argument('--trials',type=int,default=9)
    parser.add_argument('--seed',type=int,default=20261007)
    parser.add_argument('--cxx',default=os.environ.get('CXX','g++'))
    args=parser.parse_args()
    if not 16<=args.n<=16384 or not 3<=args.trials<=31:
        parser.error('n must be in [16,16384]; trials in [3,31]')
    outdir=args.out.resolve();outdir.mkdir(parents=True,exist_ok=True)
    build=ROOT/'build/bench';build.mkdir(parents=True,exist_ok=True)
    # Linux/macOS g++/clang++ path. Windows users can run under WSL.
    library=build/('libbench.dylib' if sys.platform=='darwin' else 'libbench.so')
    source=ROOT/'benchmarks/kernels.cpp'
    command=[args.cxx,'-O3','-std=c++20','-shared','-fPIC','-ffp-contract=off',
             '-I',str(ROOT/'cpp/include'),str(source),'-o',str(library)]
    protocol={
        'seed':args.seed,'n_per_family':args.n,'trials':args.trials,'batch_repeats':4,
        'max_gain':1.-1e-4,'grids':[1024,16384],
        'source_hashes':{str(p.relative_to(ROOT)):digest(p) for p in
                         [source, Path(__file__), ROOT/'cpp/include/dexted_dsp/biquad.hpp',
                          *sorted((ROOT/'src/dexted_dsp').glob('*.py'))]},
        'method_order_seed':932851,'compile_command':command,
        'notes':['No fast-math; FMA contraction off; all native kernels compiled together.',
                 'Grid cache warmed before each timed trial; preparation not timed.',
                 'All native methods include validity and denominator checks; grids may exit early.',
                 'Both exact methods are checked before timing; no generated model tuning.',
                 'Synthetic stress fixtures are NOT representative of real-world prevalence.',
                 'Float64 algebraic test is a non-certified numerical baseline, often much faster.',
                 'No python-control/SLICOT, ADAC end-to-end, audio-quality or video-quality benchmark.']}
    save(outdir/'protocol.json',protocol)
    env={'timestamp_utc':datetime.now(timezone.utc).isoformat(), 'platform':platform.platform(),
         'machine':platform.machine(),'cpu':cpu_model(),'logical_cpus':os.cpu_count(),
         'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,
         'compiler':subprocess.check_output([args.cxx,'--version'],text=True).splitlines()[0],
         'thread_settings':{k:os.environ.get(k) for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']},
         'timer':'time.perf_counter_ns','cpu_pinning':False,
         'caveat':'Shared virtualized host; frequency scaling and load are not controlled.'}
    save(outdir/'environment.json',env)
    subprocess.run(command,check=True)
    lib=ct.CDLL(str(library))
    pf=np.ctypeslib.ndpointer(dtype=np.float32,ndim=2,flags='C_CONTIGUOUS')
    pi=np.ctypeslib.ndpointer(dtype=np.int32,ndim=1,flags='C_CONTIGUOUS')
    for name in ['exact_batch','float64_batch']:
        fn=getattr(lib,name);fn.argtypes=[pf,ct.c_size_t,ct.c_double,pi];fn.restype=None
    lib.grid_batch.argtypes=[pf,ct.c_size_t,ct.c_double,ct.c_size_t,pi];lib.grid_batch.restype=None
    data=generate(args.seed,args.n)
    np.savez_compressed(outdir/'fixtures.npz',**data)
    result={'protocol':protocol,'fixtures_sha256':digest(outdir/'fixtures.npz'),'families':{}}
    timing_rng=random.Random(protocol['method_order_seed']);gamma=protocol['max_gain']
    for name,x in data.items():
        models=[Biquad.from_coefficients(row) for row in x]
        truth=np.asarray([reference_decision(f,gamma) for f in models],dtype=bool)
        integer=np.asarray([certify(f,gamma).certified for f in models],dtype=bool)
        if np.any(integer!=truth):raise AssertionError('Python exact/reference discrepancy')
        out=np.zeros(len(x),dtype=np.int32)
        methods={
            'integer':lambda:lib.exact_batch(x,len(x),gamma,out),
            'grid1024':lambda:lib.grid_batch(x,len(x),gamma,1024,out),
            'grid16384':lambda:lib.grid_batch(x,len(x),gamma,16384,out),
            'float64_algebraic':lambda:lib.float64_batch(x,len(x),gamma,out)}
        correctness={}
        for method,call in methods.items():
            call();correctness[method]=errors(out,truth)
        if any(correctness['integer'].values()):raise AssertionError('native exact/reference discrepancy')
        times={k:[] for k in methods}
        for _ in range(args.trials):
            order=list(methods);timing_rng.shuffle(order)
            for method in order:
                call=methods[method]
                call()  # important: different grid lengths replace the cache
                start=time.perf_counter_ns()
                for _ in range(protocol['batch_repeats']):call()
                elapsed=time.perf_counter_ns()-start
                times[method].append(elapsed/len(x)/protocol['batch_repeats']/1000)
        medians={k:float(np.median(v)) for k,v in times.items()}
        result['families'][name]={
            'n':len(x),'exact_pass':int(truth.sum()),'correctness':correctness,
            'median_us':medians,'raw_us_per_filter':times,
            'paired_grid1024_over_integer':float(np.median(np.array(times['grid1024'])/times['integer']))}
        print(name,result['families'][name],flush=True)
    # Native bit-level port tests, independent from synthesis distribution.
    bits_rng=np.random.default_rng(args.seed+100)
    bitrows=np.ascontiguousarray(bits_rng.integers(0,2**32,size=(2048,5),dtype=np.uint32).view(np.float32))
    native=np.zeros(len(bitrows),dtype=np.int32)
    lib.exact_batch(bitrows,len(bitrows),1.,native)
    mismatches=0
    for row,actual in zip(bitrows,native):
        try:expected=int(reference_decision(Biquad.from_coefficients(row)))
        except ValueError:expected=-1
        mismatches += expected!=int(actual)
    result['native_bit_patterns']={'n':len(bitrows),'mismatches':int(mismatches)}
    if mismatches:raise AssertionError('native IEEE bit test discrepancy')
    # Python end-to-end comparison: same loop and cached SciPy frequency vector.
    models=[Biquad.from_coefficients(row) for row in data['high_q'][:min(args.n,128)]]
    omega=np.linspace(0,np.pi,1024)
    def scipy_check(f):
        a1,a2=f.a[1:]
        if not(abs(a2)<1 and 1+a1+a2>0 and 1-a1+a2>0):return False
        _,h=signal.freqz(f.b,f.a,worN=omega)
        return bool(np.max(np.abs(h))<gamma)
    funcs={'python_integer_api':lambda f:certify(f,gamma).certified,
           'fraction_reference':lambda f:reference_decision(f,gamma),
           'scipy_freqz1024':scipy_check}
    py_times={k:[] for k in funcs}
    for _ in range(args.trials):
        order=list(funcs);timing_rng.shuffle(order)
        for name in order:
            fn=funcs[name];[fn(f) for f in models[:4]]
            start=time.perf_counter_ns();[fn(f) for f in models]
            py_times[name].append((time.perf_counter_ns()-start)/len(models)/1000)
    result['python_high_q']={'n':len(models),'raw_us_per_filter':py_times,
        'median_us':{k:float(np.median(v)) for k,v in py_times.items()},
        'note':'Python API/object overhead INCLUDED; separate from native batch kernel graph.'}
    # Controlled compensation case, not a quality benchmark.
    rows=[Biquad.from_coefficients(r,precision='float32') for r in
          [[1,-.75,0,-.125,0],[.75,-.09375,0,-.75,0]]]
    proof=certify_cascade(rows)
    if not proof['certified'] or not verify_cascade(proof,rows):raise AssertionError('cascade proof failed')
    result['cascade_demo']={'sections':[list(f.coefficients) for f in rows],
        'individual_certified':[certify(f).certified for f in rows],
        'total_transfer_constant':.75, 'joint_certificate':proof,
        'rational_recheck':True}
    save(outdir/'benchmark.json',result)
    print('RESULTS',outdir/'benchmark.json',flush=True)

if __name__=='__main__':main()
