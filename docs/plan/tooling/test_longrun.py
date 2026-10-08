"""Bootstrap infrastructure tests, not a replacement for DSP qualification."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from scipy.signal import sosfilt
import longrun

class LongrunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = longrun.load_manifest(longrun.DEFAULT_MANIFEST)

    def assert_bad_manifest(self, change):
        d = copy.deepcopy(self.manifest)
        change(d)
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)/'bad.json'
            p.write_text(json.dumps(d), encoding='utf-8')
            with self.assertRaises(ValueError):
                longrun.load_manifest(p)

    def test_inventory_exact(self):
        x = longrun.inventory(self.manifest)
        self.assertEqual((x['records'], x['record_hours'], x['channel_hours']), (24, 76, 248))
        self.assertEqual(x['scalar_samples'], 23270400000)
        self.assertEqual(x['uncompressed_float32_bytes'], 93081600000)

    def test_pilot_really_three_hours(self):
        rows = longrun.choose(self.manifest, 'pilot')
        self.assertEqual(len(rows), 6)
        self.assertTrue(all(r['duration_seconds'] == 1800 for r in rows))
        self.assertEqual(sum(r['duration_seconds'] for r in rows), 10800)

    def test_smoke_is_explicitly_short(self):
        rows = longrun.choose(self.manifest, 'smoke')
        self.assertTrue(all(r['duration_seconds'] == 2 and r['planned_duration_seconds'] == 1800 for r in rows))

    def test_generator_independent_of_block_partition(self):
        for r in longrun.choose(self.manifest, 'pilot'):
            whole = longrun.samples(r, 43011, 911)
            parts = np.concatenate([longrun.samples(r, 43011, 127), longrun.samples(r, 43138, 784)])
            self.assertTrue(np.array_equal(whole, parts), r['id'])

    def test_distinct_seed_changes_values(self):
        r = copy.deepcopy(self.manifest['records'][0])
        a = longrun.samples(r, 1300, 200)
        r['seed'] += 1
        self.assertFalse(np.array_equal(a, longrun.samples(r, 1300, 200)))

    def test_absolute_counter_not_short_clip_loop(self):
        r = self.manifest['records'][2]  # wideband
        self.assertFalse(np.array_equal(longrun.samples(r, 0, 256), longrun.samples(r, 48000*60, 256)))

    def test_tail_is_zero_but_not_entire_record(self):
        r = self.manifest['records'][0]
        self.assertTrue(np.any(longrun.samples(r, 0, 200)))
        end = r['duration_seconds'] * r['sample_rate_hz']
        self.assertFalse(np.any(longrun.samples(r, end-500, 500)))

    def test_reset_state_negative_control_is_detectable(self):
        sos = np.asarray(longrun.REFERENCE_SOS, dtype=np.float32)
        x = np.ones((4096, 2), dtype=np.float32)*0.4
        good = sosfilt(sos, x, axis=0)
        wrong = np.concatenate([sosfilt(sos, x[:2048], axis=0), sosfilt(sos, x[2048:], axis=0)])
        self.assertGreater(float(np.max(np.abs(good-wrong))), 1e-3)

    def test_duplicate_ids_rejected(self):
        self.assert_bad_manifest(lambda d: d['records'][1].update(id=d['records'][0]['id']))

    def test_duplicate_seeds_rejected(self):
        self.assert_bad_manifest(lambda d: d['records'][1].update(seed=d['records'][0]['seed']))

    def test_duration_boolean_rejected(self):
        self.assert_bad_manifest(lambda d: d['records'][0].update(duration_seconds=True))

    def test_short_loop_label_rejected(self):
        self.assert_bad_manifest(lambda d: d['records'][0].update(loop_short_clip=True))

    def test_fake_industrial_source_rejected(self):
        self.assert_bad_manifest(lambda d: d['records'][0].update(source_kind='industrial'))

    def test_path_traversal_id_rejected(self):
        self.assert_bad_manifest(lambda d: d['records'][0].update(id='../escape'))

    def test_unknown_subset_rejected(self):
        with self.assertRaises(ValueError):
            longrun.choose(self.manifest, 'pilot', ['NOT-A-RECORD'])

    def test_outside_frame_range_rejected(self):
        r = self.manifest['records'][0]
        with self.assertRaises(ValueError):
            longrun.samples(r, r['duration_seconds']*r['sample_rate_hz'], 1)

if __name__ == '__main__':
    unittest.main()
