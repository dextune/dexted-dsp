# 벤치마크 방법·결과·재현 안내

[English](../en/BENCHMARKS.md) · [한국어](../ko/BENCHMARKS.md) · [简体中文](../zh-CN/BENCHMARKS.md) · [日本語](../ja/BENCHMARKS.md)

[Dexted DSP](../../README.ko.md)

## 1. 질문과 자료 출처

실험의 질문은 **구현별 엄격한 biquad 이득 검사 시간이 얼마이며, 구성한 입력에서 어떤 수치 방식이 정확한 유리수 판정과 달라지는가**입니다. 음성 향상, 영상 복원, FFT 속도 또는 OpenAI Crouzeix 정리를 실험한 것이 아닙니다.

아래 표는 [benchmark.json](../../benchmarks/results/benchmark.json)에서 산출했습니다. 원본 v0.1.0 실행이며 [environment.json](../../benchmarks/results/environment.json)의 기록 시각은 `2026-10-07T14:04:45.884162+00:00`입니다. 이번 개정은 저장된 자료를 감사하고 **별도의** 작은 실행 점검을 수행했습니다. 더 빠른 결과로 원본을 바꾸지 않았습니다.

## 2. 판정 대상과 비교 구현

검사하는 조건은 실수 분모 `z²+a1 z+a2`가 엄격히 Schur 안정이고, 동시에 `sup |H(exp(i omega))| < gamma`라는 것입니다. 제한값은 binary64 `gamma=0.9999`입니다. 입력은 binary32로 저장한 후 값이 변하지 않도록 상위 정밀도로 읽습니다. 등호는 불합격입니다.

| 방식 키 | 구현 | 의미 |
|---|---|---|
| `integer` | 배포 C++ 헤더의 정수 계수 해석, Jury 조건, 정확한 이차식 부호 검사 | 제공된 계수와 명시한 모델에 대해 정확 |
| `grid1024` | 자체 기준선. `[0,pi]` 양 끝점을 포함한 균일 격자, 복소 double 응답, 삼각함수 캐시 | 샘플만 검사하며 연속 구간 인증은 아님 |
| `grid16384` | 같은 코드를 16,384개 주파수로 실행 | 격자를 늘려도 증명이 되지는 않음 |
| `float64_algebraic` | 동일한 Jury·이차식 아이디어를 binary64로 계산. 구간 연산 없음 | 매우 빠르지만 상쇄로 부호가 달라질 수 있음 |
| `python_integer_api` | 실제 Python 공개 API | 인증서 객체 구성과 호출 비용 포함 |
| `fraction_reference` | `reference.py`의 별도 유리수 표현 | 참조 판정이며 외부 검증은 아님 |
| `scipy_freqz1024` | 설치된 SciPy `signal.freqz` 호출과 분모·제한값 검사 | Python 응답 샘플링 비교이며 C++ 커널이 아님 |

SciPy 문서는 `freqz`를 주파수 응답 계산으로 설명합니다 [SCIPY-FREQZ]. 네이티브 격자 코드는 SciPy나 ADAC 코드를 복사하지 않았습니다. 이 공개판은 ADAC 전체 처리, SLICOT, MATLAB 또는 모든 H-infinity 해법과 비교하지 않습니다.

## 3. 데이터 생성과 정밀도

NumPy 난수 시드는 **20261007**입니다. [run.py](../../benchmarks/run.py)의 `generate()`가 시험군별 1,024개를 생성한 뒤 전체 계수 배열을 연속 메모리의 binary32로 변환합니다. 모두 합성 데이터이며 실제 녹음이나 제품 사용 빈도를 반영하지 않습니다.

| 시험군 | 최종 binary32 변환 전 생성 방식 |
|---|---|
| 일반 | 극점 반경 `[0.02,0.995)` 균등분포, 각도 `[0.02,pi-0.02)` 균등분포, 분자 3개는 평균 0·표준편차 0.25 정규분포 |
| 고공진 | `scipy.signal.iirpeak(f,Q)`, `f`는 `[0.005,0.995)`, `Q=10^U`에서 `U`는 `[2,6)` 균등분포. 분자에 `10^V`, `V`는 `[-0.4,0.4)`를 곱함 |
| 한계 근처 | 1차 필터를 biquad에 넣음. 극점 `r`은 `[0.02,0.99)`, 최대 이득은 `1+U`, `U`는 `[-0.0005,0.0005)` |
| 불안정 분모 | 공액 극점 반경 `[1.00001,1.3)`, 위와 같은 각도 범위, 분자 표준편차 0.1 |

| 시험군 | 필터 수 | 정확 판정 합격 | 정확 판정 미충족 |
| --- | --- | --- | --- |
| 일반 필터 | 1024 | 611 | 413 |
| 고공진 스트레스 | 1024 | 539 | 485 |
| 이득 한계 근처 | 1024 | 431 | 593 |
| 불안정 분모 | 1024 | 0 | 1024 |

기준 정답은 더 촘촘한 격자가 아닌 `Fraction`으로 계산합니다. Python 정수와 C++ 정수가 이 참조 판정과 일치해야 측정을 진행합니다. 추가로 시드 `20261107`, 제한값 1.0에서 **binary32 임의 비트 패턴 2,048개 행**을 검사합니다. 잘못된 입력은 오류를 반환해야 합니다. 이는 이식·비트 해석 검사이지 다섯 번째 속도 시험군이 아닙니다.

Python 비교에는 고공진 데이터의 **처음 128개**를 재사용합니다. 독립적인 홀드아웃 자료가 아닙니다. 시드를 고정한 것은 재현성을 위한 것이며 사전 등록이나 모집단 대표성을 주장하지 않습니다.

## 4. 시간 측정의 범위와 공정성

네이티브 방식은 GCC 14.2.0에서 `-O3 -std=c++20 -shared -fPIC -ffp-contract=off`로 함께 컴파일했습니다. fast-math는 사용하지 않았습니다. 9회 반복마다 시드 **932851**로 실행 순서를 섞습니다. 각 방식은 측정 직전에 한 번 호출해 해당 격자의 캐시를 준비한 후 전체 배치를 4번 실행합니다.

$$t_{\text{filter},\mu s}=\frac{t_{\text{elapsed},ns}}{1024\cdot4\cdot1000}.$$

`time.perf_counter_ns`를 사용합니다. 네이티브 시간에는 배치에 분산된 ctypes 호출 비용, 결과 기록, 입력 검사와 분모 검사가 포함됩니다. 데이터 생성·참조 정답 계산·정확성 비교·격자 캐시 생성은 제외합니다. 격자는 위반을 발견하면 조기 종료하며 제곱근·나눗셈 없이 크기 제곱을 비교합니다.

Python은 별도의 필터별 루프, 캐시된 omega 벡터, 4개 모델 워밍업을 사용합니다. 필터 객체는 **측정 전에** 만들며, 실제 함수 호출·정확 API의 인증서 객체 구성·루프·결과 리스트 비용은 포함합니다. SciPy는 전체 응답 벡터를 계산하므로 C++ 조기 종료 커널과 연산량이 같지 않습니다. 두 실험을 구분하십시오.

호스트는 AMD EPYC 9V74, Linux x86-64, 논리 CPU 5개 노출, Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0을 보고했습니다. `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`이며 MKL 설정은 없었습니다. **CPU 고정·동작 주파수 통제·전용 머신은 사용하지 않았습니다.** 시간은 해당 환경의 관측값이지 이식 가능한 성능 보장이 아닙니다.

## 5. C++ 결과와 통계량

단위는 모두 **µs/필터**입니다. 막대는 중앙값, 수염은 9회 관측의 최소·최대이며 **신뢰구간이 아닙니다.**

| 시험군 | 정확한 정수 검사 | 1,024점 격자 | 16,384점 격자 | Float64 수식 검사 | 격자 1,024 / 정수¹ |
| --- | --- | --- | --- | --- | --- |
| 일반 필터 | 0.564106 | 1.686392 | 27.877729 | 0.011137 | 2.989× |
| 고공진 스트레스 | 0.599275 | 2.161358 | 33.816509 | 0.012064 | 3.607× |
| 이득 한계 근처 | 0.377707 | 0.932293 | 16.152820 | 0.011086 | 2.468× |
| 불안정 분모 | 0.008509 | 0.006741 | 0.007093 | 0.006717 | 0.792× |

¹ 본문의 속도비는 `median(격자 시간) / median(정수 시간)`입니다. JSON에는 다른 통계량인 `median(격자_i / 정수_i)`도 저장합니다.

| 시험군 | 반복별 비율의 중앙값 |
| --- | --- |
| 일반 필터 | 3.037857× |
| 고공진 스트레스 | 3.502723× |
| 이득 한계 근처 | 2.433858× |
| 불안정 분모 | 0.786818× |

관측 시간 범위:

| 시험군 | 정확한 정수 검사 | 1,024점 격자 | 16,384점 격자 | Float64 수식 검사 |
| --- | --- | --- | --- | --- |
| 일반 필터 | 0.538766 – 0.621713 | 1.570972 – 1.937667 | 26.413858 – 29.532372 | 0.010687 – 0.012078 |
| 고공진 스트레스 | 0.570299 – 0.719463 | 2.028531 – 4.190899 | 32.702964 – 41.433221 | 0.011120 – 0.015795 |
| 이득 한계 근처 | 0.360094 – 0.428116 | 0.876417 – 0.980895 | 14.860312 – 17.181955 | 0.010205 – 0.015665 |
| 불안정 분모 | 0.008354 – 0.008915 | 0.006572 – 0.007166 | 0.006672 – 0.010472 | 0.006342 – 0.008800 |

![C++ 검사 시간](../../benchmarks/figures/native_latency.svg)

앞의 세 시험군은 정수 검사에 유리하지만, 불안정 분모 즉시 거절은 수치 방식에 유리합니다. Float64 수식 검사는 전체적으로 더 빠릅니다. 비교의 핵심은 상쇄 근처의 정확성 비용이지 모든 방식에 대한 절대적인 속도 우위가 아닙니다. CI에는 “항상 더 빨라야 합격”이라는 조건이 없습니다.

## 6. 정확성: 수치마다 분모를 구분해야 합니다

고공진 자료의 `false_accepts`는 정확한 두 조건이 거짓인데 1을 반환한 경우, `false_rejects`는 조건이 참인데 0을 반환한 경우입니다. **참조 미충족 485개**, **참조 합격 539개**입니다.

| 검사 방식 | 잘못된 합격 / 실제 미충족 485개 | 잘못된 거절 / 실제 충족 539개 |
| --- | --- | --- |
| 정확한 정수 검사 | 0 | 0 |
| 1,024점 격자 | 356 | 0 |
| 16,384점 격자 | 213 | 0 |
| Float64 수식 검사 | 2 | 5 |

구성한 스트레스 분포의 건수입니다. 예를 들어 잘못된 합격 356개는 **356%가 아니며**, 전체 1,024개로 나눈 비율과 실제 미충족 485개로 나눈 비율은 서로 다른 질문에 답합니다. 실제 제품 위험 빈도를 추정하지 않습니다. 다른 시험군은 네 방식 모두 불일치 0건입니다. 음수 반환은 `invalid_or_error`로 별도 기록하고 합격시키지 않습니다.

![고공진 오판 건수](../../benchmarks/figures/high_q_correctness.svg)

참조 구현도 같은 프로젝트 안에 있습니다. 일치는 유용한 회귀검사 근거지만 독립적인 수학 증명이나 외부 기관 감사가 아닙니다. 정확한 부호만으로 충분한 이유는 유도식에서 설명하며, 촘촘한 격자 비교만으로 이를 증명할 수는 없습니다.

## 7. Python 결과·체인 예제·숨은 공진

| Python 수준 방식 | 중앙값 µs/필터 |
| --- | --- |
| python_integer_api | 7.811008 |
| fraction_reference | 63.969969 |
| scipy_freqz1024 | 71.832703 |

![Python API 검사 시간](../../benchmarks/figures/python_latency.svg)

고공진 128개, 9회 반복이며 C++와 시간 범위가 다릅니다. 이를 언어를 섞은 알고리즘 속도 비교로 해석하지 마십시오.

저장된 `cascade_demo`의 두 안정한 필터는 전체 전달함수가 정확히 **0.75**입니다. 각 필터는 개별 이득 1 검사를 통과하지 못하지만 합동 인증은 통과하고 유리수로 덮개를 재검사합니다. 이는 정확성 예제이지 체인 속도 연구가 아닙니다. C++ 막대에는 SOS 체인 시간이 없습니다.

![숨은 공진 예제](../../benchmarks/figures/hidden_peak.svg)

`alpha=2^-14`일 때 `H(z)=alpha(1-z^-2)/(1+(1-alpha)z^-2)`의 `omega=pi/2` 이득은 2입니다. 양 끝점을 포함한 1,024점 격자는 pi/2를 정확히 포함하지 않습니다. 그림은 해석적으로 아는 값을 보여주며 샘플 곡선으로 최대값을 인증하지 않습니다.

## 8. 자료 위치와 JSON 필드

| 파일·필드 | 의미 |
|---|---|
| `benchmark.json → families.NAME.median_us.METHOD` | 시험군·방식의 기록된 중앙값 |
| `families.NAME.raw_us_per_filter.METHOD` | 반복 순서를 유지한 9개 원시 시간 |
| `families.NAME.correctness.METHOD` | 잘못된 합격·거절·입력 오류 건수 |
| `families.NAME.exact_pass` | 정확한 두 조건을 모두 만족한 수 |
| `paired_grid1024_over_integer` | 반복별 비율의 중앙값. 중앙값의 비율과 다름 |
| `python_high_q` | 별도 API 실험의 입력 수와 모든 반복 시간 |
| `native_bit_patterns` | 별도 비트 해석·잘못된 입력 대조 검사 |
| [fixtures.npz](../../tools/restore_fixtures.py) | 저장한 binary32 배열. `allow_pickle=False`로 로드 |
| [protocol.json](../../benchmarks/results/protocol.json) | 시드·개수·컴파일 명령·코드 파일 12개의 SHA-256 |
| [environment.json](../../benchmarks/results/environment.json) | 기록 당시 호스트와 설치 버전 |
| [summary.csv](../../benchmarks/results/summary.csv) | 중앙값·범위·건수의 파생 자료. 새 측정이 아님 |
| [검증 로그 안내](../../validation/README.md) | 원본 빌드·검사 이력과 중간 검토 자료 |

## 9. 기준 자료를 덮어쓰지 않는 재현

프로젝트 환경에 `.[bench]`를 설치합니다. `requirements-bench-tested.txt`는 당시 버전 기록입니다. 다른 Python 버전에서는 호환되는 선택 의존성을 사용하고 그 차이를 기록하십시오.

```bash
python tools/audit_benchmark.py
python tools/audit_benchmark.py --recheck-fixtures
python benchmarks/run.py --n 32 --trials 3 --out validation/my-smoke
```

Linux/macOS에서 전체 측정:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python benchmarks/run.py \
  --n 1024 --trials 9 --seed 20261007 --out validation/my-run
python benchmarks/plot.py --results validation/my-run/benchmark.json \
  --out validation/my-run/figures
python tools/audit_benchmark.py --results validation/my-run/benchmark.json --recheck-fixtures
```

Windows의 네이티브 벤치마크는 WSL에서 실행하십시오. `run.py` 기본 경로는 `benchmarks/results`를 덮어쓰므로 검토 중에는 `--out`을 사용합니다. 측정 대상 코드가 바뀌면 해시 감사가 실패하는 것이 정상입니다. 바뀐 알고리즘은 새로 측정해야 하며 기존 해시를 편집해서 맞추면 안 됩니다.

같은 시드라도 의존성·플랫폼에 따라 생성 계수와 시간이 달라질 수 있습니다. 원본 입력을 감사하려면 재생성한 계수만 보지 말고 **저장된 NPZ**를 사용하십시오. 배열이 같아도 NPZ를 다시 압축하면 파일 바이트가 달라질 수 있으며 감사는 제공한 파일 자체의 해시를 확인합니다.

## 10. 검토 한계

GCC 14.2/Boost 인라인 경고는 `validation/benchmark_run.log`에 보존했으며 숨기지 않았습니다. 기존 sanitizer 검사는 실행한 사례에서 통과했을 뿐 모든 입력을 보장하지 않습니다. 고차·MIMO 범용 솔버, ADAC 전체 성능, 실시간 처리량, 음질·화질, 실행 중 산술 안전 또는 원정리 검증을 주장하지 않습니다. `validation/docs_refresh/benchmark_smoke`는 별도 명령 실행 점검이며 README 그래프의 근거 데이터가 아닙니다.

[OAI-README]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/README.md
[OAI-325]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex
[OAI-DFT]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex
[CP-2017]: https://arxiv.org/abs/1702.00668
[SCIPY-FREQZ]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html
[PYPA]: https://packaging.python.org/en/latest/tutorials/packaging-projects/

<!-- benchmark-sha256: 0332cbc6a22ebf2da482a043b3f206ae175bcab5d71f640417c96c46c7ac99a0 -->


**측정 이력.** 표의 수치는 이전 연구명 **CertifiedDSP**에서 기록한 결과입니다. Dexted DSP 변경은 이름·네임스페이스·CLI·인증서 스키마 변경이며 수학 판정식 변경이 아닙니다. 원본 측정값과 당시 소스를 보존합니다. [이름 변경 및 재현](../REBRANDING.md) · [소스 매핑](../../benchmarks/results/rebrand-map.json).


**소스 체크아웃 데이터:** NPZ는 Git에 저장하지 않고 필요할 때 재생성합니다. 고정된 벤치마크 의존성을 설치하고 `python tools/restore_fixtures.py`를 실행하십시오. 원본 SHA-256과 일치해야 하며 측정값은 바뀌지 않습니다.
