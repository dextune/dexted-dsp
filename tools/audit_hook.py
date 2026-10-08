#!/usr/bin/env python3
"""Validate README's archived counts and the executable hidden-peak hook.

Never recompute historical timing data or reinterpret a grid as a certificate.
"""
from __future__ import annotations
import csv
import json
from pathlib import Path

from dexted_dsp.demo import hidden_peak_demo

ROOT = Path(__file__).resolve().parents[1]


def audit() -> dict:
    with (ROOT/'benchmarks/results/summary.csv').open(newline='',encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    high_q={r['method']:r for r in rows if r['family']=='high_q'}
    assert {k:int(high_q[k]['false_accepts']) for k in ('integer','grid1024','grid16384')} == {
        'integer':0,'grid1024':356,'grid16384':213}
    assert int(high_q['integer']['n'])==1024
    assert 1024-int(high_q['integer']['exact_pass'])==485
    demo=hidden_peak_demo(grid_size=1024)
    assert demo['contradiction'] is True
    assert abs(demo['grid']['estimated_max_gain']-.0397432122)<1e-8
    assert demo['exact']['status']=='gain_limit_not_met'
    assert demo['analytical']['peak_gain']==2
    readme=(ROOT/'README.md').read_text(encoding='utf-8')
    for token in ('356 / 485','213 / 485','0 / 485','0.03974','2.0',
                  'demo hidden-peak','synthetic'):
        assert token in readme,f'Landing page missing factual caveat/evidence: {token}'
    return {'status':'passed','archived_high_q_failures':485,'archived_false_accepts':{'grid1024':356,'grid16384':213,'exact':0},
            'demo_sampled_peak':demo['grid']['estimated_max_gain'],'analytical_global_peak':2,
            'caveat':'historical synthetic fixtures, not production prevalence'}


if __name__=='__main__':
    print(json.dumps(audit(),indent=2))
