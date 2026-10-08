"""Mutation tests for planning contracts; never impersonate core qualification."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from audit_core_spec import audit, DEFAULT


class CoreSpecTests(unittest.TestCase):
    def mutate(self, file, change):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)/'plan'
            shutil.copytree(DEFAULT.parent, root, ignore=shutil.ignore_patterns('__pycache__'))
            path = root/'core'/file
            data = json.loads(path.read_text(encoding='utf-8'))
            change(data)
            path.write_text(json.dumps(data,allow_nan=False),encoding='utf-8')
            with self.assertRaises(ValueError):
                audit(root/'core')

    def test_complete_contracts(self):
        result = audit()
        self.assertEqual(result['requirements'],18)
        self.assertEqual(result['specified_core_tests'],42)
        self.assertEqual(result['actual_core_tests_executed'],0)
        self.assertFalse(result['industrial_qualified'])

    def test_missing_requirement(self):
        self.mutate('contracts/requirements.json', lambda x:x['requirements'].pop())

    def test_unknown_test(self):
        self.mutate('contracts/requirements.json', lambda x:x['requirements'][0]['tests'].append('CT-99'))

    def test_cycle(self):
        self.mutate('contracts/requirements.json', lambda x:x['work_packages'][0]['depends_on'].append('CW-21'))

    def test_invented_parent(self):
        self.mutate('contracts/requirements.json', lambda x:x['work_packages'][0]['parent_work_packages'].append('Z99'))

    def test_false_approval(self):
        self.mutate('contracts/requirements.json', lambda x:x['requirements'][0].update(status='APPROVED'))

    def test_optional_scope_promotion(self):
        self.mutate('contracts/requirements.json', lambda x:x['requirements'][-1].update(release_blocker=True))

    def test_resource_target_drift(self):
        self.mutate('contracts/budgets.json', lambda x:x['standard'].update(job_seconds=50))

    def test_latency_target_drift(self):
        self.mutate('contracts/budgets.json', lambda x:x['prepared_verified_decision_targets'][3].update(p95_ms=999))

    def test_missing_long_record(self):
        self.mutate('contracts/longrun-matrix.json', lambda x:x['record_ids'].pop())

    def test_fabricated_core_run(self):
        self.mutate('contracts/longrun-matrix.json', lambda x:x.update(actual_core_executed=True))

    def test_duration_multiplication_error(self):
        self.mutate('contracts/longrun-matrix.json', lambda x:x.update(expected_filter_hours=76))

    def test_missing_independent_runtime(self):
        self.mutate('contracts/longrun-matrix.json', lambda x:x['runtime_lanes'].pop())

    def test_analytic_coefficient_tamper(self):
        self.mutate('contracts/analytic-cases.json', lambda x:x['cases'][0]['sos'][0].__setitem__(0,.5))

    def test_analytic_threshold_tamper(self):
        self.mutate('contracts/analytic-cases.json', lambda x:x['cases'][0].update(gamma=2.))

    def test_false_analytic_execution(self):
        self.mutate('contracts/analytic-cases.json', lambda x:x['cases'][0].update(executed_against_core=True))


if __name__ == '__main__':
    unittest.main()
