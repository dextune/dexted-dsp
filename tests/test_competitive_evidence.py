"""Regression and adversarial mutation tests for published competitor evidence."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
sys.path.insert(0,str(ROOT/"benchmarks/competitive"))
from audit_competitive import audit
from plot import generate, hidden_peak_values

ARCHIVE=ROOT/"benchmarks/competitive/results/run-20261008.json"


class CompetitiveEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(ARCHIVE.read_text(encoding="utf-8"))

    def test_frozen_evidence_integrity(self):
        result=audit(ARCHIVE,archived=True)
        self.assertEqual(result["cases"],9)
        self.assertEqual(result["trials_per_method"],30)
        self.assertEqual(result["memory_repeats_per_method"],30)
        self.assertEqual(result["false_accepts"]["scipy_before"],1)
        self.assertEqual(result["false_accepts"]["control_before"],1)
        self.assertEqual(result["false_accepts"]["scipy_after"],0)
        self.assertEqual(result["false_accepts"]["control_after"],0)

    def test_svg_is_exactly_from_raw_data(self):
        figs=generate(self.data)
        self.assertEqual(set(figs),{"decision.svg","runtime.svg","memory.svg","decision-mobile.svg","runtime-mobile.svg","memory-mobile.svg","peak-gap.svg","peak-gap-mobile.svg"})
        for name,content in figs.items():
            self.assertIn('aria-labelledby="title desc"',content)
            self.assertEqual((ROOT/"benchmarks/competitive/figures"/name).read_text(encoding="utf-8"),content)

    def test_peak_gap_uses_frozen_coefficients_and_exact_algebra(self):
        vals=hidden_peak_values(self.data)
        self.assertAlmostEqual(vals["sampled"],0.0397432122,delta=1e-8)
        self.assertEqual(vals["exact"],2.0)
        self.assertEqual(vals["threshold"],1.0)
        self.assertTrue(vals["sampled"] < 1 < vals["exact"])

    def assert_rejected_mutation(self,mutator):
        change=copy.deepcopy(self.data)
        mutator(change)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"tampered.json"
            path.write_text(json.dumps(change),encoding="utf-8")
            with self.assertRaises(AssertionError):
                audit(path,archived=True)

    def test_reject_removed_raw_trial(self):
        self.assert_rejected_mutation(lambda d:d["cases"][0]["raw_ms"]["scipy_before"].pop())

    def test_reject_edited_summary(self):
        self.assert_rejected_mutation(lambda d:d["summary"]["scipy_after"].__setitem__("false_accepts",99))

    def test_reject_changed_fixture_coefficients(self):
        self.assert_rejected_mutation(lambda d:d["cases"][0]["sos"][0].__setitem__(0,0.0))

    def test_reject_removed_case(self):
        self.assert_rejected_mutation(lambda d:d["cases"].pop())

    def test_reject_falsified_source_digest(self):
        self.assert_rejected_mutation(lambda d:d["inputs"].__setitem__("run_source_sha256","0"*64))


if __name__=="__main__":
    unittest.main()
