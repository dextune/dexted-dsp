# 08. 코어 테스트·독립 오라클·적대적 검증 행렬

[코어 명세 홈](README.md) · [기계 판독 trace](contracts/requirements.json)

## 1. 테스트 ID와 실행 상태

아래 CT는 **구현할 테스트 명세**입니다. 기존 유사 테스트가 있어도 같은 ID의 evidence·환경·assertion을 검토하기 전에는 DONE으로 올리지 않습니다. `tooling/test_core_spec.py`는 이 명세의 구조를 검사할 뿐 아래 코어 테스트를 실행하지 않습니다.

| ID | 입력·자극 | 기대 결과/불변조건 | lane |
|---|---|---|---|
| CT-01 | 0/1/32/33 rows, row 5/6/7 elements, oversized bytes | 유효한 1..32×6만 수용; limit+1까지 소비 | PR |
| CT-02 | infinite iterator, blocking next, float conversion exception | 횟수 제한·worker hard timeout; parent 생존; PASS 없음 | isolated |
| CT-03 | ±0, min subnormal, min normal, max finite, NaN/Inf, bool/complex | finite represented semantics 보존; invalid 분리 | PR/native |
| CT-04 | f32 round twice, a0 mismatch, source ndarray 변경, wrong γ bits | 인증 대상 불변/precision mismatch 차단 | PR |
| CT-05 | stable Jury interior와 각 경계의 ±1 ULP | strict equality reject; independent rational 일치 | PR |
| CT-06 | constant/linear/convex/concave P, interior vertex, endpoint vertex | 정확한 quadratic truth; division by zero 없음 | PR |
| CT-07 | unity γ=1·nextafter(1), hidden peak γ=2·nextafter(2) | 등호 fail, 다음 representable threshold에서 pass | PR |
| CT-08 | m=1/2/4/8/16/32 dyadic polynomial expansion | independent Q 전개와 모든 계수 일치 | nightly |
| CT-09 | positive common scale/gcd, zero polynomial, trailing zero | 부호·ratio 보존; zero는 strict fail | PR |
| CT-10 | Bernstein leaf reconstruction, degree 0/1/64 | 정확한 affine identity와 split identity | PR/nightly |
| CT-11 | P=(3c-1)^2, P identically 0, narrow negative interval | tangency unknown 허용, oracle fail; zero는 fail | PR |
| CT-12 | max_depth 0/1/64, node cap 경계, maxbits/proof cap | 소진은 UNKNOWN_RESOURCE/blocked, no partial PASS | isolated |
| CT-13 | one frontier unresolved와 elsewhere rejection | 정책별 unknown/reject 차이 기록; false certified 없음 | PR/native |
| CT-14 | bracket upper not found, midpoint unknown, zero gain, overflow display | valid bracket 불변; unavailable/partial 구분 | PR |
| CT-15 | cover gap/overlap/duplicate/outside interval/reorder | invalid cover 거절; valid unsorted legacy policy 별도 | PR/fuzz |
| CT-16 | huge integer/depth/index, duplicate JSON keys, trailing bytes | conversion 전 상한, invalid certificate | fuzz |
| CT-17 | caller γ/precision/section order/fs/hash 바꾼 proof | identity mismatch, deployment blocked | PR |
| CT-18 | legacy biquad/cascade v1 + inspection v1/v2 golden | supported legacy truth 보존 | PR |
| CT-19 | future critical schema, optional diagnostics 없는 새 envelope | unknown schema blocked; mandatory scope 검사 | PR |
| CT-20 | base certified 후 optional bounds timeout | base truth 보존, 요구 policy별 gate 결정 | PR |
| CT-21 | verify 후 payload bit flip/파일 교체/동시 rename | 배포 직전 mismatch 차단 | integration |
| CT-22 | producer true stub, verifier bypass, cancelled result, empty proof | false delivery PASS 0; negative control 실제 탐지 | integration |
| CT-23 | mutable/cache collision/stale version/wrong policy cache hit | recheck binding, cross-request 오염 없음 | nightly |
| CT-24 | f32 Python/native identical raw input, gamma f64 bits | completed mathematical verdict 일치 | matrix |
| CT-25 | Python/native 다른 early-unknown 정책 | 완결 판정 모순 0; 미완결 차이는 coverage 표시 | matrix |
| CT-26 | allocation exception/-1/-2/-3/미지 return code, canary buffers | C 경계 exception 0, code==1만 positive | native isolated |
| CT-27 | chunk lengths와 channel counts 1/2/8, state resume | same arithmetic bit equality; wrong state 탐지 | longrun |
| CT-28 | f32/f64/independent runtime same input bytes | 사전 filter별 tolerance, unknown tolerance는 not evaluated | longrun |
| CT-29 | 24 record×8 valid filters 전량 streaming | 192 terminal cases,608 filter-hours,전체 frames/hash | qualification |
| CT-30 | state reset/channel share/frame loss/RNG reset 주입 | detector sensitivity 확보; mutation별 검출 | longrun negative |
| CT-31 | high-Q dwell/impulse tail/nonzero state | settling/tail 충분성 근거, H∞/sample-peak 혼동 없음 | slow oracle |
| CT-32 | timeout/kill/diskfull 중 JSONL 기록·resume | 예정 slots 모두 terminal; success marker 위조 없음 | isolated |
| CT-33 | hardware/precision/family별 ≥30 원시 측정 | censoring 포함, setup exclusions·RSS 귀속 정확 | benchmark |
| CT-34 | 24h×3·72h×1 wall-clock queue/worker soak | duration 실측·RSS 추세·recovery 목표 만족 | qualification |
| CT-35 | package install·legacy+new facade·docs smoke | 소스 경로 없이 작동; 지원 조합 명시 | release |
| CT-36 | seeded corpus oracle-resolved/unresolved 전량 audit | false certified=0, ordinary UNKNOWN≤0.1%, 행 누락0 | qualification |
| CT-37 | SOS stationary polynomial identities·endpoints·repeated roots | 모든 real root 포함, degree 상한·flat 별도 | extension |
| CT-38 | tied maxima, numerator zero, D interval crosses0 | tie 미삭제; refinement 또는 unresolved | extension |
| CT-39 | native proof 길이조회/짧은 buffer/동시 요청 | bounds-safe output, Python consumer validity | extension |
| CT-40 | native proof overflow/unsupported ABI/version | partial proof로 통과 금지, legacy ABI 유지 | extension |
| CT-41 | interval recurrence, rounding/FMA/FTZ 모델·state bounds | 보수 enclosure와 전제 확인; 미지원은 UNSUPPORTED | research |
| CT-42 | directed acos/pi 변환, c≈±1, interval monotonicity | 모든 Hz endpoint outward, 미수렴은 미인증 | research |

## 2. 정확성 분모와 verdict 비교

각 case에 `oracle_truth`, `producer_math`, `producer_execution`, `consumer`, `deployment`, `expected_control`을 따로 저장합니다. valid oracle pass/fail, invalid expected, oracle unresolved, producer unknown, timeout, not_run을 분리합니다. mismatch assert로 프로그램이 중단되어도 dataset ledger는 모든 예정 ID를 보존해야 합니다.

'거짓 인증 0'과 'verifiable positive 100%'를 함께 봅니다. ordinary를 모두 unknown으로 처리하면 correctness 안전성은 유지되지만 가용성 목표는 실패입니다. stress의 unknown을 ordinary 통계에서 숨기지 말고 별도 표를 반드시 보입니다.

## 3. 독립성 수준

L1: producer vs 별도 Fraction consumer는 다른 표현이지만 같은 프로젝트입니다. L2: 별도 QQ root-count oracle는 다른 알고리즘이며 shipping helpers를 import하지 않습니다. L3: 다른 조직이 source/input digest를 확인해 재현하고 수학 리뷰합니다. 자체 실행 로그만으로 L3를 선언하지 않습니다.

수치 lane f64나 매우 조밀한 frequency grid는 참고값입니다. high precision에서도 enclosure·root completeness 없이 정확한 truth라고 부르지 않습니다. oracle가 자원 한도를 넘으면 ORACLE_UNRESOLVED를 기록하고 release-required case는 게이트를 열어둡니다.

## 4. metamorphic/반례 축

identity section 추가, section permutation, 정확한 양의 common scale, safe gain scaling, precision-explicit round-trip, true identity cascade, exact cancellation을 검사합니다. section permutation은 ideal transfer gain을 보존하지만 runtime state와 serialized identity는 바뀝니다. 불안정 pole의 exact cancellation도 section-stability 규칙에서는 실패입니다.

positive coefficient gcd normalization은 P와 같은 부호지만 independent N/D scaling은 ratio를 바꿀 수 있으므로 negative mutation에 넣습니다. bisect count 증가는 시간 한도 때문에 항상 더 강한 판정을 주리라고 가정하지 않습니다. 동일 deterministic resource model 아래 이미 proven positive 결과가 negative로 바뀌면 defect입니다.

## 5. CI와 정식 검증 분리

PR: 작은 analytic boundary/golden/parser/coverage fixtures. nightly: 50,000 seeded case·bounded fuzz·m≤16 differential; 외부 데이터 필요 없는 부분부터 시작합니다. weekly: m=32, 6×30분 core-linked pilot, native full matrix. release: 100,000 coefficient plan의 resolved/unresolved 회계,192 full runs,실자료,wall-clock soak,외부 감사입니다.

단순 필터 개수나 '총 tests passed'로 규모를 합치지 않습니다. plan audit job이 green이어도 CT-29/34는 실행되지 않았을 수 있습니다. disabled/skipped/unsupported는 passed가 아니며 mandatory lane이 없으면 release approver가 차단해야 합니다.
