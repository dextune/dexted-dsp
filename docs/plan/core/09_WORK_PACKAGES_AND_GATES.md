# 09. 구현 순서, 함수별 작업, 상위 플랜과의 추적

[코어 명세 홈](README.md) · [상위 45개 WBS](../08_ROADMAP_WORKPACKAGES.md) · [기계 판독 WBS](contracts/requirements.json)

## 1. 작업 정의와 공수 원칙

CW는 기존 마스터 WBS의 **세분화**이며 별개의 추가 24개 프로젝트가 아닙니다. 상위 PD와 CW 견적을 둘 다 더하지 않습니다. 24주·252PD 기준안은 자동 연장하거나 유지 가능하다고 단정하지 않습니다. CW-21에서 코드 audit·외부 의존성과 실제 견적을 대조해 capacity를 재승인합니다. 여기서는 허위 정밀도의 함수별 시간을 제시하지 않고 착수 조건·산출물·완료 기준을 고정합니다.

담당은 역할입니다. 아직 외부 reviewer가 확보됐다는 뜻이 아닙니다. 수학 변경은 author와 다른 reviewer의 sign-off가 필요하고 P0 true-certification defect는 점수로 상쇄하지 않습니다.

## 2. 상세 작업 24개

| ID/우선 | 변경 대상·산출물 | 선행 CW | 상위 WBS | 완료 판단 |
|---|---|---|---|---|
| CW-01 P0 | 현재 source/legacy golden/oracle baseline inventory | 없음 | S02,M03 | hashes·states·실행 경계 동결, CT-18 |
| CW-02 P0 | bounded input adapter·owning artifact | 01 | M04,A02 | CT-01~04 전부 통과 |
| CW-03 P0 | biquad witness contract와 invariants | 01 | M01,M03 | strict quadratic·Jury CT-05~07 |
| CW-04 P0 | SOS prepared polynomial·budget-aware subdivision | 02,03 | M04,M05 | CT-08~13, zero/tangency unknown 정책 |
| CW-05 P0 | typed result·reason/execution 분리 | 01 | A01,B01 | enum truth table, bool misuse 거절 |
| CW-06 P0 | process supervisor·resource enforcement | 02,05 | A05,M04 | next hang/OOM/cancel 후 부모 복구, CT-12/32 |
| CW-07 P0 | hardened parser·independent consumer | 02,04,06 | A03,M02 | CT-15~19, producer helper 독립성 |
| CW-08 P0 | envelope writer·legacy readers·golden | 03,07 | A03,R01 | schema 이동과 bits/caller binding |
| CW-09 P0 | decision-only facade·optional bounds 분리 | 04,05,07 | A01,M06 | CT-14/20, verified decision 성능 경계 |
| CW-10 P1 | positive scale/cache 최적화와 benchmark | 09 | M06,B04 | correctness 우선, p95/p99/RSS/coverage 비교 |
| CW-11 P0 | native ABI·bounded FFI·errors | 02,05 | A06,T05 | CT-24~26, -3 truthiness 방지 |
| CW-12 P0 | fixture inventory·actual CoreAdapter | 07,08,11 | D01,D04,T01 | 최소8 valid 필터·4 controls, source call trace |
| CW-13 P0 | independent RuntimeAdapter·state snapshots | 12 | T03,A02 | CT-27/28, tolerance 승인 |
| CW-14 P0 | 예정 case ledger·atomic partial evidence | 05,06 | B01,D06 | CT-32, fail-fast 뒤 not_run 보존 |
| CW-15 P0 | 24×8 longrun matrix·dwell/tail test | 12,13,14 | D04,T03,T04 | CT-29/31,192 full slots+독립 lane |
| CW-16 P0 | mutation detector·TOCTOU·deployment gate | 07,08,14 | A04,T02,T06 | CT-21/22/30,실제 실패 주입 |
| CW-17 P0 | all-case oracle ledger·cohort/holdout audit | 04,07,14 | M02,T01,D02 | CT-36,unknown/unresolved/no leakage |
| CW-18 P0 | isolated timings/RSS·censoring·paired stats | 09,11,14,17 | B02,B03,B04 | CT-33,두 실제 comparator·모든 불리한 결과 |
| CW-19 P0 | 3 host 차등 +24h/72h soak | 11,15,16,18 | T05,T07,B05 | CT-34,지원/미지원 enforcement 공개 |
| CW-20 P0 | clean package·CI tiers·rollback 증거 | 08,16,17 | R01,R03,R04 | CT-35,legacy+new facade full regression |
| CW-21 P0 | 요구·증거 감사·외부 수학 리뷰·capacity 재승인 | 17,18,19,20 | G01,R05,G02 | 모든 필수 CR evidence·reviewer,미달 BLOCKED |
| CW-22 후속 | SOS stationary isolation·ties·Hz optional | 04,07,17 | M05,M06(확장) | CT-37/38/42,별도 scope 승인 |
| CW-23 후속 | native proof serialization·consumer crosscheck | 08,11 | A06(확장) | CT-39/40,기존 ABI 미변경 |
| CW-24 연구 | runtime interval/roundoff/state 안전성 명제 | 13,17 | M01,T04(연구) | CT-41,제한된 모델·독립 수학 승인 |

CW-12의 실자료 파트너 의존, CW-21의 R05 외부 전문가 의존은 표의 CW 간선만으로 해결되지 않습니다. 상위 S03/D03/D05/P01/P02/G3/G6가 열려 있으면 CW가 완료되어도 industrial release는 차단됩니다.

## 3. 권장 commit/PR 순서

첫 묶음: CW-01~03 (실패 fixtures→adapter→부호 명세). 둘째: CW-04~08 (budget/result/worker/parser/version). 셋째: CW-09/11/14/17 (facade/native/ledger/oracle). 넷째: CW-12/13/15/16 (core-linked multiple filter longrun와 deployment attacks). 다섯째: CW-18~21 (비용·장비·내구성·release 검토)입니다. CW-10은 정확성 기반 위에서 병렬 진행하되 false certification 수정보다 우선하지 않습니다.

각 코드 PR은 `(CR,INV,CT,CW)`를 적고 변경 파일·signature·legacy 영향·before/after raw evidence·rollback plan을 포함합니다. 코드·oracle·acceptance threshold를 동시에 바꾼 PR은 별도 승인 없이 합치지 않습니다. 한 commit의 성공을 다음 commit에도 자동 적용하지 않습니다.

## 4. 코어 승인 게이트

**CG0 계약 동결:** baseline,ordinary cohort,worker limits,signature/schema 제안,gate authority 승인. 목표는 요구안임을 표시합니다.

**CG1 정확성·경계:** CT-01~26 중 해당 core 범위 mandatory 모두 실행,모든 INV 추적,legacy 불일치 0,false certification 0,typed failure closed.

**CG2 통합 검증:** 실제 설치 core call trace,192 slot schedule 완료,유효 input hashes,독립 runtime,negative controls 탐지. 미확보 actual filters/tolerances는 NOT_READY.

**CG3 비용·복구:** section/precision별 SLO,complete ledger,censoring,RSS,3 host와 실제 wall-clock soak. 장비 차이·unsupported 조합 공개.

**CG4 외부·출시:** 외부 review,customer coefficients/real long data,상위 G0~G7 evidence,승인자·지원 계약·rollback. 계획서·테스트 개수·평균점수로 대체 금지.

CG는 상위 G 게이트의 core 관점 세부 체크리스트입니다. 별도 이름의 gate를 만들었다고 기존 산업용 목표 12개를 축소하지 않습니다.
