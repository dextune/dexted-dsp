#!/usr/bin/env python3
"""Stream deterministic long fixtures without loading or storing whole recordings.

This is a qualification-PLAN bootstrap harness, not Dexted's audio engine and
not a proof of physical device arithmetic. Numerical lanes use scipy.sosfilt.
Add --with-dexted to certify the represented reference coefficients once per
record using an installed Dexted DSP package. No network or downloads occur.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time

BASE = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = BASE / 'manifests' / 'long-signals-v1.json'
KINDS = {'sweep', 'multitone', 'wideband', 'transients', 'silence_recovery', 'drift'}
REFERENCE_SOS = [[0.125, 0.25, 0.125, 1., -0.5, 0.125],
                 [0.25, 0., 0., 1., -0.5, 0.]]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def positive_integer(value, name: str, upper: int) -> int:
    if type(value) is not int or not 1 <= value <= upper:
        raise ValueError(f'{name}: expected integer in [1, {upper}]')
    return value


def load_manifest(path: Path) -> dict:
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('schema') != 'dexted-dsp/industrial-long-signals/v1':
        raise ValueError('unrecognized manifest schema')
    rows = data.get('records')
    if not isinstance(rows, list) or not rows:
        raise ValueError('nonempty records list required')
    ids, seeds = set(), set()
    for r in rows:
        key = r.get('id')
        if not isinstance(key, str) or not key or not key.replace('-', '').isalnum():
            raise ValueError('id must be nonempty alphanumeric/hyphen (no paths)')
        if key in ids:
            raise ValueError('duplicate record id: ' + key)
        ids.add(key)
        if r.get('source_kind') != 'synthetic':
            raise ValueError('this generator accepts synthetic records only')
        if r.get('dtype') != 'float32' or r.get('kind') not in KINDS:
            raise ValueError('unsupported dtype or signal kind')
        positive_integer(r.get('sample_rate_hz'), 'sample_rate_hz', 192000)
        positive_integer(r.get('channels'), 'channels', 8)
        positive_integer(r.get('duration_seconds'), 'duration_seconds', 86400)
        seed = positive_integer(r.get('seed'), 'seed', 2**31-1)
        if seed in seeds:
            raise ValueError('record seeds must differ')
        seeds.add(seed)
        profiles = r.get('profiles')
        if not isinstance(profiles, list) or not profiles or not set(profiles) <= {'pilot', 'qualification'}:
            raise ValueError('invalid profile membership')
        if r.get('loop_short_clip') is not False:
            raise ValueError('short-clip looping prohibited in this manifest')
    return data


def inventory(data: dict) -> dict:
    rows = data['records']
    scalar_samples = sum(r['duration_seconds'] * r['sample_rate_hz'] * r['channels'] for r in rows)
    return {'records': len(rows),
            'record_hours': sum(r['duration_seconds'] for r in rows) / 3600,
            'channel_hours': sum(r['duration_seconds'] * r['channels'] for r in rows) / 3600,
            'scalar_samples': scalar_samples, 'uncompressed_float32_bytes': scalar_samples * 4,
            'storage_gib': scalar_samples * 4 / 2**30}


def choose(data: dict, profile: str, ids: list[str] | None = None) -> list[dict]:
    actual_profile = 'pilot' if profile == 'smoke' else profile
    rows = [copy.deepcopy(r) for r in data['records'] if actual_profile in r['profiles']]
    if ids:
        if len(ids) != len(set(ids)) or not set(ids) <= {r['id'] for r in rows}:
            raise ValueError('duplicate or unknown --record for selected profile')
        rows = [r for r in rows if r['id'] in ids]
    if not rows:
        raise ValueError('no matching records')
    if profile == 'smoke':
        for r in rows:
            r['planned_duration_seconds'] = r['duration_seconds']
            r['duration_seconds'] = 2
    return rows


def samples(record: dict, start: int, count: int):
    """Absolute-index synthesis; chunk boundaries never reset phase or RNG.

    Counter mixing is modulo 2**64, with the upper 24 bits mapped to noise.
    Sines/exp are evaluated in NumPy float64 then explicitly rounded to float32.
    Byte identity is required in a pinned toolchain; cross-libm identity is NOT
    promised. Same record seed + schema + toolchain + indices => same samples.
    """
    import numpy as np
    total = record['duration_seconds'] * record['sample_rate_hz']
    if type(start) is not int or type(count) is not int or start < 0 or count < 1 or start+count > total:
        raise ValueError('sample range outside record')
    fs, channels, seed = record['sample_rate_hz'], record['channels'], record['seed']
    frame = np.arange(start, start+count, dtype=np.uint64)[:, None]
    ch = np.arange(channels, dtype=np.uint64)[None, :]
    with np.errstate(over='ignore'):
        z = (frame * np.uint64(channels) + ch + np.uint64(seed) * np.uint64(0x9E3779B97F4A7C15))
        z = (z ^ (z >> 30)) * np.uint64(0xBF58476D1CE4E5B9)
        z = (z ^ (z >> 27)) * np.uint64(0x94D049BB133111EB)
        z = z ^ (z >> 31)
    noise = ((z >> 40).astype(np.float64) / 2**23) - 1.0
    t = frame.astype(np.float64) / fs
    offset = ch.astype(np.float64) * 0.37 + (seed % 997) / 997
    duration = record['duration_seconds']
    kind = record['kind']
    if kind == 'sweep':
        f0, f1 = fs / 960, fs * 0.45
        k = math.log(f1/f0) / duration
        phase = 2 * np.pi * f0 * np.expm1(k*t) / k
        x = 0.55*np.sin(phase+offset) + 0.08*noise
    elif kind == 'multitone':
        x = (0.18*np.sin(2*np.pi*fs*0.0173*t+offset)
             + 0.16*np.sin(2*np.pi*fs*0.1237*t+offset*1.3)
             + 0.14*np.sin(2*np.pi*fs*0.24991*t+offset*2.1) + 0.06*noise)
    elif kind == 'wideband':
        x = (0.2+0.3*t/duration)*noise + 0.07*np.sin(2*np.pi*0.131*t+offset)
    elif kind == 'transients':
        pulses = (((frame + np.uint64(seed)) % np.uint64(fs*7+31)) < 3).astype(np.float64)
        x = 0.72*pulses + 0.06*noise
    elif kind == 'silence_recovery':
        # Several unequal active intervals, not a short audio clip loop.
        p = t/duration
        gate = ((p < 0.13) | ((p > 0.31) & (p < 0.54)) | ((p > 0.76) & (p < 0.88)))
        x = gate*(0.45*noise + 0.16*np.sin(2*np.pi*fs*0.11*t+offset))
    else:
        phase = 2*np.pi*(fs*0.012*t + fs*0.009*t*t/(2*duration))
        x = 0.35*np.sin(phase+offset) + 0.12*(t/duration-0.5) + 0.09*noise
    # Tail is included in the stated duration; still propagate filter state.
    tail = min(60., duration*0.1)
    x = np.where(t >= duration-tail, 0., x)
    return np.asarray(x, dtype='<f4', order='C')


def process_peak_rss_bytes() -> int | None:
    try:
        import resource
        value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return int(value if sys.platform == 'darwin' else value*1024)
    except (ImportError, AttributeError):
        return None


def run_record(record: dict, chunk_frames: int, output: Path, retain: bool, with_dexted: bool) -> dict:
    import numpy as np
    from scipy.signal import sosfilt
    started = time.perf_counter()
    total, channels = record['duration_seconds']*record['sample_rate_hz'], record['channels']
    sos32 = np.asarray(REFERENCE_SOS, dtype=np.float32)
    sos64 = sos32.astype(np.float64)
    cert_status, verified = 'NOT_RUN', None
    if with_dexted:
        from dexted_dsp import from_sos, certify_cascade, verify_cascade
        rows = from_sos(sos32, precision='float32')
        proof = certify_cascade(rows, 1.0, max_depth=32, max_nodes=5000)
        cert_status = proof['status']  # retain UNKNOWN, never reduce it to mathematical FAIL
        verified = verify_cascade(proof, rows, 1.0) if proof.get('certified') else False
        (output/(record['id']+'.proof.json')).write_text(json.dumps(proof, indent=2)+'\n', encoding='utf-8')
        if cert_status != 'certified' or verified is not True:
            raise RuntimeError(f'{record["id"]}: reference proof did not pass: {cert_status}')
    states = [np.zeros((2, 2, channels), dtype=d) for d in (np.float32, np.float32, np.float64)]
    input_hash, output_hash = hashlib.sha256(), hashlib.sha256()
    peak_in = peak_out = error64 = error_partition = 0.
    energy_in = energy_out = 0.
    byte_count = frame_count = chunks = 0
    waveform = (output/(record['id']+'.f32le')).open('xb') if retain else None
    try:
        for start in range(0, total, chunk_frames):
            x = samples(record, start, min(chunk_frames, total-start))
            raw = x.tobytes(order='C')
            input_hash.update(raw)
            if waveform is not None:
                waveform.write(raw)
            y, states[0] = sosfilt(sos32, x, axis=0, zi=states[0])
            # Same numerical engine, different block split: state-continuity check,
            # NOT an independent mathematical oracle.
            cut = min(127, len(x))
            parts = []
            for part in (x[:cut], x[cut:]):
                if len(part):
                    yy, states[1] = sosfilt(sos32, part, axis=0, zi=states[1])
                    parts.append(yy)
            split = np.concatenate(parts, axis=0)
            ref, states[2] = sosfilt(sos64, x.astype(np.float64), axis=0, zi=states[2])
            if not (np.isfinite(x).all() and np.isfinite(y).all() and np.isfinite(ref).all()
                    and all(np.isfinite(z).all() for z in states)):
                raise AssertionError('nonfinite stream/state')
            error_partition = max(error_partition, float(np.max(np.abs(y-split))))
            error64 = max(error64, float(np.max(np.abs(y.astype(np.float64)-ref))))
            if error_partition != 0. or error64 > 3e-6:
                raise AssertionError('reference-filter numerical regression (not a universal DSP tolerance)')
            output_hash.update(y.astype('<f4', copy=False).tobytes())
            peak_in = max(peak_in, float(np.max(np.abs(x))))
            peak_out = max(peak_out, float(np.max(np.abs(y))))
            energy_in += float(np.sum(x.astype(np.float64)**2))
            energy_out += float(np.sum(y.astype(np.float64)**2))
            byte_count += len(raw)
            frame_count += len(x)
            chunks += 1
    finally:
        if waveform is not None:
            waveform.close()
    if frame_count != total or byte_count != total*channels*4:
        raise AssertionError('truncated or miscounted stream')
    result = {'id': record['id'], 'source_kind': 'synthetic', 'kind': record['kind'],
              'duration_seconds': record['duration_seconds'], 'frames': frame_count,
              'scalar_samples': frame_count*channels, 'input_bytes_processed': byte_count,
              'sample_rate_hz': record['sample_rate_hz'], 'channels': channels,
              'input_sha256': input_hash.hexdigest(), 'output_sha256': output_hash.hexdigest(),
              'waveform_retained': retain, 'chunks': chunks, 'chunk_frames': chunk_frames,
              'numerical_engine': 'scipy.signal.sosfilt; reference filter only',
              'partition_max_abs_error': error_partition, 'float32_vs_float64_max_abs_error': error64,
              'reference_filter_error_threshold': 3e-6, 'input_peak': peak_in, 'output_peak': peak_out,
              'input_rms': math.sqrt(energy_in/(total*channels)),
              'output_rms': math.sqrt(energy_out/(total*channels)),
              'dexted_core_executed': with_dexted, 'certificate_status': cert_status,
              'certificate_verified': verified, 'elapsed_wall_seconds': time.perf_counter()-started,
              'process_lifetime_peak_rss_bytes': process_peak_rss_bytes(), 'status': 'passed'}
    if 'planned_duration_seconds' in record:
        result['planned_duration_seconds'] = record['planned_duration_seconds']
    return result


def run(args) -> int:
    import numpy as np
    import scipy
    manifest = load_manifest(args.manifest)
    rows = choose(manifest, args.profile, args.record)
    if args.profile == 'qualification' and not args.confirm_long_run:
        raise ValueError('qualification requires --confirm-long-run; 76 record-hours, potentially 93 GB')
    positive_integer(args.chunk_frames, 'chunk_frames', 2**20)
    args.out.mkdir(parents=True, exist_ok=False)  # immutable run directory
    results = []
    for record in rows:
        r = run_record(record, args.chunk_frames, args.out, args.retain_waveforms, args.with_dexted)
        results.append(r)
        (args.out/(r['id']+'.json')).write_text(json.dumps(r, indent=2, allow_nan=False)+'\n', encoding='utf-8')
        print(json.dumps({'id': r['id'], 'status': r['status'], 'seconds_of_data': r['duration_seconds'],
                          'seconds_of_execution': round(r['elapsed_wall_seconds'], 3)}), flush=True)
    report = {'schema': 'dexted-dsp/longrun-bootstrap-evidence/v1', 'status': 'passed',
              'notice': 'Synthetic fixture + reference-runtime harness evidence, NOT industrial qualification.',
              'profile': args.profile, 'manifest_sha256': digest(args.manifest), 'runner_sha256': digest(Path(__file__)),
              'record_count': len(results), 'record_hours': sum(r['duration_seconds'] for r in results)/3600,
              'scalar_samples': sum(r['scalar_samples'] for r in results),
              'dexted_core_executed': args.with_dexted,
              'wall_clock_soak_completed': False, 'real_industrial_data_used': False,
              'rss_scope': 'process-lifetime high water includes Python, NumPy, SciPy, hashing and all lanes; not isolated library cost',
              'environment': {'utc': datetime.now(timezone.utc).isoformat(), 'python': sys.version,
                              'numpy': np.__version__, 'scipy': scipy.__version__, 'platform': platform.platform()},
              'records': results}
    (args.out/'summary.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('status', 'profile', 'record_count', 'record_hours', 'scalar_samples', 'dexted_core_executed')}))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    val = sub.add_parser('validate')
    val.add_argument('--manifest', type=Path, default=DEFAULT_MANIFEST)
    runp = sub.add_parser('run')
    runp.add_argument('--manifest', type=Path, default=DEFAULT_MANIFEST)
    runp.add_argument('--profile', choices=('smoke', 'pilot', 'qualification'), default='smoke')
    runp.add_argument('--record', action='append')
    runp.add_argument('--out', type=Path, required=True)
    runp.add_argument('--chunk-frames', type=int, default=65536)
    runp.add_argument('--retain-waveforms', action='store_true')
    runp.add_argument('--with-dexted', action='store_true')
    runp.add_argument('--confirm-long-run', action='store_true')
    args = parser.parse_args()
    try:
        if args.command == 'validate':
            print(json.dumps(inventory(load_manifest(args.manifest)), indent=2))
            return 0
        return run(args)
    except (OSError, ValueError, ImportError, AssertionError, RuntimeError) as exc:
        print(json.dumps({'status': 'failed', 'error': str(exc)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
