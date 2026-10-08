# Documentation / 문서 / 文档 / ドキュメント

The executable library uses classical fixed-filter mathematics. The OpenAI Crouzeix
reference is explicitly conditional and is not used in measured runtime code.

| Language | Project README | Provenance / OpenAI | Benchmarks | Usage | Testing | Mathematics |
|---|---|---|---|---|---|---|
| English | [README](../README.md) | [Sources and process](en/PROVENANCE.md) | [Methodology](en/BENCHMARKS.md) | [User guide](en/USER_GUIDE.md) | [Test guide](en/TESTING.md) | [Derivations](en/MATHEMATICS.md) |
| 한국어 | [README](../README.ko.md) | [출처와 연구 과정](ko/PROVENANCE.md) | [비교·측정 방법](ko/BENCHMARKS.md) | [사용 가이드](ko/USER_GUIDE.md) | [테스트 가이드](ko/TESTING.md) | [수학적 유도](ko/MATHEMATICS.md) |
| 简体中文 | [README](../README.zh-CN.md) | [来源与研究过程](zh-CN/PROVENANCE.md) | [基准测试](zh-CN/BENCHMARKS.md) | [使用指南](zh-CN/USER_GUIDE.md) | [测试指南](zh-CN/TESTING.md) | [数学推导](zh-CN/MATHEMATICS.md) |
| 日本語 | [README](../README.ja.md) | [出典と研究過程](ja/PROVENANCE.md) | [ベンチマーク](ja/BENCHMARKS.md) | [利用ガイド](ja/USER_GUIDE.md) | [テストガイド](ja/TESTING.md) | [数学的導出](ja/MATHEMATICS.md) |

Machine-readable evidence: [sources and pinned revisions](provenance/sources.json),
[raw timings](../benchmarks/results/benchmark.json),
[CSV summary](../benchmarks/results/summary.csv),
[documentation-refresh validation](../validation/docs_refresh/summary.json).

## Translation policy / 번역 원칙 / 翻译原则 / 翻訳方針

- Commands, API symbols, status strings, paths and result values are identical across languages.
- 명령·API·상태 문자열·경로·측정값은 번역하지 않으며 언어별 수치를 변경하지 않습니다.
- 命令、API、状态字符串、路径和测量数据保持一致，不按语言改写结果。
- コマンド、API、状態文字列、パス、測定値は全言語で一致させます。

No independent professional-language review is claimed. Figure labels are shared in
English; each benchmark guide explains the legends and caveats in its own language.
The low-level [API reference](API.md) is shared. New contributors should update all
four primary language sets when changing behavior or published numbers.

## Release guides / 공개 가이드 / 发布指南 / 公開ガイド

[English](en/RELEASING.md) · [한국어](ko/RELEASING.md) · [简体中文](zh-CN/RELEASING.md) · [日本語](ja/RELEASING.md)
