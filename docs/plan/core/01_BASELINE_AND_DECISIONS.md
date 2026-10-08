# 01. 현행 소스 진단과 확정할 설계 결정

[코어 명세 홈](README.md) · [요구사항 계약](contracts/requirements.json)

## 1. 기준과 조사 방법

기준 커밋은 `9f6df34d45f418995dedf18e3b328524dd18ec6b`입니다. 기존 마스터 플랜·streaming runner와 GitHub의 현재 `verify.py`, `peak.py`, `peak_region.py`, `inspection.py`, `native.py`, C++ cascade를 대조했습니다. 아래 항목은 코드에 보이는 구조와 개발 과제입니다. 악용 가능성·정확성 결함을 재현했다고 주장하는 vulnerability 보고서는 아닙니다.

## 2. 현행 함수와 구체적 개발 간극

| 파일·함수(현존) | 확인한 동작 | 개발할 것 / 연결 ID |
|---|---|---|
| `model.py: Biquad.from_coefficients, from_sos` | 명시적 f32 변환, a0=1 요구, iterable 소비 | row 7개/section 33개까지만 읽는 상한, 실행 가능한 사용자 iterator 격리 / CR-01 |
| `cascade.py: validate_sections` | `tuple(sections)` 후 최대 32 검사 | 길이 제한 전에 전체 materialization 방지 / CR-01 |
| `biquad.py: certify` | exact Jury+quadratic strict 판정 | golden 불변, 경계 및 positive-scale 최적화 증명 / CR-02 |
| `cascade.py: gap_polynomial, prove_positive` | integer gap, dyadic cover, unknown | 입력→gap→subdivision 전체 예산; 실패 witness와 reason 유지 / CR-03, CR-04 |
| `verify.py: verify_cascade` | caller 입력 바인딩, Fraction cover 검사; 전용 sandbox 아님 | parser byte/number 상한, bounded expected iterable, verifier 독립 예산 / CR-05 |
| `verify.py: verify_biquad` | witness 전체 대신 원래 rational decision을 재계산 | v1 동작 보존, 새로운 hardened envelope만 witness 엄격 계약 / CR-06 |
| `inspection.py: inspect_sos, inspect_cascade` | decision 후 bounds 별도 재계산 | 신규 decision-only facade; optional refinement가 판정을 덮지 않음 / CR-07 |
| `inspection.py: verify_inspection` | legacy/v2 proof 및 bounds·region 재생성 검사 | 외부 정책보다 proof의 budgets를 신뢰하지 않는 reader / CR-05, CR-06 |
| `peak.py: bound_sos_peak_gain` | witness lower와 증명된 upper, budget_limited | 조기 중단 시 유효 bracket 보존, 상대 폭 필드의 의미 명확화 / CR-08 |
| `peak_region.py: localize_peak` | 단일 biquad만 exact c 구간, Hz는 근사 | SOS 전체 stationary isolation은 신규 후속 API / CR-16 |
| `native.py: NativeCascade.check` | f32 전용·반환 상태 문자열, 먼저 tuple 생성 | bounded rows, ABI 오류 테이블, 지원/unsupported 조합 / CR-09 |
| `cpp/.../cascade.hpp: positive_over_interval` | depth-limit에서 즉시 unknown 반환 | Python과 탐색 정책 차이 문서화·trace 검증 / CR-09 |
| `benchmarks/competitive/run.py: run` | 작은 사례마다 bool, mismatch 시 assert 중단 | UNKNOWN/error 보존, 모든 예정 case 종결 로그 / CR-10 |
| `docs/plan/tooling/longrun.py: run_record` | `--with-dexted`로 고정 참조 SOS 1회 인증 가능, 3개 SciPy lane | 다양한 filter fixture, expected reject/unknown, engine adapter, 증거 영속화 / CR-11~13 |

현재 producer는 32개 section을 받을 수 있지만 산업용 ordinary 성능 계약은 1~16입니다. Python f64 지원을 C++ f64 지원으로 오인하지 않습니다. 신규 모듈은 이 문서에 설계했을 뿐 아직 라이브러리에 존재하지 않습니다.

## 3. 설계 결정 기록

**CD-01 / P0:** 기존 public entry point와 v1/v2 증명 스키마의 의미를 바꾸지 않습니다. 강화된 네트워크/파일 경계는 새로운 facade와 versioned envelope를 사용합니다. 새 consumer의 엄격한 wire validation을 기존 dict API의 소급 검증 기준으로 강제하지 않습니다.

**CD-02 / P0:** positive 판정은 정수/유리 증거에만 근거합니다. float grid, fast analytic estimate, 외부 scalar norm은 split 순서·대조 결과에만 사용합니다. 최적화가 proof trace를 바꾸면 새 producer build로 남기되 truth는 동일해야 합니다.

**CD-03 / P0:** 적대적 Python 객체는 데이터가 아니라 실행 가능한 코드입니다. max+1 iterator 검사는 횟수만 제한하며 `next()`가 멈추는 경우의 시간 한도를 보장하지 못합니다. 신뢰되지 않은 요청은 bounded byte format을 통해 worker로 전달합니다.

**CD-04 / P0:** 수학 결과와 실행 결과는 서로 다른 필드입니다. timeout, OOM, cancelled는 gain failure가 아닙니다. 모든 실패는 배포를 차단하되 일반 필터를 전부 UNKNOWN으로 만드는 구현도 coverage gate에 실패합니다.

**CD-05 / P0:** proof 생성·검증·입력 재확인까지가 verified decision입니다. 보고서 생성과 peak refinement는 별도 계약·측정입니다. 기존 함수의 비용을 조용히 줄인 뒤 과거 benchmark와 같은 명칭으로 speedup을 주장하지 않습니다.

**CD-06 / 후속:** SOS peak location·native proof export는 v1.0의 gate를 막지 않습니다. 정확한 거절 witness와 C ABI 오류 안정화는 핵심입니다. '모든 확장 P0' 분류는 마스터 플랜의 scope와 충돌하므로 폐기합니다.

## 4. 호환성 동결 목록

`certify`, `certify_cascade`, `verify_biquad`, `verify_cascade`, `inspect_*`, `verify_inspection`, `GainBounds`, `PeakRegion`의 기존 테스트를 그대로 실행합니다. CLI exit 0/1/2/3, `a0=1`, γ의 엄격 양수, represented coefficient semantics는 유지합니다. `+0/-0`는 실수로 같아도 배포 바이트 바인딩에서 구분합니다.

새 상태 객체의 `bool(result)`는 예외를 던지도록 제안합니다. 기존 반환 dict나 bool의 의미를 뒤집지 않습니다. 기본 public API에서 자동 다운로드/컴파일, 전역 float rounding mode 변경, 전역 Python 정수 변환 제한 해제를 하지 않습니다.

## 5. baseline 재검증 산출물

구현 시작 시 소스 blob 목록, Python wheel/native hash, 기존 인증서 파일 hash, corpus membership, 환경, 원시 반복 시간을 신규 run 디렉터리에 저장합니다. 이전 `bootstrap-pilot.json`의 `dexted_core_executed=false`와 기존 timing archive를 수정하지 않습니다. 코어 파일 변경 시 오래된 benchmark source hash 감사가 깨지는 것은 정상 신호이므로 새로운 versioned evidence를 생성합니다.
