# Dexted DSP — migration and measurement provenance

[English](../../README.md) · [한국어](../ko/README.md) · [简体中文](../zh-CN/README.md) · [日本語](../ja/README.md)

Dexted DSP is the maintained project at **dextune/dexted-dsp**. The earlier
conversation artifacts used the working name **CertifiedDSP**. This source
import preserves the numerical algorithms and the inherited MIT notice.
There is no implied OpenAI ownership, endorsement, independent audit or PyPI release.

| Interface | Previous working name | Maintained name |
|---|---|---|
| Python distribution | `certified-dsp` | `dexted-dsp` |
| Python import | `certified_dsp` | `dexted_dsp` |
| CLI | `certdsp` | `dexted-dsp` |
| Module CLI | `python -m certified_dsp` | `python -m dexted_dsp` |
| CMake package | `CertifiedDSP` | `DextedDSP` |
| CMake target | `CertifiedDSP::certified_dsp` | `DextedDSP::dexted_dsp` |
| C++ namespace | `certdsp` | `dexted_dsp` |
| C API | `certdsp_biquad_f32` | `dexted_dsp_biquad_f32` |
| JSON schemas | `certified-dsp/.../v1` | `dexted-dsp/.../v1` |

Regenerate saved certificates with the new package. Old import names and schema
labels are not accepted as aliases. No filter coefficients are changed by this migration.

## Evidence integrity

`benchmarks/results/benchmark.json`, `protocol.json`, `fixtures.npz`,
`environment.json` and `summary.csv` are preserved **byte for byte**.
The speed figures describe that archived run, not newly measured Dexted DSP timings.

Original benchmarked files are stored under `benchmarks/archive/v0.1.0/`.
`benchmarks/results/rebrand-map.json` binds the old hashes and paths to the
renamed files and records the literal substitutions. The audit script checks
both the original hashes and that current sources differ only by those substitutions.
Do not edit the old hash registry to pretend renamed code was the original timed source.

```bash
python -m pip install '.[bench]'
python -m pip install -r benchmarks/requirements-bench-tested.txt
python tools/restore_fixtures.py
python tools/audit_benchmark.py --recheck-fixtures
```

New measurements go in a separate output directory:

```bash
python benchmarks/run.py --n 1024 --trials 9 --seed 20261007 --out validation/my-run
python benchmarks/plot.py --results validation/my-run/benchmark.json --out validation/my-run/figures
```

Historical logs keep their former package names and paths intentionally. Current
installation instructions and runnable examples use Dexted DSP. Generated wheels,
virtual environments and native binaries are not committed to the source repository.

## 한국어

이전 CertifiedDSP를 Dexted DSP로 변경했습니다. 패키지·명령어·인증서 스키마가
변경되므로 이전 인증서는 새 버전에서 다시 생성하십시오. 수학 판정식과 기존
측정 데이터는 바꾸지 않았습니다. 이전 소스와 해시는 보존되며, 감사 스크립트가
이름 치환 외의 코드 변경이 없는지 확인합니다. 기존 속도 수치는 새 이름으로
재측정한 결과가 아닙니다. PyPI 게시는 별도 절차입니다.

## 简体中文

原 CertifiedDSP 已更名为 Dexted DSP。包名、命令和证书模式已更改，旧证书应重新生成。
代数判定式和已有测量数据保持不变。保留原源码及哈希，审计脚本验证更改仅为名称替换。
已有速度数据并非更名后的重新计时。PyPI 发布是另一项独立操作。

## 日本語

旧 CertifiedDSP を Dexted DSP に変更しました。パッケージ名・コマンド・証明書スキーマが
変わるため、以前の証明書は再生成してください。代数的判定式と既存の測定値は変更していません。
元のソースとハッシュを保持し、監査スクリプトで名称置換以外の変更がないことを確認します。
既存の速度値は改名後の再測定ではありません。PyPI 公開は別の操作です。

## Source-only Git checkout

The generated fixture NPZ is omitted from Git. `tools/restore_fixtures.py`
reconstructs it with the pinned NumPy/SciPy versions and refuses to write unless
its bytes match the original SHA-256. Distribution ZIPs may already include it.
The benchmark audit invokes this restoration when the archived input is absent.
