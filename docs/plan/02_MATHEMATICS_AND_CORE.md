# 02. 수학적 정확성, 코어 고도화, 독립 검증

[문서 홈](README.md) · [테스트 프로토콜](05_TEST_PROTOCOL_AND_ORACLES.md)

## 1. 인증 명제의 정확한 문장

고정된 실수 계수의 SISO 전달함수에 대해 모든 SOS 분모가 엄격히 Schur stable이고 `sup_{ω∈[0,π]} |H(e^{jω})| < γ`인지 검사합니다. `γ>0`이며 입력 binary32/binary64 값을 실수로 정확하게 해석합니다. 이는 float32 연산기로 계산한 모든 출력의 안전성을 인증하는 문장이 아닙니다.

`sup|H|`는 주파수 응답 이득이며, 적절한 안정성·초기 정지 조건에서의 에너지 이득과 관련됩니다. 이를 임의 입력의 sample-peak 클리핑 상한과 동일시하지 않습니다. “주파수 이득 1 미만이면 모든 샘플이 원래 peak보다 작다”는 추론은 본 제품에서 허용하지 않습니다. 비영 초기 상태의 과도 응답, internal state overflow, section 중간 이득은 별도 대상입니다.

## 2. 보존해야 하는 현재 구현과 증명 의무

[현재 biquad 증명](../research/proofs/biquad.md), [cascade 증명](../research/proofs/cascade.md), [계수 모델](../../src/dexted_dsp/model.py), [cascade 코드](../../src/dexted_dsp/cascade.py)를 기준으로 회귀를 막습니다.

| 의무 ID | 의무 | 확인 방법 | 산출물 |
|---|---|---|---|
| M-01 | 정밀도 변환 후 실제 비트값을 인증 | hex·binary dump·정밀도별 round-trip | 계수 바인딩 테스트 |
| M-02 | 분모 안정성 조건의 엄격 부등식 보존 | exact Jury 조건, 경계·극점 독립 점검 | 부호·등호 테스트 표 |
| M-03 | 제곱 응답 다항식 전개가 정확 | 별도 전개로 계수 전체 비교 | property regression |
| M-04 | biquad 양의 다항식 판정의 완전성 | 끝점·내부 vertex·중복근·상수식 | rational reference 대조 |
| M-05 | SOS Bernstein leaf의 충분조건 | dyadic 구간 변환 및 양의 계수 검사 | 재검증 가능한 cover |
| M-06 | leaf 집합이 전체 구간을 덮음 | 빈틈·중복·깊이·끝점 악성 mutation | 독립 verifier 거절 테스트 |
| M-07 | UNKNOWN이 CERTIFIED로 승격되지 않음 | budget 0/최소값/중단/재시도 | 상태 전이 테스트 |
| M-08 | 거절 이유가 실제 반례와 일치 | 위반점 exact rational gap ≤0 또는 불안정 증거 | rejection witness 계획 |
| M-09 | 표시용 근사값이 판정에 사용되지 않음 | Hz/float 표시 변조와 exact proof 분리 | schema 테스트 |
| M-10 | 핵심 refactor가 과거 인증서를 깨지 않음 | 기존 v1/v2 fixture를 양방향 검증 | 호환성 매트릭스 |

## 3. 입력 의미와 경계값 정책

NaN, infinity, bool/string disguised numeric, complex, 비정규화 a0, 빈 배열, section 초과, 잘못된 gamma는 명확한 invalid 입력입니다. generator/iterator에 대한 최대 길이 검사도 필요합니다. 현행 `tuple(sections)`처럼 먼저 전체를 소비하는 경로가 외부 무한 generator나 초대형 입력을 받을 수 있는지 조사하고, 공개 경계에서는 상한+1개까지만 읽도록 설계합니다.

`+0/-0`의 수학적 동등성과 byte-level binding을 구분합니다. 기본 v1.0 계약은 사용자가 배포한 비트를 바인딩하고, 정규화 정책을 schema/version으로 고정합니다. 임의 epsilon으로 STRICT `<`를 `≤`로 바꾸지 않습니다. 동일성 경계에서 미세한 rounding margin을 끼워 넣어 통과시키지 않습니다.

float32 rounding은 명시적 옵션이며 기본값·배포 정밀도·검사 precision 불일치를 진단합니다. a0 정규화, SOS 순서 변경, 계수 scaling은 기존 배포 값을 바꾸므로 별도 transformation record를 생성하고 재인증합니다. 상쇄된 불안정 pole이 전체 전달함수에서 보이지 않아도 각 section 안정성 정책은 유지합니다.

## 4. 세 종류의 독립 검증

### 4.1 독립 알고리즘 오라클

SymPy의 유리 다항식 root counting/격리 기능을 활용한 별도 구현을 유지합니다([S04](11_SOURCES_AND_BASELINE.md#s04)). SOS의 `γ²D(c)-N(c)`를 독립적으로 전개하고 닫힌 `[-1,1]` 구간의 근과 부호로 판정합니다. shipping Bernstein helper를 오라클에서 import하지 않습니다. 경계의 중근과 끝점 근을 반드시 포함합니다.

오라클도 무한 자원을 갖지 않습니다. 오라클 timeout은 `ORACLE_UNRESOLVED`로 기록하며, 해당 행을 정답이 있는 성공률 분모에 넣지 않습니다. 그러나 원본 데이터셋과 unresolved 통계에서는 삭제하지 않습니다. 리소스를 늘린 별도 exact solver·수작업 증명으로 해결하기 전까지 release-required 사례는 미통과입니다.

### 4.2 인증서 소비자 검증

독립적으로 표현한 rational verifier가 입력 계수·임계값·proof cover를 다시 검사합니다. producer와 같은 함수 재호출만으로 “독립”이라고 광고하지 않습니다. producer verdict, verifier verdict, oracle truth를 결과 schema의 서로 다른 필드에 보존합니다. 세 결과가 모두 같다는 것은 도구 간 교차검증이지 사람의 외부 감사가 아닙니다.

### 4.3 외부 수학·구현 리뷰

외부 reviewer에게 증명 명제, 정의역, source snapshot, 미해결 경계, 자원 제한, 공격 fixture, 오라클 설계, 알려진 결함을 제공합니다. 최소 1명의 DSP/수치·형식 검증 전문가가 핵심 증명 의무를 검토하고, 작성자가 아닌 코드 reviewer가 구현과 verifier의 가정을 대조합니다. 이해상충·보수·검토 범위를 기록합니다. 검토자가 “시험 통과 확인”만 했으면 “수학적 증명 감사”라고 부르지 않습니다.

## 5. 코어 개선의 우선순위

**P0:** 상태·입력 바인딩·certificate consumer 상한·재현 가능한 verifier를 먼저 고정합니다. 성능 refactor 전에 현재 proof object의 golden fixture와 oracle crosscheck를 동결합니다.

**P1:** 다항식 최대공약인수 약분/공통 scale 제거, 중복 계산 cache, section별 조기 안정성 검사, 빠른 충분조건을 평가합니다. 모든 fast path의 `certified`는 같은 proof consumer를 통과해야 합니다. float64 추정은 분할 순서의 힌트로만 사용하고 최종 긍정 판정에는 사용하지 않습니다.

**P2:** 증명 실패의 정확한 witness·진단, full-inspection과 decision-only의 비용 분리, 배치의 프로세스 격리, 재현 가능한 native 연산 경계입니다. 불필요한 peak-bound refinement를 의사결정 경로에서 분리하지만 API와 산출물 이름을 바꿔 비용 비교가 정직하도록 합니다.

## 6. 자원 예산과 수학적 상태

| 계층 | G0 기본 요구안 | 소진 시 상태 | 금지 사항 |
|---|---|---|---|
| 입력 parser | 입력 128KiB, 최대 32 SOS, nesting/숫자 길이 제한 | INVALID_INPUT / UNSUPPORTED_POLICY | 잘라 읽고 나머지 무시 |
| proof parser | proof 4MiB, 개별 정수 문자열 길이·cover 수 제한 | INVALID_CERTIFICATE | 전역 파서 제한 해제 |
| core worker | 기본 5s/256MiB, 노드 50,000, 깊이 64 정책 | UNKNOWN_RESOURCE_LIMIT | 실패를 수학적 반례라고 표시 |
| 확장 offline queue | 명시 승인된 30s/1GiB 프로필 | UNKNOWN 또는 결과 | 일반 처리 예산을 묵시적으로 확대 |
| exact oracle | 별도 worker와 상한, slow queue | ORACLE_UNRESOLVED | UNKNOWN을 정답 PASS로 가정 |

정수 크기·상한은 실제 worst case fixture를 통해 G0/G1에서 조정합니다. 상한이 표현 가능한 정상 proof를 거절할 때는 명확한 정책 오류로 보고하고 우회 코드를 추가하지 않습니다. 외부 hard timeout이 worker를 종료해도 상위 프로세스는 살아 있어야 하며 성공 파일이 남으면 안 됩니다.

## 7. 범위를 넓히기 전에 필요한 별도 증명

전체 SOS peak location은 gain positivity와 다른 문제입니다. 상태가 있는 filter switching은 각 구간의 안정성 인증을 이어 붙인 것으로 전체 안정성이 증명되지 않습니다. 내부 overflow와 최종 출력 이득도 다릅니다. 실제 유한 정밀도 보증을 추가할 때는 arithmetic model, rounding mode, FMA/FTZ/DAZ, 초기 상태, 입력 상한, 중간 state 상한, 오차 누적 모델을 별도 명세해야 합니다.

OpenAI/math 연계는 연구 트랙으로 유지합니다. 본 산업용 GOAL 달성에 필요하지 않은 신규 정리 통합으로 핵심 정확성·고객 검증 일정을 지연시키지 않습니다.

## 8. 완료 정의

모든 M-ID에 테스트·증명 위치·담당 reviewer가 연결되어야 합니다. oracle disagreement는 0이어야 하며, resolve하지 못한 release-required 사례가 있으면 G2를 닫지 않습니다. 경계·자원 초과의 UNKNOWN은 정직한 결과지만 해당 고객 배포를 자동 승인하는 결과는 아닙니다.
