# 06. 실측 벤치마크, 메모리·통계, 결과 공개

[문서 홈](README.md) · [기존 경쟁 비교](../../benchmarks/competitive/README.md)

## 1. 현행 pilot에서 반드시 개선할 사항

기준 commit의 `benchmarks/competitive/run.py`는 실제 SciPy/python-control을 호출하고 원시 timing을 남깁니다. 그러나 `proof_gate()`가 UNKNOWN을 `False`로 축약하고, oracle PASS와 그 결과가 다르면 assertion으로 전체 실행을 중단합니다. 현재의 작은 성공적 pilot과 별개로, 이 방식은 산업용 대규모 corpus의 미결 상태·실패 행을 온전히 보고하기에 부족합니다.

새 runner는 `mathematical_status`, `execution_status`, `deployment_decision`, `oracle_status`, `verification_status`를 분리해야 합니다. 모든 case 결과에 이유·proof 또는 failure witness·원시 입력·예산·오류를 남깁니다. 이 문서는 그 수정 계획이며 현재 source의 버그를 이미 고쳤다는 뜻이 아닙니다.

기존 합성 9건 수치와 그래프는 동결합니다. 새 결과로 과거 파일을 덮어쓰지 않고 `protocol-v2/run-id/` 같은 별도 버전 경로를 사용합니다.

## 2. 비교할 작업 계약

| 측정 이름 | 포함 작업 | 제외 또는 별도 측정 |
|---|---|---|
| numerical_response_scipy | `signal.freqz_sos` + 명시한 grid 판정 | 인증 아님, 준비 비용 별도 |
| numerical_response_control | `frequency_response` + 같은 주파수·정책 | 모델 변환 비용 별도 |
| exact_decision | 준비된 계수의 stability/gain predicate | 파싱·proof 소비·bounds 별도 |
| decision_and_verify | predicate + proof serialization + 독립 소비자 검증 | optional peak refinement 별도 |
| full_inspection | 입력 처리부터 보고서·bounds까지 | 명시한 I/O 포함 여부 |
| before_after_pipeline | 같은 기존 workflow vs workflow+검증 | 변경되지 않은 DSP 처리 작업은 같게 유지 |
| long_signal_adapter | 실제 파형과 기존 처리기의 처리·관측 | Dexted의 audio 처리속도로 표현 금지 |

SciPy의 SOS response와 python-control의 응답은 numerical evaluation입니다([S01](11_SOURCES_AND_BASELINE.md#s01), [S03](11_SOURCES_AND_BASELINE.md#s03)). 인증 기능이 추가되는 After는 동일한 작업량의 속도 경쟁이 아닙니다. 사용자 가치의 질문은 추가 비용을 감수할 만한 규격 위반을 얼마나 발견하고, 얼마나 자주 판정하지 못하는가입니다.

## 3. 공정성 조건

표현 계수, threshold, stability precheck, sampling grid와 endpoint 포함 여부, dtype, same host, single-thread 설정, cache/warmup, early-exit, 객체 생성 범위를 같게 맞춥니다. `control.frequency_response`의 단위는 rad/s이며 이산시간계에서 `ω·dt`로 unit circle을 평가하므로 dt=1 관례 또는 실제 dt 변환을 정확히 기록합니다. Hz/rad/sample 변환 오류를 unit test로 검출합니다.

SOS→하나의 고차 transfer polynomial로 바꾸는 과정은 부동소수점 변환 오차가 생길 수 있는 별도 boundary입니다. 기존 pilot의 방식은 그대로 설명하되, 새 비교에는 section-wise response product 또는 section-preserving representation을 추가하여 원래 SOS 값에 대한 비교인지 확인합니다. 준비 단계의 polynomial convolution 후 값을 원래 계수와 수학적으로 완전히 같다고 단정하지 않습니다. representation conditioning 문제와 Dexted 가치의 문제를 섞지 않습니다.

dense/adaptive numerical response도 보조 baseline으로 넣어 고정 1024 grid에만 유리한 사례를 선정하지 않습니다. 단 adaptive grid가 통과해도 mathematical certificate가 되는 것은 아닙니다. high-order norm 계산을 추가할 때는 요구 dependency·tolerance·수렴 실패를 공개합니다.

## 4. 시간 프로토콜

최소 30회 untrimmed time observations를 case/method별로 측정하고, warmup 수·randomized interleaving seed를 사전 고정합니다. 3개 독립 실행 session을 다른 시점에 수행하며 host state·CPU scaling·thermal·실행 우선순위·컨테이너 제한을 저장합니다.

p50/p95/p99의 percentile interpolation method를 고정합니다. 30회만으로 case별 p99가 안정적이라고 주장하지 않습니다. p99가 SLA에 중요하면 표적 family에서 1,000회 이상 관측하거나 표본 불확실성을 명시합니다. 측정 횟수를 늘려도 서로 비슷한 계수 9개의 산업 대표성이 높아지는 것은 아닙니다.

cold import, dependency import, warm prepared call, certificate verification, file I/O, 실패 path, UNKNOWN path의 latency를 분리합니다. 결과를 빨리 반환하는 FAIL만 모아서 API가 빠르다고 홍보하지 않습니다.

## 5. 비용 계산

paired trial이 확보되면 `delta_i = after_i - before_i`의 분포를 산출합니다. 서로 다른 pooled median의 차이는 `median(after)-median(before)`라고 적고 paired overhead라고 부르지 않습니다. 구체 사례마다 median/p95와 반복 관측 수를 보존합니다.

case를 무작정 풀링하지 않고 ordinary/high-Q/boundary/real/invalid와 section count별 결과를 먼저 냅니다. 전체 수치는 어떤 가중치로 모았는지 밝힙니다. 고객 분포를 모르면 “benchmark equal-case-weighted”라고 표시합니다. 고차 FAIL/UNKNOWN을 제외한 숫자를 기본 headline으로 사용하지 않습니다.

부트스트랩 신뢰구간은 case/session 계층을 보존하는 cluster resampling을 사용합니다. 30회 반복 호출을 독립적인 30개 제품 사례처럼 resample하지 않습니다. 0 observed failures는 “위험 0%”가 아닙니다. 독립 동일 분포 Bernoulli 표본에 한해서만 0실패의 한쪽 95% 상한 `1-0.05^(1/n)` 같은 해석이 가능하며, 구성된 adversarial corpus에는 그대로 적용하지 않습니다. 수학적 명제의 증명과 구현 표본의 통계도 별개입니다.

## 6. 메모리 프로토콜

`tracemalloc`만으로 native allocation이나 전체 RSS를 평가했다고 주장하지 않습니다. 다음 네 값을 별도로 측정합니다.

| 값 | 수집 방법 | 주의 |
|---|---|---|
| Python allocation peak | 별도 instrumented trials | time loop와 분리 |
| process peak RSS | isolated worker의 OS 계측 | Python·dependencies의 baseline도 포함 |
| incremental retained RSS | 동일 worker에서 작업 전·후·idle 측정 | allocator cache와 누수 구별 |
| native sanitizer/allocation | 지원 build에서 ASan/UBSan/allocator 도구 | instrumentation overhead 공개 |

방법별 worker를 분리하고 import 완료 baseline을 기록합니다. 이전 방법의 RSS high-water를 다음 방법에 귀속시키지 않습니다. Mac/Linux RSS 단위·Windows 계측 차이, 자식 프로세스 포함 여부를 명시합니다. 메모리 샘플러의 주기 때문에 짧은 spike를 놓칠 수 있으면 OS high-water와 함께 설명합니다.

장시간 자료 기본 경로는 chunk streaming입니다. peak RSS가 파일 전체 길이에 선형으로 증가하면 설계 결함입니다. input file cache/OS page cache를 core heap이라고 해석하지 않습니다. 93GB corpus의 압축률·download time은 별도 계측하며 core latency에 숨기지 않습니다.

## 7. 정확도·가용성·배포 정책 지표

`false_certified`, `wrong_mathematical_rejection`, `unknown_on_safe`, `unknown_on_unsafe`, `invalid_handling_error`, `oracle_unresolved`, `verification_failure`, `execution_error`, `not_run`를 고유 case별로 계산합니다. 별도로 `deployment_false_pass`와 `deployment_blocks_safe`를 계산합니다.

판정 coverage는 `(CERTIFIED + valid REJECTED)/(oracle resolved valid cases)`이며, 충분조건 알고리즘의 UNKNOWN은 coverage 부족으로 남습니다. 안전한 입력을 전부 UNKNOWN 처리해서 false PASS 0을 달성하는 제품은 실용성 목표를 통과하지 못합니다.

## 8. README·차트·증거 공개 규칙

첫 차트는 같은 계수에서 기존 측정값·실제 인증 범위·허용 한계를 보여줍니다. 두 번째는 두 comparator의 잘못된 배포 통과 감소를 표시합니다. 세 번째는 증가한 latency와 RSS를 보여줍니다. 실측과 analytical 값, input duration과 wall time, synthetic과 real을 시각적으로 구분합니다.

막대그래프는 0-origin 같은 단위를 기본으로 사용합니다. log axis가 꼭 필요하면 이유·눈금·정확한 숫자를 함께 표기합니다. p95를 작은 글씨에 숨기지 않고 family별 UNKNOWN도 보입니다. 원시 JSON/CSV에서 결정적으로 생성하고 차트의 값·모바일 가독성을 CI/수동 검토합니다. 근거 없는 speedup/음질/안전 광고는 차단합니다.

## 9. 완료 정의

같은 입력·정밀도·호스트의 최소 두 실제 comparator, 전량 raw observations, 통계 방법, 모든 불리한 행, memory scope, source/environment provenance가 존재해야 합니다. 최소 3 host-family와 외부 조직 1곳의 correctness reproduction이 없다면 “독립 검증된 산업 benchmark”라고 부르지 않습니다.
