# 研究経緯と OpenAI の参照範囲

[English](../../en/development/PROVENANCE.md) · [한국어](../../ko/development/PROVENANCE.md) · [简体中文](../../zh-CN/development/PROVENANCE.md) · [日本語](PROVENANCE.md)

[Dexted DSP](../README.md)

## 1. 「OpenAI を参考にした」の 3 つの意味

**研究資料:** [`openai/math` の原稿集][OAI-README]を起点に信号処理への応用を検討しました。**条件付き定理:** 特定の Crouzeix 原稿を別の研究文書の仮定にしました。**AI 支援による実装:** 対話的な研究・プログラミングを通じてこのリポジトリを構成しました。これらは別であり、ランタイムが OpenAI 製、OpenAI 監査済み、または測定した最適化が新しい OpenAI 定理であることを意味しません。

上流は原稿ごとに検証段階が異なると記しています。そこに原稿が存在するだけでは、下流の DSP ソフトウェアを形式検証済みと表示できません [OAI-README]。

## 2. 固定した出典と位置

| ID | 原文と参照位置 | 用途 |
|---|---|---|
| OAI-README | コミット `adc7f1241b42e322a6451854ab7e4b4c146bf78a` の `README.md` | 原稿集の出自と検証上の注意 |
| OAI-325 | *A direct proof of the complete Crouzeix inequality*、2026-09-26、`build/main.tex` §1 の `thm:main`、`W(A)` と `P[A]` の定義 | 行列値多項式の完全型定数 2 不等式を条件付きで使用 |
| OAI-DFT | *An explicit power saving for the exact discrete Fourier transform*、2026-09-25、`build/sections/introduction.tex` の計算モデルと `cor:decimal` 直後の注意 | 範囲選定。浮動小数点 FFT の実装・速度測定では未使用 |

固定 URL と Git blob ハッシュは [sources.json](../../research/provenance/sources.json)に記録しています。LaTeX 原文の定理を確認しており、Lean カーネルは実行していません。日付は参照した原稿のもので、その後の最新改訂を確認したという主張ではありません。

[OpenAI 主定理の原文][OAI-325] · [OpenAI DFT の計算モデルと制約][OAI-DFT]

採用した仮定は次です。

$$\|P[A]\|_2\le 2\max_{z\in W(A)}\|P(z)\|_2,\qquad P[A]=\sum_k A^k\otimes B_k.$$

チャネル係数行列が可換とは限らないため、**行列値・完全型**であることが重要です。比較対象は Crouzeix–Palencia (2017) の完全型定数 `1+sqrt(2)` です [CP-2017]。一般の定数 2 の原証明を独立に検証したとは主張していません。

## 3. 実行コードの数学的依存

| 構成要素 | 数学的基礎 | 状態 |
|---|---|---|
| `src/dexted_dsp/biquad.py`、`cpp/include/dexted_dsp/biquad.hpp` | 基本 Schur/Jury 条件、2 次式の正値性、厳密な 2 進有理数演算 | 実行可能。OpenAI の新定理に非依存 |
| `src/dexted_dsp/cascade.py` | 絶対値 2 乗多項式の積、Bernstein 正値性・細分 | Python 実行可能。予算付きの十分条件認証 |
| `reference.py`、`verify.py` | 別表現の有理数演算、区間被覆の確認 | 再検査であり外部機関認証ではない |
| `benchmarks/kernels.cpp` | 整数判定、応答サンプリング、float64 代数基準 | 測定対象。Crouzeix 依存なし |
| [条件付き研究文書](../../research/proofs/crouzeix.md) | 一般の基底行列について OAI-325 を仮定 | 文書のみ。製品 API なし |

古典的方法の発明は主張しません。配備値の契約、整数判定、確認可能な証明書、別表現の再検査器、API、再現可能な比較が実装上の貢献です。

## 4. 開発の流れと確認可能な成果物

以下は公開できる成果物に基づく説明であり、記録のない「無限最適化」の実行回数を主張するものではありません。

| 段階 | 決定・実装 | この版にある証拠 |
|---|---|---|
| 範囲選定 | 原稿と信号処理のつながりを検討し、漸近理論と配備可能な方法を分離 | 固定出典リスト、本書 |
| 仮定の隔離 | 一般 Crouzeix 拡張を条件付き文書とし、エンジンから除外 | `docs/research/proofs/crouzeix.md`、コード依存関係 |
| 問題設定 | 固定実係数 2 次節、明示した配備精度、厳密ゲイン上限 | `model.py`、数学文書 |
| 厳密判定 | 2 進有理数を整数化し、安定性、端点、必要な内部最小点を検査 | `biquad.py`、ネイティブヘッダー |
| カスケード拡張 | 周波数補償を保った全体多項式の正値性を認証 | `cascade.py`、`verify.py` |
| 別表現との対照 | `Fraction` 比較、期待入力との対応、改ざん・保留の拒否 | `tests/test_dexted_dsp.py` |
| 公平性の検討 | 高速 float64 基準を保持、グリッドを予熱、早期終了・入力検査を揃える | `run.py`、`kernels.cpp`、`protocol.json` |
| 中間結果の保持 | 都合のよい実行だけを選ばず、レビュー・入力検査の前後を保存 | `validation/runs/v0.1.0/benchmark_before_review*`、`benchmark_before_input_validation*` |
| パッケージ化 | Python/C++/CLI、インストール検査、ローカルログ | 元の `validation/runs/v0.1.0/summary.json` とビルドログ |
| 文書改訂 | 4 言語、出典追跡、保存測定の監査、例の再実行、小規模ベンチ確認 | `validation/docs_refresh/`、測定ソースハッシュ不変 |

以前のアーカイブのハッシュは [sources.json](../../research/provenance/sources.json)にあります。過去の対話に含まれる別の性能値・メディア実験・旧ベンチマークを**現在の結果に繰り上げていません**。README の数値は `benchmarks/results/benchmark.json` のみから導出しています。

## 5. 条件付き拡張が意味するもの

OAI-325 を仮定すると、独立テンソル軸のうち非正規軸 `r` 個の係数は `2^r`、正規軸は 1 です。共通の固定基底でチャネル多項式だけが変わる場合、積の上界は `(2q)^T` ではなく `2 q^T` です。相対状態摂動 `epsilon` を加えると、十分な減衰条件 `q+2 epsilon<1` が得られます。

同じ議論で定数 `1+sqrt(2)` を使う場合と比較して、十分条件としての摂動半径は `(1+sqrt(2))/2-1`、約 **20.71%** 拡大します。これは 2 つの十分条件の代数比較であり、実測音質・画質、真の最大ロバスト性、任意の時変系の認証ではありません。詳細は[研究文書](../../research/proofs/crouzeix.md)にあります。

## 6. 帰属・再利用・検証の境界

OpenAI/ADAC の実装、原稿ソース、第三者メディア、重み、秘密情報を同梱していません。参照リンクは推奨・提携・保証を意味しません。以前の実装の MIT 表記を [LICENSE](../../../LICENSE) と [NOTICE](../../legal/NOTICE.md)に保持しています。Boost は外部ビルド依存、NumPy/SciPy/Matplotlib は任意の測定ツールです。

一般 Crouzeix 原証明、すべてのコンパイラー最適化の正しさ、物理装置の挙動を独立監査していません。条件付き研究文書を取り除いても、厳密 biquad/カスケードの実行コードと測定値の数学的根拠は変わりません。

[OAI-README]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/README.md
[OAI-325]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex
[OAI-DFT]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex
[CP-2017]: https://arxiv.org/abs/1702.00668
[SCIPY-FREQZ]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html
[PYPA]: https://packaging.python.org/en/latest/tutorials/packaging-projects/
