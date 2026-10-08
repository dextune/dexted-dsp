"""Exact symbolic/real-root checks; optional dependency only in audit CI job."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'benchmarks'/'suites'))
HAS_SYMPY=importlib.util.find_spec('sympy') is not None


@unittest.skipUnless(HAS_SYMPY,'SymPy is optional; full audit runs in exact-oracle CI')
class ExactSympyOracleTests(unittest.TestCase):
    def setUp(self):
        from sympy_oracle_audit import oracle_verdict
        self.verdict=oracle_verdict

    def test_exact_unity_and_tight_threshold(self):
        unity=[[1.,0.,0.,1.,0.,0.]]
        self.assertEqual(self.verdict(unity,1.),'gain_limit_not_met')
        self.assertEqual(self.verdict(unity,1.000000001),'certified')

    def test_hidden_peak_and_exact_equality(self):
        a=2.**-14
        peaked=[[a,0.,-a,1.,0.,1.-a]]
        self.assertEqual(self.verdict(peaked,1.),'gain_limit_not_met')
        self.assertEqual(self.verdict(peaked,2.),'gain_limit_not_met')
        self.assertEqual(self.verdict(peaked,2.0001),'certified')

    def test_pole_instability_precedes_gain(self):
        self.assertEqual(self.verdict([[0.,0.,0.,1.,0.,1.]],1.),'denominator_not_schur')

    def test_compensating_sections_are_judged_jointly(self):
        first=[1.,-.75,0.,1.,-.125,0.]
        second=[.75,-.09375,0.,1.,-.75,0.]
        self.assertEqual(self.verdict([first],1.),'gain_limit_not_met')
        self.assertEqual(self.verdict([second],1.),'gain_limit_not_met')
        self.assertEqual(self.verdict([first,second],1.),'certified')

    def test_frozen_holdout_reference(self):
        from sympy_oracle_audit import audit
        report=audit(count=64,split='holdout',seed=20261008,
            compare_library=False,reference_path=ROOT/'validation/oracle/reference_holdout_64.json')
        self.assertTrue(report['reference_verified'])
        self.assertEqual(report['cases'],64)
        self.assertEqual(report['exact_oracle_passes']+report['exact_oracle_failures'],64)


if __name__=='__main__':unittest.main()
