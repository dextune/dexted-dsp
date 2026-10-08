# 10. 후속 SOS 피크 위치와 장치 연산 오차의 상세 설계

[코어 명세 홈](README.md) · [수학 불변조건](02_ALGORITHMS_AND_INVARIANTS.md)

**범위:** CW-22/23은 후속 확장, CW-24는 연구입니다. 설계가 있다는 사실과 해당 알고리즘이 구현·증명·산업용 승인됐다는 사실을 구별합니다.

## 1. 전체 SOS의 stationary polynomial

original sections의 Schur 안정성 검사 뒤 exact N(c),D(c)를 준비합니다. D>0에서 `R=N/D`, `T=N'D-ND'`입니다. N,D의 degree가 각각 ≤2m이면 T의 최대 degree는 ≤4m-2 (m=32에서 ≤126)입니다. 같은 최고차항의 leading derivative term cancellation을 exact arithmetic으로 처리하고 trailing zeros를 제거합니다. 한 다항식 degree가 낮을 때에도 실제 degree를 다시 계산합니다.

T=0 identically면 rational ratio가 band에서 constant입니다. numerator가 zero인 flat response를 포함해 전체 [-1,1]을 maximizer region으로 반환합니다. 그 외에는 양 끝점 ±1과 T의 모든 distinct real root가 후보입니다. T의 repeated root를 sign-change grid로 찾지 않습니다.

## 2. exact root isolation 절차

QQ→primitive ZZ 변환, square-free factorization, exact root counting으로 닫힌 band 내 root 개수를 확정합니다. rational endpoints와 isolated intervals의 topology를 검증합니다. root가 정확한 rational이면 singleton으로 보존하고 endpoints와 중복 제거합니다. 각 interval에는 exactly one distinct root가 있음을 보이고, 외부 나머지 구간의 root count가 0임을 certificate로 제공합니다.

bounded pure exact implementation 또는 승인된 외부 exact arithmetic backend를 선택합니다. SymPy를 shipping mandatory dependency로 넣을지 여부는 별도 ADR이며, 최초 구현에서는 optional offline plugin과 independent consumer 설계를 우선합니다. 이름은 **제안** `localize_sos_peak(sections, isolation_bits, limits)`입니다.

## 3. candidate pruning과 ties

각 candidate interval I에서 N,D의 conservative rational ranges를 구합니다. Bernstein enclosure의 D lower가 0 이하일 수 있습니다. 실제 D가 양수라는 사실과 느슨한 interval lower를 혼동하지 않고 I를 더 분할합니다. budget가 끝나면 미해결 구간을 그대로 남기며 invalid filter로 단정하지 않습니다. squared numerator는 이론상 N≥0이므로 별도 증명에 근거해 lower를 max(0,nlo)로 조정할 수 있습니다.

D lower>0이면 `R(I)⊆[max(0,nlo)/dhi, nhi/dlo]`입니다. 어떤 candidate의 upper가 다른 곳의 valid lower보다 **엄격히 작을 때만** 제거합니다. 같거나 overlap이면 유지합니다. 따라서 returned union은 모든 global maximizers를 포함하지만 spurious candidates를 포함할 수 있습니다. isolation bits 달성이 global uniqueness 또는 peak-value equality 판정 완료를 뜻하지 않습니다.

result는 cosine_intervals, root counts, candidate_count, survivor_count, resolved/partial/flat, resource reason, optional squared gain brackets를 갖습니다. timeout이면 전체 [-1,1] fallback을 유효하지만 미정밀한 enclosure로 표시할 수 있고, 이를 '피크 위치를 정확히 특정'했다고 광고하지 않습니다.

## 4. Hz의 엄밀한 변환

`f=fs*acos(c)/(2π)`는 c에 대해 단조 감소하므로 [cl,ch]를 [f(ch),f(cl)]로 바꿉니다. rational endpoints를 double로 round해서 acos를 한 번 호출하는 현행 display는 certified Hz 구간이 아닙니다.

엄밀한 확장은 MPFR 같은 correctly rounded primitives의 아래/위 방향 계산을 합성해 fs·acos·π·곱셈·나눗셈의 모든 오차를 포함합니다([S5](11_RUNBOOK_REVIEW_AND_SOURCES.md#s5)). fs itself는 정확한 represented value라는 전제가 필요하며 clock tolerance는 별도 interval입니다. c≈±1에서 conditioning이 나빠지면 precision을 늘리거나 partial을 반환합니다. directed arithmetic 함수 하나를 호출했다고 전체 복합식 enclosure가 자동 보장되지는 않습니다.

## 5. 실제 연산 모델의 출발점

DF-II transposed 한 section을 예로 들면 `y=b0*x+s1`, `s1'=b1*x-a1*y+s2`, `s2'=b2*x-a2*y`입니다. rounding 위치는 multiply/add마다인지 FMA인지, storage cast가 언제인지 정확히 고정합니다. SciPy sosfilt의 realization은 [S2](11_RUNBOOK_REVIEW_AND_SOURCES.md#s2)를 참고하되 고객 DSP kernel의 실제 명령 순서가 같다고 가정하지 않습니다.

spec input: represented coefficients, implementation hash, input amplitude/energy bounds, initial state set, arithmetic precision·rounding·FMA/FTZ/DAZ/saturation policy, finite horizon 또는 invariant-set claim입니다. nonfinite 입력·overflow·unsupported flags는 증명 정의역 밖입니다.

## 6. 두 단계의 연구 계획

**finite-horizon:** rational/interval recurrence로 연산별 local error와 state/output enclosure를 N step 전파합니다. state 재시작·연산순서·채널 공유를 검증하고, interval 폭이 커지면 undecided로 남깁니다. random simulation이 enclosure 안에 있는 것은 보조 테스트이지 proof가 아닙니다.

**infinite-horizon:** `e[k+1]=A e[k]+δ[k]` 형태에서 local error bounds와 state reachability를 동시에 확보합니다. 어떤 norm에서 `||A^k||≤Cρ^k`, ρ<1을 증명하고 geometric accumulation을 사용하거나 invariant polytope/ellipsoid를 증명합니다. pole radius<1 하나만으로 C와 transient를 생략하지 않습니다. nonlinear saturation·time-varying coefficients는 별도 모델입니다.

**중단 기준:** overflow 가능성을 배제하지 못하거나 interval dependency로 폭이 폭발하면 `NOT_PROVED/UNSUPPORTED`입니다. empirical longrun이 좋아 보여도 '장치 안전성 증명'으로 승격하지 않습니다. 반례는 minimal arithmetic trace와 exact inputs로 저장합니다.

## 7. 기능 승격 조건

CW-22는 CT-37/38/42, CR-16·INV-09/11의 독립 검증을 통과한 뒤 versioned optional API로 배포합니다. CW-24는 CT-41, model premises 목록, 별도 수학 reviewer와 고객 use case 승인 후에만 새로운 claim scope를 추가합니다. 기존 strict-frequency-gain certificate의 의미를 장치 출력 안전성으로 확장하지 않습니다.
