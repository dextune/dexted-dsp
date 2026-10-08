# 05. 다층 테스트 프로토콜과 독립 오라클

[문서 홈](README.md) · [데이터 전략](04_DATASET_AND_LONGRUN.md)

## 1. 실행 순서

`manifest/license 검증 → 입력 freeze → 오라클 정답 계산 → core/consumer 교차검증 → 실제 DSP adapter 장시간 처리 → 배포 게이트 fault injection → 운영 soak → 통계 산출 → 외부 재현` 순서로 수행합니다. 단계별 결과는 독립된 artifact입니다. 오라클의 실패 때문에 원본 사례가 결과 파일에서 사라지면 안 됩니다.

각 실행은 plan_version, fixture_hash, source SHA, dependency lock, binary build, host, arithmetic settings, command line, seed, start/end UTC, raw observations, 종료 코드, incomplete 여부를 기록합니다. 일부 자료만 실행했을 때 실제 실행 ID 목록과 선택 규칙을 명시합니다.

## 2. 계수·수학 테스트 A

| Test ID | 대상 / 자극 | 기대 행동 | 실패 증거 |
|---|---|---|---|
| A-001 | 안전한 dyadic biquad, gamma에 충분한 여유 | core CERTIFIED, consumer true, exact oracle PASS | 세 상태·입력·proof |
| A-002 | 기존 hidden peak와 여러 peak 위치 변형 | 고정 grid가 놓쳐도 exact FAIL 또는 정당한 UNKNOWN | peak witness와 grid settings |
| A-003 | exact unity/equality, gamma 1 ULP 전후 | strict 조건의 등호 거절 | rational threshold·최솟값 |
| A-004 | 안정성 경계 `a2=±1`, Jury endpoint=0 | 안정성 거절, gain 통과와 혼동 금지 | 실패 section·exact inequalities |
| A-005 | 전체 gain 보상되는 cascade | section별 gain만 보고 과잉 거절하지 않음 | 전체 gap polynomial·oracle |
| A-006 | 전체 TF에서 취소되는 불안정 section | per-section 정책에 따라 거절 | cancellation 전후 명시 |
| A-007 | f64 설계값과 f32 export가 다른 사례 | 실제 export값만 인증 | raw hex·rounding recipe |
| A-008 | 비경계 1~16 SOS, 다수 family | 정답 일치, ordinary UNKNOWN 목표 확인 | family별 분모/미결 수 |
| A-009 | 17~32 SOS, 높은 차수·큰 rational | 시간/메모리 상한 준수 | UNKNOWN reason·nodes·RSS |
| A-010 | proof cover에 gap/duplicate/깊이 변조 | consumer false | 원본·변조 proof hash |
| A-011 | gamma/fs/precision/input hash 바꿈 | 외부 기대 입력과 mismatch로 거절 | 변경 필드·상태 |
| A-012 | NaN/Inf/complex/nonunit a0/초대형 자료 | 명확한 invalid, worker 보호 | resource·parser log |
| A-013 | 보간·정규화·section 재순서 | artifact 변경 감지, 필요 시 재인증 | transformation chain |
| A-014 | 동일 입력 legacy v1/v2 proof | 문서화된 호환성 또는 명확한 unsupported | matrix result |
| A-015 | native f32와 Python exact f32 | 정책·판정 일치, error code 보존 | ABI/build/coeff hashes |

### Oracle PASS/FAIL/UNRESOLVED와 관측 결과

정답을 아는 유효 사례에서 `truth=FAIL & verdict=CERTIFIED`는 unsafe false acceptance입니다. `truth=PASS & verdict=REJECTED`는 잘못된 수학적 거절입니다. `truth=PASS & verdict=UNKNOWN`은 incomplete decision이며, 안전을 위해 배포는 차단하지만 수학적 false rejection으로 합치지 않습니다. 정책-level blocked-safe rate는 별도 지표로 셉니다.

invalid 자료는 유효 필터 정확도 분모와 분리합니다. oracle unresolved를 라이브러리 실패나 성공으로 임의 분류하지 않습니다. 실행이 중단되어 아직 평가되지 않은 사례는 NOT_RUN으로 남깁니다. 계산한 일부 성공만 요약하여 전체 100,000건 통과라고 보고하지 않습니다.

## 3. 독립성·회귀·fuzz

producer의 polynomial helper를 오라클이 재사용하지 않도록 import dependency를 검사합니다. SymPy exact QQ root counting을 주 오라클로 유지하고 분석적으로 정답을 아는 family를 보조 오라클로 제공합니다. floating dense grid와 `mpmath` 고정 정밀도 계산은 진단/근사 교차검사이며 interval/정확한 부호 인증 없이는 정답의 최종 근거가 아닙니다.

모든 발견된 반례를 minimal regression fixture로 줄이고 축약 전 원본 해시를 보존합니다. 삭제가 아니라 별도 quarantine 상태로 관리합니다. 입력형 fuzz와 수학 계수 fuzz를 분리하여 50,000 cases/night를 초기 운영 목표로 둡니다. 시간이 오래 걸리는 고차수는 정해진 nightly budget 밖의 slow lane에서 계속 추적합니다. 성능이 불리하다고 구성 비율을 낮추지 않습니다.

## 4. 장시간 신호 테스트 B

### 4.1 시험 행렬

최소한 24건 합성 전량과 승인된 20건 실자료를 실제 frame 단위로 처리합니다. 모두 같은 필터 하나로만 처리하지 않고 각 기록에 ordinary, high-Q, cascade compensation, large-internal-state를 최소 한 번씩 배치합니다. 전체 전수 cross product를 항상 실행할 필요는 없지만 pairwise coverage와 위험 조합의 필수 full run을 사전에 고정합니다.

precision은 f32/f64, rate는 자료의 원본값 및 승인된 resampling variant, block은 1/127/128/129/255/256/257/1024/4093/65536을 포함합니다. tiny block 전체 24h가 과도할 경우 짧은 경계 case와 장시간 가변 block schedule을 별도 실험으로 정의합니다. 짧은 경계 결과를 24h tiny-block 처리로 표시하지 않습니다.

### 4.2 실행 중 보존할 것

블록 사이 필터 state, 채널 상태의 격리, 절대 sample index, clock/gap metadata, 변환된 계수 artifact hash를 보존합니다. 정확한 초기 rest와 임의 비영 초기 상태 시험을 분리합니다. warmup과 tail을 잘라냈다면 그 길이와 목적을 기록합니다. “전체 파일”이라는 지표에서는 처리한 warmup/tail도 frame count에 반영합니다.

### 4.3 계측 항목

입력·출력·내부 state의 peak/RMS, NaN/Inf/overflow count, subnormal 관측, f32 대 f64 error, high precision window error, chunk-invariance, dropped/duplicated frame, 마지막 frame index, raw input/output SHA를 기록합니다. 고정 window의 max error만으로 전체 max error를 추정하지 않습니다.

정밀도 오차 허용값은 모든 필터에 임의로 같은 `1e-6`을 적용하지 않습니다. ordinary/reference filter의 사전 허용오차와 high-Q/conditioned filter의 상대·절대·에너지 오차를 구분합니다. 작은 참조 출력에서 relative error가 폭증하는 경우 absolute floor를 사전에 정합니다. 허용오차를 시험 결과에 맞춰 사후 완화하지 않습니다.

이번 bootstrap의 `3e-6`은 제공한 두 dyadic section 참조 필터에만 적용되는 regression 상한이며, 산업용 일반 필터의 공인 정확도 규격이 아닙니다.

### 4.4 필수 negative control

상태를 블록마다 0으로 만드는 adapter, 채널 state를 공유하는 adapter, 한 frame을 건너뛰거나 두 번 처리하는 adapter, 잘못된 precision label, stale coefficient hash를 주입합니다. 이들 의도적 결함을 검사기가 놓치면 정상 자료의 PASS도 신뢰하지 않습니다.

지나치게 좁은 공진을 검출하기 위해 peak dwell과 off-peak control을 짝지어 실행합니다. 짧은 sweep에서 출력이 작다고 실제 전 대역 최대값이 작다고 판단하지 않습니다. 실제 renderer에 clipping/nonlinearity가 있으면 ideal LTI reference와 비교할 수 있는 범위를 명시합니다.

## 5. 운영 내구 테스트 C

**가상 입력 길이와 벽시계 시간은 다릅니다.** 24h 신호를 10분에 처리했으면 24h material coverage, 10분 execution입니다. worker soak는 실제 monotonic wall time을 측정합니다.

| Test ID | 시나리오 | 요구 결과 |
|---|---|---|
| C-001 | 24h 연속 작업 큐 ×3회, 여러 입력 family | hang·메모리 누수·누락 job 없음 |
| C-002 | 72h 최종 release candidate soak | baseline 이후 지속 증가 원인 없음, 종료·회수 정상 |
| C-003 | 작업 중 worker kill/restart | 불완전 proof가 successful release가 되지 않음 |
| C-004 | hard timeout·메모리 상한·취소 | UNKNOWN/실행 오류를 보존하고 다음 job 정상 |
| C-005 | disk full·권한 오류·깨진 report | atomic 저장 실패; 이전 성공 산출물 오염 없음 |
| C-006 | 병렬 요청·동일 이름·중복 job | idempotency/충돌 정책 준수, artifact 교차 오염 없음 |
| C-007 | 인증 후 계수 교체 / 캐시 stale | 배포 직전 hash mismatch로 차단 |
| C-008 | rollback·버전 교체·구 schema | 호환성 표대로 동작, 조용한 재해석 없음 |

RSS 기준은 warmup 30분 이후의 retained memory를 주기적으로 측정합니다. 단순 process high-water가 한 번 증가했다고 누수로 단정하지 않습니다. slope, 작업 종료 후 안정 수준, allocator reuse, retained object count를 함께 봅니다. 초기 요구안은 idle-after-job RSS 증가가 `max(32MiB, baseline의 5%)`를 넘거나 지속 상승 추세면 조사·게이트 정지입니다. 정당화된 cache는 상한과 회수 정책을 기록합니다.

## 6. 정확성 검증과 성능 측정의 분리

timing loop에 SymPy truth 계산·파형 생성·tracemalloc을 섞지 않습니다. cold-start/파일 읽기/객체 변환 비용이 필요한 end-to-end 측정은 별도 이름을 사용합니다. 장시간 데이터 도구의 elapsed time에는 synthesis·hash·세 numerical lane이 모두 포함되므로 이것을 Dexted 처리 latency라고 표기하지 않습니다.

30회 반복은 최소 microbenchmark 측정 단위이지 독립 사례 수가 아닙니다. 9개 계수 ×30번은 정답 평가 270개가 아니라 9개 사례에 대한 시간 관측 270개입니다. 정답 지표는 고유 계수/정책 쌍 기준으로 산출합니다.

## 7. 종료·재실행 규칙

한 사례가 실패해도 가능한 다른 사례의 결과를 계속 기록하되, process-level unsafe 상황은 격리합니다. 결과 파일은 JSONL append 또는 atomic case file로 남기고 최종 summary에는 expected/completed/failed/unknown/not-run를 모두 싣습니다. 재시도 결과가 성공해도 첫 실패를 덮어쓰지 않습니다. 원인분석 없이 “flaky”로 취급하지 않습니다.

## 8. 완료 정의

A/B/C의 필수 case가 모두 계획 ID와 증거로 연결되고, 의도적 결함이 탐지되며, 같은 commit에서 재현되어야 합니다. 별도 외부 review/현장 데이터 게이트가 남아 있으면 전체 산업용 승인은 아직 아닙니다.
