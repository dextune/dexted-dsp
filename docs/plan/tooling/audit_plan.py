#!/usr/bin/env python3
"""Audit plan consistency and bootstrap evidence; does not qualify Dexted DSP."""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

import longrun

BASE = Path(__file__).resolve().parents[1]


def read_json(path: str):
    return json.loads((BASE/path).read_text(encoding='utf-8'))


def audit() -> dict:
    expected = ['README.md','01_GOALS_AND_SCOPE.md','02_MATHEMATICS_AND_CORE.md',
                '03_ARCHITECTURE_AND_API.md','04_DATASET_AND_LONGRUN.md',
                '05_TEST_PROTOCOL_AND_ORACLES.md','06_BENCHMARK_AND_OBSERVABILITY.md',
                '07_SECURITY_RELEASE_OPERATIONS.md','08_ROADMAP_WORKPACKAGES.md',
                '09_ACCEPTANCE_AND_ADVERSARIAL_REVIEW.md','10_EXECUTION_RUNBOOK.md',
                '11_SOURCES_AND_BASELINE.md']
    assert all((BASE/p).is_file() for p in expected), 'missing principal document'
    data = longrun.load_manifest(BASE/'manifests/long-signals-v1.json')
    inv = longrun.inventory(data)
    assert inv['records'] == 24 and inv['record_hours'] == 76 and inv['channel_hours'] == 248
    assert inv['uncompressed_float32_bytes'] == 93081600000
    corpus = read_json('manifests/coefficient-corpus-v1.json')
    assert sum(r['target_count'] for r in corpus['strata']) == corpus['synthetic_total'] == 100000
    assert sum(r['target_count'] for r in corpus['strata'] if r['oracle_required']) == 90000
    assert corpus['real_export_target'] == 3000 and corpus['real_holdout_minimum'] == 1000
    assert corpus['real_data_acquired'] is False
    goals = read_json('manifests/qualification-gates-v1.json')['goals']
    assert {g['id'] for g in goals} == {f'IND-{i:02d}' for i in range(1,13)}
    assert all(g['status'] == 'PLANNED' and not g['evidence'] and g['approved_by'] is None for g in goals)
    wbs = read_json('manifests/work-packages-v1.json')
    items = wbs['items']
    by_id = {r['id']:r for r in items}
    assert len(by_id) == len(items) == 45
    assert sum(r['estimated_person_days'] for r in items) == wbs['estimated_person_days'] == 252
    assert wbs['estimated_person_days'] <= wbs['effective_person_days'] == 294
    assert all(set(r['depends_on']) <= set(by_id) for r in items)
    pending = set(by_id)
    while pending:
        ready = {i for i in pending if not (set(by_id[i]['depends_on']) & pending)}
        assert ready, 'cyclic work package dependencies'
        pending -= ready
    sources = read_json('manifests/external-sources-v1.json')['records']
    assert all(s['acquisition_status'] == 'NOT_ACQUIRED' and s['original_sha256'] is None
               and s['redistribution_approved'] is False for s in sources)
    checked, external_repo_unavailable = 0, set()
    for path in BASE.rglob('*.md'):
        text = path.read_text(encoding='utf-8')
        text = re.sub(r'^```[^\n]*\n.*?^```[^\n]*$', '', text, flags=re.M|re.S)
        for target in re.findall(r'\]\(([^)]+)\)', text):
            target = target.split()[0].strip('<>')
            if '://' in target or target.startswith(('#','mailto:')):
                continue
            target = unquote(target.split('#',1)[0])
            if not target:
                continue
            resolved = (path.parent/target).resolve()
            if resolved.is_relative_to(BASE):
                assert resolved.exists(), f'broken plan link {path.name}: {target}'
                checked += 1
            elif resolved.exists():
                checked += 1
            else:
                # In ZIP-only context the original repository is not present.
                # Do not pretend to have validated those source links.
                external_repo_unavailable.add(target)
    python_count = 0
    for path in (BASE/'tooling').glob('*.py'):
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
        python_count += 1
    e = read_json('evidence/bootstrap-pilot.json')
    assert e['status'] == 'passed' and e['profile'] == 'pilot'
    assert e['manifest_sha256'] == longrun.digest(BASE/'manifests/long-signals-v1.json')
    assert e['runner_sha256'] == longrun.digest(BASE/'tooling/longrun.py')
    assert e['record_count'] == len(e['records']) == 6 and e['record_hours'] == 3
    assert e['scalar_samples'] == 1036800000
    assert e['dexted_core_executed'] is False and e['wall_clock_soak_completed'] is False
    assert e['real_industrial_data_used'] is False
    assert {r['id'] for r in e['records']} == {r['id'] for r in longrun.choose(data,'pilot')}
    for r in e['records']:
        assert r['duration_seconds'] == 1800 and r['status'] == 'passed'
        assert r['frames'] == r['sample_rate_hz']*r['duration_seconds']
        assert r['scalar_samples'] == r['frames']*r['channels']
        assert r['input_bytes_processed'] == r['scalar_samples']*4
        assert r['partition_max_abs_error'] == 0 and r['float32_vs_float64_max_abs_error'] <= 3e-6
        assert r['certificate_status'] == 'NOT_RUN' and r['certificate_verified'] is None
        assert len(r['input_sha256']) == 64 and len(r['output_sha256']) == 64
    assert len({r['input_sha256'] for r in e['records']}) == 6
    return {'status':'passed','scope':'planning consistency + synthetic bootstrap evidence only',
            'principal_documents':len(expected),'markdown_documents':len(list(BASE.rglob('*.md'))),
            'goal_count':len(goals),'work_packages':len(items),'estimated_person_days':252,
            'synthetic_inventory':inv,'bootstrap_records_executed':6,'bootstrap_record_hours':3,
            'python_files_parsed':python_count,'local_links_checked':checked,
            'repository_links_unavailable_in_zip':sorted(external_repo_unavailable),
            'not_claimed':['industrial qualification','actual Dexted core longrun','external review','wall-clock soak']}


if __name__ == '__main__':
    try:
        print(json.dumps(audit(),indent=2,ensure_ascii=False,allow_nan=False))
    except (OSError, ValueError, KeyError, AssertionError) as exc:
        print(json.dumps({'status':'failed','error':str(exc)}),file=sys.stderr)
        raise SystemExit(1)
