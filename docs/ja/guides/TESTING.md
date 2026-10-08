# テスト手順と期待結果

[English](../../en/guides/TESTING.md) · [한국어](../../ko/guides/TESTING.md) · [简体中文](../../zh-CN/guides/TESTING.md) · [日本語](TESTING.md)

[Dexted DSP](../README.md)

## 1. 検査層を区別する

| 層 | コマンド・データ | 意味 |
|---|---|---|
| コア回帰 | unittest 35 メソッド | API、厳密判定、制限、証明書、CLI |
| 文書シナリオ | `documentation_smoke.py` の 12 検査 | 例と終了コード仕様 |
| ネイティブ実行 | 複数 assertion を含む CTest 1 項目 | C++ ヘッダー/C ABI の境界例 |
| ネイティブローダー | 固定シードの 256 フィルター | ctypes と暗黙の精度変更拒否 |
| 保存全規模ベンチ | 4,096 フィルターと別の 2,048 ビットパターン行 | 比較結果と復号検査 |
| 文書改訂スモーク | 4 × 32 フィルター、3 試行 | コマンド経路確認。公開時間表ではない |

1 メソッドが多くの乱数ケースを含む場合があります。35 個の独立実験、外部監査、Lean 実行ではありません。元ログは `validation/`、改訂ログは `validation/docs_refresh/` に分けています。

## 2. 測定用依存なしで最低限のテスト

[利用ガイド](../getting-started/USER_GUIDE.md)のインストール後、ソースルートで実行します。

```bash
python -m unittest discover -s tests -v
python tools/documentation_smoke.py
python examples/basic.py
python examples/cascade.py
```

コアの期待要約は `Ran 35 tests ... OK`。文書スクリプトは `"status": "passed"` と `"checks": 12` の JSON を出力します。基本例は `certified` と有理数再検査成功、カスケード例は個別失敗と共同 `certified` を示します。

厳密な等号、隠れた共振、分母境界極、不安定極の相殺、明示 float32 変換、極端な有限値、不正・複素入力、整数/Fraction の乱数照合、偽の成功フラグ、不正な被覆、予算不足、CLI の入力保護を検査します。

コアには 2,500 ケースのシード固定比較、最大 1,200 ビットパターン試行のうち有限行だけの検査、100 候補の補償カスケードがあります。ベンチマークの 4,096/2,048 とは別データです。

個別回帰:

```bash
python -m unittest discover -s tests -p test_dexted_dsp.py -k hidden_peak -v
python -m unittest discover -s tests -p test_dexted_dsp.py -k unknown -v
python -m unittest discover -s tests -p test_dexted_dsp.py -k tampering -v
```

各コマンドは 1 テストを選び成功するはずです。否定テストは数学的な主張を正しく拒否・保留することで成功します。

## 3. CLI の全終了経路

| 入力・操作 | 期待状態 | 終了コード |
|---|---|---|
| `safe.json` | `certified` | 0 |
| `hidden_peak.json` | `gain_limit_not_met` | 1 |
| `budget_limited.json --max-depth 0` | `unknown` | 3 |
| 同じ入力で `--max-depth 16` | `certified` | 0 |
| 不正 JSON または非対応型 | `invalid_input` | 2 |
| 別係数に対して旧証明書を確認 | `verified: false` | 1 |

`python tools/documentation_smoke.py` がこれらのコードを自動確認します。手動では直後に POSIX の `echo $?`、PowerShell の `$LASTEXITCODE` を使用します。予期した失敗コマンドを未処理の `set -e` ブロックに入れないでください。

予算増加後に成功しても、現在の `unknown` 判定は配備拒否のままです。ゲイン制約失敗は一般フィードバック不安定性の証明ではありません。

## 4. ネイティブビルドと連携テスト

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
# Linux の共有ライブラリ例:
python tools/native_smoke.py "$PWD/build/libdexted_dsp.so"
```

期待出力は `native tests: PASS`、CTest は 1 項目成功です。ローダーは 256 件、不一致 0、`implicit_rounding_rejected: true` を出します。他の OS は実際の絶対ライブラリパスを使ってください。ネイティブベンチは別ビルド経路で、API テストの代わりにはなりません。

コンパイラー警告を保持してください。元の GCC/Boost 警告と sanitizer 記録は[ベンチマーク詳細](../benchmarks/BENCHMARKS.md)にあります。CTest 成功は全警告が無害である証明ではありません。

## 5. 計時しない保存資料監査

```bash
python tools/audit_benchmark.py
# インストール済みプロジェクトと NumPy が必要:
python tools/audit_benchmark.py --recheck-fixtures
```

前者は NPZ ハッシュ、ソース 12 ファイルのハッシュ、試行数、中央値、ペア比率、件数の一貫性を検査します。後者は `allow_pickle=False` で配列を読み、**全 4,096 判定**を整数と Fraction で再計算し、群ごとの合格数を確認します。

期待フィールドは `status: passed`、`fixture_rows: 4096`、再検査時には `exact_recheck_rows: 4096`。過去のネイティブ時間や全数値ベースラインの過去の誤判定数を再測定するのではなく、保存資料と現在の厳密判定を検査します。

測定ソースを変えたときにハッシュが失敗するのは有用な保護です。旧実行の監査では元に戻し、新コードは新しく測定してください。過去のハッシュを編集して一致させてはいけません。

## 6. 再計測とグラフ生成

```bash
python -m pip install '.[bench]'
python benchmarks/run.py --n 32 --trials 3 --out validation/my-smoke
python benchmarks/run.py --n 1024 --trials 9 --seed 20261007 --out validation/my-run
python benchmarks/plot.py --results validation/my-run/benchmark.json --out validation/my-run/figures
```

記録設定に合わせる場合 OpenBLAS/OMP は単一スレッドにします。ネイティブ測定にはコンパイラーと Boost、Windows では WSL が必要です。分布、費用除外、版は [BENCHMARKS.md](../benchmarks/BENCHMARKS.md)にあります。

再現成功とは、厳密参照との不一致がなく、出力が有効で、環境を正直に記録したことです。**高速化の再達成は必須ではありません。** 欲しい見出しが得られるまで遅い実行を捨てず、同じ入力値とコード版で前後を保管してください。

元の図だけを再描画する場合:

```bash
python benchmarks/plot.py --results benchmarks/results/benchmark.json --out validation/redrawn-figures
```

## 7. 開発ソースではなく配布物を検査する

ルートで別環境を作成します。

```bash
python -m pip install build
python -m build
python -m venv .wheel-test
# POSIX:
.wheel-test/bin/python -m pip install --no-deps dist/dexted_dsp-0.1.0-py3-none-any.whl
.wheel-test/bin/python -m unittest discover -s tests -v
.wheel-test/bin/python tools/documentation_smoke.py
# Windows では .wheel-test\Scripts\python.exe に置換
```

`PYTHONPATH=src` を設定するとソースが wheel の欠落を隠すため、この検査では設定しないでください。再ビルドには任意の開発ツールを入れ、`python -m build`、`python -m twine check dist/*` を使います。ビルド・確認は公開ではありません。README メタデータ変更後は wheel も再生成します。

## 8. 文書と公開前のチェック

```bash
python tools/check_links.py
python tools/check_documentation.py
python tools/audit_benchmark.py
```

ローカルリンク、4 言語の必須文書、共通のベンチマーク識別子、結果表、保存ソースとの一致を確認します。翻訳のすべての意味や数学を検証するものではなく、ホスト CI・外部監査も意味しません。

公開前には [validation/docs_refresh/summary.json](../../../validation/docs_refresh/summary.json)を読み、ログを保持し、README が対象の測定に対応することを確認して配布メタデータを再ビルドし、[公開手順](../development/RELEASING.md)へ進んでください。ZIP チェックサムと `MANIFEST.sha256` はファイル識別用であり、数学的正しさを証明しません。

[OAI-README]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/README.md
[OAI-325]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex
[OAI-DFT]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex
[CP-2017]: https://arxiv.org/abs/1702.00668
[SCIPY-FREQZ]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html
[PYPA]: https://packaging.python.org/en/latest/tutorials/packaging-projects/
