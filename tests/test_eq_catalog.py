"""Contract tests for deterministic audio-EQ coefficient exports."""
from __future__ import annotations
import hashlib
from pathlib import Path
import math
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'benchmarks'/'suites'))
from eq_catalog import (generate,canonical_bytes,design_biquad,f32,
                        DEFAULT_COUNT,DEFAULT_SEED)

EXPECTED_SHA='873ce092e2fe7fa7e8d16c8fd50b251f377c05c4a02ed267e6917d7599a69120'


class DesignedEQCatalogTests(unittest.TestCase):
    def test_frozen_catalog_hash_and_both_splits(self):
        result=generate()
        self.assertEqual(result['count'],1200)
        self.assertEqual(hashlib.sha256(canonical_bytes(result)).hexdigest(),EXPECTED_SHA)
        hold=[x for x in result['cases'] if x['split']=='holdout']
        self.assertGreater(len(hold),200)
        self.assertLess(len(hold),400)
        self.assertEqual(len({x['id'] for x in result['cases']}),1200)
        self.assertEqual(set(x['family'] for x in result['cases']),
                         {'peaking','notch','lowpass','highpass'})

    def test_quantized_export_and_contract(self):
        for case in generate(count=80)['cases']:
            for row in case['sos']:
                self.assertEqual(len(row),6)
                self.assertEqual(row[3],1.0)
                for v in row:
                    self.assertTrue(math.isfinite(v))
                    self.assertEqual(f32(v),v)
                a1,a2=row[4:]
                self.assertLess(abs(a2),1.)
                self.assertGreater(1+a1+a2,0.)
                self.assertGreater(1-a1+a2,0.)

    def test_gain_and_shape_validation(self):
        with self.assertRaises(ValueError):design_biquad('invalid',48000,1000,1)
        with self.assertRaises(ValueError):design_biquad('notch',48000,24000,1)
        with self.assertRaises(ValueError):design_biquad('peaking',48000,1000,0)
        with self.assertRaises(ValueError):design_biquad('peaking',48000,float('nan'),1)
        with self.assertRaises(ValueError):generate(count=0)

    def test_peaking_gain_dependent(self):
        positive=design_biquad('peaking',48000,1000,1,6)
        negative=design_biquad('peaking',48000,1000,1,-6)
        self.assertNotEqual(positive,negative)
        flat=design_biquad('peaking',48000,1000,1,0)
        self.assertEqual(flat[:3],[1.,flat[4],flat[5]])


if __name__=='__main__':unittest.main()
