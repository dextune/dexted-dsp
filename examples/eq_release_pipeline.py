#!/usr/bin/env python3
"""Practical parametric-EQ export -> exact gain proof -> proof verification.

Uses the W3C Audio EQ Cookbook's biquad formulae; all design inputs are
illustrative, not a manufacturer's settings. Final coefficients are rounded
to binary32 before inspection. No audio is played or modified.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'benchmarks'/'suites'))
from eq_catalog import design_biquad
from dexted_dsp import inspect_sos, verify_inspection

SAMPLE_RATE=48000
BANDS=(('peaking',180.,1.2,-3.),('peaking',1600.,.85,4.),
       ('peaking',8400.,1.3,-2.))


def make_chain():
    return [design_biquad(kind,SAMPLE_RATE,frequency,q,db)
            for kind,frequency,q,db in BANDS]


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--max-gain',type=float,default=2.0,help='Strict linear-amplitude ceiling')
    p.add_argument('--proof',type=Path,help='Optional output JSON path, must not exist')
    p.add_argument('--report',type=Path,help='Optional output Markdown path, must not exist')
    args=p.parse_args()
    sos=make_chain()
    result=inspect_sos(sos,precision='float32',fs=SAMPLE_RATE,
                       max_gain=args.max_gain,peak_bits=4,max_nodes=5000,max_depth=32)
    envelope=result.as_dict()
    verified=result.certified and verify_inspection(envelope,sos,precision='float32',
                            fs=SAMPLE_RATE,max_gain=args.max_gain)
    if result.certified and not verified:
        raise AssertionError('A producer PASS must have a verified proof')
    if len([x for x in (args.proof,args.report) if x is not None])==2 and args.proof.resolve()==args.report.resolve():
        p.error('--proof and --report must differ')
    for target in (args.proof,args.report):
        if target and target.exists():p.error(f'will not overwrite output: {target}')
    if args.proof:
        args.proof.parent.mkdir(parents=True,exist_ok=True)
        result.save(args.proof)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(result.markdown(),encoding='utf-8')
    print(json.dumps({'kind':'W3C-cookbook application-shaped synthetic 3-band EQ',
          'sample_rate_hz':SAMPLE_RATE,'export_precision':'float32',
          'section_count':len(sos),'max_gain_strict':args.max_gain,
          'status':result.status,'reason':result.reason,
          'verified_certificate':bool(verified),
          'peak_gain_interval':result.gain_bounds.as_dict() if result.gain_bounds else None},indent=2))
    return 0 if result.certified and verified else (3 if result.status=='unknown' else 1)


if __name__=='__main__':
    raise SystemExit(main())
