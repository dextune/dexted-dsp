#!/usr/bin/env python3
"""Audit saved benchmark data, code hashes and optional exact fixture decisions.

No timing benchmark is run. No network connection is made. Missing archived fixtures
may be reconstructed locally after verifying their original SHA-256.
Run from an installed source tree: python tools/audit_benchmark.py --recheck-fixtures
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import runpy
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def audit(results: Path, recheck: bool = False, strict_current: bool = False) -> dict:
    data = json.loads(results.read_text(encoding='utf-8'))
    protocol = data['protocol']
    mapping_path = ROOT/'benchmarks/results/rebrand-map.json'
    mapping = json.loads(mapping_path.read_text()) if mapping_path.is_file() else None
    archived = {i['original_path']:i for i in mapping['files']} if mapping else {}
    mismatched = []
    for p,h in protocol['source_hashes'].items():
        item = archived.get(p)
        source = ROOT/item['archived_path'] if item and h == item['original_sha256'] else ROOT/p
        if not source.is_file() or sha(source) != h:
            mismatched.append(p)
    # The historic benchmark's archived sources must remain byte-identical.
    # A changed checkout is expected after new features, but its timings must
    # NEVER be represented as the archived v0.1.0 measurements.
    current_drift = []
    if mapping:
        for item in mapping['files']:
            old = ROOT/item['archived_path']
            current = ROOT/item['current_path']
            if not old.is_file() or sha(old) != item['original_sha256']:
                mismatched.append(item['archived_path'])
                continue
            transformed = old.read_text(encoding='utf-8')
            for before,after in mapping['replacements']:
                transformed = transformed.replace(before,after)
            if (not current.is_file() or sha(current) != item['current_sha256']
                    or transformed != current.read_text(encoding='utf-8')):
                current_drift.append(item['current_path'])
    if mismatched:
        raise ValueError('ARCHIVED source hash mismatch: ' + ', '.join(mismatched))
    if strict_current and current_drift:
        raise ValueError('Current checkout differs from archived snapshot: ' + ', '.join(current_drift))
    fixture_path = results.parent/'fixtures.npz'
    if not fixture_path.is_file() and results == (ROOT/'benchmarks/results/benchmark.json').resolve():
        runpy.run_path(str(ROOT/'tools/restore_fixtures.py'))['restore']()
    if sha(fixture_path) != data['fixtures_sha256']:
        raise ValueError('Fixture file SHA-256 mismatch')
    trial_count = protocol['trials']
    count = 0
    for name, family in data['families'].items():
        count += family['n']
        if not 0 <= family['exact_pass'] <= family['n']:
            raise ValueError(f'{name}: invalid reference counts')
        for method, timings in family['raw_us_per_filter'].items():
            if len(timings) != trial_count or any(not math.isfinite(x) or x<=0 for x in timings):
                raise ValueError(f'{name}/{method}: invalid timings')
            if not math.isclose(statistics.median(timings),family['median_us'][method],rel_tol=1e-12):
                raise ValueError(f'{name}/{method}: incorrect stored median')
            c = family['correctness'][method]
            if not 0<=c['false_accepts']<=family['n']-family['exact_pass']:
                raise ValueError(f'{name}/{method}: impossible false-accept count')
            if not 0<=c['false_rejects']<=family['exact_pass']:
                raise ValueError(f'{name}/{method}: impossible false-reject count')
        paired = statistics.median(g/e for g,e in zip(
            family['raw_us_per_filter']['grid1024'], family['raw_us_per_filter']['integer']))
        if not math.isclose(paired,family['paired_grid1024_over_integer'],rel_tol=1e-12):
            raise ValueError(f'{name}: paired speed ratio mismatch')
    for method, timings in data['python_high_q']['raw_us_per_filter'].items():
        if len(timings)!=trial_count or not math.isclose(
                statistics.median(timings),data['python_high_q']['median_us'][method],rel_tol=1e-12):
            raise ValueError(f'{method}: Python timing mismatch')
    result = {'status':'passed','benchmark_sha256':sha(results),
              'source_files_checked':len(protocol['source_hashes']),
              'fixture_rows':count,'timing_trials':trial_count,
              'fixture_sha256_verified':True,'exact_recheck_rows':0,
              'current_source_changed_since_v0_1':current_drift,
              'note':'Historical archive verified; changed checkout code is NOT benchmarked by these archived timings.'}
    if recheck:
        try:
            import numpy as np
            from dexted_dsp import Biquad, certify
            from dexted_dsp.reference import reference_decision
        except ImportError as exc:
            raise ValueError('Install this project and NumPy before --recheck-fixtures') from exc
        with np.load(fixture_path,allow_pickle=False) as archive:
            for name,family in data['families'].items():
                rows=archive[name]
                if rows.shape!=(family['n'],5) or rows.dtype != np.dtype('float32'):
                    raise ValueError(f'{name}: unexpected fixture shape/dtype')
                passes=0
                for row in rows:
                    f=Biquad.from_coefficients(row)
                    reference=reference_decision(f,protocol['max_gain'])
                    if certify(f,protocol['max_gain']).certified != reference:
                        raise ValueError(f'{name}: integer/Fraction disagreement')
                    passes+=int(reference)
                if passes != family['exact_pass']:
                    raise ValueError(f'{name}: reference pass count changed')
                result['exact_recheck_rows']+=len(rows)
        result['note']+=' Recheck uses two project implementations, not independent mathematics.'
    return result

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--results',type=Path,default=ROOT/'benchmarks/results/benchmark.json')
    p.add_argument('--recheck-fixtures',action='store_true')
    p.add_argument('--require-current-snapshot',action='store_true',help='fail if current source differs from archived benchmark revision')
    args=p.parse_args()
    try:
        print(json.dumps(audit(args.results.resolve(),args.recheck_fixtures,args.require_current_snapshot),indent=2))
        return 0
    except (ValueError,KeyError,OSError,TypeError) as exc:
        print(json.dumps({'status':'failed','error':str(exc)}),file=sys.stderr)
        return 1

if __name__=='__main__':
    raise SystemExit(main())
