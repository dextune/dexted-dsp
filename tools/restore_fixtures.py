#!/usr/bin/env python3
"""Restore the archived benchmark inputs and require a byte-identical SHA-256.

No timings are run or replaced. No network request is made. Source checkouts
omit the generated NPZ; distribution bundles may already contain it.
"""
from __future__ import annotations
import hashlib
import importlib.util
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def restore() -> dict:
    target = ROOT/'benchmarks/results/fixtures.npz'
    expected = json.loads((ROOT/'benchmarks/results/benchmark.json').read_text())['fixtures_sha256']
    if target.is_file():
        content = target.read_bytes()
        generated = False
    else:
        import numpy as np
        import scipy
        if (np.__version__, scipy.__version__) != ('2.3.5', '1.17.0'):
            raise ValueError('Install requirements-bench-tested.txt to reconstruct the archived byte-identical fixtures')
        spec = importlib.util.spec_from_file_location('dexted_benchmark_generator', ROOT/'benchmarks/run.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        buffer = io.BytesIO()
        np.savez_compressed(buffer, **module.generate(20261007, 1024))
        content = buffer.getvalue()
        generated = True
    actual = hashlib.sha256(content).hexdigest()
    if actual != expected:
        raise ValueError('Archived fixture SHA-256 mismatch; no replacement was written')
    if generated:
        target.write_bytes(content)
    return {'status':'passed','generated':generated,'rows':4096,'sha256':actual}


if __name__ == '__main__':
    print(json.dumps(restore(), indent=2))
