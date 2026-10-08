# Validation evidence (historical)

These records document earlier **local** checks and must not be confused with GitHub Actions or independent mathematical certification. Existing log/JSON contents are preserved byte-for-byte across this reorganization.

| Dataset | Location | What it covers |
|---|---|---|
| Initial v0.1.0 records | [runs/v0.1.0/](runs/v0.1.0/) | Original Python/C++ checks, generated wheel, CMake integration, benchmark run, sanitizer and earlier comparison logs |
| Documentation refresh | [docs_refresh/](docs_refresh/) | Four-language consistency, packaging and re-run documentation checks |
| Rebranding review | [rebrand/](rebrand/) | Dexted DSP renaming, package rebuild and regression records |

Key original run: [benchmark_run.log](runs/v0.1.0/benchmark_run.log) · [original summary](runs/v0.1.0/summary.json) · [documentation summary](docs_refresh/summary.json) · [rebrand tests](rebrand/core-tests-final.log).

**Do not overwrite the original benchmark artifacts.** New measurements should be written into a new, clearly dated directory and identified as a separate experiment. The authoritative frozen timing table is [benchmarks/results/benchmark.json](../benchmarks/results/benchmark.json).
