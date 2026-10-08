<div align="center">

# Dexted DSP

**Exact filter checks. Inspectable evidence.**

Offline verification for fixed digital filters · Python & C++20

[![CI](https://github.com/dextune/dexted-dsp/actions/workflows/ci.yml/badge.svg)](https://github.com/dextune/dexted-dsp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![C++20](https://img.shields.io/badge/C%2B%2B-20-blue.svg)](CMakeLists.txt)
[![Research alpha](https://img.shields.io/badge/status-research%20alpha-orange.svg)](CHANGELOG.md)

[English](README.md) · [한국어](README.ko.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md)

[Documentation](docs/README.md) · [Contributing](CONTRIBUTING.md)

</div>

---

**周波数を数点ずつ調べるのではなく、固定デジタルフィルターが全周波数でゲイン上限を満たすかを厳密に判定します。**

Python · C++20 · CLI · 厳密整数演算 · 再検査可能な証明書 · 再現可能な測定データ

**v0.1.0 · 研究用アルファ。** [dextune/dexted-dsp](https://github.com/dextune/dexted-dsp) で管理する AI 支援の独立プロジェクトです。OpenAI の製品・公式連携・外部監査済み安全認証ツールではありません。本リポジトリのソースからインストールしてください。PyPI 公開を意味しません。

## 現在利用できる機能

実行可能な対象は**固定された実係数の biquad（2 次フィルター）**と、Python 版の**直列カスケード**です。各分母の厳密な安定性と、指定された厳密な全周波数ゲイン上限を検査します。実際の配備精度に係数を変換した後、配備前にオフラインで実行してください。音声再生、フィルター自動最適化、任意のニューラルネットワーク解析、物理的な装置の安全認証は行いません。

動画の各画素に同じ固定時間フィルターを独立に適用する場合には、このモデルを利用できます。ただし、一般的な動画復元ネットワーク全体がこの条件を満たすわけではありません。多倍長整数と動的メモリを使用するため、リアルタイム音声コールバック内では呼び出さないでください。

## インストールと実行

リポジトリを clone し、ソースからインストールします。非公開の間は GitHub のアクセス権が必要です。

```bash
git clone https://github.com/dextune/dexted-dsp.git
cd dexted-dsp
python -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows PowerShell では: .venv\Scripts\Activate.ps1
python -m pip install .
python examples/basic.py
python tools/documentation_smoke.py
```

Python 3.10 以降が必要です。**コア実行部分**に第三者ランタイム依存はありませんが、ソースインストール時にビルドツールがダウンロードされる場合があります。オフライン用 wheel は[公開ガイド](docs/ja/RELEASING.md)に従って先にビルドしてください。`dist/` は Git の追跡対象外です。

```python
from dexted_dsp import Biquad, certify, verify_biquad

f = Biquad.from_coefficients(
    [0.25, 0.0, 0.0, -0.5, 0.0],  # b0, b1, b2, a1, a2; a0 = 1
    precision="float32",
)
report = certify(f, max_gain=1.0)
assert report.certified
assert verify_biquad(report.as_dict(), f, max_gain=1.0)
print(report.status)  # certified
```

`max_gain` は入力する**検査上限**であり、計算された最大ゲインではありません。条件は `<=` ではなく `<` です。係数または上限を変えると、保存済み証明書の入力との対応が失われます。

```bash
python -m dexted_dsp check examples/safe.json --output certificate.json
python -m dexted_dsp verify examples/safe.json certificate.json
python -m dexted_dsp check examples/hidden_peak.json
# 最後のコマンドは終了コード 1 が期待値の否定テストです。
```

終了コードは `0` が認証・再検査成功、`1` が条件不成立・無効な証明書、`2` が入力エラー、`3` が予算不足による**判定保留**です。配備判定では 0 だけを受理してください。インストール後の `dexted-dsp` コマンドも同じ機能です。

## OpenAI の何を参考にしたのか

研究の出発点は [`openai/math` の数学原稿集][OAI-README]です。参照版は更新される main ではなく、コミット **`adc7f1241b42e322a6451854ab7e4b4c146bf78a`** に固定しています。上流 README は、原稿ごとに検証の段階が異なると説明しています。

| 出典または数学的手法 | 本プロジェクトでの役割 | ベンチマークで実行したか |
|---|---|---|
| OpenAI 結果群 325、*A direct proof of the complete Crouzeix inequality*、§1 主定理 [OAI-325] | 行列多項式の誤差と限定的な時変系についての条件付き研究 | **いいえ** |
| OpenAI の厳密 DFT 論文の序論、計算モデルと制約 [OAI-DFT] | 研究範囲の選定。漸近的な厳密演算の結果を実用浮動小数点 FFT の高速化と混同しないための参照 | **いいえ** |
| 古典的な 2 次 Schur/Jury 条件と `cos(omega)` の 2 次式 | 実行される厳密 biquad 判定 | **はい** |
| 古典的な Bernstein 正値性と厳密細分 | Python のカスケード証明書と有理数再検査 | カスケードの例で使用。**C++ 時間グラフには含まれません** |

**測定された高速化は Crouzeix 定理によるものではありません。** OpenAI の証明コードや DSP ソースをランタイムにコピーしていません。一般的な定数 2 の原定理を独立に検証しておらず、`crouzeix_certify()` API も提供していません。OpenAI が原稿を生成した過程と、本プロジェクトの AI 支援による実装過程は別です。

作業の流れは、数学候補の検討 → 理論的仮定と実行手法の分離 → 厳密判定の実装 → 別表現の有理数演算との照合 → C++ への移植 → 強い数値ベースラインとの比較 → 失敗・修正履歴の保持 → パッケージ化・文書化です。証拠との対応は[研究経緯と出典](docs/ja/PROVENANCE.md)にまとめています。

## ベンチマークで測定した内容

以下は**元の v0.1.0 に保存された測定値**です。翻訳の際に有利な実行結果へ差し替えていません。今回の文書改訂ではハッシュと判定を再検査し、小規模な実行確認は別の記録として保存しました。

| 項目 | 記録された設定 |
|---|---|
| 入力 | 合成データ 4 群 × binary32 フィルター 1,024 個 = **4,096 個** |
| 上限・乱数 | binary64 `max_gain=0.9999`、入力シード `20261007`、方式順序シード `932851` |
| 計測 | 9 試行、各計時でネイティブバッチを 4 回実行、`perf_counter_ns` |
| C++ ビルド | GCC 14.2.0、`-O3 -std=c++20 -ffp-contract=off`、fast-math なし |
| ホスト | 共有 Linux x86-64 が AMD EPYC 9V74 と可視論理 CPU 5 個を報告。CPU 固定なし |
| Python 環境 | Python 3.13.5、NumPy 2.3.5、SciPy 1.17.0、記録された描画依存は Matplotlib 3.10.8 |

ネイティブ時間は **µs/フィルター、9 試行の中央値**です。4 方式すべてが入力と分母を検査します。グリッドには事前に温めた三角関数キャッシュと早期終了を認め、キャッシュ構築時間は計時しません。

| 試験群 | 厳密整数判定 | 1,024 点グリッド | 16,384 点グリッド | Float64 代数判定 | グリッド 1,024 / 整数¹ |
| --- | --- | --- | --- | --- | --- |
| 一般フィルター | 0.564106 | 1.686392 | 27.877729 | 0.011137 | 2.989× |
| 高 Q ストレス | 0.599275 | 2.161358 | 33.816509 | 0.012064 | 3.607× |
| ゲイン上限付近 | 0.377707 | 0.932293 | 16.152820 | 0.011086 | 2.468× |
| 不安定な分母 | 0.008509 | 0.006741 | 0.007093 | 0.006717 | 0.792× |

¹ 最終列は**2 つの中央値の比**であり、試行ごとの比の中央値とは異なります。両方の統計量、観測最小・最大、計時対象は[ベンチマーク詳細](docs/ja/BENCHMARKS.md)に記載しています。

![4 方式と 4 試験群の C++ 検査時間](benchmarks/figures/native_latency.svg)

最初の 3 群では整数判定が 1,024 点グリッドより速い一方、不安定な分母の即時拒否では遅くなりました。**Float64 代数判定はさらに高速です。** 丸めによる誤判定があっても、この強い基準を除外していません。数値は配備前の検査時間であり、音声処理速度や音質改善ではありません。

### 正確性と Python 呼び出し費用は別の問題です

高 Q 群の有理数参照判定は合格 539 件、不合格 485 件です。以下は件数であり、実製品の故障率の推定ではありません。

| 方式 | 誤受理 / 参照判定で不合格の 485 件 | 誤棄却 / 参照判定で合格の 539 件 |
| --- | --- | --- |
| 厳密整数判定 | 0 | 0 |
| 1,024 点グリッド | 356 | 0 |
| 16,384 点グリッド | 213 | 0 |
| Float64 代数判定 | 2 | 5 |

他の 3 群では 4 方式すべてに記録上の不一致がありません。誤受理は**数学的条件を満たさない入力を合格させたこと**であり、任意のフィードバック網が必ず発散することまでは意味しません。

![高 Q 群での有理数参照判定との不一致](benchmarks/figures/high_q_correctness.svg)

![呼び出し費用を含む Python API 比較](benchmarks/figures/python_latency.svg)

Python グラフは高 Q フィルター 128 個に対し、インストールされた SciPy の `signal.freqz` を直接呼び出します。この関数は指定周波数で応答を評価するもので、厳密証明書の API ではありません [SCIPY-FREQZ]。Python の個別呼び出し時間と C++ バッチカーネル時間を混ぜて比較しないでください。

![グリッド間にある解析的に既知の狭いピーク](benchmarks/figures/hidden_peak.svg)

隠れたピークの例では `omega=pi/2` でゲインが厳密に 2 です。図はこの代数的事実の説明であり、密な曲線自体が証明ではありません。

### 元データと再現

[JSON・各試行時間](benchmarks/results/benchmark.json) · [CSV 要約](benchmarks/results/summary.csv) · [係数配列](tools/restore_fixtures.py) · [手順・ソースハッシュ](benchmarks/results/protocol.json) · [環境](benchmarks/results/environment.json) · [元の実行ログ](validation/benchmark_run.log)

```bash
python -m pip install '.[bench]'
python -m pip install -r requirements-bench-tested.txt
python tools/restore_fixtures.py
python tools/audit_benchmark.py --recheck-fixtures
# コマンド経路の小規模確認。公開ベンチマークとは別です。
python benchmarks/run.py --n 32 --trials 3 --out validation/my-smoke
# 元データを上書きしない全規模の再計測:
python benchmarks/run.py --n 1024 --trials 9 --seed 20261007 --out validation/my-run
python benchmarks/plot.py --results validation/my-run/benchmark.json --out validation/my-run/figures
```

ネイティブベンチマークは Linux/macOS の GNU/Clang ツール環境を対象とし、Windows では WSL を使用します。図の内部ラベルは共通の英語表記で、各言語のガイドに凡例と読み方を記載しています。

## テストと連携

```bash
python -m unittest discover -s tests -v
python tools/documentation_smoke.py
python examples/cascade.py
# 任意の C++ ビルド: C++20、CMake >=3.20、Boost >=1.74 ヘッダーが必要
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
```

コアには **35 個の unittest メソッド**があり、一部は内部で乱数ケースを検査します。文書スモークテストではさらに **12 シナリオ**を検査します。保存済みベンチマークには 4,096 個の配備係数と別の 2,048 行のビットパターンがあります。これらは異なる検査層で、外部機関による独立監査の回数ではありません。期待される拒否・予算不足・wheel 検査・トラブル対処は[テストガイド](docs/ja/TESTING.md)を参照してください。

## 文書と制約

| 文書 | 内容 |
|---|---|
| [利用ガイド](docs/ja/USER_GUIDE.md) | インストール、入力意味、Python/SOS/CLI、予算、C++、CI、対処 |
| [テストガイド](docs/ja/TESTING.md) | 期待出力、合格・拒否・保留、回帰検査と再現 |
| [ベンチマーク詳細](docs/ja/BENCHMARKS.md) | 分布、比較方式、計時範囲、元データの項目、限界 |
| [研究経緯と出典](docs/ja/PROVENANCE.md) | OpenAI の参照位置、依存境界、開発の証拠 |
| [数学ガイド](docs/ja/MATHEMATICS.md) | 導出、証明書の意味、条件付き拡張 |
| [API 契約](docs/API.md) / [公開手順](docs/ja/RELEASING.md) | 低レベル仕様とリポジトリ・パッケージ公開 |

証明書は与えられた配備係数による理想的な固定線形系だけを対象にします。実行中の丸め・オーバーフロー・リミットサイクル、任意変調、フィードバック構造、AI 動作、聴覚保護、PSNR/STOI/PESQ は保証しません。`unknown` は配備を拒否してください。JSON 証明書は電子署名でも、悪意ある入力に対するサンドボックスでもありません。

[MIT ライセンス](LICENSE) · [NOTICE](NOTICE.md) · [セキュリティ](SECURITY.md) · [Issues](https://github.com/dextune/dexted-dsp/issues)。新数学の発明、外部独立監査、物理機器の安全認証を主張しません。CI バッジは GitHub Actions の状態を表示し、[ローカル検証記録](validation/rebrand/)とは区別します。

[OAI-README]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/README.md
[OAI-325]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex
[OAI-DFT]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex
[CP-2017]: https://arxiv.org/abs/1702.00668
[SCIPY-FREQZ]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html
[PYPA]: https://packaging.python.org/en/latest/tutorials/packaging-projects/

**測定の由来。** 表の数値は旧研究名 **CertifiedDSP** で記録しました。Dexted DSP への変更は名称・名前空間・CLI・証明書スキーマのみで、代数的判定式は変わりません。元の測定値と測定時のソースを保持しています。[移行と再現](docs/REBRANDING.md) · [ソース対応表](benchmarks/results/rebrand-map.json)。

**ソースチェックアウトのデータ：** NPZ は Git に保存せず必要時に再構築します。固定したベンチマーク依存関係を入れ、`python tools/restore_fixtures.py` を実行してください。元の SHA-256 との一致が必須で、測定値は置き換えません。

<!-- benchmark-sha256: 0332cbc6a22ebf2da482a043b3f206ae175bcab5d71f640417c96c46c7ac99a0 -->
