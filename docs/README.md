# Dexted DSP — documentation hub

All detailed documentation lives under `docs/`. The [GitHub README](../README.md) is a short landing page; this index is the canonical navigation entry.

## Choose your language

| Language | Full overview | Getting started | Testing | Benchmarks | Mathematics | Provenance | Releases |
|---|---|---|---|---|---|---|---|
| English | [Overview](en/README.md) | [Guide](en/getting-started/USER_GUIDE.md) | [Guide](en/guides/TESTING.md) | [Details](en/benchmarks/BENCHMARKS.md) | [Derivations](en/mathematics/MATHEMATICS.md) | [Sources](en/development/PROVENANCE.md) | [Guide](en/development/RELEASING.md) |
| 한국어 | [개요](ko/README.md) | [설치·사용](ko/getting-started/USER_GUIDE.md) | [테스트](ko/guides/TESTING.md) | [벤치마크](ko/benchmarks/BENCHMARKS.md) | [수학](ko/mathematics/MATHEMATICS.md) | [출처](ko/development/PROVENANCE.md) | [배포](ko/development/RELEASING.md) |
| 简体中文 | [概览](zh-CN/README.md) | [使用](zh-CN/getting-started/USER_GUIDE.md) | [测试](zh-CN/guides/TESTING.md) | [基准测试](zh-CN/benchmarks/BENCHMARKS.md) | [数学](zh-CN/mathematics/MATHEMATICS.md) | [来源](zh-CN/development/PROVENANCE.md) | [发布](zh-CN/development/RELEASING.md) |
| 日本語 | [概要](ja/README.md) | [使い方](ja/getting-started/USER_GUIDE.md) | [テスト](ja/guides/TESTING.md) | [性能評価](ja/benchmarks/BENCHMARKS.md) | [数学](ja/mathematics/MATHEMATICS.md) | [出典](ja/development/PROVENANCE.md) | [リリース](ja/development/RELEASING.md) |

## Shared canonical references

- [API reference and C++/Python contract](reference/README.md)
- [Formal derivations, proof limitations, OpenAI reference](research/README.md)
- [Architecture, changelog, legal notice and contributing](project/README.md)
- [Benchmark raw evidence and source snapshots](../benchmarks/README.md)
- [Validation logs and immutable historical evidence](../validation/README.md)

### Provenance and verification boundary

The runnable exact biquad/cascade predicates use classical mathematical methods. The external [OpenAI math research](research/openai-math/REFERENCES.md) provides an **assumed** Crouzeix theorem for a separate research note; it is not integrated into the published runtime or its benchmarks. Do not represent tests or mathematical notes as third-party certification.

Reference command: run `python tools/check_links.py`, `python tools/check_documentation.py`, and `python -m unittest discover -s tests -v` from the repository root. Benchmark source hashes are not modified by this documentation-only move.
