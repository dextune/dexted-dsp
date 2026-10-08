# Local validation evidence

`summary.json` records the executed checks and unexecuted claims separately.
`installed_wheel_tests.log` is from a fresh venv, offline wheel installation,
then `python -I -m unittest` against the installed package (not PYTHONPATH=src).
`native_wrapper.log` tests 256 calls through the actually built shared library.
`cmake_consumer.log` is from a separate CMake project using an installed package.
`sdist_rebuild.log` records an offline wheel build from the included source archive,
using the existing build backend on the host.

`benchmark_run.log` corresponds to `benchmarks/results/benchmark.json` and its
final source hashes. Earlier review runs are retained rather than silently removed.
GCC/Boost optimizer warnings are visible in the logs. `sanitizers.log` covers only
the exercised native tests; a successful sanitizer run is not a general memory-safety proof.

These are local automated checks, not a hosted GitHub CI run, external review,
proof-assistant certification or a perceptual-quality evaluation.
