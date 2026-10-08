# 02. 수학 알고리즘과 보존 불변조건

[코어 명세 홈](README.md) · [기존 biquad 증명](../../research/proofs/biquad.md) · [기존 cascade 증명](../../research/proofs/cascade.md)

## 1. 정의역과 판정 명제

각 section은 `Hj(z)=(b0+b1 z^-1+b2 z^-2)/(1+a1 z^-1+a2 z^-2)`입니다. 모든 입력은 finite represented f32/f64 값에서 정확한 dyadic으로 해석합니다. `H=∏Hj`, `1≤m≤32`, `γ>0`이며 각 section 안정성과 `sup |H(e^iω)|<γ`가 동시에 참이어야 CERTIFIED입니다. 안정성은 약분 전 분모에 적용합니다.

초기 정지 상태·stable LTI의 에너지 이득 명제와 sample-peak clipping을 구분합니다. 주파수 상한만으로 `max|y[n]| ≤ γ max|x[n]|`를 선언하지 않습니다. 출력 sample peak, 내부 state, 유한 정밀도 연산은 별도 모델입니다.

## 2. 정확한 다항식 변환

`c=cos(ω)`이고 `Q(x,y,z;c)=(x-z)^2+y^2+2y(x+z)c+4xz c²`입니다. 각 section에서 모든 계수와 a0=1을 같은 양의 이진 분모 `sj`로 정수화합니다. `Nj=Q(B0,B1,B2)`, `Dj=Q(sj,A1,A2)`이면 scale이 ratio에서 취소되어 `|H|²=N/D`, `N=∏Nj`, `D=∏Dj`입니다.

`γ=u/v` (u,v 양의 정수)일 때 `P(c)=u²D(c)-v²N(c)`를 구성합니다. `D>0`임을 section 안정성으로 확보한 뒤에만 positivity와 이득 조건을 동치로 사용합니다. section별 scale을 numerator/denominator에 다르게 적용하지 않습니다. 뒤의 zero coefficients는 degree를 줄일 수 있지만 다항식 `[0]`은 그대로 남깁니다.

## 3. 불변조건 등록부

| ID | 명제 | 구현 시 강제할 조건 |
|---|---|---|
| INV-01 | represented 입력이 변경되지 않음 | f32 rounding은 딱 한 번, raw bits와 float.hex round-trip |
| INV-02 | Schur strictness | `sj-abs(A2)>0`, `sj+A1+A2>0`, `sj-A1+A2>0`; 등호 거절 |
| INV-03 | P 부호는 실제 gain gap 부호 | 정확한 정수 전개, scale 기록, division은 exact |
| INV-04 | biquad 판단은 완전 | endpoints+필요한 내부 vertex의 양수성 검사 |
| INV-05 | CERTIFIED cover는 전역 proof | 모든 leaf coefficients >0; t=[0,1] 정확히 덮음 |
| INV-06 | REJECTED_GAIN에는 비양수 근거 | exact point 또는 검증 가능한 algebraic zero; 자원 소진과 구별 |
| INV-07 | UNKNOWN은 truth가 아님 | lower/upper/proof로 승격 금지, 기존 유효 증거만 유지 |
| INV-08 | bound bracket가 참 peak 포함 | `0≤L≤peak≤U`; refinement마다 폭 비증가 |
| INV-09 | 모든 maximizer 포함 | stationary/root count 완전성, tie를 제거하지 않음 |
| INV-10 | consumer는 caller에 결속 | threshold·precision·section 순서·배포 bytes 독립 입력 |
| INV-11 | 수치 display가 proof에 영향 없음 | Hz·decimal 그래프를 truth의 입력으로 사용 금지 |
| INV-12 | 최적화는 양의 동치변형 | gcd content >0만 제거, 부호 반전·임의 ε 불가 |

## 4. Biquad 결정 절차 — CR-02

`P(c)=a c²+b c+d`로 적습니다. `P(-1)=a-b+d`, `P(1)=a+b+d` 둘 다 양수여야 합니다. `a>0`이고 `-2a<b<2a`면 내부 최소점이 존재하므로 `4ad-b²>0`도 필요합니다. 그 외에는 endpoints로 충분합니다. 상수/일차/영 다항식, vertex가 끝점인 경우를 별도 golden으로 둡니다.

REJECTED witness는 끝점 `c=±1` 또는 내부 vertex `c=-b/(2a)`의 rational 값입니다. 안정성 실패가 우선되면 section index와 실패한 Jury 식을 기록합니다. γ=peak의 등호를 임의 tolerance로 통과시키지 않습니다.

## 5. SOS Bernstein 판정 — CR-03

`t=(c+1)/2`, `0≤t≤1`로 바꾼 degree n 다항식을 Bernstein basis에 정확히 변환합니다. binomial denominator의 양의 LCM으로 공통 scale을 곱해 integer coefficients를 유지합니다. de Casteljau 분할은 child마다 `2^n`의 **양수**를 곱한 동일 함수의 표현입니다.

worker는 `(coeffs,index,depth)` DFS frontier를 보존합니다. 기본 순서는 left-first로 고정합니다. leaf의 모든 계수가 양수이면 그 닫힌 구간을 승인합니다. endpoint coefficient가 0 이하이면 그 dyadic t와 `c=2t-1`를 반례로 반환합니다. 전부 소비한 후에만 certified입니다. frontier가 남거나 한 leaf라도 depth/node/time/bit 상한으로 미해결이면 unknown입니다.

각 child에 budget를 새로 부여하지 않습니다. 생성 전 예상 bit growth를 계산하고 child 생성 후 실측 bit length를 다시 검사합니다. 초기 polynomial 전개·basis conversion·proof 조립도 동일 요청 예산에 포함합니다. 단일 C bigint 연산을 Python signal로 항상 중단할 수 있다고 가정하지 않고 외부 hard kill을 둡니다.

**완결성 한계:** `P(c)=(3c-1)^2`는 c=1/3의 접점 때문에 strict positivity에 실패하지만 dyadic 샘플에서 0이 되지 않습니다. 유한 Bernstein 예산에서는 UNKNOWN일 수 있습니다. 이를 '위반 없음'으로 처리하지 않습니다. 독립 root oracle는 정확히 실패를 알 수 있습니다. 출시 범위에서 algebraic rejection extension을 사용하지 않으면 이 사례의 UNKNOWN을 그대로 허용·표시합니다.

## 6. oracle 규칙

독립 구현은 각 SOS를 rational로 별도 전개해 Q를 만들며 producer의 `gap_polynomial`을 import하지 않습니다. QQ Poly의 P가 zero면 strict 실패, 닫힌 [-1,1]에 root가 하나라도 있으면 strict 실패, root가 없고 P(0)>0이면 통과입니다. 상수식과 endpoints를 explicit 처리합니다. SymPy root-count API는 [S1](11_RUNBOOK_REVIEW_AND_SOURCES.md#s1)를 참고하며 timeout은 `ORACLE_UNRESOLVED`입니다.

producer의 unknown과 oracle의 fail은 모순이 아닙니다. producer certified/oracle fail 또는 producer gain fail/oracle pass만 수학적 불일치입니다. oracle unresolved를 PASS로 간주하지 않습니다.

## 7. gain enclosure와 성능 최적화

lower는 exact rational witness ratio의 아래 방향 sqrt로 얻습니다. upper는 `Pγ>0`의 실제 proof로만 설정합니다. γ 중점에서 unknown이면 L을 올리지도 U를 내리지도 않습니다. 이미 valid bracket가 있으면 `budget_limited`로 반환하고, upper를 못 만들면 unavailable입니다.

`relative_width_target_bits`는 현행 bisection 횟수와 동일한 의미라고 추정하지 않습니다. 새 report에는 requested width, achieved rational width, refinements, termination reason을 구분합니다. target을 못 채워도 bracket 자체는 유효할 수 있습니다.

최적화 후보는 common positive gcd content 제거, coefficients의 immutable prepared cache, binomial table cache와 numerator/denominator product 재사용입니다. N과 D 각각을 따로 primitive로 만들어 ratio를 바꾸지 않습니다. 공통 인수 약분은 original per-section stability를 먼저 검사하며 consumer가 original coefficients로 proof를 재검사할 수 있어야 합니다. float 기반 순서는 advisory이며 proof acceptance에는 미사용입니다.

## 8. 문서/구현 승인 산출물

각 INV는 CR 요구·CT 테스트·CW 작업에 연결합니다. rational derivative identity, scaled Bernstein identity, 증명된 모든 rejection witness, metamorphic invariance를 source diff와 함께 review합니다. proof 공식이 맞아도 finite parser/overflow/allocator가 안전하다는 뜻은 아니므로 03~06 계약을 별도로 통과해야 합니다.
