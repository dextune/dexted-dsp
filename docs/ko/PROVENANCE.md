# 연구 과정과 OpenAI 참고 범위

[English](../en/PROVENANCE.md) · [한국어](../ko/PROVENANCE.md) · [简体中文](../zh-CN/PROVENANCE.md) · [日本語](../ja/PROVENANCE.md)

[Dexted DSP](../../README.ko.md)

## 1. “OpenAI를 참고했다”는 말의 세 가지 의미

**연구 자료:** [`openai/math` 원고 모음][OAI-README]에서 신호처리로 연결할 후보를 찾았습니다. **조건부 정리:** 특정 Crouzeix 원고를 별도 연구 문서의 가정으로 사용했습니다. **AI 보조 개발:** 이 저장소는 대화형 연구·프로그래밍 과정에서 구성했습니다. 세 가지는 서로 다릅니다. 실행 엔진이 OpenAI 구현이라는 뜻도, OpenAI가 감사했다는 뜻도, 측정한 속도 개선이 새로운 OpenAI 정리라는 뜻도 아닙니다.

원본 저장소는 원고들의 검증 단계가 서로 다르다고 명시합니다. 그 저장소에 원고가 존재한다는 사실만으로 이를 참고한 DSP 프로그램을 형식 검증 완료라고 표시할 수는 없습니다 [OAI-README].

## 2. 고정한 원문 버전과 위치

| ID | 원문·참고 위치 | 사용한 부분 |
|---|---|---|
| OAI-README | 커밋 `adc7f1241b42e322a6451854ab7e4b4c146bf78a`의 `README.md` | 자료 출처와 검증 단계 주의사항 |
| OAI-325 | *A direct proof of the complete Crouzeix inequality*, 2026-09-26, `build/main.tex` §1의 `thm:main`, `W(A)`·`P[A]` 정의 | 행렬 계수 다항식의 완전형 상수 2 부등식을 조건부 가정으로 사용 |
| OAI-DFT | *An explicit power saving for the exact discrete Fourier transform*, 2026-09-25, `build/sections/introduction.tex`의 계산 모델 및 `cor:decimal` 다음 제한 설명 | 연구 범위를 정할 때 참고. 부동소수점 FFT 구현이나 속도 실험에 사용하지 않음 |

전체 고정 URL과 Git blob 해시는 [sources.json](../provenance/sources.json)에 기록했습니다. 정리 내용은 LaTeX 원문으로 확인했고 Lean 커널을 실행하지 않았습니다. 날짜는 참고한 원고의 날짜이며 이후 수정본의 최신성을 주장하지 않습니다.

[OpenAI 주정리 원문][OAI-325] · [OpenAI DFT 계산 모델과 제한][OAI-DFT]

사용한 Crouzeix 가정은 다음과 같습니다.

$$\|P[A]\|_2\le 2\max_{z\in W(A)}\|P(z)\|_2,\qquad P[A]=\sum_k A^k\otimes B_k.$$

채널 계수 행렬이 가환하지 않을 수 있으므로 **행렬 계수·완전형**이라는 조건이 중요합니다. 비교 대상은 Crouzeix–Palencia의 2017년 완전형 상수 `1+sqrt(2)`입니다 [CP-2017]. 여기서 OpenAI의 일반적인 상수 2 증명 전체를 독립 재검증한 것은 아닙니다.

## 3. 실제 코드의 의존 관계

| 구성 요소 | 필요한 수학 | 상태 |
|---|---|---|
| `src/dexted_dsp/biquad.py`, `cpp/include/dexted_dsp/biquad.hpp` | 기본 Schur/Jury 조건, 이차식 양수성, 정확한 이진 유리수 연산 | 실행 가능. OpenAI의 새 정리와 독립적 |
| `src/dexted_dsp/cascade.py` | 크기 제곱 다항식의 곱, Bernstein 양수성·구간 분할 | Python 실행 가능. 자원 제한이 있는 충분조건 인증 |
| `reference.py`, `verify.py` | 별도로 표현한 유리수 연산과 구간 덮개 검사 | 재검사이며 외부 기관 인증은 아님 |
| `benchmarks/kernels.cpp` | 정수식, 주파수 샘플링, float64 수식 기준선 | 측정 대상. Crouzeix에 의존하지 않음 |
| [조건부 연구 문서](../math/crouzeix.md) | 일반 기저 행렬에 대해 OAI-325를 가정 | 문서만 제공. 제품 API 없음 |

고전적인 수학 방법을 새로 발명했다고 주장하지 않습니다. 배포 계수의 의미를 명확히 하고, 정확한 정수 판정·검사 가능한 인증서·별도 표현의 재검사·인터페이스·재현 가능한 비교를 구성한 것이 구현상의 기여입니다.

## 4. 개발 단계와 확인할 수 있는 산출물

아래는 공개 가능한 작업 산출물 중심의 과정입니다. 검증되지 않은 “무한 최적화” 수행 횟수를 주장하지 않습니다.

| 단계 | 결정·구현 내용 | 이 공개판의 근거 |
|---|---|---|
| 연구 범위 선정 | 원고 모음에서 신호처리 연결을 검토하고 점근 이론과 실용 알고리즘을 구분 | 고정한 원문 목록, 이 문서 |
| 가정 분리 | 일반 Crouzeix 확장은 조건부 문서로 남기고 실행 엔진에서 제외 | `docs/math/crouzeix.md`, 코드 의존 관계 |
| 처리 대상 고정 | 고정 계수 실수 2차 필터, 명시적 배포 정밀도, 엄격한 이득 제한 | `model.py`, 수학 문서 |
| 정확 판정 구현 | 이진 유리수를 정수화해 안정성·양 끝점·필요한 내부 최솟값 검사 | `biquad.py`, C++ 헤더 |
| 체인 확장 | 주파수별 보상을 유지한 전체 다항식 양수성 인증 | `cascade.py`, `verify.py` |
| 별도 유리수식 대조 | `Fraction` 비교, 원본 입력 결속, 위조·판정보류 거절 | `tests/test_dexted_dsp.py` |
| 비교의 공정성 검토 | 빠른 float64 기준선을 유지하고, 격자 캐시·조기 거절·입력 검사를 맞춤 | `benchmarks/run.py`, `kernels.cpp`, `protocol.json` |
| 중간 결과 보존 | 유리한 실행만 고르지 않고 검토·입력 검증 전후 자료를 보존 | `validation/benchmark_before_review*`, `benchmark_before_input_validation*` |
| 패키징 | Python·C++·CLI, 설치 검사와 로컬 로그 | 원본 `validation/summary.json`, 빌드 로그 |
| 문서 개정 | 4개 언어 문서, 출처 추적, 저장 자료 감사, 예제 재실행·작은 벤치마크 실행 점검 | `validation/docs_refresh/`, 측정 소스 해시 동일 |

선행 아카이브 해시는 [sources.json](../provenance/sources.json)에 있습니다. 이전 대화의 다른 측정값·미디어 실험·벤치마크 수정본을 **현재 측정 결과로 옮겨 쓰지 않았습니다.** 현재 README의 수치는 `benchmarks/results/benchmark.json` 하나에서 가져옵니다.

## 5. 조건부 확장 결과의 의미

OAI-325를 가정하면 독립적인 텐서 축 중 비정규 축 `r`개에 대한 계수는 `2^r`이며 정규 축의 비용은 1입니다. 공통 고정 기저에 대해 채널 계수 다항식만 바뀌는 경우 전체 곱의 상계는 `(2q)^T`가 아닌 `2 q^T`입니다. 상대 상태 교란 `epsilon`을 추가하면 충분한 감쇠 조건 `q+2 epsilon<1`을 얻습니다.

동일한 논증에 기존 상수 `1+sqrt(2)`를 사용하는 경우와 비교하면, 인증 가능한 교란 반경의 충분조건이 `(1+sqrt(2))/2-1`, 약 **20.71%** 넓어집니다. 이는 두 충분조건의 수식 비교입니다. 측정한 음질·화질, 실제 최대 강인성 또는 모든 시변 시스템에 대한 일반 인증이 아닙니다. 상세 증명과 가정은 [연구 문서](../math/crouzeix.md)에 남겼습니다.

## 6. 출처·재사용·검증의 한계

OpenAI·ADAC 구현, 원고 소스, 음원·영상, 모델 가중치나 비공개 자격증명을 동봉하지 않았습니다. 링크는 출처이지 보증이나 제휴 표시가 아닙니다. 선행 구현의 MIT 고지를 [LICENSE](../../LICENSE)와 [NOTICE](../../NOTICE.md)에 유지했습니다. Boost는 외부 C++ 빌드 의존성이며 NumPy·SciPy·Matplotlib은 선택적 벤치마크 도구입니다.

일반 Crouzeix 원증명, 모든 컴파일러 최적화의 건전성, 물리적 기기 동작을 독립 감사하지 않았습니다. 조건부 연구 문서를 제거하더라도 현재 정확 biquad·체인 실행 코드와 측정 결과의 수학적 근거는 바뀌지 않습니다.

[OAI-README]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/README.md
[OAI-325]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex
[OAI-DFT]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex
[CP-2017]: https://arxiv.org/abs/1702.00668
[SCIPY-FREQZ]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html
[PYPA]: https://packaging.python.org/en/latest/tutorials/packaging-projects/
