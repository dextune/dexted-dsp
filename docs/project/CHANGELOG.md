# Changelog

## Unreleased — 9.5-plan implementation

See [the source implementation changelog](HOOK_CHANGELOG.md). Historical v0.1.0 benchmarks remain frozen and do not measure this unreleased code revision.

## 0.1.0 — Dexted DSP source import

- Adopt Dexted DSP as the maintained project name at `dextune/dexted-dsp`.
- Rename the Python distribution/import, CLI, CMake package, C++ namespace and C symbols.
- Give the four-language READMEs a repository-first landing page and real project links.
- Retain measured benchmark data verbatim and archive the corresponding original source.
- Recheck all 4,096 saved fixtures after the rename; no algebraic algorithm change.
- Keep general Crouzeix extensions conditional and out of the runtime.


## 0.1.0 documentation revision 1 — 2026-10-07

- English default README plus complete Korean, Simplified Chinese and Japanese sets.
- Per-language provenance, benchmarks, usage, testing and mathematical derivations.
- Pinned OpenAI sources; explicit separation of classical runtime and conditional extensions.
- Raw-data-derived CSV, benchmark artifact audit, 12 runnable documentation checks.
- Original runtime source hashes and published timing artifacts retained unchanged.
- Rebuilt unpublished wheel/sdist README metadata; version remains 0.1.0.
- Local validation evidence kept separately in `validation/docs_refresh/`.


## 0.1.0 — 2026-10-07

Research alpha prepared for publication, not uploaded to PyPI or GitHub.

- Exact integer strict-gain decision for fixed real biquads, Python and C++20.
- Explicit binary32 coefficient conversion and SciPy SOS-layout input helper.
- Integer Bernstein cascade certificates with separately expressed rational rechecking.
- JSON CLI, fail-closed exit codes, type annotations, optional C ABI/ctypes loader.
- Elementary derivations and a separate conditional Crouzeix research note.
- Re-executed native and Python benchmarks, raw timings and source hashes.
- Unit tests, native tests, examples, packaging and CI definitions.

Not included: arbitrary graph parsing, automatic filter repair, Crouzeix runtime
certification, GPU/WASM, real-time audio processing, runtime-roundoff proof or perceptual-quality evaluation.
