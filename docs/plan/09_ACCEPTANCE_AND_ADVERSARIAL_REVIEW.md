# 09. 출시 게이트, 승인 증거, 냉정한 적대적 리뷰

[문서 홈](README.md) · [작업 목록](08_ROADMAP_WORKPACKAGES.md)

## 1. 점수가 아닌 게이트

“내부 자체평가 9.5”를 산업용 합격 기준으로 사용하지 않습니다. 수학적 soundness·실제 데이터·출처·외부 검토·배포 책임 중 하나라도 빠지면 전체 출시를 막습니다. 승인 상태는 evidence와 검토자 기록으로만 변경합니다.

`PLANNED`: 기준만 존재합니다. `IMPLEMENTED`: 코드/자료 준비 도구가 있습니다. `EXECUTED`: 지정 corpus·환경·source에서 실제 시험했습니다. `EXTERNALLY_REPRODUCED`: 작성 조직 밖의 주체가 독립적으로 실행했습니다. `APPROVED`: 지정 책임자가 범위와 미해결 이슈를 검토해 승인했습니다. SKIPPED/NOT_RUN/BLOCKED를 PASS로 집계하지 않습니다.

## 2. G0~G7 출시 게이트

| 게이트 | 필요한 증거 | 필수 통과 조건 | 중단 조건 / 승인 역할 |
|---|---|---|---|
| G0 범위·정책 | 지원 계약, 고객 요구, 지표·host 사전 등록 | IND 목표·분모·범위·예산 동결 | 범위 불명확 / PM+수학 |
| G1 코어 경계 | M-ID 증명 의무, input/proof 상한, golden·mutation | unsafe positive path 없음, UNKNOWN fail-closed | 엄격 부등식 훼손·자원 무제한 / 수학+코어 |
| G2 합성 정확성 | 100,000 계수 결과, 모든 valid oracle 상태, consumer proof | resolved case에 false certification 0, required unresolved 해결 | 누락 행·순환 오라클·잘못된 인증 / QA+수학 |
| G3 실제 자료 | 3,000 export·1,000 holdout·3 partner, 실제 long 20건 | 권한·길이·lineage·독립 group 충족 | 합성으로 실제 자료 대체·권한 불명 / 데이터+PM |
| G4 실행·실측 | 24건76h + 실제 장시간, 24h×3/72h×1 soak, 3 host | 배포 오류 0, 기본 SLO·resource·state 시험 충족 | 기간 속임·메모리 은폐·불리한 사례 제거 / QA |
| G5 배포·보안 | wheel/native clean install, SBOM·출처, incident/rollback | 지원 matrix·consumer·signing/provenance·운영체계 | 소스와 배포 binary 불일치 / release |
| G6 외부 수용 | 외부 정확성 재현, 수학/구현 review, 3 shadow 프로젝트, 10 user | P0 지적 해결·9/10 도입 목표·권한 유지 | reviewer 독립성 부재·고객 영향 미평가 / 외부+PM |
| G7 최종 승인 | 전체 evidence bundle, 잔여 위험, 지원·release notes | 모든 필수 게이트 APPROVED, P0 미해결 0 | 다른 좋은 점수로 중요 미달 상쇄 / PM+수학+release |

현재 doc/tooling의 PASS는 G2/G4 전체 PASS가 아닙니다. 24건 중 pilot 6건만 실행했으면 나머지 18건은 NOT_RUN입니다. 실제 현장 data와 외부 review가 없으면 G3/G6는 BLOCKED입니다.

## 3. 요구사항 추적표

| Goal | 작업 연결 | 핵심 테스트 | 필수 artifact |
|---|---|---|---|
| IND-01 | M01/M02/A03/T01/R05 | A-001~A-011 | oracle/core/verifier case table, proof, external review |
| IND-02 | A01/A04/A05/T06 | A-009/A-012, C-003~C-008 | state-transition·deployment-negative reports |
| IND-03 | S03/D02/D03 | lineage·license audit | real export manifest + holdout hashes |
| IND-04 | D01/T01/B01 | A-008/A-009 | ordinary denominator·margin bins·UNKNOWN counts |
| IND-05 | B02/B04/M06 | timing protocol | raw repetitions·family p95/p99·host |
| IND-06 | M04/A05/B03/T07 | DoS·timeout·RSS | OS memory·worker termination evidence |
| IND-07 | D04/D05/T03/T04 | B full stream | real frames·input hashes·engine identity |
| IND-08 | T06/T07 | C-001/C-002 | monotonic 24h/72h log·RSS trends |
| IND-09 | T05/B05 | same-input multi-host | independent organization report |
| IND-10 | R01/R02/R03 | clean consumer | artifact checksums·SBOM·provenance |
| IND-11 | U01/U02/B06 | external user task | anonymized observation·9/10 result |
| IND-12 | R04/G01/G02 | rollback drill | incident plan·sign-off·support policy |

기계 판독 목표는 [qualification manifest](manifests/qualification-gates-v1.json), 작업 의존성은 [work package manifest](manifests/work-packages-v1.json)로 제공합니다. 표와 JSON 숫자가 달라지면 문서 audit가 실패하도록 관리합니다.

## 4. 적대적 리뷰 질문과 요구 증거

**“모든 입력을 UNKNOWN 처리해 false PASS 0을 만든 것 아닌가?”** 정확성 표와 별도로 ordinary safe 집합의 UNKNOWN·deployment blocks를 확인합니다. coverage gate 없이 soundness 숫자 하나만 제시하면 반려합니다.

**“같은 만든 예제에 유리한 경우만 남긴 것 아닌가?”** 실행 전 frozen IDs, 독립 parent split, lineage, 실패·타임아웃 포함 완료 수를 확인합니다. 30회 반복을 30개 독립 사례로 계산하면 반려합니다.

**“오라클과 라이브러리가 같은 오류를 공유하는가?”** 서로 다른 expansion 및 root-count/positivity 알고리즘, analytically known cases, import graph, 외부 수학 검토를 확인합니다. 함수 재호출만으로 독립성을 주장하면 반려합니다.

**“긴 자료라고 했지만 짧은 신호를 반복했는가?”** sample counter, input hashes, parent trace, generator recipe, actual decoded frame count를 확인합니다. 반복은 반복 stress라고 명시할 수 있지만 신규 실제 연속 기록 수로 계산하지 않습니다.

**“24시간 데이터 처리와 24시간 가동을 바꿔 말했는가?”** monotonic wall-clock evidence를 따로 확인합니다. material_hours가 24라는 JSON만 있으면 soak 게이트는 NOT_RUN입니다.

**“본격적인 DSP 처리의 정밀도를 Dexted가 증명한 것처럼 보이는가?”** proof scope가 fixed real coefficients에 국한되는지, 실제 엔진이 누구인지, rounding/state overflow/nonlinearity가 별도인지 확인합니다.

**“메모리 수치가 낮은 이유가 native buffer 누락인가?”** traced heap·RSS·baseline·isolated worker·native instrumentation 범위를 확인합니다. pooled process high-water 하나를 라이브러리 증분 메모리라고 부르면 반려합니다.

**“비교 대상에 불리한 coefficient representation을 강요했는가?”** SOS→polynomial 변환 오차, units, precision, 초기 모델 construction, grid endpoints를 확인합니다. library 자체 결함과 임의 sampling policy의 한계를 구별합니다.

**“인증이 맞아도 실제 배포 파일은 다른가?”** export binary→decoded input→proof→final product payload의 hash chain과 TOCTOU negative test를 확인합니다.

**“중요 실패를 평균 9.5점으로 덮었는가?”** gate별 P0 issue·unresolved·external review 상태를 확인합니다. 자체 점수는 산업용 승인 증거가 아닙니다.

## 5. 결함 우선순위와 재시험

P0는 false certification, 배포 false PASS, 위조 proof 수용, OOM/hang로 운영 파괴, 민감 자료 노출, release artifact mismatch입니다. 즉시 관련 배포 승인을 중지하고 원인·영향 범위를 분석합니다. P1은 계약한 ordinary SLO/UNKNOWN 비율 미달, 잘못된 수학적 거절, 필수 호환성/사용성 실패입니다. 지원 범위를 바꾸려면 고객·계획 승인 절차가 필요합니다.

수정 후 minimal regression 하나만 통과하고 끝내지 않습니다. 영향받는 proof obligation, dtype/family, certificate consumer, native build, benchmark source-hash, 장시간/운영 경로의 회귀 범위를 명시합니다. 이전 실패 로그를 지우지 않습니다.

## 6. 승인 파일 규칙

[gate sign-off template](templates/gate-signoff.md)에 명제·scope·source SHA·input hash·실행 상태·외부 reviewer·미달 사항·결정을 씁니다. 날짜·이름·권한이 비어 있는 template은 승인 문서가 아닙니다. 해당 환경에서만 유효한 예외는 expiry·고객 승인·영향 범위를 명시하며 수학적 거짓 인증 예외는 허용하지 않습니다.
