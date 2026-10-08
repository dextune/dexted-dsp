<div align="center">

# Dexted DSP

**Exact filter checks. Inspectable evidence.**

Offline verification for fixed digital filters · Python & C++20

[![CI](https://github.com/dextune/dexted-dsp/actions/workflows/ci.yml/badge.svg)](https://github.com/dextune/dexted-dsp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](../../LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](../../pyproject.toml)
[![C++20](https://img.shields.io/badge/C%2B%2B-20-blue.svg)](../../CMakeLists.txt)
[![Research alpha](https://img.shields.io/badge/status-research%20alpha-orange.svg)](../project/CHANGELOG.md)

[English](../../README.md) · [한국어](README.md) · [简体中文](../zh-CN/README.md) · [日本語](../ja/README.md)

[Documentation](../README.md) · [Contributing](../../.github/CONTRIBUTING.md)

</div>

---

**일부 주파수만 검사하는 대신, 고정 디지털 필터가 전체 주파수에서 이득 제한을 만족하는지 정확하게 판정합니다.**

Python · C++20 · CLI · 정확한 정수 연산 · 재검사 가능한 인증서 · 재현 가능한 측정 자료

**v0.1.0 · 연구용 알파.** [dextune/dexted-dsp](https://github.com/dextune/dexted-dsp)에서 관리하는 AI 보조 개발 독립 프로젝트입니다. OpenAI의 제품·공식 통합·외부 공인 안전 인증 도구가 아닙니다. 저장소 소스로 설치하며 PyPI 게시를 전제하지 않습니다.

## 현재 사용할 수 있는 기능

실행 가능한 대상은 **고정 계수 실수 biquad**와 Python의 **직렬 필터 체인**입니다. 각 분모의 엄격한 안정성과 지정한 전체 주파수 이득 제한을 검사합니다. 실제 배포 정밀도로 계수를 변환한 다음, 배포 전에 실행하십시오. 오디오 재생, 필터 자동 최적화, 임의 신경망 분석 또는 물리적 장치 안전 인증은 제공하지 않습니다.

영상의 각 픽셀에 동일한 고정 시간 필터를 적용하는 경우에는 이 모델을 사용할 수 있습니다. 그러나 일반적인 영상 복원망 전체가 자동으로 이 모델에 해당하지는 않습니다. 큰 정수 연산과 동적 메모리를 사용하므로 실시간 오디오 콜백 안에서 호출하지 마십시오.

## 설치 및 실행

저장소를 복제한 뒤 소스에서 설치하십시오. 비공개 상태에서는 GitHub 접근 권한이 필요합니다.

```bash
git clone https://github.com/dextune/dexted-dsp.git
cd dexted-dsp
python -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows PowerShell에서는: .venv\Scripts\Activate.ps1
python -m pip install .
python examples/basic.py
python tools/documentation_smoke.py
```

Python 3.10 이상이며 **핵심 실행 코드**에는 외부 런타임 의존성이 없습니다. 소스 설치 시 빌드 도구를 내려받을 수 있습니다. 오프라인 설치용 wheel은 [공개 가이드](development/RELEASING.md)에 따라 먼저 생성하십시오. `dist/`는 Git 추적 대상이 아닙니다.

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

`max_gain`은 계산 결과인 최대 이득이 아니라 **검사할 제한값**입니다. 조건은 `<=`가 아닌 `<`입니다. 계수나 제한값이 달라지면 저장한 인증서의 입력 일치 검사를 통과하지 못합니다.

```bash
python -m dexted_dsp check examples/safe.json --output certificate.json
python -m dexted_dsp verify examples/safe.json certificate.json
python -m dexted_dsp check examples/hidden_peak.json
# 마지막 명령은 의도적으로 종료 코드 1을 반환하는 부정 테스트입니다.
```

CLI 종료 코드: `0` 인증·재검사 성공, `1` 조건 미충족·잘못된 인증서, `2` 입력 오류, `3` 자원 제한에 따른 **판정 보류**. 배포 단계에서는 오직 0만 합격으로 처리하십시오. 설치된 `dexted-dsp` 명령도 동일하게 동작합니다.

## OpenAI의 어느 부분을 참고했습니까?

연구의 출발점은 [`openai/math` 수학 원고 모음][OAI-README]입니다. 변경되는 최신 브랜치 대신 **`adc7f1241b42e322a6451854ab7e4b4c146bf78a` 커밋**을 참고 버전으로 고정했습니다. 저장소 README 자체도 원고별 검증 단계가 서로 다르다고 설명합니다.

| 참고 원문 또는 수학 | 이 프로젝트에서의 역할 | 벤치마크 실행에 사용했습니까? |
|---|---|---|
| OpenAI 결과군 325, *A direct proof of the complete Crouzeix inequality*, §1 주정리 [OAI-325] | 행렬 다항식 오차와 제한된 시변 시스템의 조건부 확장 연구 | **아닙니다** |
| OpenAI의 정확한 DFT 논문, 서론의 계산 모델과 제한 설명 [OAI-DFT] | 연구 범위 선정에 참고. 점근적 정확 산술 결과를 실용 FFT 가속으로 해석하지 않음 | **아닙니다** |
| 고전적인 2차 Schur/Jury 조건 및 `cos(omega)` 이차식 | 실행되는 정확 biquad 판정의 핵심 | **사용합니다** |
| 고전적인 Bernstein 양수성 및 정확한 구간 분할 | Python 직렬 필터 인증과 유리수 재검사 | 체인 예제에 사용하며, **C++ 속도 막대에는 포함하지 않음** |

**측정한 속도 향상은 Crouzeix 정리에서 나온 것이 아닙니다.** OpenAI의 증명 코드나 DSP 코드를 실행 엔진에 복사하지 않았습니다. 일반적인 상수 2 원정리를 독립적으로 검증하지 않았으며 `crouzeix_certify()` API도 제공하지 않습니다. OpenAI가 원고를 만든 과정과 이 프로젝트의 AI 보조 개발 과정은 별개입니다.

진행 과정은 수학 후보 검토 → 이론적 가정과 실행 알고리즘 분리 → 정확 판정 구현 → 별도 유리수식과 대조 → C++ 이식 → 강한 수치 기준선과 비교 → 실패·수정 기록 보존 → 패키징·문서화입니다. 단계별 산출물은 [연구 과정과 출처](development/PROVENANCE.md)에 연결했습니다.

## 벤치마크: 무엇을 측정했습니까?

아래는 **기존 v0.1.0에 저장된 측정값**입니다. 번역하면서 더 유리한 결과를 골라 교체하지 않았습니다. 이번 문서 개정에서는 해시와 판정을 재검사했으며, 별도의 작은 실행 점검은 원본 벤치마크를 대체하지 않습니다.

| 항목 | 기록된 설정 |
|---|---|
| 입력 | 합성 시험군 4종 × binary32 필터 1,024개 = **4,096개** |
| 제한값·시드 | binary64 `max_gain=0.9999`, 입력 시드 `20261007`, 방식 순서 시드 `932851` |
| 측정 | 9회 반복, 각 반복에서 네이티브 배치 4회 실행, `perf_counter_ns` |
| C++ 빌드 | GCC 14.2.0, `-O3 -std=c++20 -ffp-contract=off`, fast-math 미사용 |
| 호스트 | 공유 Linux x86-64 환경에서 보고된 AMD EPYC 9V74, 논리 CPU 5개 노출, CPU 고정 미사용 |
| Python 환경 | Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, 기록된 그래프 의존성 Matplotlib 3.10.8 |

C++ 시간 단위는 **µs/필터, 9회 중앙값**입니다. 네 방식 모두 입력 유효성과 분모를 검사합니다. 격자 방식에는 미리 채운 삼각함수 캐시와 조기 거절을 허용하며, 캐시 생성 시간은 측정에 넣지 않았습니다.

| 시험군 | 정확한 정수 검사 | 1,024점 격자 | 16,384점 격자 | Float64 수식 검사 | 격자 1,024 / 정수¹ |
| --- | --- | --- | --- | --- | --- |
| 일반 필터 | 0.564106 | 1.686392 | 27.877729 | 0.011137 | 2.989× |
| 고공진 스트레스 | 0.599275 | 2.161358 | 33.816509 | 0.012064 | 3.607× |
| 이득 한계 근처 | 0.377707 | 0.932293 | 16.152820 | 0.011086 | 2.468× |
| 불안정 분모 | 0.008509 | 0.006741 | 0.007093 | 0.006717 | 0.792× |

¹ 마지막 열은 **두 중앙값의 비율**입니다. 반복별 비율의 중앙값과는 다릅니다. 두 통계량, 관측 최소·최대 및 측정 포함 범위는 [벤치마크 상세](benchmarks/BENCHMARKS.md)에 적었습니다.

![C++ 방식 4종 및 시험군 4종의 검사 시간](../../benchmarks/figures/native_latency.svg)

정수 검사는 앞의 세 시험군에서 1,024점 격자보다 빨랐지만, 불안정한 분모를 즉시 거절하는 경우에는 느렸습니다. **Float64 수식 검사는 훨씬 빠릅니다.** 반올림에 따른 오판이 있어도 이 강한 기준선을 제외하지 않았습니다. 이 수치는 배포 전 검사 시간이며 오디오 처리 속도나 음질 개선 수치가 아닙니다.

### 정확성과 Python 호출 비용은 별도 문제입니다

고공진 시험군의 유리수 참조 판정은 539개 합격, 485개 미충족입니다. 아래는 건수이며 실제 제품의 오류 발생률 추정이 아닙니다.

| 검사 방식 | 잘못된 합격 / 실제 미충족 485개 | 잘못된 거절 / 실제 충족 539개 |
| --- | --- | --- |
| 정확한 정수 검사 | 0 | 0 |
| 1,024점 격자 | 356 | 0 |
| 16,384점 격자 | 213 | 0 |
| Float64 수식 검사 | 2 | 5 |

나머지 세 시험군은 네 방식 모두 기록된 불일치가 0건입니다. 잘못된 합격은 **수학적 조건을 만족하지 않는 입력을 통과시켰다**는 의미이며, 임의의 피드백망이 반드시 발산한다는 뜻은 아닙니다.

![유리수 참조 판정 대비 고공진 오판](../../benchmarks/figures/high_q_correctness.svg)

![호출 비용을 포함한 Python API 비교](../../benchmarks/figures/python_latency.svg)

Python 그래프는 고공진 필터 128개에 대해 설치된 SciPy의 `signal.freqz`를 직접 호출합니다. 이 함수는 지정한 주파수의 응답을 계산하는 도구이지 정확한 인증기로 설명되는 함수가 아닙니다 [SCIPY-FREQZ]. Python 호출 비용과 C++ 배치 커널 시간을 섞어 비교하지 마십시오.

![격자 사이에 존재하는 해석적으로 확인된 공진](../../benchmarks/figures/hidden_peak.svg)

숨은 공진 예제는 `omega=pi/2`에서 이득이 정확히 2입니다. 그래프는 이 대수적 사실을 보여주는 그림이며, 촘촘하게 그린 곡선 자체가 증명은 아닙니다.

### 원시 자료와 재현

[전체 JSON·반복 시간](../../benchmarks/results/benchmark.json) · [CSV 요약](../../benchmarks/results/summary.csv) · [계수 배열](../../tools/restore_fixtures.py) · [프로토콜·소스 해시](../../benchmarks/results/protocol.json) · [환경](../../benchmarks/results/environment.json) · [원본 실행 로그](../../validation/runs/v0.1.0/benchmark_run.log)

```bash
python -m pip install '.[bench]'
python -m pip install -r benchmarks/requirements-bench-tested.txt
python tools/restore_fixtures.py
python tools/audit_benchmark.py --recheck-fixtures
# 명령 동작 점검용 작은 시험이며 공개 벤치마크와는 별개입니다.
python benchmarks/run.py --n 32 --trials 3 --out validation/my-smoke
# 원본 결과를 덮어쓰지 않는 전체 재측정:
python benchmarks/run.py --n 1024 --trials 9 --seed 20261007 --out validation/my-run
python benchmarks/plot.py --results validation/my-run/benchmark.json --out validation/my-run/figures
```

네이티브 벤치마크는 Linux/macOS의 GNU/Clang 도구 구성을 대상으로 합니다. Windows에서는 WSL을 사용하십시오. 그래프 내부 표기는 공통 영문이며 각 언어의 상세 가이드에 범례와 해석을 설명했습니다.

## 테스트와 연동

```bash
python -m unittest discover -s tests -v
python tools/documentation_smoke.py
python examples/cascade.py
# 선택적 C++ 빌드: C++20, CMake >=3.20, Boost >=1.74 헤더 필요
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
```

핵심 테스트는 **unittest 메서드 35개**이며 일부 메서드 내부에서 무작위 사례를 반복 검사합니다. 문서 스모크 테스트는 **12개 시나리오**를 추가로 확인합니다. 기존 벤치마크에는 배포 계수 4,096개와 별도 비트 패턴 2,048개가 있습니다. 서로 다른 검증 계층이며 외부 기관의 독립 검증 횟수가 아닙니다. 실패 예제·예산 초과·wheel 설치 검사·문제 해결은 [테스트 가이드](guides/TESTING.md)에 정리했습니다.

## 문서와 제한

| 문서 | 내용 |
|---|---|
| [사용 가이드](getting-started/USER_GUIDE.md) | 설치, 계수 의미, Python·SOS·CLI, 예산, C++, CI, 문제 해결 |
| [테스트 가이드](guides/TESTING.md) | 예상 출력, 합격·거절·보류, 회귀검사와 벤치마크 재현 |
| [벤치마크 상세](benchmarks/BENCHMARKS.md) | 분포, 모든 비교 방식, 시간 경계, 데이터 필드, 한계 |
| [연구 과정과 출처](development/PROVENANCE.md) | OpenAI 참고 위치, 의존 관계, 개발 단계별 근거 |
| [수학 가이드](mathematics/MATHEMATICS.md) | 유도식, 인증서 의미, 조건부 확장 |
| [API 계약](../reference/API.md) / [공개 절차](development/RELEASING.md) | 저수준 인터페이스 및 저장소·패키지 배포 절차 |

인증은 제공된 배포 계수의 이상적인 고정 선형 시스템에 한정됩니다. 실행 중 반올림·오버플로·리미트 사이클, 임의 변조·피드백 구조·AI 동작, 청각 보호, PSNR·STOI·PESQ를 증명하지 않습니다. `unknown`은 배포를 거절해야 합니다. JSON 인증서는 전자서명이나 악의적 입력에 대한 보안 샌드박스가 아닙니다.

[MIT 라이선스](../../LICENSE) · [NOTICE](../legal/NOTICE.md) · [보안](../../.github/SECURITY.md) · [이슈](https://github.com/dextune/dexted-dsp/issues). 새 수학의 발명·외부 독립 감사·물리적 기기 안전 인증을 주장하지 않습니다. CI 배지는 GitHub Actions 상태를 표시하며 [로컬 검증 기록](../../validation/rebrand/)과 구분됩니다.

[OAI-README]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/README.md
[OAI-325]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex
[OAI-DFT]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex
[CP-2017]: https://arxiv.org/abs/1702.00668
[SCIPY-FREQZ]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html
[PYPA]: https://packaging.python.org/en/latest/tutorials/packaging-projects/

**측정 이력.** 표의 수치는 이전 연구명 **CertifiedDSP**에서 기록한 결과입니다. Dexted DSP 변경은 이름·네임스페이스·CLI·인증서 스키마 변경이며 수학 판정식 변경이 아닙니다. 원본 측정값과 당시 소스를 보존합니다. [이름 변경 및 재현](../project/REBRANDING.md) · [소스 매핑](../../benchmarks/results/rebrand-map.json).

**소스 체크아웃 데이터:** NPZ는 Git에 저장하지 않고 필요할 때 재생성합니다. 고정된 벤치마크 의존성을 설치하고 `python tools/restore_fixtures.py`를 실행하십시오. 원본 SHA-256과 일치해야 하며 측정값은 바뀌지 않습니다.

<!-- benchmark-sha256: 0332cbc6a22ebf2da482a043b3f206ae175bcab5d71f640417c96c46c7ac99a0 -->

## 신규 소스 기능 (미출시)

[주파수 샘플링이 피크를 놓치는 데모](../../examples/hidden_peak/README.md) · [SOS 검사 및 엄밀한 최대 이득 구간 API](../product/inspection.md) · [미완료 검증·배포 조건](../product/implementation-status.md). 기존 벤치마크는 v0.1.0 기록이며 신규 코드 성능 측정이 아닙니다.


## 신규 소스: 최대 이득의 주파수 위치 격리

단일 안정 biquad에 대해 `localize_peak`는 전역 최대 이득의 모든 위치를 포함하는 `cos(ω)`의 **정확한 유리수 구간**을 반환합니다. Hz 표시는 **근삿값이며 인증된 Hz 구간이 아닙니다**. [수학적 근거](../research/proofs/peak-localization.md) · [25개 합성 SOS 파일럿](../../benchmarks/suites/PROTOCOL_V2.md). 외부 독립 검증은 별도입니다.
