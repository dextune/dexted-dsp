# 산업용 전환 위험 등록부 — 초기 분석

| ID | 위험 / 관측 trigger | 영향 | 대응·중단 기준 | 담당 / WBS |
|---|---|---|---|---|
| R-01 | oracle FAIL인데 CERTIFIED | 잘못된 배포 승인 | 즉시 release 정지·반례·외부 review | 수학 / M02,T01,R05 |
| R-02 | UNKNOWN bool 축약·누락 행 | 가용성/정확성 왜곡 | 상태 schema·전량 JSONL | QA / B01 |
| R-03 | 실제 계수/권한 미확보 | 산업 대표성 없음 | G3 BLOCKED, 합성 대체 금지 | PM / S03,D03 |
| R-04 | 24h 데이터를 24h soak로 오인 | 운영 결함 미검출 | monotonic 벽시계 증거 별도 | QA / T07 |
| R-05 | 같은 source 조각의 holdout 누수 | 외부 일반화 과장 | product/session lineage split | 데이터 / D02 |
| R-06 | proof parser·높은 차수 DoS | OOM·서비스 장애 | 상한·worker hard stop | 코어 / M04,A05 |
| R-07 | native buffer 미계측 | 메모리 비용 누락 | isolated RSS·sanitizer | QA / B03 |
| R-08 | filter state 매 block reset | 장시간 output 왜곡 | 의도적 reset negative control | 통합 / T03 |
| R-09 | 인증 후 export 변조 | proof가 다른 계수를 인증 | 최종 payload hash gate | 통합 / A04 |
| R-10 | numerical polynomial 변환 conditioning | 비교 불공정·결과 왜곡 | section-preserving comparator | 수학 / B02 |
| R-11 | 실제 소리·설계의 무단 공개 | 개인정보·영업비밀·권한 침해 | private storage·review·redaction | 데이터 / D05,D06 |
| R-12 | reviewer 부족·자체점수 대체 | 독립성 없음 | G6 BLOCKED, 조기 reviewer 예약 | PM / R05 |
| R-13 | 일정 맞추려 정확성/범위 조용히 완화 | 제품 계약 위반 | G0 change control·버전 분리 | PM / G01 |
| R-14 | 높은 Q의 짧은 dwell·부족한 tail | resonance 미검출 | 독립 peak·settling 기준 | 수학 / T04 |
| R-15 | CI green을 산업 인증으로 홍보 | 신뢰·법적 위험 | claim review·게이트 상태 표시 | release / G02 |

각 위험은 발생일·담당자·완화 상태·잔여 위험·재시험 evidence를 추가해 관리합니다. 미발생/미평가를 해결 완료로 표시하지 않습니다.
