# 03. Python 코어의 파일·함수 단위 개발 명세

[코어 명세 홈](README.md) · [알고리즘](02_ALGORITHMS_AND_INVARIANTS.md) · [budget 계약](contracts/budgets.json)

## 1. 계층 구조와 의존 방향

현행 `model → biquad/cascade → inspection`을 유지하고 외부 입력 경계용 신규 `request.py`, `budget.py`, `worker.py`, `envelope.py`, `gate.py`를 제안합니다. 코어는 SciPy/SymPy/NumPy에 의존하지 않습니다. oracle와 신호 처리 adapter는 tools/tests에만 위치합니다. report는 producer를 호출할 수 있으나 independent proof checker가 producer verdict를 재사용해서는 안 됩니다.

**아래 이름과 signature는 구현할 계약 초안입니다. 현재 import 가능한 public API가 아닙니다.** 릴리스 전 name/API review와 golden compatibility가 필요합니다. 새로운 함수명을 문서 smoke에서 실행 가능한 예제로 소개하지 않습니다.

## 2. 데이터 구조

`CoefficientArtifact`는 `precision`, ordered six-column rows의 raw hex, raw payload digest, a0 policy, normalized real values를 immutable tuple로 보관합니다. 사용자가 준 ndarray/view가 이후 바뀌어도 인증 대상이 바뀌지 않도록 owning copy를 만듭니다. float64 wrapper 안에 저장된 f32라도 precision과 source bit width를 유지합니다.

`CheckRequest`는 artifact, positive finite binary64 γ, strict=true, sample_rate metadata(optional), budget_profile, requested output 종류(decision/proof/bounds), caller policy ID를 포함합니다. policy와 artifact identity는 caller가 제공하며 report에서 가져오지 않습니다.

`CheckResult`는 `math_status`, `execution_status`, `reason`, `proof_status`, `identity_status`, `core_build`, `telemetry`, optional proof/bounds로 구성합니다. math_status는 certified/rejected/unknown 또는 null입니다. invalid_input은 math null, cancelled/timeout은 unknown입니다. `__bool__`은 TypeError로 막고 `.deployment_allowed`도 verifier·policy·bytes가 확인되기 전엔 false입니다.

## 3. 입력·준비 함수의 명세

| 파일·함수 | 입력 → 출력 | 알고리즘·예외 | 완료 테스트 |
|---|---|---|---|
| 신규 `request.py: bounded_take(values, limit, field)` | iterable, int → tuple | limit+1개의 next만 호출; 초과 INVALID_INPUT, next 예외 별도 원인; infinite next는 worker timeout | CT-01,02 |
| 기존 `model.py: Biquad.from_coefficients` | 5 values → Biquad | 신규 adapter가 숫자 검증 후 호출; f32 once; max+1 wrapping은 별도 helper로 회귀 관리 | CT-03,04 |
| 기존 `model.py: from_sos` + 신규 `parse_sos_payload` | bytes/rows → artifact | byte length 128KiB 확인 후 bounded row/section; a0 !=1, NaN, complex, bool/string reject | CT-01~04 |
| 신규 `request.py: freeze_request` | artifact, policy → CheckRequest | copy before hash; γ/from bits, dtype explicit; no silent normalize/sort | CT-04,21 |
| 신규 `cascade.py: prepare_cascade` | validated rows, budget → immutable N,D,stable witness | actual prepared object는 private; degree/bit checks; checksum guard | CT-08,09,23 |

운영망에 노출되는 경계는 JSON/raw bytes만 받습니다. Python 임의 객체의 float conversion이 사용자 코드를 실행할 수 있으므로 타입 검사와 격리를 구분합니다. conversion이 필터 값을 round하는 행위인지 identity validation인지 보고합니다. float32 overflow나 rounding 후 a0 변경이 발생하면 invalid이지 gain fail이 아닙니다.

## 4. 판정·bounds 함수의 명세

| 파일·함수 | 개발 내용 | 성공/중단 후 불변조건 | 테스트 |
|---|---|---|---|
| 기존 `biquad.certify` | 수학 경로는 그대로; 새로운 facade에서 telemetry·witness 연결 | exact legacy 결정·schema 유지 | CT-05~07 |
| 기존 `cascade.gap_polynomial` | prepared N,D 및 positive common scale 재사용 | CR-03: 원래 P와 부호 동일, zero vector 보존 | CT-08,09 |
| 기존 `cascade.prove_positive` / 신규 `_prove_with_budget` | budget/context 인자를 내부 경로로 분리; legacy wrapper default 유지 | 완전 cover만 pass, budget reason과 frontier counts 남김 | CT-10~13 |
| 신규 `check_sos` | frozen request → CheckResult | producer+consumer를 실행하고 strict typed fields로 결과 생성 | CT-15,20,22 |
| 기존 `peak.bound_sos_peak_gain` / 신규 `_refine_with_budget` | shared total refinement budget; achieved width·termination 표시 | valid bracket만 유지, UNKNOWN으로 경계 갱신 금지 | CT-14 |
| 기존 `inspection.inspect_*` | 기존 full inspection 유지; 새 lightweight facade를 별도 노출 | bounds 실패가 이미 verified한 decision을 뒤집지 않음 | CT-20 |
| 기존 `inspection.verify_inspection` | legacy readers 유지; hardened envelope reader는 별도 | 기존 report comparison 동작과 새 wire canonicality를 혼합하지 않음 | CT-18,19 |

**decision-only 경로 의사코드** (현재 API 아님):

```text
supervisor starts isolated worker with total deadline and RSS enforcement
frozen = parse_and_freeze(caller_bytes, caller_policy)
producer = exact_decide(frozen, remaining_budget)
if producer is not CERTIFIED:
    append terminal result incl. witness / unknown reason
    return deployment_blocked
proof = serialize_with_cap(producer, caller_limits)
verification = independently_verify(proof, frozen, remaining_budget)
if verification is not VALID:
    append proof failure or verifier resource exhaustion
    return deployment_blocked
return VERIFIED_DECISION (optional refinement is a separate requested task)
```

positive producer 결과만으로 `.deployment_allowed=True`를 설정하지 않습니다. verifier timeout이 나면 기존 producer 판정은 telemetry에 보존할 수 있지만 workflow 결과는 NOT_VERIFIED/blocked입니다.

## 5. budget·작업자·캐시 함수

`Budget.checkpoint(stage, estimated_new_bits=0)`는 monotonic deadline, 누적 nodes, max degree, max integer bits, proof bytes를 검사합니다. stage마다 budget reset 금지입니다. raising `ResourceLimit(reason,stage)`를 호출 경계에서 UNKNOWN으로 변환합니다. ValueError/MemoryError/KeyboardInterrupt를 하나의 gain fail로 뭉개지 않습니다.

`worker.run_isolated(request_bytes, limits)`는 child spawn → quota 적용 확인 → READY → WORK → TERMINAL → reap 구조를 갖습니다. quota 설정이 안 되면 hardened deployment 모드는 실행하지 않습니다. deadline에 soft cancel, 짧은 종료 유예, hard kill/reap을 시행하고 stdout의 임시 PASS는 인정하지 않습니다. 부모는 생존하며 partial evidence와 exit code를 남깁니다. socket/pipe 응답 크기도 제한합니다.

`gate.commit_artifacts(result, expected_bytes)`는 같은 file system 내 임시 디렉터리에 proof·request·status를 저장하고 fsync/rename합니다. 마지막 successful marker 직전에 caller payload를 재검사합니다. Windows 파일 잠김/rename semantics는 따로 테스트합니다. 디스크 부족, 충돌, 취소는 success marker가 없는 상태로 종결합니다.

`prepare_cache`는 full input identity, precision, threshold 또는 threshold-independent prepared payload 구분, algorithm revision, policy hash를 key에 포함합니다. verdict cache와 prepared polynomial cache를 분리합니다. 캐시가 hit해도 consumer의 외부 입력 binding을 생략하지 않습니다. 실패/partial result는 positive cache에 쓰지 않습니다. request가 끝나면 references를 해제하고 bounded LRU를 사용합니다.

## 6. 구현 순서와 review 포인트

먼저 golden tests와 현재 schema round-trip을 고정합니다. 다음으로 bounded adapters, typed result, request budget, hardened proof parser, isolated supervisor, lightweight facade 순서입니다. 마지막에만 positive-scale/caching 최적화를 켭니다. 한 PR에서 schema·predicate·oracle를 모두 바꾸지 않습니다.

각 함수 PR에는 실패 reproducer, worst-input count, expected status, 기존 default behavior 비교, heap/RSS 결과를 포함합니다. 신뢰된 in-process API에서 어떤 오류가 exception인지와 hardened worker에서 어떤 machine status로 매핑되는지 표를 유지합니다.
