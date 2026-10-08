import copy
import io
import json
import math
import random
import struct
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

from dexted_dsp import (Biquad, certify, certify_cascade, from_sos,
                           verify_biquad, verify_cascade)
from dexted_dsp.reference import reference_decision
from dexted_dsp.cascade import prove_positive
from dexted_dsp.cli import main


def section(values, precision='float64'):
    return Biquad.from_coefficients(values, precision=precision)


class BiquadTests(unittest.TestCase):
    def test_constant_pass(self):
        self.assertTrue(certify(section([.5,0,0,0,0])).certified)

    def test_strict_equality_rejected(self):
        self.assertEqual(certify(section([1,0,0,0,0])).status,'gain_limit_not_met')

    def test_denominator_failure_distinguished(self):
        self.assertEqual(certify(section([0,0,0,0,1])).status,'denominator_not_schur')

    def test_pole_zero_cancellation_does_not_hide_unstable_section(self):
        self.assertFalse(certify(section([1,-2,0,-2,0]),2).certified)

    def test_hidden_peak(self):
        a=2**-14
        f=section([a,0,-a,0,1-a])
        self.assertFalse(certify(f).certified)
        self.assertTrue(certify(section([a*7/16,0,-a*7/16,0,1-a])).certified)

    def test_one_pole_endpoint(self):
        self.assertFalse(certify(section([.5,0,0,-.5,0])).certified)
        self.assertTrue(certify(section([.25,0,0,-.5,0])).certified)

    def test_gamma_variation(self):
        f=section([1,0,0,0,0])
        self.assertFalse(certify(f,math.nextafter(1.,0.)).certified)
        self.assertTrue(certify(f,math.nextafter(1.,2.)).certified)

    def test_extreme_values(self):
        values=[0., -0., math.ulp(0.), 1e-300, 1e300, float.fromhex('0x1.fffffffffffffp+1023')]
        for x in values:
            for gamma in [math.ulp(0.),1e-300,1.,1e300]:
                with self.subTest(x=x,gamma=gamma):
                    f=section([x,0,0,0,0])
                    self.assertEqual(certify(f,gamma).certified,reference_decision(f,gamma))

    def test_invalid_gamma(self):
        for x in [0,-1,math.nan,math.inf,True,'1',None]:
            with self.subTest(x=x), self.assertRaises(ValueError):
                certify(section([.5,0,0,0,0]),x)

    def test_invalid_coefficients(self):
        for x in [math.nan,math.inf,-math.inf,True,'0.5',None,1+2j]:
            with self.subTest(x=x), self.assertRaises(ValueError):
                section([x,0,0,0,0])

    def test_invalid_shapes(self):
        for row in [[],[1,2], [0]*6]:
            with self.assertRaises(ValueError): section(row)
        with self.assertRaises(ValueError): Biquad((0,0),(1,0,0))
        with self.assertRaises(ValueError): Biquad((1,0,0),(2,0,0))

    def test_explicit_float32_rounding(self):
        a=section([.1,0,0,0,0],precision='float32')
        self.assertEqual(a.b[0],struct.unpack('!f',struct.pack('!f',.1))[0])
        self.assertNotEqual(a.b[0],.1)
        with self.assertRaises(ValueError): section([1e300,0,0,0,0],precision='float32')
        with self.assertRaises(ValueError): section([0]*5,precision='float16')

    def test_sos_layout(self):
        self.assertEqual(from_sos([[.5,0,0,1,0,0]])[0],section([.5,0,0,0,0]))
        for rows in [[],[[1,0,0,2,0,0]],[[1,2]]]:
            with self.assertRaises(ValueError): from_sos(rows)

    def test_seeded_fraction_agreement(self):
        rng=random.Random(801721)
        for _ in range(2500):
            r=rng.uniform(.01,1.15);t=rng.uniform(0,math.pi)
            f=section([rng.uniform(-2,2) for _ in range(3)]+[-2*r*math.cos(t),r*r],precision='float32')
            gamma=2**rng.uniform(-3,3)
            self.assertEqual(certify(f,gamma).certified,reference_decision(f,gamma))

    def test_random_binary32_bit_patterns(self):
        rng=random.Random(291714)
        count=0
        for _ in range(1200):
            row=[struct.unpack('!f',struct.pack('!I',rng.getrandbits(32)))[0] for _ in range(5)]
            if not all(map(math.isfinite,row)):continue
            f=section(row)
            self.assertEqual(certify(f).certified,reference_decision(f))
            count+=1
        self.assertGreater(count,1100)

    def test_json_witness(self):
        f=section([.5,0,0,0,0]);p=certify(f).as_dict()
        self.assertTrue(verify_biquad(json.loads(json.dumps(p)),f))
        self.assertIsInstance(p['witness']['jury'][0],str)

    def test_certificate_input_binding(self):
        f=section([.5,0,0,0,0]);p=certify(f).as_dict()
        self.assertFalse(verify_biquad(p,section([.75,0,0,0,0])))
        self.assertFalse(verify_biquad(p,f,.75))
        q=copy.deepcopy(p);q['status']='other';self.assertFalse(verify_biquad(q,f))

    def test_forged_certified_flag(self):
        f=section([2,0,0,0,0]);p=certify(f).as_dict()
        p['status']='certified';p['certified']=True
        self.assertFalse(verify_biquad(p,f))


class CascadeTests(unittest.TestCase):
    def setUp(self):
        self.rows=[section([1,-.75,0,-.125,0]),section([.75,-.09375,0,-.75,0])]

    def test_compensation_certified(self):
        self.assertFalse(certify(self.rows[0]).certified)
        self.assertFalse(certify(self.rows[1]).certified)
        p=certify_cascade(self.rows)
        self.assertTrue(p['certified']);self.assertTrue(verify_cascade(p,self.rows))

    def test_single_constant(self):
        f=section([.5,0,0,0,0]);p=certify_cascade([f])
        self.assertTrue(p['certified']);self.assertTrue(verify_cascade(p,[f]))

    def test_equality_failed(self):
        p=certify_cascade([section([1,0,0,0,0])])
        self.assertEqual(p['status'],'condition_failed')

    def test_section_stability(self):
        p=certify_cascade([section([0,0,0,0,1])])
        self.assertEqual(p['status'],'denominator_not_schur')

    def test_unknown_is_not_pass(self):
        p=prove_positive([1,0,1],max_depth=0)
        self.assertEqual(p['verdict'],'unknown')
        p=prove_positive([1,0,1],max_depth=2)
        self.assertEqual(p['verdict'],'certified')

    def test_negative_midpoint_witness(self):
        p=prove_positive([-1,0,2],max_depth=2)
        self.assertEqual(p['verdict'],'condition_failed')

    def test_polynomial_tangency(self):
        self.assertEqual(prove_positive([0,0,1])['verdict'],'condition_failed')

    def test_budget_validation(self):
        for options in [{'max_depth':-1},{'max_nodes':0},{'max_depth':True},{'max_nodes':100001}]:
            with self.assertRaises(ValueError):certify_cascade(self.rows,**options)
        with self.assertRaises(ValueError):certify_cascade([])
        with self.assertRaises(ValueError):certify_cascade(self.rows*17)

    def test_proof_tampering(self):
        p=certify_cascade(self.rows)
        for cover in [[],[[0,1]],[[0,0],[0,0]],[[-1,0]],[[0,-1]],[[True,0]],[[0,129]]]:
            q=copy.deepcopy(p);q['cover']=cover
            self.assertFalse(verify_cascade(q,self.rows))
        self.assertFalse(verify_cascade(p,self.rows,.9))
        self.assertFalse(verify_cascade(p,list(reversed(self.rows))))

    def test_false_cover_is_not_accepted(self):
        bad=[section([2,0,0,0,0])]
        p=certify_cascade(bad);p.update(status='certified',certified=True,cover=[[0,0]])
        self.assertFalse(verify_cascade(p,bad))

    def test_seeded_positive_certificates(self):
        rng=random.Random(282718)
        accepted=0
        for _ in range(100):
            a=rng.uniform(.1,.85);b=rng.uniform(.01,.09);k=rng.uniform(.1,.9)
            rows=[section([1,-a,0,-b,0],precision='float32'),
                  section([k,-k*b,0,-a,0],precision='float32')]
            p=certify_cascade(rows,max_nodes=4000)
            if p['certified']:
                self.assertTrue(verify_cascade(p,rows));accepted+=1
        self.assertGreater(accepted,95)


class CLITests(unittest.TestCase):
    def run_cli(self,*args):
        out,err=io.StringIO(),io.StringIO()
        with redirect_stdout(out),redirect_stderr(err): code=main(list(map(str,args)))
        return code,out.getvalue(),err.getvalue()

    def test_check_verify_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            inp,out=Path(d)/'in.json',Path(d)/'out.json'
            inp.write_text(json.dumps({'type':'biquad','coefficients':[.5,0,0,0,0]}))
            self.assertEqual(self.run_cli('check',inp,'--output',out)[0],0)
            self.assertEqual(self.run_cli('verify',inp,out)[0],0)

    def test_fail_exit(self):
        with tempfile.TemporaryDirectory() as d:
            inp=Path(d)/'in.json';inp.write_text(json.dumps({'type':'biquad','coefficients':[2,0,0,0,0]}))
            self.assertEqual(self.run_cli('check',inp)[0],1)

    def test_cascade_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            inp,out=Path(d)/'in.json',Path(d)/'out.json'
            inp.write_text(json.dumps({'type':'cascade','sections':[[.5,0,0,0,0]]}))
            self.assertEqual(self.run_cli('check',inp,'--output',out)[0],0)
            self.assertEqual(self.run_cli('verify',inp,out)[0],0)

    def test_no_input_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            inp=Path(d)/'in.json';text=json.dumps({'type':'biquad','coefficients':[.5,0,0,0,0]});inp.write_text(text)
            self.assertEqual(self.run_cli('check',inp,'--output',inp)[0],2)
            self.assertEqual(inp.read_text(),text)

    def test_invalid_input(self):
        with tempfile.TemporaryDirectory() as d:
            inp=Path(d)/'in.json'
            for text in ['[]','{bad','{"type":"faust"}','{"type":"biquad","coefficients":[NaN,0,0,0,0]}']:
                inp.write_text(text);self.assertEqual(self.run_cli('check',inp)[0],2)

    def test_version(self):
        with redirect_stdout(io.StringIO()),self.assertRaises(SystemExit) as context:
            main(['--version'])
        self.assertEqual(context.exception.code,0)

if __name__=='__main__':unittest.main()
