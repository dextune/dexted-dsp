# 07. 보안, 공급망, 배포, 장기 운영

[문서 홈](README.md) · [아키텍처](03_ARCHITECTURE_AND_API.md)

## 1. 위협 모델

입력 계수 JSON·인증서·데이터 경로·archive·고객 metadata는 신뢰하지 않습니다. 공격자는 큰 정수/cover/깊은 JSON으로 CPU·메모리를 고갈시키거나, 인증 대상과 실제 배포 파일을 바꾸거나, report의 표시값으로 검토자를 속이거나, dependency/workflow를 바꿔 잘못된 wheel을 배포할 수 있습니다. 해시 하나를 붙이는 것으로 모든 위협이 해결되지 않습니다.

| 위험 | 예방·탐지 통제 | release-blocking 시험 |
|---|---|---|
| parser 자원 고갈 | bytes·nesting·array·정수 문자열 상한, early rejection | 초대형·깊은 JSON·무한 iterable |
| algorithmic DoS | worker timeout/RSS/노드·깊이 상한 | near-boundary·고차수·비정상 입력 |
| forged/stale proof | 외부 입력 바인딩, strict consumer, schema 거절 | 계수/limit/cover/precision 변조 |
| TOCTOU | 최종 배포 payload 재해시, immutable artifact | 인증 후 계수 바꿔치기 |
| archive/path 문제 | path traversal·symlink·decompression limits | `../`, 절대경로, 과도한 압축비 |
| 공급망 변경 | pinned workflow·least privilege·artifact provenance | 다른 commit/build에 대한 설치 차단 |
| 고객 정보 유출 | offline default·redaction·권한별 보관 | 로그에 실제 음성·원 설계 유출 여부 |

## 2. 보안 설계 원칙

기본적으로 네트워크를 사용하지 않는 라이브러리·검증 경로를 유지합니다. 외부 corpus 다운로드는 별도 acquisition 명령과 사용자 승인 아래 진행합니다. 다운로드를 설치 훅이나 unit test에서 자동 실행하지 않습니다.

C API는 모든 예외를 경계 안에서 처리하고 버퍼 길이·null·count overflow를 검사합니다. Python API도 무제한 메모리 소비를 일으키는 입력을 정식 지원 경로에서 차단합니다. 내부 불변식 오류와 사용자의 잘못된 입력을 다른 오류로 분류합니다.

인증 실패 이후에는 안전한 대체 계수를 임의로 선택하지 않습니다. 배포 정책이 last-known-good 또는 manual approval을 정의할 수 있지만 고객이 명시적으로 승인해야 합니다. fail-closed가 서비스 전체 무중단을 의미하지는 않습니다.

## 3. 개발·검토 통제

NIST SSDF의 안전한 개발 관행을 참고해 요구사항·보호된 코드·검증·취약점 대응 책임을 운영합니다([S07](11_SOURCES_AND_BASELINE.md#s07)). 이것은 NIST가 제품을 인증했다는 주장이 아닙니다.

core predicate/verifier 변경에는 수학 검토와 코드 review 두 종류를 요구합니다. lock/dependency/schema/workflow 변경도 검토 대상입니다. historical benchmark source와 raw evidence는 변경 금지 또는 명시적인 새 버전으로만 추가합니다. 단순 docs 변경이 코드 hash를 바꾸지 않도록 합니다.

branch protection·required checks·release environment approval을 구성할 계획이지만, 이 문서만으로 GitHub 권한 설정이 실제 변경되지는 않습니다. 승인이 필요한 관리 작업은 repository owner의 명시적 수행 기록을 남깁니다. 서명되지 않은 commit을 서명된 것으로 표시하지 않습니다.

## 4. 패키징·지원 매트릭스

Python 기준 환경을 release별로 명시하고 현재 `Python>=3.10` 선언의 호환 범위와 실제 CI 조합을 대조합니다. 새 Python 버전이 나왔다는 이유로 미시험 버전을 지원 표에 자동 추가하지 않습니다. native는 OS/architecture/compiler/runtime library별 지원 artifact를 구별합니다.

source tree outside에서 설치한 wheel만 import하도록 clean consumer를 실행합니다. wheel→sdist 재빌드·CMake install/export consumer·동일 f32 fixtures·기존 certificate migration을 검사합니다. editable install만으로 배포 검증을 끝내지 않습니다. package에 테스트용 긴 음원·고객 자료·수백 MB 증거가 포함되지 않도록 manifest 검사를 둡니다.

## 5. 공급망 및 출처 증거

각 release에 commit/tree SHA, source archive checksum, wheel/native checksum, dependency lock, compiler/build flags, SBOM, license notice, 시험 결과, 서명 또는 provenance verification 방법을 붙입니다. SLSA 1.2의 source/build provenance 구조를 참고하되 실제 달성한 level을 감사 없이 임의 주장하지 않습니다([S08](11_SOURCES_AND_BASELINE.md#s08)).

PyPI 공개 배포는 owner·namespace·법적 고지·지원 정책을 확인하고 별도 승인합니다. Trusted Publishing/OIDC는 수동 장기 토큰 대신 CI identity를 활용하는 옵션입니다([S09](11_SOURCES_AND_BASELINE.md#s09)). 설정 완료와 보안 적합성은 직접 검증해야 합니다. 이 계획 작성 작업은 PyPI에 배포하거나 repo를 공개로 바꾸지 않습니다.

## 6. 버전·호환성·지원 정책

v1.0 이전에 public API와 certificate schema의 안정화 범위를 문서화합니다. breaking change는 major version 또는 명시된 certificate migration으로 처리합니다. minor release가 기존 proof의 의미를 바꿔서는 안 됩니다. 과거 인증의 수학적 내용과 특정 implementation version의 결함 유무를 구별합니다.

지원 기간은 제안값 12개월의 stable line으로 시작하고 staffing 검토 후 확정합니다. 보안·정확성 결함에 대한 대응 목표를 다음처럼 제안합니다: critical false certification은 인지 즉시 release 정지·공지 판단, 영업일 1일 이내 triage, 재현/우회책/고객 영향 범위 우선 공개. “모든 결함을 24시간 안에 완전 수정” 같은 불가능한 약속은 하지 않습니다.

## 7. 사고 대응과 rollback

1. 재현된 false certification은 incident ID로 등록하고 영향 가능한 release·입력 family를 잠급니다.
2. 해당 버전/정책에 대한 신규 배포 승인을 정지합니다. 고객 원자료는 공개 이슈에 붙이지 않습니다.
3. 영향을 받는 인증서 목록을 input hash·producer build로 찾고 재검증 계획을 제공합니다.
4. 마지막 안전한 release로 rollback하거나 manual review로 전환합니다. 안전성 불명확한 이전 버전을 자동 선택하지 않습니다.
5. 수정에는 반례·root cause·proof obligation 변화·독립 reviewer 확인이 필요합니다.
6. 수정판의 회귀·패키지·장시간/운영 시험을 마치고 release note와 revocation advisory를 기록합니다.

문제의 숫자를 README에서 지우는 것으로 incident를 종료하지 않습니다. 과거 evidence는 정정 안내와 함께 보존합니다.

## 8. 데이터 보존·개인정보

합성 raw는 재생성 가능하더라도 release에 사용한 manifest·generator·environment와 입력 SHA를 장기 보존합니다. 실제 자료는 계약된 retention·접근 통제·삭제 요청을 따라 관리하고 공개 보고서에는 비식별 요약만 올립니다. 외부 재현용 자료 접근이 제한되면 검증자가 확인할 수 있는 범위와 제약을 보고합니다.

GitHub Actions artifact 만료를 영구 증거 저장으로 오해하지 않습니다. 릴리스 근거는 내용 주소 기반 저장소나 승인된 영구 저장 위치에 별도 보존하고 무결성을 정기 검사합니다. 저장소·계정·출판 workflow의 권한 복구 절차도 runbook에 포함합니다.

## 9. 운영 승인에 필요한 최소 산출물

지원 표, threat model, 취약점 연락처, incident template, dependency/license audit, clean-install report, native ABI report, atomic gate test, rollback drill, source/binary provenance, owner 승인 기록이 필요합니다. 하나라도 계획 상태이면 정식 릴리스 체크리스트에 미완료로 남습니다.
