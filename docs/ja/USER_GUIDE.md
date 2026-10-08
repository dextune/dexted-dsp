# 利用ガイド: インストール・API・連携

[English](../en/USER_GUIDE.md) · [한국어](../ko/USER_GUIDE.md) · [简体中文](../zh-CN/USER_GUIDE.md) · [日本語](../ja/USER_GUIDE.md)

[Dexted DSP](../../README.ja.md)

## 1. モデルが適用できるか確認する

対象は**固定実係数・正規化済み biquad**、またはその 1–32 節の直列接続です。与えられた分母の厳密な安定性と理想線形応答の上限を検査します。FLAMO/PyTorch グラフの自動解析、FAUST/VST/ONNX の読み取り、係数の自動修正は行いません。

正規化と float32 変換も含め、**最終的に配備する係数**を出力してください。再生・配備前にオフラインで検査します。このガイドのコマンドは音声を再生せず、装置を制御しません。

## 2. インストール方法

すべて展開後の `dexted-dsp/` ルートで実行し、`docs/ja/` からは実行しないでください。

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
python -m dexted_dsp --version
```

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install .
python -m dexted_dsp --version
```

期待バージョンは `0.1.0`。有効化せず POSIX の `.venv/bin/python`、Windows の `.venv\Scripts\python.exe` を直接使えば、PowerShell 実行ポリシーを変更する必要はありません。宣言した最小バージョンは Python 3.10 であり、ホスト上の OS/バージョン別 CI は公開後に実行してください。

### オフライン wheel / 開発用

```bash
python -m pip install build
python -m build
python -m pip install --no-deps dist/dexted_dsp-0.1.0-py3-none-any.whl
# ソース編集時の別の選択肢。ビルドツールの取得が必要な場合があります。
python -m pip install -e .
```

環境ごとに**一つの方法**を選びます。未公開なので、インデックスの `pip install dexted-dsp` がこのプロジェクトとは限りません。wheel は Python ランタイムで、ネイティブバイナリは含みません。文書・図・テスト・ソースは ZIP/sdist にあるため、例を動かす場合はソースツリーを残してください。構成は PyPA を参考にしています [PYPA]。

## 3. 入力の意味と精度

$$H(z)=\frac{b_0+b_1z^{-1}+b_2z^{-2}}{1+a_1z^{-1}+a_2z^{-2}}.$$

| 入力 API | 順序 |
|---|---|
| `Biquad.from_coefficients()` | `[b0,b1,b2,a1,a2]` の 5 値 |
| `Biquad(b=..., a=...)` | `(b0,b1,b2)` と `(1,a1,a2)` |
| `from_sos()` | SciPy の `[b0,b1,b2,a0,a1,a2]`、`a0==1` 必須 |
| CLI `type="cascade"` | `sections` の各行は **5 値**。SciPy の 6 値ではない |

`a0` の自動正規化はしません。実配備側で正規化・丸めを実施し、その結果を渡してください。他のツールの分母符号規約も確認してください。

Python/JSON の 10 進数はまず有限 binary64 に変換されます。`precision="float32"` は係数を明示的に binary32 に再丸めし、`float64` は解析した値を保持します。その後に**表現された 2 進有理数**を厳密に認証します。解析前の理想的な 10 進数の認証ではありません。float32 係数でも上限は binary64 です。NaN・無限・複素・bool・文字列・非正の上限は拒否します。float32 オーバーフローはエラーで、微小値のゼロへの丸めは指定した変換の結果です。

## 4. 単一フィルターと結果

```python
from dexted_dsp import Biquad, certify, verify_biquad
f = Biquad.from_coefficients([0.25, 0, 0, -0.5, 0], precision="float32")
report = certify(f, max_gain=1.0)
print(report.status)
print(report.denominator_stable)
print(verify_biquad(report.as_dict(), f, max_gain=1.0))
```

期待出力:

```text
certified
True
True
```

| 状態 | 意味 |
|---|---|
| `certified` | 両方の厳密条件が成立 |
| `denominator_not_schur` | 分母が厳密な単位円内部安定性を満たさない |
| `gain_limit_not_met` | 分母は安定だが指定ゲイン上限を満たさない |

`max_gain_limit` は**要求された上限**を保存します。実際の最大ゲイン、ピーク周波数、dB マージン、知覚品質スコアは返しません。定数ゲイン 1 に対する `certify(Biquad.from_coefficients([1,0,0,0,0]),1.0)` は `<1` でないため拒否します。

エラーは明示的に処理します。

```python
from dexted_dsp import Biquad, certify

def accept_exported_filter(values):
    try:
        f = Biquad.from_coefficients(values, precision="float32")
        result = certify(f, max_gain=1.0)
    except (ValueError, TypeError):
        return False
    return result.certified
```

これは記述したフィルターモデルのゲートであり、周囲のフィードバック系全体の証明ではありません。

## 5. カスケードと SciPy

```python
from dexted_dsp import from_sos, certify_cascade, verify_cascade
sections = from_sos([
    [1.0, -0.75, 0.0, 1.0, -0.125, 0.0],
    [0.75, -0.09375, 0.0, 1.0, -0.75, 0.0],
], precision="float32")
proof = certify_cascade(sections, max_gain=1.0)
assert proof["certified"]
assert verify_cascade(proof, sections, max_gain=1.0)
```

全伝達関数は厳密に 0.75 です。共同認証は周波数ごとの補償を保ち、個別最大値の積では失われる場合があります。`from_sos` 自体は SciPy を import しません。任意の `examples/scipy_sos.py` は SciPy で Butterworth SOS を設計し、丸めた係数を上限 1.01 で確認します。

カスケードの状態は `certified`、`denominator_not_schur`、`condition_failed`、`unknown`。`condition_failed` は厳密ゲイン差多項式の非正値という根拠を持ち、`unknown` は予算内で証明を作れなかっただけです。安定・不安定・配備可のいずれも意味しません。他の節で極が相殺されるように見えても、不安定な節は拒否します。

標準予算は `max_depth=48`、`max_nodes=20000`。上限は深さ 128、100,000 ノード、32 節です。予算増加が有効な場合はありますが、ゼロ近傍の高次式を高速処理できる保証はありません。

## 6. JSON CLI と証明書

[safe.json](../../examples/safe.json) の形式:

```json
{
  "type": "biquad",
  "precision": "float32",
  "max_gain": 1.0,
  "coefficients": [0.25, 0, 0, -0.5, 0]
}
```

```bash
python -m dexted_dsp check examples/safe.json --output certificate.json
python -m dexted_dsp verify examples/safe.json certificate.json
```

検査は完全な JSON、再検査は `{"verified": true}` を出力します。`--output` で入力パスは上書きできません。出力先の親ディレクトリを先に作ってください。JSON の上限は 1 MiB で、ファイル実行やサービス送信はしません。

非ゼロ終了で停止するシェルとは別に、期待される拒否例を実行します。

```bash
python -m dexted_dsp check examples/hidden_peak.json
# 期待値: gain_limit_not_met、終了コード 1。
python -m dexted_dsp check examples/budget_limited.json --max-depth 0
# 期待値: unknown、終了コード 3。
python -m dexted_dsp check examples/budget_limited.json --max-depth 16
# 同梱したこの例では certified、終了コード 0。
```

後の 2 コマンドは、保留が不成立の証明ではないことを示します。状態と終了コードを確認し、文字列「certified」の検索だけで通さないでください。false のフィールド名にも現れます。成功証明書だけを再検査できます。元の入力、上限、証明書、版を一緒に保持してください。証明書は署名されず、再検査器が条件と入力対応を再構成します。

## 7. C++ / C 連携

C++20 コンパイラー、CMake >=3.20、Boost >=1.74 ヘッダーが必要です。Debian/Ubuntu の例は `sudo apt-get install g++ cmake libboost-dev`。macOS は通常のパッケージマネージャー、Windows は互換ツールチェーンと Boost を設定します。Python コアにこれらは不要です。

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
cmake --install build --prefix ./local-install
```

```cpp
#include <dexted_dsp/biquad.hpp>
int main() {
    const float coefficients[5] = {0.25f, 0, 0, -0.5f, 0};
    const int verdict = dexted_dsp::certify_biquad_f32(coefficients, 1.0);
    return verdict == 1 ? 0 : 1;
}
```

戻り値は `1` 成功、`0` 不合格、`-1` 無効入力。C ABI は例外を捕捉し `-2` も返す・保存します。**そのまま bool へ変換しないでください。** 負のエラーコードも true になります。ヘッダー API は割り当て例外を投げる場合があります。fast-math は禁止です。

CMake 利用側は `find_package(DextedDSP CONFIG REQUIRED)` を呼び、`DextedDSP::dexted_dsp` にリンクし、インストール前置きパスを `CMAKE_PREFIX_PATH` で渡します。ネイティブ係数は binary32 専用で上限は binary64。ネイティブカスケード認証は未実装です。

任意の Python ネイティブ接続確認、Linux 例:

```bash
python tools/native_smoke.py "$PWD/build/libdexted_dsp.so"
```

ローダーは信頼できる明示的な絶対パスを要求し、暗黙の係数丸めを拒否します。他の OS ではライブラリ名と位置が異なります。[API 契約](../API.md)を参照してください。

## 8. CI への組み込み

```bash
python -m dexted_dsp check examples/safe.json --output certificate.json
python -m dexted_dsp verify examples/safe.json certificate.json
```

例を実際の出力係数に置き換え、3 を含むすべての非ゼロコードで配備を停止してください。同梱 GitHub Actions は Python/C++/ビルドを検査しますが、設定の存在は実際のホスト実行を意味しません。実リポジトリで成功するまで成功バッジを公開しないでください。

## 9. トラブル対処

| 症状 | 確認・対応 |
|---|---|
| モジュールや `dexted-dsp` が見つからない | 同じ環境で `python -m pip` と `python -m dexted_dsp` を使う |
| float32 超過・係数エラー | 最終有限実数値を調べる。黙ってクリップして旧証明書を使い回さない |
| 単位ゲインが拒否される | 条件は厳密。根拠ある大きい上限を明示し、隠れた許容差にしない |
| `unknown` | ノード・深さ・条件の余裕を調べ、上限内で予算を増やすか配備拒否 |
| 旧証明書が通らない | 係数順序、正規化、丸め、節の順序、同じ上限かを確認 |
| Boost が見つからない | ヘッダーを導入し、特殊配置では CMake 検索パスを指定 |
| ネイティブが係数を拒否 | 出力値を明示的に float32 にする |
| ヘッドレス描画エラー | `MPLBACKEND=Agg` と書き込み可能な `MPLCONFIGDIR` を設定 |
| ベンチマーク値が異なる | 版、入力、CPU 負荷、フラグ、スレッドを確認。速度で正確性を代用しない |

不具合報告には最小の係数 JSON、期待条件と実際の状態、版、OS/コンパイラーとログを添付します。許可なく非公開音源、認証情報、独占モデルを添付しないでください。

[OAI-README]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/README.md
[OAI-325]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex
[OAI-DFT]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex
[CP-2017]: https://arxiv.org/abs/1702.00668
[SCIPY-FREQZ]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html
[PYPA]: https://packaging.python.org/en/latest/tutorials/packaging-projects/
