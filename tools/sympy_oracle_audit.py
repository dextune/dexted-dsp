#!/usr/bin/env python3
"""Independent algorithmic audit of strict SOS frequency-gain decisions.

Mathematical check: form the exact rational polynomial
  gamma^2 * prod |a_j(e^iw)|^2 - prod |b_j(e^iw)|^2
in c=cos(omega); then use SymPy's *exact polynomial real-root counting*
on [-1,1] plus one exact sign evaluation.  The shipping Dexted DSP SOS
producer instead uses Bernstein positivity subdivision.  Sampling is NOT
used to establish correctness. This is a separate software implementation,
not an independent human proof audit or a formal-methods verification.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import random
import sys
import time

try:
    import sympy as sp
except ImportError as exc:
    raise SystemExit("Requires: python -m pip install 'sympy>=1.13,<2'") from exc

ROOT = Path(__file__).resolve().parents[1]
SUITES = ROOT / 'benchmarks' / 'suites'
CATALOG_DIGEST = '873ce092e2fe7fa7e8d16c8fd50b251f377c05c4a02ed267e6917d7599a69120'
DEFAULT_COUNT = 1200
DEFAULT_SEED = 20261008


def exact_fraction(value: float) -> sp.Rational:
    # The inputs are already rounded to binary32; float preserves that value.
    n,d = float(value).as_integer_ratio()
    return sp.Rational(n,d)


def squared_response(row: list[sp.Rational], c: sp.Symbol) -> sp.Poly:
    # Independent expansion: cos(2w)=2*cos(w)^2-1.
    u,v,w=row
    return sp.Poly(u*u+v*v+w*w + 2*(u*v+v*w)*c +
                   2*u*w*(2*c*c-1), c, domain='QQ')


def oracle_verdict(sos: list[list[float]], gain: float) -> str:
    """Complete, exact decision for stable fixed SOS; no resource-limited UNKNOWN.

    Distinguishes the project's required per-section Schur stability from its
    strict full-cascade gain bound. Does not attempt physical runtime safety.
    """
    if not sos or len(sos)>32:
        raise ValueError('1..32 SOS rows required')
    c=sp.Symbol('c',real=True)
    numer=sp.Poly(1,c,domain='QQ')
    denom=sp.Poly(1,c,domain='QQ')
    for item in sos:
        if len(item)!=6 or item[3]!=1.:
            raise ValueError('normalized SOS rows of length 6 required')
        r=list(map(exact_fraction,item))
        if not (abs(r[5])<1 and 1+r[4]+r[5]>0 and 1-r[4]+r[5]>0):
            return 'denominator_not_schur'
        numer *= squared_response(r[:3],c)
        denom *= squared_response([r[3],r[4],r[5]],c)
    gamma=exact_fraction(gain)
    if gamma<=0:
        raise ValueError('strict positive gain required')
    gap=gamma**2*denom - numer
    if gap.is_zero:
        return 'gain_limit_not_met'
    # count_roots returns count on the CLOSED interval, including exact
    # tangencies and equality at +/-1. Crossing and touching are both FAIL.
    if gap.count_roots(-1,1):
        return 'gain_limit_not_met'
    # No real zeros: continuity means the sign is constant on [-1,1].
    return 'certified' if gap.eval(0)>0 else 'gain_limit_not_met'


def select_cases(cases: list[dict], *, count: int, split: str, seed: int) -> list[dict]:
    if count<1:
        raise ValueError('count must be >=1')
    rng=random.Random(seed)
    available=[x for x in cases if split=='all' or x['split']==split]
    if count>len(available):
        raise ValueError(f'{count} requested but {len(available)} available')
    groups={name:[] for name in ('peaking','notch','lowpass','highpass')}
    for case in available:
        groups[case['family']].append(case)
    for group in groups.values(): rng.shuffle(group)
    chosen=[]
    # Predeclared fair family balancing rather than selecting favorable cases.
    while len(chosen)<count:
        advanced=False
        for name in groups:
            if groups[name] and len(chosen)<count:
                chosen.append(groups[name].pop());advanced=True
        if not advanced:break
    return sorted(chosen,key=lambda case:case['id'])


def audit(*, count: int=40, split: str='holdout', seed: int=20261008,
          compare_library: bool=True, reference_path: Path | None=None) -> dict:
    sys.path.insert(0,str(SUITES))
    from eq_catalog import canonical_bytes, generate
    catalog=generate(count=DEFAULT_COUNT,seed=DEFAULT_SEED)
    digest=hashlib.sha256(canonical_bytes(catalog)).hexdigest()
    if digest!=CATALOG_DIGEST:
        raise ValueError('catalog changed from predeclared SHA256 '+CATALOG_DIGEST)
    if compare_library:
        from dexted_dsp import from_sos,certify_cascade,verify_cascade
    cases=select_cases(catalog['cases'],count=count,split=split,seed=seed)
    started=time.monotonic()
    results=[]
    for case in cases:
        expected=oracle_verdict(case['sos'],case['max_gain'])
        result={'id':case['id'],'family':case['family'],'split':case['split'],
                'sections':case['sections'],'oracle_verdict':expected}
        if compare_library:
            rows=from_sos(case['sos'],precision='float32')
            proof=certify_cascade(rows,case['max_gain'],max_depth=32,max_nodes=3500)
            actual=proof['status']
            verified=bool(verify_cascade(proof,rows,case['max_gain'])) if proof['certified'] else False
            valid=(actual==expected or actual=='unknown' or
                   (actual=='condition_failed' and expected=='gain_limit_not_met'))
            if not valid or (proof['certified'] and not verified):
                raise AssertionError('oracle mismatch '+json.dumps({**result,'actual':actual,
                                    'verified':verified,'sos':case['sos'],'gain':case['max_gain']}))
            result.update(actual=actual,verified_pass=verified)
        results.append(result)
    if reference_path is not None:
        stored=json.loads(reference_path.read_text(encoding='utf-8'))
        current={'schema':'dexted-dsp/holdout-sympy-v1',
                 'catalog_sha256':digest,'count':count,'seed':seed,'split':split,
                 'verdicts':{r['id']:r['oracle_verdict'] for r in results}}
        if stored!=current:
            raise AssertionError('independent reference fixture changed; do not rewrite without review')
    summary={'schema':'dexted-dsp/sympy-oracle-audit/v1','status':'passed','reference_verified':reference_path is not None,
             'oracle_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'catalog_sha256':digest,'cases':len(results),'selection_seed':seed,
             'selection_split':split,'sympy_version':sp.__version__,
             'runtime_seconds':round(time.monotonic()-started,6),
             'library_compared':compare_library,
             'exact_oracle_passes':sum(x['oracle_verdict']=='certified' for x in results),
             'exact_oracle_failures':sum(x['oracle_verdict']!='certified' for x in results),
             'production_unknown':sum(x.get('actual')=='unknown' for x in results),
             'verifiable_producer_passes':sum(bool(x.get('verified_pass')) for x in results),
             'method':'SymPy exact rational polynomial root counting over closed [-1,1]',
             'scope':'application-shaped SYNTHETIC filters; no external mathematics audit or runtime-roundoff proof',
             'results':results}
    return summary


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--count',type=int,default=40)
    p.add_argument('--split',choices=('holdout','development','all'),default='holdout')
    p.add_argument('--seed',type=int,default=20261008)
    p.add_argument('--oracle-only',action='store_true',help='check mathematics without importing Dexted DSP')
    p.add_argument('--check-reference',type=Path,help='Compare each result against pinned exact reference JSON')
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    report=audit(count=args.count,split=args.split,seed=args.seed,
                 compare_library=not args.oracle_only,reference_path=args.check_reference)
    if args.output:
        if args.output.exists():raise SystemExit('refusing to overwrite saved audit')
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    # Print compact summary; per-case results live in --output when requested.
    print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))


if __name__=='__main__':main()
