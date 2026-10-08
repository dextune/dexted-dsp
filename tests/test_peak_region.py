"""Reproducible exact peak-location regression and certificate tamper checks."""
import copy
from fractions import Fraction as Q
import io
import json
import math
from pathlib import Path
import random
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

from dexted_dsp import (Biquad, inspect_biquad, localize_peak,
                        verify_inspection)
from dexted_dsp.cli import main


def intervals(region):
    return [(Q(a),Q(b)) for a,b in region.cosine_intervals]


def ratio(f,c):
    """Independent Fraction response: expand |p0+p1*e^-iw+p2*e^-2iw|^2."""
    x,y,z=map(Q,f.b)
    u,v,w=map(Q,f.a)
    def squared(a,b,d):
        return ((a-d)**2+b*b)+2*b*(a+d)*c+4*a*d*c*c
    return squared(x,y,z)/squared(u,v,w)


class ExactPeakLocalizationTests(unittest.TestCase):
    def test_hidden_peak_exact_cosine(self):
        a=2**-14
        f=Biquad.from_coefficients([a,0,-a,0,1-a],precision='float32')
        r=localize_peak(f,fs=48000)
        self.assertEqual(intervals(r),[(Q(0),Q(0))])
        self.assertEqual(r.status,'isolated')
        self.assertEqual(r.frequency_hz_approx,((12000.,12000.),))
        self.assertFalse(r.as_dict()['frequency_hz_certified'])

    def test_endpoint_and_tied_peaks(self):
        low=Biquad.from_coefficients([.5,0,0,-.5,0])
        self.assertEqual(intervals(localize_peak(low)),[(Q(1),Q(1))])
        high=Biquad.from_coefficients([1,0,1,0,0])
        self.assertEqual(intervals(localize_peak(high)),[(Q(-1),Q(-1)),(Q(1),Q(1))])
        middle=Biquad.from_coefficients([1,0,-1,0,0])
        self.assertEqual(intervals(localize_peak(middle)),[(Q(0),Q(0))])

    def test_entire_band_flat_and_zero(self):
        constant=Biquad.from_coefficients([.75,-.375,0,-.5,0])
        zero=Biquad.from_coefficients([0,0,0,0,0])
        for f in (constant,zero):
            with self.subTest(coefficients=f.coefficients):
                r=localize_peak(f,fs=48000)
                self.assertEqual(r.status,'flat')
                self.assertEqual(intervals(r),[(Q(-1),Q(1))])

    def test_unstable_has_no_peak_region(self):
        f=Biquad.from_coefficients([1,0,0,0,1])
        self.assertIsNone(localize_peak(f))
        self.assertIsNone(inspect_biquad(f).peak_region)

    def test_invalid_input_budgets_and_fs(self):
        f=Biquad.from_coefficients([1,0,0,0,0])
        for bad in (True,-1,65,'24',None):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                localize_peak(f,isolation_bits=bad)
        for bad in (0,-1,float('nan'),float('inf'),True):
            with self.subTest(fs=bad),self.assertRaises(ValueError):
                localize_peak(f,fs=bad)

    def test_random_dyadic_global_max_within_survivor_union(self):
        """Independent exact grid witness must not dominate surviving extrema.

        This is regression evidence, not an independent mathematical proof.
        """
        rng=random.Random(95307)
        for _ in range(400):
            b=[rng.randrange(-20,21)/16 for _ in range(3)]
            a1=rng.randrange(-14,15)/16
            a2=rng.randrange(-7,8)/16
            if not(abs(a2)<1 and 1+a1+a2>0 and 1-a1+a2>0):
                continue
            f=Biquad.from_coefficients(b+[a1,a2])
            region=localize_peak(f,isolation_bits=22)
            self.assertIsNotNone(region)
            cand=[]
            for lo,hi in intervals(region):
                # Exact candidate upper using a rational interval bound.
                x,y,z=map(Q,f.b);u,v,w=map(Q,f.a)
                n=((x-z)**2+y*y,2*y*(x+z),4*x*z)
                d=((u-w)**2+v*v,2*v*(u+w),4*u*w)
                def extremes(p):
                    vals=[p[0]+p[1]*t+p[2]*t*t for t in (lo,hi)]
                    if p[2]:
                        vertex=-p[1]/(2*p[2])
                        if lo<vertex<hi:
                            vals.append(p[0]+p[1]*vertex+p[2]*vertex*vertex)
                    return min(vals),max(vals)
                nmin,nmax=extremes(n)
                dmin,dmax=extremes(d)
                self.assertGreater(dmin,0)
                cand.append(nmax/dmin)
            best_upper=max(cand)
            for k in range(65):
                c=Q(k-32,32)
                self.assertLessEqual(ratio(f,c),best_upper)

    def test_inspection_proof_version_and_tampering(self):
        f=Biquad.from_coefficients([.25,0,0,-.5,0],precision='float32')
        report=inspect_biquad(f,precision='float32',fs=48000,region_bits=18).as_dict()
        self.assertEqual(report['schema'],'dexted-dsp/inspection/v2')
        self.assertTrue(verify_inspection(report,f,precision='float32',fs=48000))
        for key,value in [('region_bits',True),('region_bits',65)]:
            bad=copy.deepcopy(report);bad[key]=value
            self.assertFalse(verify_inspection(bad,f,precision='float32',fs=48000))
        bad=copy.deepcopy(report);bad['peak_region']['cosine_intervals']=[['-1','1']]
        self.assertFalse(verify_inspection(bad,f,precision='float32',fs=48000))
        bad=copy.deepcopy(report);bad['peak_region']['frequency_hz_approx']=[[41000.,48000.]]
        self.assertFalse(verify_inspection(bad,f,precision='float32',fs=48000))
        bad=copy.deepcopy(report);bad.pop('peak_region')
        self.assertFalse(verify_inspection(bad,f,precision='float32',fs=48000))
        # Existing serialized v1 proof envelopes remain valid.
        legacy=copy.deepcopy(report)
        legacy['schema']='dexted-dsp/inspection/v1'
        legacy.pop('peak_region');legacy.pop('region_bits')
        self.assertTrue(verify_inspection(legacy,f,precision='float32',fs=48000))

    def test_cli_sample_rate_and_region_bits(self):
        with tempfile.TemporaryDirectory() as d:
            inp=Path(d)/'input.json';out=Path(d)/'proof.json'
            inp.write_text(json.dumps({'type':'biquad','coefficients':[.25,0,0,-.5,0],
                                       'precision':'float32','max_gain':1.,'sample_rate_hz':48000}))
            with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
                code=main(['inspect',str(inp),'--output',str(out),'--region-bits','12'])
            self.assertEqual(code,0)
            data=json.loads(out.read_text())
            self.assertEqual(data['region_bits'],12)
            self.assertEqual(data['peak_region']['frequency_hz_approx'],[[0.,0.]])
            with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
                self.assertEqual(main(['verify',str(inp),str(out)]),0)
            inp.write_text(json.dumps({'type':'biquad','coefficients':[.25,0,0,-.5,0],
                                       'precision':'float32','max_gain':1.,'sample_rate_hz':44100}))
            with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
                self.assertEqual(main(['verify',str(inp),str(out)]),1)


if __name__=='__main__':
    unittest.main()
