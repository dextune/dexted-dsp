#!/usr/bin/env python3
"""Check pilot raw data/timing calculations against pinned fixture/source hashes."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import statistics

from run_pilot_v2 import ROOT, FIXTURE, digest, percentile


def audit(result_file:Path, *, require_current:bool=True)->dict:
    result=json.loads(result_file.read_text())
    if result['schema']!='dexted-dsp/pilot-v2/v1':
        raise ValueError('wrong result schema')
    if result['fixture_sha256']!=digest(FIXTURE):
        raise ValueError('fixture sha mismatch')
    changed=[path for path,expected in result['source_sha256'].items()
             if not (ROOT/path).is_file() or digest(ROOT/path)!=expected]
    if require_current and changed:
        raise ValueError('source drift since experiment: '+', '.join(changed))
    trials=result['protocol']['trials']
    fixture=json.loads(FIXTURE.read_text())
    expected_cases={item['id']:item for item in fixture['cases']}
    ids=set()
    for case in result['cases']:
        if case['id'] in ids:
            raise ValueError('duplicate case')
        ids.add(case['id'])
        if case['id'] not in expected_cases:
            raise ValueError('unknown measurement case')
        expected=expected_cases[case['id']]
        if case['family']!=expected['family'] or case['split']!=expected['split'] or case['sections']!=len(expected['sos']):
            raise ValueError('case metadata does not match pinned input')
        if case['inspection_status']=='certified' and case['exact_status']!='certified':
            raise ValueError('inspection false certification')
        if case['exact_status']=='certified' and case['exact_certificate_verified'] is not True:
            raise ValueError('unverified exact PASS')
        for method,values in case['raw_ms'].items():
            if len(values)!=trials or any(not math.isfinite(v) or v<=0 for v in values):
                raise ValueError('invalid raw times')
            if not math.isclose(statistics.median(values),case['median_ms'][method],rel_tol=1e-12):
                raise ValueError('incorrect median')
            if not math.isclose(percentile(values,95),case['p95_ms'][method],rel_tol=1e-12):
                raise ValueError('incorrect p95')
    counts={
        'cases':len(ids),
        'assessed_exact':sum(x['exact_status']!='unknown' for x in result['cases']),
        'unknown':sum(x['exact_status']=='unknown' for x in result['cases']),
        'false_accepts_grid':sum(x['sampling_pass'] and x['exact_status'] not in ('certified','unknown') for x in result['cases']),
        'false_rejects_grid':sum(not x['sampling_pass'] and x['exact_status']=='certified' for x in result['cases']),
    }
    if result['totals']!=counts:
        raise ValueError('totals mismatch')
    return {'status':'passed','cases':len(ids),'trials_per_method':trials,
            'current_source_matches':not changed,'source_drift':changed,
            'limitations':'saved-data arithmetic audit, not independent correctness or timing replication'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('result',type=Path)
    p.add_argument('--allow-source-drift',action='store_true')
    args=p.parse_args()
    print(json.dumps(audit(args.result,require_current=not args.allow_source_drift),indent=2))

if __name__=='__main__':
    main()
