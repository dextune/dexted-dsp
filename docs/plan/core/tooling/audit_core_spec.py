#!/usr/bin/env python3
"""Audit engineering SPECIFICATIONS, never execute/qualify the DSP core.

Standard-library-only. Missing source links in a ZIP are disclosed; internal
plan links and all requirement/work/test/budget invariants remain mandatory.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import re
import struct
from urllib.parse import unquote

DEFAULT = Path(__file__).resolve().parents[1]
BASELINE = '9f6df34d45f418995dedf18e3b328524dd18ec6b'


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def index(items, prefix: str, count: int):
    require(isinstance(items, list), prefix + ' list missing')
    require(all(isinstance(x, dict) for x in items), prefix + ' row type')
    keys = [x.get('id') for x in items]
    require(len(keys) == count and set(keys) == {f'{prefix}-{i:02}' for i in range(1, count+1)}, prefix + ' ID coverage')
    return dict(zip(keys, items))


def audit(base: Path = DEFAULT) -> dict:
    base = base.resolve()
    parent = base.parent
    data = load(base/'contracts/requirements.json')
    require(data['schema'] == 'dexted-dsp/core-spec-trace/v1', 'trace schema')
    require(data['baseline_commit'] == BASELINE, 'baseline changed without review')
    require(data['core_implementation_changed'] is False and data['industrial_qualified'] is False, 'false completion claim')
    req = index(data['requirements'], 'CR', 18)
    tests = index(data['tests'], 'CT', 42)
    work = index(data['work_packages'], 'CW', 24)
    inv = index(data['invariants'], 'INV', 12)
    master = {x['id'] for x in load(parent/'manifests/work-packages-v1.json')['items']}
    matrix_text = (base/'08_TEST_MATRIX_AND_ORACLES.md').read_text(encoding='utf-8')
    wbs_text = (base/'09_WORK_PACKAGES_AND_GATES.md').read_text(encoding='utf-8')
    docs = list(base.glob('*.md'))
    require(len(docs) == 12 and (base/'README.md').is_file(), '12 core documents required')
    for table in (req, tests, work, inv):
        for row in table.values():
            require((base/row['document']).is_file(), 'missing referenced document')
    for key, r in req.items():
        number = int(key[-2:])
        require(r['status'] == 'PLANNED' and r['evidence'] == [] and r['approved_by'] is None, 'unexecuted requirement falsely completed')
        require(r['release_blocker'] is (number <= 15), 'required/future scope changed')
        require(r['tests'] and set(r['tests']) <= tests.keys(), 'orphan requirement test')
        require(r['invariants'] and set(r['invariants']) <= inv.keys(), 'orphan invariant')
        expected_work = {k for k, w in work.items() if key in w['requirements']}
        require(expected_work and set(r['work_packages']) == expected_work, 'work backlinks mismatch')
        require(bool(r['code_targets']), 'function-level targets missing')
        for t in r['code_targets']:
            require(t['state'] in ('EXISTING', 'PROPOSED') and bool(t['symbol']), 'target maturity not specified')
            require(not Path(t['path']).is_absolute() and '..' not in Path(t['path']).parts, 'unsafe code path')
    for key, t in tests.items():
        require(t['status'] == 'SPECIFIED_NOT_EXECUTED' and t['evidence'] == [], 'test execution fabricated')
        require(set(t['requirements']) == {k for k, r in req.items() if key in r['tests']} and bool(t['requirements']), 'test reverse trace mismatch')
        require(f'| {key} |' in matrix_text, 'missing detailed test definition')
    for key, w in work.items():
        require(w['status'] == 'PLANNED' and w['approved_by'] is None and w['evidence'] == [], 'work completion fabricated')
        require(w['parent_work_packages'] and set(w['parent_work_packages']) <= master, 'unknown master WBS')
        require(set(w['depends_on']) <= work.keys() and key not in w['depends_on'], 'bad dependency')
        require(w['requirements'] and set(w['requirements']) <= req.keys(), 'unknown work requirement')
        require(w['effort_accounting'] == 'decomposition_not_additive', 'double-counted effort')
        require(f'| {key} ' in wbs_text, 'missing work definition')
    pending = set(work)
    while pending:
        ready = {k for k in pending if not (set(work[k]['depends_on']) & pending)}
        require(bool(ready), 'cyclic work graph')
        pending -= ready
    budgets = load(base/'contracts/budgets.json')
    require(budgets['status'] == 'PROPOSED_NOT_MEASURED' and budgets['evidence'] == [] and budgets['approved_by'] is None, 'budget not a measured result')
    goals = {g['id']: g['targets'] for g in load(parent/'manifests/qualification-gates-v1.json')['goals']}
    standard = budgets['standard']
    require(standard['job_seconds'] == goals['IND-06']['default_job_seconds_max'], 'parent time target drift')
    require(standard['worker_rss_mib'] == goals['IND-06']['core_worker_rss_mib_max'], 'parent memory target drift')
    require(standard['proof_bytes'] == goals['IND-06']['proof_bytes_max'], 'parent proof cap drift')
    targets = budgets['prepared_verified_decision_targets']
    require([t['sections'] for t in targets] == [1,2,4,8,16], 'section coverage')
    for t in targets:
        require(t['precisions'] == ['float32','float64'], 'precision coverage')
        require(0 < t['p95_ms'] <= t['p99_ms'] < standard['job_seconds']*1000, 'latency budget inconsistency')
        require(t['unknown_fraction_max'] == goals['IND-04']['unknown_fraction_max'], 'coverage target drift')
    require(targets[0]['p95_ms'] == goals['IND-05']['biquad_p95_ms_max'], 'biquad target drift')
    require(targets[3]['p95_ms'] == goals['IND-05']['sos8_p95_ms_max'] and targets[3]['p99_ms'] == goals['IND-05']['sos8_p99_ms_max'], 'SOS8 target drift')
    require(budgets['extended']['explicit_opt_in'] is True and budgets['timeout_observation'] == 'right_censored_not_success', 'unfair measurement policy')
    long = load(base/'contracts/longrun-matrix.json')
    records = load((base/'contracts'/long['record_manifest']).resolve())['records']
    require(long['record_ids'] == [r['id'] for r in records] and len(records) == 24, 'long record membership drift')
    hours = sum(r['duration_seconds'] for r in records)/3600
    require(hours == long['input_record_hours'] == 76, 'long source hours drift')
    filters = long['valid_filters']
    require(len(filters) == 8 and {f['id'] for f in filters} == {f'F{i:02}' for i in range(1,9)}, 'filter slots missing')
    require(all(f['coefficient_status'] == 'TO_BE_GENERATED_AND_FROZEN' and f['sos_bits'] is None and f['oracle_status'] == 'NOT_RUN' for f in filters), 'invented filter evidence')
    require(len(long['controls']) == 4 and len({c['id'] for c in long['controls']}) == 4, 'negative controls missing')
    require(len(long['runtime_lanes']) == len(set(long['runtime_lanes'])) == 4, 'runtime lanes missing')
    require(long['expected_record_filter_runs'] == len(records)*len(filters) == 192, 'record-filter accounting')
    require(long['expected_filter_hours'] == hours*len(filters) == 608, 'filter hours accounting')
    require(long['expected_processing_lane_hours'] == long['expected_filter_hours']*4 == 2432, 'lane hours accounting')
    require(long['core_execution_required'] is True and all(long[k] is False for k in ('actual_core_executed','full_qualification_executed','wall_clock_soak_executed')), 'longrun execution fabricated')
    analytic = load(base/'contracts/analytic-cases.json')
    require(analytic['status'] == 'SPECIFICATION_NOT_CORE_RUN', 'analytic fixture scope')
    cases = analytic['cases']
    require(len(cases) == 10 and len({c['id'] for c in cases}) == 10, 'analytic cases missing')
    for c in cases:
        require(c['executed_against_core'] is False, 'unrun analytic example marked tested')
        require(c['precision'] == 'float32' and 0 < c['gamma'] < math.inf, 'analytic precision/gain')
        require(struct.pack('>d', c['gamma']).hex() == c['gamma_bits'], 'gamma bit drift')
        require(len(c['sos']) == len(c['rows_bits']) >= 1, 'rows mismatch')
        for values, bits in zip(c['sos'], c['rows_bits']):
            require(len(values) == len(bits) == 6 and values[3] == 1, 'SOS layout')
            require(all(type(x) in (float,int) and math.isfinite(x) for x in values), 'nonfinite analytic fixture')
            require([struct.pack('>f', x).hex() for x in values] == bits, 'coefficient bits drift')
            require(all(struct.unpack('>f',bytes.fromhex(b))[0] == x for x,b in zip(values,bits)), 'not represented f32')
    links = 0
    outside_missing = set()
    for path in docs:
        text = re.sub(r'^```[^\n]*\n.*?^```[^\n]*$', '', path.read_text(encoding='utf-8'), flags=re.M|re.S)
        for raw in re.findall(r'\]\(([^)]+)\)', text):
            target = unquote(raw.split('#',1)[0])
            if not target or '://' in target:
                continue
            resolved = (path.parent/target).resolve()
            if resolved.is_relative_to(parent):
                require(resolved.exists(), f'broken internal plan link: {path.name}/{target}')
                links += 1
            elif resolved.exists():
                links += 1
            else:
                outside_missing.add(target)
    return {'status':'passed','scope':'documentation_and_contracts_only','baseline_commit':BASELINE,
            'core_documents':len(docs),'requirements':len(req),'invariants':len(inv),'specified_core_tests':len(tests),
            'work_packages':len(work),'required_work_packages':21,'future_work_packages':3,
            'analytic_specification_cases':len(cases),'planned_record_filter_runs':192,'planned_filter_hours':608,
            'local_links_checked':links,'repository_links_unavailable_in_zip':sorted(outside_missing),
            'actual_core_tests_executed':0,'industrial_qualified':False}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base', type=Path, default=DEFAULT)
    args = p.parse_args()
    try:
        result = audit(args.base)
    except (ValueError, KeyError, TypeError, OSError, struct.error) as exc:
        print(json.dumps({'status':'failed','error':str(exc)},ensure_ascii=False))
        return 1
    print(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
