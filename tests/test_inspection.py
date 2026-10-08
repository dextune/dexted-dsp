"""Acceptance and adversarial tests for the public inspection experience."""
import copy
from fractions import Fraction
import io
import json
import math
import random
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

from dexted_dsp import (Biquad, bound_peak_gain, bound_sos_peak_gain,
                        inspect_biquad, inspect_cascade, inspect_sos, verify_inspection)
from dexted_dsp.cli import main
from dexted_dsp.demo import hidden_peak_demo
from dexted_dsp.peak import _biquad_gap_sign
from dexted_dsp.reference import reference_decision


class PeakBoundsTests(unittest.TestCase):
    def test_known_constant(self):
        for gain in (0, .25, .5, 1, 2):
            with self.subTest(gain=gain):
                f = Biquad.from_coefficients([gain,0,0,0,0])
                b = bound_peak_gain(f)
                self.assertIsNotNone(b)
                lo,hi=Fraction(b.lower_ratio),Fraction(b.upper_ratio)
                self.assertLessEqual(lo,Fraction(gain))
                self.assertGreaterEqual(hi,Fraction(gain))
                self.assertTrue(lo <= gain <= hi)
                self.assertTrue(b.lower_bound <= gain <= b.upper_bound)

    def test_unstable_has_no_bound(self):
        self.assertIsNone(bound_peak_gain(Biquad.from_coefficients([.5,0,0,0,1])))

    def test_strict_equality_remains_failure(self):
        f=Biquad.from_coefficients([1,0,0,0,0])
        self.assertFalse(_biquad_gap_sign(f,Fraction(1)))
        self.assertTrue(_biquad_gap_sign(f,Fraction(1,1)+Fraction(1,2**30)))

    def test_random_exact_gain_interval(self):
        rng=random.Random(902817)
        for _ in range(240):
            r=rng.uniform(.05,.99)
            theta=rng.uniform(.02,math.pi-.02)
            row=[rng.uniform(-.9,.9) for j in range(3)]+[-2*r*math.cos(theta),r*r]
            f=Biquad.from_coefficients(row,precision='float32')
            b=bound_peak_gain(f,precision_bits=16)
            self.assertIsNotNone(b)
            lo,hi=Fraction(b.lower_ratio),Fraction(b.upper_ratio)
            self.assertLess(lo,hi)
            self.assertFalse(_biquad_gap_sign(f,lo))
            self.assertTrue(_biquad_gap_sign(f,hi))
            # Cross-check if representable thresholds permit it.
            self.assertEqual(reference_decision(f,float(hi)),True)
            self.assertLessEqual(b.lower_bound,b.upper_bound)

    def test_invalid_precision_bits(self):
        f=Biquad.from_coefficients([.5,0,0,0,0])
        for value in (True,-1,65,'8',None):
            with self.subTest(value=value),self.assertRaises(ValueError):
                bound_peak_gain(f,precision_bits=value)

    def test_hidden_peak_global_enclosure(self):
        a=2.0**-14
        f=Biquad.from_coefficients([a,0,-a,0,1-a],precision='float32')
        b=bound_peak_gain(f)
        self.assertLessEqual(Fraction(b.lower_ratio),2)
        self.assertGreaterEqual(Fraction(b.upper_ratio),2)


class HighLevelInspectionTests(unittest.TestCase):
    def setUp(self):
        self.sos=[[1,-.75,0,1,-.125,0],[.75,-.09375,0,1,-.75,0]]

    def test_sos_compensation(self):
        r=inspect_sos(self.sos,precision='float32')
        self.assertTrue(r.certified)
        self.assertEqual(r.status,'certified')
        self.assertTrue(verify_inspection(r.as_dict(),self.sos,precision='float32'))
        self.assertLessEqual(Fraction(r.gain_bounds.lower_ratio),Fraction(3,4))
        self.assertGreaterEqual(Fraction(r.gain_bounds.upper_ratio),Fraction(3,4))

    def test_biquad_failed_condition_has_diagnostic(self):
        r=inspect_biquad([2,0,0,0,0],precision='float32')
        self.assertEqual(r.status,'rejected')
        self.assertEqual(r.reason,'gain_limit_not_met')
        self.assertFalse(verify_inspection(r.as_dict(),[2,0,0,0,0],precision='float32'))
        self.assertTrue(Fraction(r.gain_bounds.lower_ratio)<=2<=Fraction(r.gain_bounds.upper_ratio))

    def test_unstable_denominator_no_gain_bound(self):
        r=inspect_biquad([0,0,0,0,1])
        self.assertEqual(r.reason,'denominator_not_schur')
        self.assertIsNone(r.gain_bounds)
        sos=[[1,0,0,1,0,1]]
        self.assertIsNone(inspect_sos(sos).gain_bounds)

    def test_sos_unknown_never_passes(self):
        sos=[[2.6702880859375e-05,0,-2.6702880859375e-05,1,0,.99993896484375]]
        r=inspect_sos(sos,max_depth=0,peak_bits=0)
        self.assertEqual(r.status,'unknown')
        self.assertFalse(r.certified)
        self.assertFalse(verify_inspection(r.as_dict(),sos,precision='float32'))

    def test_sos_invalid_shapes_and_fs(self):
        for sos in ([],[[1,0,0,2,0,0]],[[1,0,0,1,0]],[[1,0,0,1,0,float('inf')]]):
            with self.subTest(sos=sos),self.assertRaises(ValueError):inspect_sos(sos)
        for fs in (0,-1,float('nan'),float('inf')):
            with self.subTest(fs=fs),self.assertRaises(ValueError):inspect_sos(self.sos,fs=fs)

    def test_binary32_label_requires_binary32_values(self):
        f=Biquad.from_coefficients([.1,0,0,0,0],precision='float64')
        with self.assertRaises(ValueError):
            inspect_biquad(f,precision='float32')
        with self.assertRaises(ValueError):
            inspect_cascade([f],precision='float32')
        report=inspect_biquad(f,precision='float64')
        self.assertFalse(verify_inspection(report.as_dict(),f,precision='float32'))

    def test_do_not_silently_normalize_a0(self):
        with self.assertRaises(ValueError):
            inspect_sos([[1,0,0,2,0,0]])

    def test_bound_certificate_tampering(self):
        f=Biquad.from_coefficients([.25,0,0,-.5,0],precision='float32')
        r=inspect_biquad(f,precision='float32',fs=48000)
        report=r.as_dict()
        self.assertTrue(verify_inspection(report,f,precision='float32',fs=48000))
        variants=[]
        for key,value in [('status','rejected'),('certified',False),('max_gain_hex','0x1.1p+0'),
                          ('precision','float64'),('sample_rate_hex','0x1.0p+0'),
                          ('input_digest','0'*64),('peak_bits',100)]:
            q=copy.deepcopy(report);q[key]=value;variants.append(q)
        q=copy.deepcopy(report);q['proof']['witness']['jury'][0]='0';variants.append(q)
        q=copy.deepcopy(report);q['gain_bounds']['upper_ratio']='0';variants.append(q)
        for case in variants:
            with self.subTest(change=case['status']):
                self.assertFalse(verify_inspection(case,f,precision='float32',fs=48000))
        self.assertFalse(verify_inspection(report,Biquad.from_coefficients([.5,0,0,-.5,0]),precision='float32',fs=48000))

    def test_sos_tampering_and_reordered_sections(self):
        r=inspect_sos(self.sos,precision='float32',peak_bits=3)
        q=r.as_dict()
        self.assertTrue(verify_inspection(q,self.sos,precision='float32'))
        q2=copy.deepcopy(q)
        q2['proof']['cover']=[[0,0],[0,0]]
        self.assertFalse(verify_inspection(q2,self.sos,precision='float32'))
        self.assertFalse(verify_inspection(q,list(reversed(self.sos)),precision='float32'))

    def test_report_json_save_and_markdown(self):
        r=inspect_sos(self.sos)
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/'report.json'
            r.save(output)
            self.assertEqual(json.loads(output.read_text()),r.as_dict())
            self.assertIn('SHA-256 input binding',r.markdown())

    def test_real_scipy_butterworth(self):
        try:
            from scipy.signal import butter
        except ImportError:
            self.skipTest('SciPy optional integration')
        sos=butter(8,.2,output='sos')
        r=inspect_sos(sos,precision='float32',fs=48000,max_gain=1.01)
        self.assertEqual(r.status,'certified')
        self.assertTrue(verify_inspection(r.as_dict(),sos,precision='float32',fs=48000,max_gain=1.01))


class UserJourneyTests(unittest.TestCase):
    def call(self,*args):
        stdout,stderr=io.StringIO(),io.StringIO()
        with redirect_stdout(stdout),redirect_stderr(stderr):
            code=main(list(map(str,args)))
        return code,stdout.getvalue(),stderr.getvalue()

    def test_hidden_peak_demo(self):
        d=hidden_peak_demo(1024)
        self.assertTrue(d['contradiction'])
        self.assertLess(d['grid']['estimated_max_gain'],1)
        self.assertEqual(d['analytical']['peak_gain'],2)
        self.assertEqual(d['exact']['status'],'gain_limit_not_met')
        self.assertEqual(self.call('demo','hidden-peak')[0],0)

    def test_bad_demo_size(self):
        self.assertEqual(self.call('demo','hidden-peak','--grid',1)[0],2)

    def test_cli_inspect_verify_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);inp=p/'filter.json';out=p/'inspection.json';md=p/'inspection.md'
            inp.write_text(json.dumps({'type':'biquad','precision':'float32','max_gain':1.,
                                      'coefficients':[.25,0,0,-.5,0]}))
            self.assertEqual(self.call('inspect',inp,'--output',out,'--report',md)[0],0)
            self.assertEqual(self.call('verify',inp,out)[0],0)
            self.assertIn('Provable peak gain interval',md.read_text())
            self.assertEqual(self.call('inspect',inp,'--report',inp)[0],2)

    def test_cli_unknown_exit3(self):
        with tempfile.TemporaryDirectory() as tmp:
            inp=Path(tmp)/'filter.json'
            inp.write_text(json.dumps({'type':'cascade','precision':'float32',
                'sections':[[2.6702880859375e-05,0,-2.6702880859375e-05,0,.99993896484375]]}))
            self.assertEqual(self.call('inspect',inp,'--max-depth',0,'--peak-bits',0)[0],3)

if __name__=='__main__':unittest.main()
