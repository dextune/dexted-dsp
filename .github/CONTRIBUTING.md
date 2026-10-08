# Contributing

Install with `python -m pip install '.[dev,bench]'`. Run Python tests, CMake/CTest
and `python tools/check_links.py` before proposing a change.

Correctness changes need an explicit statement of input assumptions, a derivation,
regression cases at strict equality, and a comparison with the exact-rational path.
Never turn UNKNOWN into a success. Never label a gain-threshold rejection as general
closed-loop instability. Report invalid input separately from mathematical failure.

Performance changes must retain baselines, fixed inputs, all repetitions and failures.
Do not compare a Python loop against native code and claim an algorithmic speedup
without a matched-language comparison. Keep source/fixture hashes with measurements.

Math notes derived from unverified source theorems must remain marked conditional.
Do not commit credentials, user media, third-party source without its license, generated
native binaries, or machine-specific build folders. The original MIT notice is retained.

This is AI-assisted research software. Human review, independent implementations and
proof-assistant verification are encouraged; current tests are not an external audit.
