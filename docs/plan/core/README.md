# Core Engineering Specification — 산업용 코어 구현 명세

**버전:** 1.0 · **작성일:** 2026-10-08 · **분석 기준:** `9f6df34d45f418995dedf18e3b328524dd18ec6b`  
**상태:** SPECIFIED / IMPLEMENTATION_NOT_STARTED. 이번 변경은 설계·검증 명세 보강입니다. 아래 신규 API·성능 목표·76시간 코어 통합 시험을 이미 구현하거나 달성했다는 뜻이 아닙니다.

[상위 마스터 플랜](../README.md) · [기존 수학 계획](../02_MATHEMATICS_AND_CORE.md)

## 이 명세의 목표

개발자가 **어느 파일·함수를 어떻게 바꾸고, 어떤 불변조건을 지키며, 어떤 반례를 통과해야 작업이 끝나는지** 알 수 있게 합니다. 정답은 기존의 고정 실수계수 LTI 명제에 국한합니다. 데이터 파일이 길다고 수학적 인증의 정의역이 넓어지지 않습니다.

산업용 v1.0 필수 경로는 입력 상한 → 정확한 판정 → 독립 proof consumer → 자원 격리 → 계수 바인딩 → 실제 처리기 통합 검증입니다. 전체 SOS 피크 위치·native proof 직렬화는 후속 기능이며, 장치 연산 오차 증명은 별도 연구입니다. 이전 대화의 모든 항목을 P0로 묶은 분류는 사용하지 않습니다.

## 문서 구조

| 문서 | 구현 시 결정하는 것 |
|---|---|
| [01 소스 진단·우선순위](01_BASELINE_AND_DECISIONS.md) | 현행 함수, 실제 간극, 필수/후속 구분, 변경 금지 계약 |
| [02 수학 알고리즘](02_ALGORITHMS_AND_INVARIANTS.md) | Jury·정수 gap·Bernstein·strict equality·gain bounds·증명 의무 |
| [03 Python 함수 명세](03_PYTHON_IMPLEMENTATION.md) | 함수별 I/O, bounded iterator, cancellation, immutable inputs, pseudocode |
| [04 인증서·독립 검증](04_CERTIFICATES_AND_VERIFIER.md) | byte format, parser limits, witness, legacy adapter, 상태 진리표 |
| [05 C++·FFI 명세](05_NATIVE_AND_FFI.md) | ABI, 소유권, 길이·예외·thread·precision, Python과 UNKNOWN 차이 |
| [06 자원·성능](06_RESOURCES_AND_PERFORMANCE.md) | section/정밀도별 SLO, 전체 작업 예산, RSS, 손실 없는 비교 |
| [07 장시간 코어 통합](07_LONGRUN_CORE_INTEGRATION.md) | 24건·76h, 최소 8개 필터, 192 record-filter runs, negative control |
| [08 테스트·공격 행렬](08_TEST_MATRIX_AND_ORACLES.md) | test ID, 정확한 예상 상태, 부호·중근·위조·실패 주입 |
| [09 구현 순서·작업 추적](09_WORK_PACKAGES_AND_GATES.md) | 24개 세부 작업, 선행조건, 상위 45 WBS와 중복 계산 방지 |
| [10 후속 알고리즘 설계](10_EXTENSIONS_AND_ROUNDOFF.md) | SOS stationary roots, ties, directed Hz, rounding/state model |
| [11 실행·검토·근거](11_RUNBOOK_REVIEW_AND_SOURCES.md) | 지금 실행되는 명령/제안 명령, 외부 근거, 반대 검토 기록 |

## 기계 판독 계약

[requirements.json](contracts/requirements.json)은 요구사항·테스트·작업의 연결을 정의합니다. [budgets.json](contracts/budgets.json)은 목표 예산이며 [longrun-matrix.json](contracts/longrun-matrix.json)은 기존 24건과 필터 매트릭스를 결합합니다. [analytic-cases.json](contracts/analytic-cases.json)은 정확한 계수의 작은 명세 예제이며 산업용 데이터셋을 대체하지 않습니다.

문서 감사는 ID 누락, 순환 의존성, 상위 목표와의 불일치, 실행되지 않은 결과의 완료 표기, 매니페스트 누락을 실패로 처리합니다. 이 감사가 통과해도 코어가 산업용으로 검증된 것은 아닙니다.

## 시작 조건과 완료 조건

착수 전에는 소스 기준 커밋, 정책 예산, 기존 인증서 golden, 독립 oracle 결과와 변경 전 성능을 동결합니다. 각 구현 PR은 요구사항 ID와 실패 테스트를 먼저 포함합니다. 동일 ID를 새 의미에 재사용하지 않습니다.

완료는 `SPECIFIED → IMPLEMENTED → TESTED → EXTERNALLY_REVIEWED → APPROVED`로 기록합니다. `UNKNOWN`을 없애기 위해 정확성을 완화하거나, 필터를 묵시적으로 재설계하거나, SciPy 출력이 그럴듯하다는 이유로 CERTIFIED를 만들면 모든 출시 게이트가 열립니다.
