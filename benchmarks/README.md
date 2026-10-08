# Benchmark reports / 벤치마크 / 基准测试 / ベンチマーク

[English](../docs/en/BENCHMARKS.md) · [한국어](../docs/ko/BENCHMARKS.md) · [简体中文](../docs/zh-CN/BENCHMARKS.md) · [日本語](../docs/ja/BENCHMARKS.md)

The four reports include distributions, exact comparator implementations, all repeat
statistics, excluded costs, input precision, confusion counts, host caveats and full
reproduction commands. Numbers refer to the unchanged original v0.1.0 run.

[Raw result JSON](results/benchmark.json) · [CSV summary](results/summary.csv) ·
[Exact binary32 fixtures](../tools/restore_fixtures.py) · [Recorded protocol](results/protocol.json) ·
[Environment](results/environment.json) · [Original run log](../validation/benchmark_run.log)

```bash
python -m pip install '.[bench]'
python -m pip install -r requirements-bench-tested.txt
python tools/restore_fixtures.py
python tools/audit_benchmark.py --recheck-fixtures
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python benchmarks/run.py --out validation/my-run
python benchmarks/plot.py --results validation/my-run/benchmark.json --out validation/my-run/figures
```

Use a separate output directory. Do not overwrite old timing evidence or select only
favorable repeats. The C++ grid/algebra comparators are project-local kernels; the
Python SciPy comparison calls `signal.freqz`. There is no ADAC end-to-end,
python-control/SLICOT, perceptual-quality or Crouzeix-runtime benchmark.

Native batch overhead and Python per-call overhead are different experiments.
Python filter objects are created before timing; certificate allocation and Python
calls/loops remain inside. Whiskers are observed min/max, not confidence intervals.
