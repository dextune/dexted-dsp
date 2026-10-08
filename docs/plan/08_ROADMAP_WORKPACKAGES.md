# 08. 단계별 일정, 책임, 상세 작업 패키지

[문서 홈](README.md) · [승인 게이트](09_ACCEPTANCE_AND_ADVERSARIAL_REVIEW.md)

## 1. 계획 가정과 자원

아래 일정은 **팀 계획용 기준안**이며 이 대화에서 미래 작업을 자동 수행한다는 약속이나 납기 보장이 아닙니다. D0는 제품 범위·인력·자료 접근을 승인한 날짜입니다. 상대 주차로 24주를 배치합니다. 실제 고객 자료와 외부 reviewer 확보가 늦어지면 gate를 늦추며 성공한 것처럼 상태를 바꾸지 않습니다.

계획 용량은 코어 1.0 FTE, 수학/수치 1.0, QA/데이터 1.0, release/통합 0.5의 **총 3.5 FTE**를 가정합니다. 24주 ×5일 ×3.5=420 person-days의 총량에서 회의·휴가·리뷰·실험 실패·미예측 작업을 고려하여 70%인 294일을 작업 배정 기준으로 잡습니다. 외부 고객의 응답·자료 권한 처리·수학 reviewer 예약 시간은 이 계산으로 보장되지 않습니다. 개인 한 명이 수행하면 일정과 독립성 구조를 다시 산정해야 합니다.

담당자 이름은 확보 전까지 역할로 표시합니다. 아직 참여를 확약하지 않은 외부 인력 이름을 쓰지 않습니다. 요구 승인/수학 검토/release 승인자가 코드 작성자와 완전히 동일한 구조를 산업용 독립 리뷰로 인정하지 않습니다.

## 2. 단계와 종료 조건

| 주차 | 단계 | 핵심 산출물 | 종료 조건 |
|---|---|---|---|
| W1~2 | 범위·파트너·baseline | S01~03, proof obligation 초안, rights 요청 | G0: 산업용 의미·대상 계약·지표 동결 |
| W3~6 | 코어·consumer·API 경계 | M01~04, A01/A03/A05, 초기 golden/fuzz | G1: 수학 의무·자원 정책·negative control |
| W7~12 | corpus·oracle·streaming | D01/D02/D04/D06, T01~04, B01~03 | G2: 합성 정확성·상태 보존·기본 장시간 기반 |
| W10~14 | 실제 자료·lineage | D03/D05, 제품 adapter, 실제 holdout | G3: 실제 자료의 수량·권한·길이 충족 |
| W13~18 | 실측·host·운영 | B04/B05, T05~07, shadow 도입 | G4: 비용·메모리·cross-host·장시간/soak |
| W17~20 | 배포·보안·재현 | R01~04, CI tier, provenance, rollback | G5: 배포·보안·유지운영 체크 통과 |
| W19~22 | 외부 리뷰·고객 수용 | R05, U02, P01/P02 | G6: 외부 정확성/수용성 검토 |
| W23~24 | 결함 정리·release freeze | G01/G02, 재시험·승인 기록 | G7: 필수 gate 전부 승인 |

겹치는 주차는 병렬 작업을 뜻합니다. 아직 완료되지 않은 입력을 가정하고 종속 게이트를 승인하지 않습니다. 예를 들어 W12까지 코어 시험이 끝나도 실제 계수 권한이 없으면 G3는 닫히지 않습니다.

## 3. 작업 목록: 구현 계획과 검증 가능한 완료 정의

PD는 담당 개발/검토 effort의 초기 추정값입니다. 대기시간이나 전체 elapsed 기간이 아닙니다. 작업별 분해·견적 재검토는 D0 이후 진행하되 목표 완화는 별도 변경 승인 대상입니다.

| ID | 우선 | 담당 역할 | 작업 / PD | 선행 작업 | 산출물 | 완료 정의 |
|---|---|---|---|---|---|---|
| S01 | P0 | PM/수학 | 범위·고객 계약 고정 / 3 | 없음 | 지원 모델·정밀도·산업용 의미·비목표 승인 | 01 문서와 goal manifest의 버전·승인자 기록 |
| S02 | P0 | QA | 현재 증거·차이점 동결 / 2 | S01 | 현재 source/benchmark/CI hash inventory | 기존 9/25/1200/64 case의 의미를 혼동하지 않은 baseline |
| S03 | P0 | PM/데이터 | 파트너·자료 권한 모집 / 5 | S01 | 3개 실제 프로젝트의 데이터·일정 합의 | 샘플 제공/보관/재현 권한과 담당자 확보 |
| M01 | P0 | 수학 | 증명 의무 추적표 / 5 | S02 | M-01~M-10 명제·코드·시험 연결 | 작성자 외 검토자가 범위와 가정 확인 |
| M02 | P0 | 수학 | 독립 오라클 강화 / 6 | M01 | 별도 polynomial expansion·exact root classifier | shipping helper 재사용 없음, analytic cases 일치 |
| M03 | P0 | 코어/QA | 경계·legacy golden corpus / 4 | M01 | unity·ULP·unstable·v1/v2 regression fixture | old artifact immutable, boundary expected truth 확정 |
| M04 | P0 | 코어 | 자원·입력 상한 / 6 | M03 | bounded parser·iterable·worker budget policy | 무한 iterable/거대 proof/timeout이 프로세스를 보호 |
| M05 | P1 | 수학/코어 | 정확한 거절 witness / 7 | M02, M03 | dyadic gain witness·section stability reason | 가능한 경우 독립 검증; 불가능하면 명확한 reason |
| M06 | P1 | 코어 | 검증된 fast path 최적화 / 8 | M02, M04 | scale 축약·cache·predicate/bounds 분리 | 모든 긍정 fast path가 동일 verifier/oracle 통과 |
| A01 | P0 | 코어 | 상태·오류 공개 계약 / 5 | S01, M03 | verdict/reason/execution/unknown 모델 | 기존 exit code 보존, truthiness로 pass 금지 |
| A02 | P0 | 통합 | 실제 export adapter / 6 | A01, S03 | 배포 비트·precision·정규화 lineage | 변형 후 재인증, 제품 payload 재해시 |
| A03 | P0 | 코어 | 인증서 소비자 경계 / 7 | M04, A01 | schema·integer/cover 상한·mismatch 검증 | 모든 필수 tamper negative control 거절 |
| A04 | P0 | 통합 | 원자적 배포 게이트 / 6 | A02, A03 | artifact freeze·atomic output·stale proof 차단 | TOCTOU/kill/diskfull에서 false deployment pass 0 |
| A05 | P0 | 코어 | 격리·취소·배치 실행 / 6 | M04, A01 | bounded worker·job ID·partial 결과 | 작업 중단 후 다음 작업 정상, 이전 실패 보존 |
| A06 | P1 | native | native 계약 안정화 / 8 | A01, M03 | ABI·error·thread·allocation 표 | C 경계 예외 0, f32 Python 판정과 일치 |
| D01 | P0 | 데이터/수학 | 10만 계수 corpus 생성 / 7 | M02, S02 | 5개 strata quota·seed·rawhex | invalid/unknown 분모 분리, 모든 ID 보존 |
| D02 | P0 | 데이터 | 계보·holdout 관리 / 4 | S03, D01 | product/session group split·dedup | 동일 parent 변형의 split 누수 0 |
| D03 | P0 | 데이터/PM | 실제 계수 3,000건 확보 / 10 | S03, D02 | rights-approved immutable exports | 3 partner, 1,000 holdout 실제 확보; 미달은 BLOCKED |
| D04 | P0 | QA/데이터 | 24건 장시간 corpus 강화 / 5 | S01 | 76h manifest·peak dwell·event schedule | 짧은 loop 아님, frame-count·hash·seed 검증 |
| D05 | P0 | 데이터 | 실자료 장시간 20건 / 8 | S03, D02 | continuous/derived 구분과 원본권한 | 개별 최소길이·source lineage·privacy 확인 |
| D06 | P0 | QA | 입력·결과 영구 증거 / 4 | D01, D04 | content-addressed storage·retention | 다른 host가 동일 raw input을 확인 가능 |
| T01 | P0 | QA/수학 | 대규모 core/oracle 교차검증 / 7 | D01, M02, A03 | 전량 resolved/unresolved 상태와 proof | unsafe certification 0, 미완료 행 삭제 0 |
| T02 | P0 | QA | consumer·parser mutation/fuzz / 6 | A03, M04 | attack fixture·nightly fuzz report | 의도적 위조 모두 탐지, crash/OOM 경계 보호 |
| T03 | P0 | QA/통합 | 실제 엔진 streaming adapter / 7 | A02, D04 | float32/f64·block-state 비교 | state reset/채널 공유/frame 누락 negative control 탐지 |
| T04 | P0 | QA/수학 | 공진·tail·고정밀 window / 7 | T03, M02 | high-Q dwell·initial-state·tail bound | 충분한 settling 해석, pointwise peak 오해 없음 |
| T05 | P0 | QA/native | OS·컴파일러 차등 검증 / 5 | A06, T01 | 3 host-family 설치·native report | 지원 조합 정확성 동일, unsupported 명시 |
| T06 | P0 | QA/통합 | 실패·복구·TOCTOU 주입 / 6 | A04, A05 | C-003~C-008 증거 | incomplete artifact가 pass되는 경로 0 |
| T07 | P0 | QA/release | 24h·72h wall-clock soak / 8 | T03, T06 | 실제 monotonic duration·RSS trend | 가상 material duration과 분리, 중단원인 해결 |
| B01 | P0 | QA | benchmark 상태 손실 제거 / 4 | A01, A05 | JSONL per-case result와 UNKNOWN 보존 | assert abort 후 성공 행만 남는 구조 제거 |
| B02 | P0 | 수학/QA | 공정한 SciPy/control 비교 / 6 | B01, D01 | SOS 표현·단위·adaptive baseline | 정밀도·grid·변환비용 명시, conditioning 대조 |
| B03 | P0 | QA | 격리 RSS/native 계측 / 5 | A05, B01 | heap/RSS/retained/native 분리 | 다른 method의 high-water 귀속 오류 0 |
| B04 | P0 | QA | 계층 통계·원시 감사 / 4 | B02, B03 | paired delta·family quantiles·cluster CI | 반복 횟수와 독립 사례 수 혼동 0 |
| B05 | P0 | 외부/QA | 외부 장비 정확성 재현 / 6 | D06, T05, B04 | 외부 조직 source/input verdict 재현 | 작성자의 또 다른 CI runner를 외부 감사로 부르지 않음 |
| B06 | P1 | UX/QA | 근거 기반 README·시각화 / 4 | B04 | 비용·unknown·모바일 포함 charts | raw 재생성 일치, 형식 아닌 blind comprehension 통과 |
| R01 | P0 | release | clean package·consumer / 6 | A03, A06 | wheel/sdist/native install·license metadata | 소스경로 없이 예제 실행, 데이터 payload 미포함 |
| R02 | P0 | release | 공급망·SBOM·출처 / 5 | R01 | pinned build·hash·attestation/SBOM | source/binary 연결 검증; 인증 level 과장 없음 |
| R03 | P0 | QA/release | 단계별 CI와 보존 / 4 | T02, B01, R01 | PR/nightly/weekly/release lane·artifact policy | 느린 시험 skip이 full-pass로 계산되지 않음 |
| R04 | P0 | PM/release | 사고·rollback·지원 계약 / 3 | S01, A04 | incident playbook·영향 버전 추적 | false-certification 가상 incident로 rollback 연습 |
| R05 | P0 | 외부/수학 | 외부 수학·구현 검토 / 8 | M01, M02, T01 | 독립 검토 범위·지적·수정·서명 | 단순 테스트 확인이 아니라 명제/구현 의무 review |
| U01 | P1 | UX/통합 | 설치·진단·제품 guide / 4 | A02, A04 | 실계수 설명·UNKNOWN·단위·예제 | 사용자가 자기 계수로 실패 이유를 찾을 수 있음 |
| U02 | P0 | UX/PM | 외부 사용자 10명 시험 / 5 | U01, B06 | 관찰 기록·성공률·막힌 단계 | 9/10 15분 목표; 실패 후 새로운 참가자로 재평가 |
| P01 | P0 | 파트너/QA | 3 프로젝트 shadow 도입 / 8 | D03, D05, A04, T06 | 기존 gate와 병행, 실제 결함·비용 수집 | 고객 승인 없는 자동배포 영향 없음 |
| P02 | P0 | 파트너/PM | canary·도입 수용성 평가 / 5 | P01, T07 | false-block/triage/rollback 결과 | 사용자 책임자가 범위·비용·재현성 승인 |
| G01 | P0 | QA | 요구사항·증거 묶음 감사 / 4 | B05, R02, R05, P02, U02 | IND/M/A/B/C IDs → artifact trace | 미실행·미달·외부 대기 항목 모두 표시 |
| G02 | P0 | PM/수학/release | 최종 G7 출시 승인 / 3 | G01, R03, R04 | 모든 필수 gate sign-off·release notes | 평균점수로 critical gap을 덮지 않고 owner가 승인 |

배정된 초기 작업 추정 합계는 **252 PD**입니다. 294 PD 유효 용량과의 차이를 정량적으로 확인하고, 새로운 작업은 기존 작업 삭제로 숨기지 말고 change log에 반영합니다. 이 수치는 성과 측정이 아니라 초기 용량 계획입니다.

## 4. Critical path와 우선순위 조정

기술 경로는 `S02→M01→M02/M03→A03→T01→R05→G01`입니다. 현장 경로는 `S03→D02→D03/D05→P01→P02→G01`입니다. 어느 하나라도 막히면 G7은 대기합니다. 외부 전문가와 자료 파트너 모집을 마지막 달로 미루지 않습니다.

성능 목표 미달이 발생하면 수학적으로 검증된 최적화 M06을 우선하되 A03/false-certification 시험을 생략하지 않습니다. native serialization, SOS peak-frequency 위치, fixed-point 지원은 첫 제품의 critical path에서 분리합니다. 반복적인 README 꾸미기만으로 핵심 게이트가 진전되었다고 계산하지 않습니다.

## 5. 작업 패키지 공통 완료 체크

각 작업은 문제 정의, 지원 범위, 변경한 코드·문서, 테스트 ID, 원시 증거 경로, 성능 영향, 알려진 제한, author 외 reviewer, rollback 영향, 관련 goal ID를 포함해야 합니다. 단순 commit 수나 구현 LOC는 완료 기준이 아닙니다.

데이터 작업은 원본 권리·hash·lineage·수량을 포함하고, 시험 작업은 실패/UNKNOWN/NOT_RUN까지 결과에 남깁니다. 외부 검토 작업은 실제 검토자·범위·지적·해결 상태가 있어야 합니다. 도구가 구현되어 있어도 필요한 corpus에서 실행하지 않았으면 EXECUTED로 올리지 않습니다.

## 6. 주간 운영과 변경 관리

주 1회 gate별 신호를 확인합니다: 신규 false certification, oracle unresolved, UNKNOWN 비율, 미해결 P0, 실자료 확보 수/시간, 누수/timeout, 권한 미확보, 외부 검토 예약 상태입니다. 일정 위험은 숫자와 의존성으로 표시합니다.

목표 변경 요청에는 이유, 변경 전후 기준, 고객 승인, 영향을 받는 기존 증거, 새로운 재시험 범위를 적습니다. 실행 결과가 나쁘다는 이유만으로 family를 빼거나 precision을 바꾸고 같은 protocol version을 유지하지 않습니다. 계획 버전과 결과 버전을 동시에 올립니다.

## 7. 후속 릴리스 후보 — 첫 제품과 분리

**v1.1 후보:** native proof serialization, 전체 SOS peak localization, 더 강한 batch API, 추가 OEM adapter입니다. **연구 후보:** certified Hz transformation, runtime roundoff/overflow bound, 시간가변·MIMO 모델, OpenAI/math 기반 새로운 인증입니다. 각 후보는 별도 명제·고객 가치·독립 평가를 통과한 뒤 정식 로드맵에 편입합니다.
