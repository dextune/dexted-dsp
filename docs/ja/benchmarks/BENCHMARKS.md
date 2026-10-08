# ベンチマークの方法・結果・再現手順

[English](../../en/benchmarks/BENCHMARKS.md) · [한국어](../../ko/benchmarks/BENCHMARKS.md) · [简体中文](../../zh-CN/benchmarks/BENCHMARKS.md) · [日本語](BENCHMARKS.md)

[Dexted DSP](../README.md)

## 1. 問いとデータの出所

実験の問いは、**各実装の厳密な biquad ゲイン条件の検査時間と、構成した入力で数値的方法が厳密有理数判定と異なるかどうか**です。音声強調、動画復元、FFT 高速化、OpenAI Crouzeix 定理を試験しているわけではありません。

表は [benchmark.json](../../../benchmarks/results/benchmark.json)から導出しています。元の v0.1.0 の測定で、[environment.json](../../../benchmarks/results/environment.json)の記録時刻は `2026-10-07T14:04:45.884162+00:00` です。文書改訂では保存資料を監査し、**別の**小規模確認を実行しました。速い結果への置換はしていません。

## 2. 判定対象と比較方式

検査するのは、実モニック分母 `z²+a1 z+a2` が厳密 Schur 安定で、かつ `sup |H(exp(i omega))| < gamma` であることです。上限は binary64 `gamma=0.9999`。入力は binary32 として保存し、値を変えずに昇格して読み取ります。等号は不合格です。

| 方式キー | 実装 | 意味 |
|---|---|---|
| `integer` | 配布 C++ ヘッダーの整数復号、Jury 条件、厳密 2 次式の符号 | 指定値とモデルに対する厳密判定 |
| `grid1024` | 独自の端点込み `[0,pi]` 等間隔グリッド、複素 double、三角関数キャッシュ | 点のサンプリングのみ。連続区間の証明ではない |
| `grid16384` | 同一実装を 16,384 点で実行 | 点を増やしても証明にはならない |
| `float64_algebraic` | 同じ Jury/2 次式を binary64 で評価。区間演算なし | 非常に速いが桁落ちで符号が変わり得る |
| `python_integer_api` | 実際の Python 公開 API | 証明書構成と個別呼び出し費用を含む |
| `fraction_reference` | `reference.py` の別表現有理数計算 | 参照判定。外部監査ではない |
| `scipy_freqz1024` | 実際の SciPy `signal.freqz` と分母・上限検査 | Python 応答評価比較。ネイティブカーネルではない |

SciPy は `freqz` を周波数応答評価と説明しています [SCIPY-FREQZ]。ネイティブグリッドは SciPy/ADAC のコピーではありません。ADAC 全体、SLICOT、MATLAB、すべての H-infinity 解法との比較も実施していません。

## 3. 入力生成と精度

NumPy の乱数シードは **20261007**。[run.py](../../../benchmarks/run.py) の `generate()` が各群 1,024 行を生成し、全体を連続 binary32 配列へ変換します。すべて合成入力で、録音や製品の使用頻度を代表しません。

| 群 | 最終 binary32 変換前の生成条件 |
|---|---|
| 一般 | 極半径 `[0.02,0.995)` 一様、角度 `[0.02,pi-0.02)` 一様、分子 3 係数は平均 0・標準偏差 0.25 の正規分布 |
| 高 Q | `scipy.signal.iirpeak(f,Q)`。`f` は `[0.005,0.995)`、`Q=10^U`、`U` は `[2,6)`。分子を `10^V`、`V` は `[-0.4,0.4)` で拡縮 |
| 上限付近 | 1 次節を biquad として表現。極 `r` は `[0.02,0.99)`、ピークは `1+U`、`U` は `[-0.0005,0.0005)` |
| 不安定分母 | 共役極の半径 `[1.00001,1.3)`、角度は上記と同様。分子の標準偏差は 0.1 |

| 試験群 | フィルター数 | 厳密判定で合格 | 厳密判定で不合格 |
| --- | --- | --- | --- |
| 一般フィルター | 1024 | 611 | 413 |
| 高 Q ストレス | 1024 | 539 | 485 |
| ゲイン上限付近 | 1024 | 431 | 593 |
| 不安定な分母 | 1024 | 0 | 1024 |

参照判定は密なグリッドではなく `Fraction` で計算します。Python とネイティブの整数結果が一致しなければ測定を受理しません。別にシード **20261107**、上限 1.0 の **2,048 行の無作為 binary32 ビットパターン**を検査します。無効な入力はエラーが期待値です。これは移植・復号検査であり、第 5 の時間測定群ではありません。

Python 比較は高 Q 配列の**最初の 128 行**を再利用し、独立のホールドアウトではありません。固定シードは再現用であり、事前登録や母集団代表性を主張しません。

## 4. 計時範囲と公平性

全ネイティブ方式を GCC 14.2.0、`-O3 -std=c++20 -shared -fPIC -ffp-contract=off` で一緒にコンパイルし、fast-math は使いません。9 試行で方式順序をシード **932851** でシャッフルします。計時直前に各方式を 1 回呼び出して適切なグリッドキャッシュを温め、その後 4 バッチを計測します。

$$t_{\text{filter},\mu s}=\frac{t_{\text{elapsed},ns}}{1024\cdot4\cdot1000}.$$

タイマーは `time.perf_counter_ns` です。ネイティブ時間にはバッチで償却した ctypes 呼び出し、出力書き込み、入力・分母検査を含め、入力生成、参照計算、正確性照合、キャッシュ生成を除外します。グリッドは違反時に早期終了し、平方根・除算なしで絶対値 2 乗を比較します。

Python 側は別のフィルター別ループ、キャッシュ済み omega ベクトル、4 モデルの予熱を使用します。フィルターオブジェクトは**計時前**に作り、関数呼び出し、厳密 API の証明書生成、ループ、結果リストの費用は含みます。SciPy は応答ベクトル全体を計算するため、ネイティブの早期終了と作業量は同じではありません。

ホストは AMD EPYC 9V74、Linux x86-64、可視論理 CPU 5、Python 3.13.5、NumPy 2.3.5、SciPy 1.17.0 を報告しました。`OMP_NUM_THREADS=1`、`OPENBLAS_NUM_THREADS=1`、MKL は未設定です。**CPU 固定・周波数制御・専用マシンではありません。** 観測値はこの環境の記録であり、移植先の保証ではありません。

## 5. ネイティブ結果と統計量

単位は **µs/フィルター**。棒は中央値、ひげは 9 回の観測最小・最大であり、**信頼区間ではありません**。

| 試験群 | 厳密整数判定 | 1,024 点グリッド | 16,384 点グリッド | Float64 代数判定 | グリッド 1,024 / 整数¹ |
| --- | --- | --- | --- | --- | --- |
| 一般フィルター | 0.564106 | 1.686392 | 27.877729 | 0.011137 | 2.989× |
| 高 Q ストレス | 0.599275 | 2.161358 | 33.816509 | 0.012064 | 3.607× |
| ゲイン上限付近 | 0.377707 | 0.932293 | 16.152820 | 0.011086 | 2.468× |
| 不安定な分母 | 0.008509 | 0.006741 | 0.007093 | 0.006717 | 0.792× |

¹ 主表は `median(グリッド時間)/median(整数時間)` です。JSON にある `median(グリッド_i/整数_i)` とは異なります。

| 試験群 | 各ペア試行の比率の中央値 |
| --- | --- |
| 一般フィルター | 3.037857× |
| 高 Q ストレス | 3.502723× |
| ゲイン上限付近 | 2.433858× |
| 不安定な分母 | 0.786818× |

観測範囲:

| 試験群 | 厳密整数判定 | 1,024 点グリッド | 16,384 点グリッド | Float64 代数判定 |
| --- | --- | --- | --- | --- |
| 一般フィルター | 0.538766 – 0.621713 | 1.570972 – 1.937667 | 26.413858 – 29.532372 | 0.010687 – 0.012078 |
| 高 Q ストレス | 0.570299 – 0.719463 | 2.028531 – 4.190899 | 32.702964 – 41.433221 | 0.011120 – 0.015795 |
| ゲイン上限付近 | 0.360094 – 0.428116 | 0.876417 – 0.980895 | 14.860312 – 17.181955 | 0.010205 – 0.015665 |
| 不安定な分母 | 0.008354 – 0.008915 | 0.006572 – 0.007166 | 0.006672 – 0.010472 | 0.006342 – 0.008800 |

![ネイティブ C++ 時間](../../../benchmarks/figures/native_latency.svg)

最初の 3 群は整数に有利ですが、不安定分母の即時拒否は数値方式に有利です。Float64 代数方式は全体としてさらに高速です。桁落ち近傍の厳密性と費用の交換条件であり、すべての手法に対する絶対的高速性ではありません。CI は速度の勝敗を合否条件にしません。

## 6. 正確性の分母を明示する

高 Q 群の `false_accepts` は厳密条件が偽なのに 1 を返した場合、`false_rejects` は真なのに 0 を返した場合です。**参照不合格 485 件、参照合格 539 件**です。

| 方式 | 誤受理 / 参照判定で不合格の 485 件 | 誤棄却 / 参照判定で合格の 539 件 |
| --- | --- | --- |
| 厳密整数判定 | 0 | 0 |
| 1,024 点グリッド | 356 | 0 |
| 16,384 点グリッド | 213 | 0 |
| Float64 代数判定 | 2 | 5 |

構成したストレス分布での件数です。誤受理 356 件は **356% ではありません**。全 1,024 件で割る率と、実際の不合格 485 件で割る率は違う問いに答えます。製品のリスク頻度は推定しません。他群は 4 方式すべて不一致 0。負の戻り値は `invalid_or_error` として別に保持し、受理しません。

![高 Q での誤判定件数](../../../benchmarks/figures/high_q_correctness.svg)

参照も同一プロジェクトの実装です。一致は有用な回帰証拠ですが、独立の数学証明や外部機関監査ではありません。厳密符号だけで十分な理由は導出で示し、密なグリッド照合では代用しません。

## 7. Python、カスケード例、隠れたピーク

| Python レベルの方式 | 中央値 µs/フィルター |
| --- | --- |
| python_integer_api | 7.811008 |
| fraction_reference | 63.969969 |
| scipy_freqz1024 | 71.832703 |

![Python API の時間](../../../benchmarks/figures/python_latency.svg)

高 Q 128 個・9 試行で、C++ とは計時範囲が異なります。これを言語間のアルゴリズム優劣に読み替えないでください。

保存された `cascade_demo` は全伝達関数が厳密に **0.75** の安定な 2 節です。個別のゲイン 1 検査は失敗し、共同認証は成功して有理数で被覆を再検査します。これは正確性の例であり、カスケード性能研究ではありません。ネイティブ棒グラフに SOS カスケード時間はありません。

![隠れたピークの例](../../../benchmarks/figures/hidden_peak.svg)

`alpha=2^-14` とすると `H(z)=alpha(1-z^-2)/(1+(1-alpha)z^-2)` は `omega=pi/2` で絶対値 2 です。端点込み 1,024 点グリッドには pi/2 が厳密には含まれません。図は解析的既知値を説明するもので、サンプル曲線は全体ピークの証明ではありません。

## 8. ファイルと JSON フィールド

| ファイル・フィールド | 意味 |
|---|---|
| `families.NAME.median_us.METHOD` | 群・方式ごとの中央値 |
| `families.NAME.raw_us_per_filter.METHOD` | 試行順を保持した 9 個の元時間 |
| `families.NAME.correctness.METHOD` | 誤受理、誤棄却、入力エラー件数 |
| `families.NAME.exact_pass` | 厳密な 2 条件を満たした数 |
| `paired_grid1024_over_integer` | 試行ごとの比率の中央値 |
| `python_high_q` | 別の API 試験、入力数と元の繰り返し時間 |
| `native_bit_patterns` | 別のネイティブ復号・無効入力検査 |
| [fixtures.npz](../../../tools/restore_fixtures.py) | 保存した binary32 値。`allow_pickle=False` でロード |
| [protocol.json](../../../benchmarks/results/protocol.json) | シード、個数、コンパイル命令、ソース 12 個の SHA-256 |
| [environment.json](../../../benchmarks/results/environment.json) | 記録時のホストと依存バージョン |
| [summary.csv](../../../benchmarks/results/summary.csv) | 中央値・範囲・件数の派生出力。新しい測定ではない |
| [検証ログ](../../../validation/README.md) | 元のビルド・テスト履歴と中間レビュー |

## 9. 元の結果を上書きしない再現

プロジェクト環境に `.[bench]` をインストールします。`benchmarks/requirements-bench-tested.txt` は当時のバージョンで、他の Python では互換性のある依存を使い差分を記録してください。

```bash
python tools/audit_benchmark.py
python tools/audit_benchmark.py --recheck-fixtures
python benchmarks/run.py --n 32 --trials 3 --out validation/my-smoke
```

Linux/macOS の全規模測定:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python benchmarks/run.py \
  --n 1024 --trials 9 --seed 20261007 --out validation/my-run
python benchmarks/plot.py --results validation/my-run/benchmark.json \
  --out validation/my-run/figures
python tools/audit_benchmark.py --results validation/my-run/benchmark.json --recheck-fixtures
```

Windows では WSL を使用します。`run.py` は標準で `benchmarks/results` を上書きするため、レビューでは `--out` を指定してください。測定対象コードを変更したらハッシュ監査が失敗するのが正常です。新アルゴリズムは再測定し、古いハッシュの編集で整合させないでください。

同じシードでも依存・プラットフォームで生成係数や時間が変わることがあります。元の値の監査には再生成ではなく**保存済み NPZ**を使用します。配列が同じでも再圧縮で NPZ のバイトが変わり得ます。監査は配布ファイルのバイトハッシュを確認します。

## 10. レビューの制約

GCC 14.2/Boost のインライン警告は `validation/runs/v0.1.0/benchmark_run.log` に残しており抑制していません。過去の sanitizer は実行したケースで通っただけで、全入力は保証しません。一般高次/MIMO 解法、ADAC 全体、リアルタイム性能、音質・画質、実行算術安全、原定理検証への主張はありません。`validation/docs_refresh/benchmark_smoke` はコマンド経路確認であり、README グラフのデータではありません。

[OAI-README]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/README.md
[OAI-325]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex
[OAI-DFT]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex
[CP-2017]: https://arxiv.org/abs/1702.00668
[SCIPY-FREQZ]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html
[PYPA]: https://packaging.python.org/en/latest/tutorials/packaging-projects/

<!-- benchmark-sha256: 0332cbc6a22ebf2da482a043b3f206ae175bcab5d71f640417c96c46c7ac99a0 -->


**測定の由来。** 表の数値は旧研究名 **CertifiedDSP** で記録しました。Dexted DSP への変更は名称・名前空間・CLI・証明書スキーマのみで、代数的判定式は変わりません。元の測定値と測定時のソースを保持しています。[移行と再現](../../project/REBRANDING.md) · [ソース対応表](../../../benchmarks/results/rebrand-map.json)。


**ソースチェックアウトのデータ：** NPZ は Git に保存せず必要時に再構築します。固定したベンチマーク依存関係を入れ、`python tools/restore_fixtures.py` を実行してください。元の SHA-256 との一致が必須で、測定値は置き換えません。
