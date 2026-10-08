# CI 계층 설계 template — 아직 새 workflow를 활성화하지 않았습니다

| lane | 트리거 계획 | 작업 | 제한·증거 |
|---|---|---|---|
| pull request | core/API/data/tooling 변경 | 기존 unit, manifest audit, 2초 smoke, small golden·tamper, clean install | 시간 budget 내 전량 수·skip 명시; 실제 장시간으로 표시 금지 |
| nightly | 승인된 매일 실행 | coefficient fuzz 50,000 목표, ordinary corpus subset, long pilot 6×30분 | immutable case logs; slow/unresolved queue 별도 |
| weekly | 승인된 정기 실행 | 합성24건76h 전량·실자료 subset·3host differential·RSS | 자료 권한·다운로드 비용·runner capacity 승인 |
| release candidate | 수동 승인 | 고정 holdout 전량, real sessions 전량, 24h×3/72h×1 wall-clock soak, 외부 재현 | G0~G7 signoff가 release의 선행 조건 |
| source or dependency change | 원인 기반 | 영향받는 proof·native·benchmark·certificate compatibility 재검증 | old evidence를 변경하지 않고 새 run |

대규모 원본 데이터는 repository 밖의 권한 제어 저장소에서 content hash로 가져옵니다. 설치 단계가 외부 음원을 자동 다운로드하지 않습니다. CI artifact 만료 전에 영구 evidence 위치로 옮기고 무결성을 확인합니다.

계획용 `longrun.py run --profile qualification`의 결과는 signal material-hours입니다. 운영 soak job은 별도의 worker orchestration과 실제 monotonic elapsed를 구현해야 합니다. 존재하지 않는 soak CLI를 이 template의 실행 가능한 명령으로 제시하지 않습니다.
