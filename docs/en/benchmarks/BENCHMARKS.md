# Benchmark methodology, results and reproduction

[English](BENCHMARKS.md) · [한국어](../../ko/benchmarks/BENCHMARKS.md) · [简体中文](../../zh-CN/benchmarks/BENCHMARKS.md) · [日本語](../../ja/benchmarks/BENCHMARKS.md)

[Dexted DSP](../../../README.md)

## 1. Question and provenance

The experiment asks: **how long do these implementations take to check a strict biquad gain condition, and which numerical methods disagree with exact rational arithmetic on constructed inputs?** It does not test speech enhancement, video restoration, FFT speed, or OpenAI's Crouzeix theorem.

All published tables below are derived from [benchmark.json](../../../benchmarks/results/benchmark.json). The data remain the original v0.1.0 run, with a timestamp recorded in [environment.json](../../../benchmarks/results/environment.json): `2026-10-07T14:04:45.884162+00:00`. The documentation refresh audits the archived data and runs a **separate** small smoke test. It does not replace them with a faster run.

## 2. Exact predicate and comparator implementations

The tested conjunction is: the real monic denominator `z²+a1 z+a2` is strictly Schur stable, **and** `sup |H(exp(i omega))| < gamma`, with binary64 `gamma=0.9999`. Inputs are stored as binary32, then promoted without changing their represented values. Equality is rejected.

| Method key | Implementation | Certification semantics |
|---|---|---|
| `integer` | Shipped C++ header; integer coefficient decoding, Jury checks, exact quadratic signs | Exact for supplied coefficient values and documented model |
| `grid1024` | Benchmark's own uniform inclusive `[0,pi]` grid; complex-double response; cached trig values | Samples only; not a continuum certificate |
| `grid16384` | Same implementation with 16,384 frequencies | Denser sampling still is not a proof |
| `float64_algebraic` | Same Jury/quadratic idea evaluated in binary64, no interval arithmetic | Strong, very fast baseline; signs can change through cancellation |
| `python_integer_api` | Actual Python public API | Includes certificate construction and per-call Python work |
| `fraction_reference` | Separate rational expression in `reference.py` | Reference decision, not external validation |
| `scipy_freqz1024` | Actual installed SciPy `signal.freqz`, plus denominator check and thresholding | Python response-sampling baseline, not a native kernel |

SciPy documents `freqz` as frequency-response evaluation [SCIPY-FREQZ]. The native grid code does **not** copy SciPy or ADAC code, and this release does not benchmark ADAC end-to-end, SLICOT, MATLAB, or all H-infinity solvers.

## 3. Dataset generation and precision

Default NumPy RNG seed: **20261007**. `generate()` in [run.py](../../../benchmarks/run.py) creates 1,024 rows per family, then casts each complete coefficient array to contiguous binary32. All families are synthetic, with no real recordings or product-frequency sampling.

| Family | Generation before final binary32 conversion |
|---|---|
| Ordinary | Pole radius uniform in `[0.02,0.995)`; angle in `[0.02,pi-0.02)`; 3 numerator coefficients normal with mean 0, SD 0.25 |
| High-Q | `scipy.signal.iirpeak(f,Q)` with `f` uniform `[0.005,0.995)`, `Q=10^U`, `U` uniform `[2,6)`; numerator multiplied by `10^V`, `V` uniform `[-0.4,0.4)` |
| Near threshold | First-order section embedded in a biquad; pole `r` uniform `[0.02,0.99)`; peak `1+U`, `U` uniform `[-0.0005,0.0005)` |
| Unstable denominator | Conjugate-pole radius uniform `[1.00001,1.3)`; same angle range; normal numerators with SD 0.1 |

| Family | Filters | Exact passes | Exact failures |
| --- | --- | --- | --- |
| Ordinary filters | 1024 | 611 | 413 |
| High-Q stress | 1024 | 539 | 485 |
| Near gain threshold | 1024 | 431 | 593 |
| Unstable denominators | 1024 | 0 | 1024 |

Truth is recomputed with `Fraction`, not a finer grid. Python integer and native integer predicates must agree with that reference before timing is accepted. The benchmark adds **2,048 independent random binary32 bit-pattern rows**, seed `20261107`, at threshold 1.0; invalid inputs are expected to return an error. These rows are a port/decoding check, not a fifth timing family.

The first **128 high-Q rows** are reused for the Python API comparison. They are not an independent held-out dataset. The seed was fixed for reproducibility; no claim of preregistration or representative prevalence is made.

## 4. Timing boundary and fairness

All native predicates are compiled together with GCC 14.2.0 using `-O3 -std=c++20 -shared -fPIC -ffp-contract=off`; no fast-math. For each of nine trials, method order is shuffled using seed **932851**. Each method is called once immediately before timing to warm the appropriate grid cache, then four whole batches are timed.

$$t_{\text{filter},\mu s}=\frac{t_{\text{elapsed},ns}}{1024\cdot4\cdot1000}.$$

The timer is `time.perf_counter_ns`. Native time includes amortized ctypes call overhead, output writes, input checks and denominator checks. It excludes fixture generation, reference computation, correctness comparison and grid-cache construction. Grid rejection exits early and compares squared magnitudes without square roots/division.

Python timing uses a separate per-filter loop, cached omega vector and warm-up on four models. Filter objects are constructed **before** its timer; actual function-call, certificate-object construction for the exact API, loop and result-list costs are included. SciPy evaluates the full response vector; this is not an identical operation count to the native early-exit kernel. Read these two experiments separately.

The host reports AMD EPYC 9V74, Linux x86-64, 5 visible logical CPUs, Python 3.13.5, NumPy 2.3.5 and SciPy 1.17.0. `OMP_NUM_THREADS=1` and `OPENBLAS_NUM_THREADS=1`; MKL was unset. There was **no CPU affinity pinning**, controlled frequency or dedicated machine. Observed timings are descriptive, not portable guarantees.

## 5. Native results and statistics

All values below are **µs/filter**. Bars are medians; whiskers are observed minimum/maximum across the nine trials, **not confidence intervals**.

| Family | Exact integer | Grid 1,024 | Grid 16,384 | Float64 algebraic | Grid 1,024 / exact¹ |
| --- | --- | --- | --- | --- | --- |
| Ordinary filters | 0.564106 | 1.686392 | 27.877729 | 0.011137 | 2.989× |
| High-Q stress | 0.599275 | 2.161358 | 33.816509 | 0.012064 | 3.607× |
| Near gain threshold | 0.377707 | 0.932293 | 16.152820 | 0.011086 | 2.468× |
| Unstable denominators | 0.008509 | 0.006741 | 0.007093 | 0.006717 | 0.792× |

¹ Main-table speed ratio is `median(grid times) / median(exact times)`. The JSON also stores the different statistic `median(grid_i / exact_i)`:

| Family | Median(grid / exact) per paired trial |
| --- | --- |
| Ordinary filters | 3.037857× |
| High-Q stress | 3.502723× |
| Near gain threshold | 2.433858× |
| Unstable denominators | 0.786818× |

Observed timing ranges:

| Family | Exact integer | Grid 1,024 | Grid 16,384 | Float64 algebraic |
| --- | --- | --- | --- | --- |
| Ordinary filters | 0.538766 – 0.621713 | 1.570972 – 1.937667 | 26.413858 – 29.532372 | 0.010687 – 0.012078 |
| High-Q stress | 0.570299 – 0.719463 | 2.028531 – 4.190899 | 32.702964 – 41.433221 | 0.011120 – 0.015795 |
| Near gain threshold | 0.360094 – 0.428116 | 0.876417 – 0.980895 | 14.860312 – 17.181955 | 0.010205 – 0.015665 |
| Unstable denominators | 0.008354 – 0.008915 | 0.006572 – 0.007166 | 0.006672 – 0.010472 | 0.006342 – 0.008800 |

![Native C++ latency](../../../benchmarks/figures/native_latency.svg)

The three first families favor exact integers over the 1,024-point sampling kernel. Immediate unstable-denominator rejection favors the numeric kernel instead. Float64 algebra is faster than exact integers throughout; the tradeoff is exactness near cancellation, not universal speed leadership. There is no speed-based pass gate in CI and no assumption that every rerun must be faster.

## 6. Accuracy: define the denominator of every claim

For high-Q data, `false_accepts` means the method returns 1 when the exact conjunction is false; `false_rejects` means it returns 0 when the conjunction is true. There are **485 reference failures** and **539 reference passes**:

| Method | False accepts / 485 reference failures | False rejects / 539 reference passes |
| --- | --- | --- |
| Exact integer | 0 | 0 |
| Grid 1,024 | 356 | 0 |
| Grid 16,384 | 213 | 0 |
| Float64 algebraic | 2 | 5 |

These are counts over a constructed stress family. For example, 356 false accepts are **not 356%**, and dividing by all 1,024 inputs answers a different question from dividing by the 485 actual failures. No product-risk prevalence is inferred. Other families record zero disagreements for all four methods. Negative return codes are stored separately as `invalid_or_error`, and are not accepted.

![High-Q incorrect decisions](../../../benchmarks/figures/high_q_correctness.svg)

The reference is another implementation in the same project; agreement is useful regression evidence, not an independent mathematical proof or institutional audit. The mathematical derivation explains why exact signs suffice. A dense sampled comparison alone could not establish that.

## 7. Python results, cascade demo and hidden peak

| Python-level method | Median µs/filter |
| --- | --- |
| python_integer_api | 7.811008 |
| fraction_reference | 63.969969 |
| scipy_freqz1024 | 71.832703 |

![Python API timings](../../../benchmarks/figures/python_latency.svg)

Python results cover 128 high-Q rows, nine trials, and a different timing scope from C++. They must not be turned into a cross-language algorithm speed claim.

The saved `cascade_demo` has two stable sections whose total transfer is exactly **0.75**. Each section fails an individual gain-1 test; joint certification passes and its cover is rationally rechecked. This is a correctness demonstration, not a cascade performance study. The measured native bar chart does not contain SOS-cascade timing.

![Hidden peak example](../../../benchmarks/figures/hidden_peak.svg)

For `alpha=2^-14`, `H(z)=alpha(1-z^-2)/(1+(1-alpha)z^-2)` has magnitude 2 at `omega=pi/2`. The 1,024-point inclusive grid has no point exactly at pi/2. The plot illustrates a known analytic value; a sampled curve cannot certify a global maximum.

## 8. Artifact map and JSON field guide

| File or field | Meaning |
|---|---|
| `benchmark.json → families.NAME.median_us.METHOD` | Recorded median for the selected family/method |
| `families.NAME.raw_us_per_filter.METHOD` | All nine per-filter timings, trial order retained |
| `families.NAME.correctness.METHOD` | False accepts, false rejects, invalid/error counts |
| `families.NAME.exact_pass` | Number satisfying the exact conjunction |
| `paired_grid1024_over_integer` | Median of per-trial ratios, not ratio of medians |
| `python_high_q` | Separate API experiment; number of rows and all raw repetitions |
| `native_bit_patterns` | Separate native decoding/invalid-input agreement check |
| [fixtures.npz](../../../tools/restore_fixtures.py) | Exact saved binary32 arrays; load with `allow_pickle=False` |
| [protocol.json](../../../benchmarks/results/protocol.json) | Seeds, counts, compiler command, 12 code-file SHA-256 values |
| [environment.json](../../../benchmarks/results/environment.json) | Host and installed versions at the recorded run |
| [summary.csv](../../../benchmarks/results/summary.csv) | Derived export of medians, ranges and counts; no new measurement |
| [validation logs](../../../validation/README.md) | Original build/test history; earlier review versions retained |

## 9. Reproduce without overwriting the baseline

Install `.[bench]` in the project environment. `benchmarks/requirements-bench-tested.txt` records the historical versions; on a different Python version use compatible optional dependencies and record that difference.

```bash
python tools/audit_benchmark.py
python tools/audit_benchmark.py --recheck-fixtures
python benchmarks/run.py --n 32 --trials 3 --out validation/my-smoke
```

Full local measurement on Linux/macOS:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python benchmarks/run.py \
  --n 1024 --trials 9 --seed 20261007 --out validation/my-run
python benchmarks/plot.py --results validation/my-run/benchmark.json \
  --out validation/my-run/figures
python tools/audit_benchmark.py --results validation/my-run/benchmark.json --recheck-fixtures
```

On Windows run the native benchmark in WSL. The default `run.py` output overwrites `benchmarks/results`, so use `--out` during review. The source audit intentionally fails when measured source files change; rerun the benchmark for changed algorithms, and do not simply edit the recorded hashes.

Dependencies and platform details can change generated arrays and timings even with the same seed. To audit the original values, use the **saved NPZ**, not merely regenerated coefficients. NPZ container bytes may also differ after repacking without array changes; the audit verifies the distributed archive bytes.

## 10. Review limits

A GCC 14.2/Boost inlining warning is preserved in `validation/runs/v0.1.0/benchmark_run.log`; it was not suppressed. Historical sanitizer tests passed on exercised cases, not all possible inputs. No claim is made about general high-order/MIMO norm solvers, end-to-end ADAC, real-time throughput, sound/image quality, runtime arithmetic safety or source-theorem verification. The separate `validation/docs_refresh/benchmark_smoke` is command-path validation only, not the benchmark behind the README charts.

[OAI-README]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/README.md
[OAI-325]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex
[OAI-DFT]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex
[CP-2017]: https://arxiv.org/abs/1702.00668
[SCIPY-FREQZ]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html
[PYPA]: https://packaging.python.org/en/latest/tutorials/packaging-projects/

<!-- benchmark-sha256: 0332cbc6a22ebf2da482a043b3f206ae175bcab5d71f640417c96c46c7ac99a0 -->


**Measurement provenance.** These numbers were recorded under the former research name **CertifiedDSP**. The Dexted DSP rename changes names, namespaces, CLI and certificate schemas—not the algebraic predicates. The original measurements and benchmarked source snapshots are retained. [Migration and reproducibility](../../project/REBRANDING.md) · [Source mapping](../../../benchmarks/results/rebrand-map.json).


**Source checkout data:** the NPZ is generated on demand, not stored in Git. Install the pinned benchmark requirements and run `python tools/restore_fixtures.py`. Reconstruction must match the original SHA-256; no measurement is replaced.
