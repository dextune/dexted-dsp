"""CT-01/03/04/05/07/10/12/15/16/17/18/20/26 safety regression."""
import copy
import json
import math
import struct
import unittest

from dexted_dsp import (Biquad, certify, certify_cascade, from_sos,
                        verify_biquad, verify_cascade, check_sos,
                        parse_certificate_json, verify_serialized_certificate)
from dexted_dsp.cascade import prove_positive, validate_sections
from dexted_dsp.native import NativeBiquad, NativeCascade
from dexted_dsp.reference import reference_decision


def biquad(values=(0.5, 0, 0, 0, 0), precision='float64'):
    return Biquad.from_coefficients(values, precision=precision)


class CoreInputHardening(unittest.TestCase):
    def test_ct01_five_coefficient_iterable_consumes_only_six(self):
        consumed = []
        def source():
            while True:
                consumed.append(None)
                yield 0
        with self.assertRaises(ValueError):
            biquad(source())
        self.assertEqual(len(consumed), 6)

    def test_ct01_sos_iterator_consumes_only_33(self):
        consumed = []
        def source():
            while True:
                consumed.append(None)
                yield [0, 0, 0, 1, 0, 0]
        with self.assertRaises(ValueError):
            from_sos(source())
        self.assertEqual(len(consumed), 33)

    def test_ct01_sos_row_iterator_consumes_only_seven(self):
        consumed = []
        def row():
            while True:
                consumed.append(None)
                yield 0
        with self.assertRaises(ValueError):
            from_sos([row()])
        self.assertEqual(len(consumed), 7)

    def test_ct01_cascade_iterator_consumes_only_33(self):
        consumed = []
        def rows():
            while True:
                consumed.append(None)
                yield biquad()
        with self.assertRaises(ValueError):
            validate_sections(rows())
        self.assertEqual(len(consumed), 33)

    def test_ct04_owning_numeric_copy(self):
        values = [0.5, 0, 0, 0, 0]
        section = biquad(values)
        values[0] = 123
        self.assertEqual(section.b[0], .5)

    def test_ct03_nonfinite_after_f32_rounding(self):
        with self.assertRaises(ValueError):
            biquad([3.402824e38, 0, 0, 0, 0], precision='float32')

    def test_ct05_one_ulp_strict_jury(self):
        for a2 in [math.nextafter(1., 0.), 1., math.nextafter(1., math.inf),
                   math.nextafter(-1., 0.), -1.]:
            f = biquad([0., 0., 0., 0., a2])
            self.assertEqual(certify(f).certified, reference_decision(f))

    def test_ct07_strict_gamma(self):
        unity = biquad([1,0,0,0,0])
        for gamma in [math.nextafter(1.,0.),1.,math.nextafter(1.,2.)]:
            self.assertEqual(certify(unity,gamma).certified,reference_decision(unity,gamma))


class CertificateHardening(unittest.TestCase):
    def setUp(self):
        self.f = biquad()
        self.good = certify(self.f).as_dict()
        self.rows = [self.f]
        self.cover = certify_cascade(self.rows)
        self.assertTrue(self.cover['certified'])

    def test_ct18_legacy_canonical_certificates(self):
        self.assertTrue(verify_biquad(self.good,self.f))
        self.assertTrue(verify_cascade(self.cover,self.rows))
        self.assertTrue(verify_serialized_certificate(json.dumps(self.good).encode(),self.f))
        self.assertTrue(verify_serialized_certificate(json.dumps(self.cover).encode(),self.rows))

    def test_ct16_changed_biquad_witness_is_rejected(self):
        for change in ['jury','polynomial_c0_c1_c2','endpoints_minus_plus']:
            bad = copy.deepcopy(self.good)
            bad['witness'][change][0] = '987654321'
            self.assertFalse(verify_biquad(bad,self.f))
        bad = copy.deepcopy(self.good)
        bad['witness']['interior_required'] = not bad['witness']['interior_required']
        self.assertFalse(verify_biquad(bad,self.f))

    def test_ct15_invalid_cascade_metadata(self):
        for key, value in [('method','tampered'),('nodes',True),('max_depth',129),
                           ('degree',True),('denominator_stable',False),
                           ('strict',1),('status','unknown')]:
            bad = copy.deepcopy(self.cover)
            bad[key] = value
            self.assertFalse(verify_cascade(bad,self.rows), key)

    def test_ct16_huge_index_fails_before_shift(self):
        bad = copy.deepcopy(self.cover)
        bad['cover'] = [[1 << 900000, 0]]
        self.assertFalse(verify_cascade(bad,self.rows))

    def test_ct15_cover_duplicate_and_overlap(self):
        for cover in ([[0,0],[0,0]], [[0,1],[0,1]], [[0,2]], [[0,1],[1,2]]):
            bad=copy.deepcopy(self.cover)
            bad['cover']=cover
            self.assertFalse(verify_cascade(bad,self.rows))

    def test_ct16_duplicate_json_key(self):
        with self.assertRaises(ValueError):
            parse_certificate_json(b'{"schema":"dexted-dsp/biquad/v1","schema":"dexted-dsp/cascade/v1"}')
        self.assertFalse(verify_serialized_certificate(b'{"schema":"dexted-dsp/biquad/v1","schema":"dexted-dsp/biquad/v1"}',self.f))

    def test_ct16_nonfinite_trailing_and_nested_json(self):
        for data in [b'{"schema":"dexted-dsp/biquad/v1","x":NaN}',
                     b'{"schema":"dexted-dsp/biquad/v1"} garbage',
                     b'\xef\xbb\xbf{"schema":"dexted-dsp/biquad/v1"}',
                     b'{"schema":"dexted-dsp/future/v9"}']:
            with self.subTest(data=data), self.assertRaises(ValueError):
                parse_certificate_json(data)
        nested={'schema':'dexted-dsp/biquad/v1','x':0}
        for _ in range(17):
            nested={'schema':'dexted-dsp/biquad/v1','x':nested}
        with self.assertRaises(ValueError):
            parse_certificate_json(json.dumps(nested).encode())

    def test_ct16_proof_cap_and_digit_cap(self):
        with self.assertRaises(ValueError):
            parse_certificate_json(b' ' * (4_194_304 + 1))
        with self.assertRaises(ValueError):
            parse_certificate_json(b'{"schema":"dexted-dsp/biquad/v1","value":'+b'9'*100+b'}')

    def test_ct17_caller_identity(self):
        self.assertFalse(verify_serialized_certificate(json.dumps(self.good).encode(),self.f,.0))
        self.assertFalse(verify_serialized_certificate(json.dumps(self.good).encode(),
                                                       biquad([0.75,0,0,0,0])))
        self.assertFalse(verify_serialized_certificate(json.dumps(self.cover).encode(),
                                                       self.rows, max_gain=.75))


class DecisionOnly(unittest.TestCase):
    def test_ct20_verified_not_deployed(self):
        result=check_sos([biquad()])
        self.assertTrue(result.verified)
        self.assertFalse(result.deployment_allowed)
        with self.assertRaises(TypeError):
            bool(result)
        self.assertEqual(len(result.input_digest),64)

    def test_ct12_tiny_proof_cap_fails_closed(self):
        result=check_sos([biquad()],max_proof_bytes=1)
        self.assertEqual(result.math_status,'certified')
        self.assertEqual(result.proof_status,'not_run')
        self.assertFalse(result.verified)

    def test_ct12_positive_polynomial_budget_exhaustion(self):
        self.assertEqual(prove_positive([1,0,1],max_depth=0)['verdict'],'unknown')
        self.assertEqual(prove_positive([1,0,1],max_depth=2)['verdict'],'certified')
        self.assertEqual(prove_positive([1<<262145])['verdict'],'unknown')

    def test_ct12_type_rejections(self):
        for kw in [{'max_depth':True},{'max_nodes':True},{'max_nodes':100001}]:
            with self.assertRaises(ValueError):
                prove_positive([1],**kw)

    def test_ct26_native_biquad_unknown_codes(self):
        api=NativeBiquad.__new__(NativeBiquad)
        for code in [-3,-2,-1,2,19]:
            api._call=lambda *_args: code
            with self.assertRaises(RuntimeError):
                api.certify(biquad())
        api._call=lambda *_args: 1
        self.assertTrue(api.certify(biquad()))
        api._call=lambda *_args: 0
        self.assertFalse(api.certify(biquad()))

    def test_ct26_native_cascade_unknown_codes(self):
        api=NativeCascade.__new__(NativeCascade)
        for code in [-2,3,99]:
            api._call=lambda *_args: code
            with self.assertRaises(RuntimeError):
                api.check([biquad()])
        api._call=lambda *_args: -3
        self.assertEqual(api.check([biquad()]),'unknown')
        api._call=lambda *_args: 1
        self.assertEqual(api.check([biquad()]),'certified')


if __name__ == '__main__':
    unittest.main()
