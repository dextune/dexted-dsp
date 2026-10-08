# Core hardening implementation record — 2026-10-08

**Base:** main at `be225818a649028716df1e44ca3669f333e38114`.
**Scope:** code+regression work only; this is **not** an industrial release approval.

## Implemented paths

| Path / function | Hardened behavior | Core specifications |
|---|---|---|
| `request.bounded_take`, `model.Biquad.from_coefficients`, `model.from_sos`, `cascade.validate_sections` | Consume at most limit+1 iterable elements; reject oversized sections/rows; own a numeric snapshot; reject nonfinite binary32 rounding | CT-01,03,04; INV-01 |
| `cascade.mul`, `gap_polynomial`, `to_bernstein_scaled`, `split_scaled`, `prove_positive` | Integer growth checks; exact strict positivity; unknown on exhausted node/depth/bit resources | CT-08~13; INV-02,03,05,07,12 |
| `verify_biquad`, `verify_cascade` | Recheck exact represented coefficients and gain; canonical biquad witness; strict cover metadata/shape, depth/index preflight, and independent rational Bernstein coverage | CT-15~18; INV-04,05,10 |
| `envelope.parse_certificate_json`, `verify_serialized_certificate` | Reject overlong payloads, duplicate JSON keys, nonfinite values, trailing garbage, unknown schemas and nested payloads; delegate proof checking to independent consumer | CT-16~19 |
| `gate.CheckResult`, `check_sos` | Typed decision-only result; explicit `verified` property; forbidden bool coercion; proof-byte cap; no deployment permission without external policy/byte/worker validation | CT-20,22; INV-07,10 |
| `native.NativeBiquad.certify`, `NativeCascade.check` | Exact `code==1` success; unexpected return codes raise errors; bounded section inputs | CT-24~26 |

## Compatibility and security

- The original `certify`, `certify_cascade`, `verify_*`, `inspect_*`, C ABI symbol signatures and v1/v2 wire schema names remain.
- New `check_sos` is **not a hard-deadline worker**, cryptographic signature, deployment authorizer, audio runtime, or substitute for a safety case.
- Hashes are input identity checks, **not signatures**. Caller must verify deployed file bytes again before release.
- Existing C++ predicate-only ABI remains unchanged. The new Python entrypoint does not claim native proof export.
- A conservative resource estimate may turn previously positive cases into `unknown`; this is safer than an unproven `certified` but reduces solver coverage.
- The Python facade does not guarantee process RSS/time limits for a blocking iterator or expensive integer arithmetic; a separate supervised process is still required to enforce hard resource budgets.
- Optional gain enclosures remain independent diagnostics and cannot upgrade an unknown proof.

## Evidence requirements still OPEN

- Core 42-case acceptance matrix: new targeted regression tests cover a subset; not all CT IDs are qualified.
- CT-02/12/21/22/32: hostile conversion subprocess timeout, hard RSS controls, atomic deployment TOCTOU and kill/resume.
- CT-27~31: frozen 24-record x 8-filter long-run interface and 192 actual streaming cases / 608 filter-hours.
- CT-33~34: isolated 30-repetition benchmark/RSS evidence, extended 24h/72h soak.
- CT-36: full oracle seed/holdout qualification with statistical unknown-coverage accounting.
- Independent third-party mathematics review, three-host validation, deployment policy approval, CG0–CG4 and upper industrial gates.
- No performance improvement or industrial release completion is claimed based on this record. Benchmark baselines must be measured separately with identical hardware and workload.

## Practical validation

On a revision containing this record, run:

```sh
python -m unittest discover -s tests -v
python -m unittest discover -s tests -p 'test_core_hardening.py' -v
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel 2
ctest --test-dir build --output-on-failure
python tools/native_cascade_differential.py "$(pwd)/build/libdexted_dsp.so"
```

Also require GitHub CI on the exact SHA before promoting a staging revision to `main`.
