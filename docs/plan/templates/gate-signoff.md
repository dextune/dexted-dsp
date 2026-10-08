# 게이트 승인 기록 — 미작성 template

이 파일 자체는 승인 증거가 아닙니다. 아래 항목을 실제 자료로 채우고 책임자가 승인해야 합니다.

| 필드 | 작성 내용 |
|---|---|
| gate ID / goal IDs | 미작성 |
| 상태: PLANNED/IMPLEMENTED/EXECUTED/EXTERNALLY_REPRODUCED/APPROVED/BLOCKED | PLANNED |
| plan version / protocol version | 미작성 |
| source commit / build / dependency lock | 미작성 |
| input manifest SHA / 실제 corpus 수·시간 | 미작성 |
| 실행 command / host / 시작·종료·monotonic elapsed | 미작성 |
| raw result location / hashes / 실패·UNKNOWN·NOT_RUN | 미작성 |
| metric 기준·분모·실측값·미달 | 미작성 |
| 외부 reviewer·조직·독립성·검토 범위 | 미작성 |
| 알려진 제한·잔여 위험·고객 영향 | 미작성 |
| author / reviewer / 최종 승인 역할 | 미작성 |
| 승인 시각·범위·예외 만료 / 재시험 조건 | 미작성 |

## 검토자의 필수 확인

판정할 수 없는 입력이 배포되지 않았는지, 실제 자료 권한과 길이가 충족되는지, 입력/출력 hash가 실제 artifact에 대응하는지 확인합니다. false certification은 예외 승인할 수 없습니다. 인력·데이터·권한 미확보는 BLOCKED입니다. 자체 점수로 필수 게이트를 대체하지 않습니다.
