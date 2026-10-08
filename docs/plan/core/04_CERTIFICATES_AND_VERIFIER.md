# 04. 인증서 프로토콜, 독립 consumer, 배포 승인 계약

[코어 명세 홈](README.md) · [함수 설계](03_PYTHON_IMPLEMENTATION.md)

## 1. 버전 전략

현행 `dexted-dsp/biquad/v1`, `cascade/v1`, `inspection/v1`, `inspection/v2`의 의미를 보존합니다. 새로운 byte-bound 운영 envelope 이름은 **제안** `dexted-dsp/verification-envelope/v1`입니다. 기존 inspection/v2에 다른 의미를 덮어쓰지 않습니다. 새 parser가 legacy payload를 읽을 때 명시적인 compatibility adapter를 사용합니다.

native API의 1 또는 Python report의 certified=true는 proof로 인정하지 않습니다. 서명/해시 검증은 정수·유리수 수학 검증을 대신하지 않습니다. 반대로 수학적으로 valid한 proof도 승인된 제품 artifact·정책이 아니면 배포할 수 없습니다.

## 2. wire 필드와 정규 인코딩

| 필드 | 표현·소유 주체 | 검사 |
|---|---|---|
| schema/model | 고정 문자열; strict-gain/fixed-real-SOS | 미지 버전·미지원 모델은 차단 |
| precision/rows_bits | f32는 8자리, f64는 16자리 소문자 hex / caller | ordered 6 columns, a0의 exact 1 bits, finite 값 |
| gamma_bits | binary64 raw hex 16자리 / caller | positive finite, strict=true; dB 아님 |
| sample_rate_bits | binary64 또는 null / caller | present이면 positive finite; scope metadata 바인딩 |
| artifact_sha256/policy_sha256 | original deployment bytes / 승인 정책 | proof 내부의 값을 caller 정책 대신 신뢰 금지 |
| producer_build/verifier_build | 버전·source/binary SHA·algorithm revision | 캐시 재사용 정책과 allowlist 검사 |
| claim/witness | typed claim + bounded exact data | 각각 독립적으로 재구성·검증 |
| execution/telemetry | stage counts, limits, durations | 진리의 증거와 구분; deadline override 허용 안 함 |
| optional_diagnostics | bounds/region/display | extension ID와 검증 상태를 따로 표시 |

canonical envelope bytes는 UTF-8, ASCII key, 정렬된 key, compact separators, finite integer/string/bool/null로 규정합니다. binary float는 JSON number가 아닌 raw hex입니다. duplicate keys, BOM, nonfinite constants, unknown critical fields, depth/길이 초과, tail garbage를 거절합니다. 이것은 **프로젝트 고유 인코딩**이지 검증 없이 RFC canonicalization 준수를 주장하는 것이 아닙니다.

proof 내부 arbitrary integers는 새 envelope에서 signed hex string을 사용합니다. 정수 canonicality는 `0` 또는 부호 없는 nonzero hex, 또는 `-`+nonzero hex이며 leading zero/negative zero를 금지합니다. raw float bit 문자열은 fixed-width leading zeros를 허용하는 **다른 타입**입니다. 수학적 -0은 0이지만 raw float -0은 artifact에서 +0과 구분됩니다.

## 3. parser와 verifier 순서

입력 byte cap → JSON nesting/token preflight → duplicate/type 검사 → 정수 string 길이 검사 → bounded convert → caller identity 비교 → section Schur 재검사 → independently expanded polynomial → proof certificate 검사 순서입니다. 4MiB proof를 읽은 뒤 한 필드가 수백만 자리임을 알아내는 구현은 금지합니다. 전역 `sys.set_int_max_str_digits(0)`를 사용하지 않습니다. legacy decimal 초대형 필드는 기본 안전 제한 안에서 처리하거나 별도 bounded chunk converter 설계를 승인받습니다.

새 proof verifier의 한도는 caller Limits가 결정합니다. proof가 요구한 max_nodes=100000을 곧바로 자신의 실행 예산으로 사용하지 않습니다. consumer는 producer helper 대신 기존 별도 rational 전개 경로를 유지하고 외부 oracle는 세 번째 구현으로 둡니다.

## 4. 허용 witness 유형

**CERTIFIED_BIQUAD:** caller 계수의 rational Jury+quadratic decision이 참인지 재계산합니다. 새 envelope에서 제공한 witness는 같은 입력의 exact 값과 일치해야 합니다. legacy verify_biquad가 informational witness를 모두 대조하지 않는 기존 정책과 구분합니다.

**CERTIFIED_SOS_COVER:** `(index,depth)`의 dyadic t-interval 목록입니다. 각 index는 0≤k<2^d, depth는 정책 이하입니다. 정렬 후 첫 lo=0, 인접 lo=이전 hi, 마지막 hi=1이어야 합니다. gap·겹침·중복·오버플로한 shift·과다 leaves를 거절합니다. 각 leaf를 c에 affine 변환해 rational Bernstein 계수가 모두 >0임을 확인합니다. topology 검사를 생략하고 leaf positivity만 검사하면 안 됩니다.

**REJECTED_STABILITY:** original section index와 실패한 Jury 식 번호, exact value를 재검사합니다. 상쇄된 pole이 있어도 original section 규칙은 동일합니다.

**REJECTED_GAIN_DYADIC:** c=-1,0,1 또는 일반 유리점과 exact `P(c)≤0` witness입니다. γ equality도 reject입니다. 점이 [-1,1] 밖이면 reject witness 자체가 invalid입니다.

**REJECTED_GAIN_ALGEBRAIC / 후속:** exact P-root가 닫힌 band에 있음을 root isolation/count proof로 보입니다. 유리점 평가에서 등호를 찾지 못했다고 무한 재시도하지 않습니다. 지원 안 하는 종류는 `UNSUPPORTED_WITNESS`로 차단하고 기존 UNKNOWN을 정직하게 남깁니다.

## 5. 승인 상태의 진리표

| producer | execution | verifier | bytes·policy | 배포 |
|---|---|---|---|---|
| certified | completed | valid | match | 승인 정책 추가 확인 후 허용 |
| certified | completed | invalid | match | 차단, certificate inconsistency |
| certified | completed | timeout/not_run | match | 차단, verification incomplete |
| certified | cancelled/error | any | any | 차단, execution incomplete |
| rejected | completed | rejection valid/미지원 | any | 차단; 위반 근거의 검증 수준 별도 |
| unknown | completed/timeout | any | any | 차단, unresolved |
| any | any | any | mismatch | 차단, stale/tampered artifact |
| null | invalid_input | not_run | any | 차단, 정의역 밖 |

새로운 diagnostics가 unknown이어도 verified base decision은 유지될 수 있습니다. 단, 고객 정책이 인증된 bounds/peak region을 필수로 요구하면 그 diagnostics 미완료는 deployment block입니다. optional을 mandatory로 바꾸는 정책 변경은 hash와 gate review 대상입니다.

## 6. golden·migration 검증

과거 v1/v2 proof에서 승인·거절·위조·precision mismatch를 각각 고정합니다. legacy reader는 과거 지원 동작을 유지하고 신규 writer는 새 envelope만 씁니다. 새 version을 모르는 reader가 unknown fields를 무시하고 통과시키지 않아야 합니다. `n` 버전의 receipt를 `n+1` verifier로 재검증하는 경우 source와 policy가 호환되는지 기록합니다.

새 serialized schema별 canonical bytes·expected digest·consumer expected verdict가 golden에 있어야 합니다. 스키마 양식 검사를 수학 증명 검사로 계산하지 않습니다. publisher identity는 필요 시 별도 attestation 계층으로 다루며 자체 해시만으로 서명했다고 표기하지 않습니다.
