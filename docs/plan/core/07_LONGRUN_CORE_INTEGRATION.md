# 07. 24건·76시간 자료를 실제 코어 검증에 연결하는 명세

[코어 명세 홈](README.md) · [기존 자료 정의](../04_DATASET_AND_LONGRUN.md) · [연결 매트릭스](contracts/longrun-matrix.json)

## 1. 현행 도구가 하는 것과 하지 않는 것

기존 `tooling/longrun.py: run_record`의 `--with-dexted`는 고정 `REFERENCE_SOS`에 대해 from_sos→certify_cascade→verify_cascade를 record 시작 때 호출할 수 있습니다. 하지만 현재 보존된 6×30분 bootstrap 결과에는 core를 호출하지 않았습니다. 이것을 core 장시간 실적으로 재명명하지 않습니다.

현재 runner는 2-section reference 필터와 3개 SciPy 수치 lane을 사용하며 예상한 reject/unknown을 만나면 RuntimeError로 전체를 중단합니다. 산업용 runner는 caller-supplied immutable filter inventory, expected failure controls, per-case terminal ledger, independent runtime adapter를 지원해야 합니다. 기존 evidence hash를 깨지 않도록 `benchmarks/industrial/`의 **신규 runner**를 구현하는 방향을 선택합니다.

## 2. 세 축과 성공 조건

A(코어)는 필터별 exact oracle truth, producer, proof consumer와 배포 바이트를 검증합니다. B(자료)는 실제 처리기의 state/roundoff/block continuity를 검사합니다. C(운영)는 계속 다른 검증 작업을 처리하는 worker의 시간·메모리·복구를 검사합니다. A/B/C 중 하나만 통과하고 전체 industrial-qualified=true를 쓰지 않습니다.

고정 필터는 매 샘플마다 인증하지 않습니다. unique artifact+policy+core build마다 인증하고, 각 record 사용 직전에 caller identity·proof를 다시 확인합니다. 같은 coefficients로 긴 입력을 1,000개 처리해도 수학적 독립 필터 수는 1개입니다.

## 3. 기존 24건 자료를 그대로 보존

| records | 개별 길이 | fs/channels | 합계 input record-hours |
|---|---:|---|---:|
| A01~A12 | 1800초 | 48000Hz/2 | 6 |
| B01~B06 | 3600초 | 96000Hz/2 | 6 |
| C01~C04 | 14400초 | 1000Hz/8 | 16 |
| D01~D02 | 86400초 | 48000Hz/2 | 48 |
| 총 24 | | | 76 |

기존 manifest의 seed/절대 샘플 위치·profile·frame count를 변경하지 않습니다. 이 master corpus는 약 93.0816GB f32 입력입니다. 같은 파형의 split을 바꾼 것은 새로운 긴 자료가 아닙니다. short clip loop는 금지합니다. fs는 normalized transfer function과 별개 metadata로 바인딩하고 물리 Hz 특정 필터가 필요하면 별도 설계 fixture를 둡니다.

## 4. 신규 frozen filter inventory — 최소 8개 valid 필터

F01 unity-margin-safe, F02 2-section lowpass, F03 4-section Butterworth, F04 8-section elliptic, F05 16-section mixed EQ, F06 32-section extended chain, F07 stable high-Q safe, F08 compensated cascade입니다. **이 8개는 생성·동결할 요구이며 현재 manifest에 실제 계수가 확보되어 있다는 뜻이 아닙니다.** approved coefficients, precision, gamma, expected truth, proof source, condition/tail 정보를 갖춰야 합니다. 생성 실패나 oracle unresolved는 fixture slot을 삭제하는 이유가 아닙니다.

별도 controls: NC01 hidden-peak exact fail, NC02 unity equality, NC03 unstable denominator, NC04 강제 resource unknown입니다. NC04의 underlying mathematical truth와 executed UNKNOWN을 따로 저장합니다. invalid/unstable 입력은 production gate가 막은 후 forensic sandbox에서만 필요 시 처리하고, unsafe waveform 처리를 mandatory 'release allowed' 경로에 넣지 않습니다.

기본 qualification은 24 records×8 valid filters = **192 record-filter runs**, input duration 합 **608 filter-hours**입니다. runtime lane은 reference f64 / deployment f32 / partition f32 / independent engine의 4개입니다. lane 수를 곱한 2,432 processing-lane-hours를 고유 input duration 76h 또는 real wall-time으로 표기하지 않습니다. 배포 자체가 f64인 제품의 별도 f64 deployment matrix는 추가 scope입니다.

최소 모든 192개에 A core receipt+B finite state checks가 필요합니다. independent engine이 미구현인 경우 3 lanes를 4로 계산하지 않습니다. 기본 8개 합성 필터는 실제 제품 계수 최소 3,000건/실자료 20건 목표를 대체하지 않습니다.

## 5. runner pipeline와 자료 구조

```text
freeze plan: record IDs + filter IDs + engine IDs + mutation IDs
for each unique filter:
    exact oracle -> typed ground truth (or unresolved)
    call actual Dexted -> serialize proof -> independent consumer
    record package path, source/wheel hash, coefficient bytes, gamma
for each scheduled record-filter:
    deployment gate checks receipt+actual payload+policy
    if blocked: persist terminal result and expected-control outcome
    else: process exact frame range with persistent independent channel state
    append checksummed JSONL; finalize summary only when all slots terminal
```

새 `CoreAdapter.prepare`는 실제 설치 패키지의 `__file__`, distribution version·wheel/source digest를 저장하여 테스트 stub 호출을 잡습니다. `certify`/`verify` 경로가 호출됐는지 instrumentation counter로 확인합니다. boolean `with_dexted=true`만 기록해서 core가 실행됐다고 인정하지 않습니다. shadow production adapter와 correctness oracle의 공통 helper 재사용을 금지합니다.

`case-result` 필수 필드: record/filter/engine IDs, planned/actual frames, input_sha256, deployment_coeff_sha256, core version/path/hash, producer math+execution, consumer status, oracle truth, gate outcome, terminal reason, output/state/checkpoint hashes, state/energy/window metrics, measured wall duration. 오류 직전 last frame와 partial digest를 남기며 최종 full digest와 혼합하지 않습니다.

## 6. streaming·state·정밀도 시험

chunk patterns는 고정 127/128/255/256/1024/4096/65536과 seed-fixed 랜덤 1..8192를 사용합니다. zero-length chunk와 마지막 partial chunk 정책을 고정합니다. channel state는 `[section,delay,channel]`의 독립 배열이고 현재 입력 모양과 일치해야 합니다. resume은 coefficient/policy/engine build/frame index/state bytes를 모두 확인합니다.

같은 엔진·동일 arithmetic order에서는 block partition 결과의 bit equality를 요구합니다. 다른 엔진 또는 FMA 연산 순서가 다르면 bit equality 대신 predeclared per-filter tolerance를 사용합니다. 단순 float64 결과를 'exact truth'로 부르지 않습니다. 독립 runtime은 Python reference recurrence 또는 다른 코드베이스 adapter로 구현하며, reference engine을 재호출한 2 lanes는 독립 engine이 아닙니다.

f32-vs-f64 허용오차는 filter ID·input bounds·state/conditioning·operation model에 연결합니다. 기존 `3e-6`은 reference filter만의 회귀 상한이며 high-Q/32-section에 일반화하지 않습니다. tolerance 미정이면 해당 비교는 NOT_EVALUATED입니다. NaN/Inf 0건, frame loss 0, channel leakage 0, stale resume 0은 모든 supported lanes 필수입니다.

## 7. peak dwell·settling·tail

76h 자료만 길다고 좁은 peak를 충분히 흥분시키는 것은 아닙니다. 전체 fixed manifest와 별도로 exact c peak 후보 주변 sine dwell·다중 톤·impulse tail을 생성합니다. 단일 mode의 `r^n`은 힌트일 뿐 반복극·비정규 state의 transient를 완전히 나타내지 않습니다. tail 허용 길이는 `||A^n||≤C r^n`의 보수적 C,r 및 input/state bound로 정하거나 unresolved로 남깁니다.

Hz display 근사로 만든 excitation은 empirical 테스트이며 Hz 인증이 아닙니다. 성능을 좋게 보이려고 중요한 long decay를 trim하지 않습니다. finite output energy와 tail bound를 구분하고 nonzero initial state는 별도 회귀 lane입니다. H∞ bound를 모든 sample-peak 안전과 동일시하지 않습니다.

## 8. 실패 주입·운영 내구성

필수 mutations: 한 block의 state reset, channel state 공유, 한 frame 누락/중복, chunk phase/RNG 재시작, coefficient bit flip, stale proof, threshold 완화, producer true stub, verifier bypass, timeout 후 success 파일 남김, disk full, mid-record kill+resume mismatch입니다. injection이 실제 측정치에 영향이 없으면 예제 부하를 강화하여 detector sensitivity를 확보하고 '탐지 통과'로 계산하지 않습니다.

24h soak 3회 및 72h soak 1회는 별도 **wall-clock** 운영 시험입니다. mixed safe/fail/unknown/invalid 검증 queue를 계속 공급하고 request latency·RSS 추세·worker recycle·backlog·cancellation을 측정합니다. 고정 파일을 100초에 처리한 76 record-hours는 이 조건을 만족시키지 않습니다.

## 9. 완료 기준

모든 예정 slot의 terminal ledger, 실제 core call 증거, source/input hash, negative controls 탐지 결과, 독립 runtime coverage, 192개 full frame 검사와 608 filter-hours의 accounting이 있어야 합니다. 일부만 smoke 실행했으면 qualification=false를 유지합니다. 실제 필터/자료·external review·wall-clock soak 게이트는 여전히 별도이며 합성 장시간 통과로 승인하지 않습니다.
