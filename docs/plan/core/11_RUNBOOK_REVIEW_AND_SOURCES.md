# 11. 실행 런북, 적대적 문서 검토, 출처

[코어 명세 홈](README.md) · [상위 실행 런북](../10_EXECUTION_RUNBOOK.md)

## 1. 이번 변경으로 실제 실행할 수 있는 명령

다음은 Python 3.10+ 표준 라이브러리만 사용하는 **문서·계약 감사**입니다. 저장소 루트에서 실행합니다.

```bash
python docs/plan/core/tooling/audit_core_spec.py
python -m unittest discover -s docs/plan/core/tooling -p 'test_*.py' -v
python docs/plan/tooling/audit_plan.py
```

추가된 명세 감사는 CR/INV/CT/CW 연결, DAG, 상위 WBS 매핑, budget 기본값과 기존 산업용 목표 일치, 24×8 longrun accounting, analytic fixture의 finite/raw-hex identity, 상대 링크를 검사합니다. 실행 결과는 `core/evidence/`에 보존합니다. 이 검사는 runtime core를 호출하지 않으며 현재 컴퓨터에서 76시간/608 filter-hours를 실행하지 않습니다.

## 2. 현재의 Dexted 연결 bootstrap 명령

기존 라이브러리 및 NumPy/SciPy를 설치한 환경에서만 다음 명령이 실행됩니다. 이번 보강에서 이 명령의 실행을 주장하지 않습니다.

```bash
python -m pip install .
python -m pip install -r docs/plan/tooling/requirements-tested.txt
python docs/plan/tooling/longrun.py run --profile smoke --with-dexted --out validation/industrial/core-smoke-new
python docs/plan/tooling/longrun.py run --profile pilot --with-dexted --out validation/industrial/core-pilot-new
```

smoke는 6건×2초입니다. pilot는 6건×30분이지만 **같은 고정 2-section reference SOS**만 사용합니다. 이 결과로 8-filter matrix, independent runtime engine, 실제 고객 데이터, 24h/72h wall-clock soak를 완료했다고 쓰지 않습니다.

## 3. 아직 실행 불가능한 신규 명령의 표시

`check_sos`, `parse_sos_payload`, `run_isolated`, `localize_sos_peak`, 새 `benchmarks/industrial/` runner는 구현 제안입니다. install 후 바로 실행된다고 쓰지 않습니다. 신규 CLI 이름과 flags는 CW-05/CW-12 review 후 고정합니다. 현재 docs 예제와 미래 pseudo command를 섞지 않습니다.

구현자가 qualification 실행 전에 준비할 조건은 approved frozen 8 filters+4 controls, 24 records, 실제 core artifact, independent consumer/oracle, 4 runtime lanes, per-filter tolerances, complete ledger schema, resource enforcement입니다. 하나라도 없으면 NOT_READY이며 shortened smoke로 qualification을 대신하지 않습니다.

## 4. 적대적 검토와 이번 명세의 해결 방식

| 비판 질문 | 이번 문서의 답변·변경 |
|---|---|
| 이미 구현한 API처럼 새 함수를 쓰는가? | 신규 함수·모듈은 PROPOSED,실행 런북에서 분리 |
| '정확성 향상'이 epsilon으로 strict equality를 통과시키는가? | INV-02/04, equality ULP golden, 최적화는 양의 동치변형만 |
| parser가 끝없는 iterator를 메모리에 올리는가? | limit+1와 next hang supervisor를 별도 계약 |
| 루프 node limit이 전체 시간·RSS를 제한하는가? | polynomial/consumer/serialization도 total budget, OS enforcement 지원표 |
| native UNKNOWN이 Python REJECTED와 다르면 무조건 버그인가? | early exit 차이와 completed contradiction을 분리 |
| P가 접점에서만 0이면 dyadic witness가 항상 존재하는가? | (3c-1)^2 counterexample과 unknown/algebraic extension 분리 |
| 긴 신호 한 번으로 모든 frequency/runtime safety를 증명하는가? | A/B/C 분리,H∞/sample-peak/state/roundoff 분리 |
| 24×8×4를 2,432시간의 새로운 녹음으로 포장하는가? | input76h/filter608h/lane2,432h/wall-time 별도 회계 |
| 이전 bootstrap를 core 실행 증거로 덮어쓰는가? | 기존 evidence immutable,dexted_core_executed=false 유지 |
| 24개 CW가 45개 WBS에 추가되어 일정이 허위가 되는가? | 상세 분해 매핑, PD 중복 금지,CW-21 재견적 승인 |
| 후속 기능이 마스터 v1.0 범위를 바꾸는가? | CR-16~18은 release blocker 아님,별도 모델 승인 |
| 문서 감사 green을 산업용 승인으로 부르는가? | evidence.scope=documentation_contracts,industrial_qualified=false |

이 표는 내부 적대적 검토입니다. 외부 수학 reviewer 서명·실제 core test execution을 의미하지 않습니다. 요구의 모호성을 줄인 것이며 산업용 제품 완성을 선언하지 않습니다.

## 5. 확인한 저장소 근거

모든 기준은 `9f6df34d45f418995dedf18e3b328524dd18ec6b`입니다. Git blob SHA는 알고리즘 검증 수단이 아니라 특정 읽은 내용을 추적하는 식별자입니다.

| 파일 | 확인한 Git blob SHA | 관찰 근거 |
|---|---|---|
| src/dexted_dsp/verify.py | f7f35a77470dc0b83666f8c69f6e2c84edb74619 | independent rational cover, hostile sandbox 아님 |
| src/dexted_dsp/peak.py | d0b5a2723d04a0db8bb89af3001808fb9f3fed79 | lower witness, proven upper, unknown/partial |
| src/dexted_dsp/peak_region.py | 0106945025637b1f8de2e29812a5d60785b423bb | 단일 biquad stationary,Hz noncertified |
| src/dexted_dsp/inspection.py | 8080de4ba446fc49de860c067dca11f6ad617d1b | decision+optional computation,legacy/v2 reader |
| src/dexted_dsp/native.py | e26489ebe0192691f48071f9b2d55960be313a83 | f32 ctypes boundary,unknown state |
| cpp/include/dexted_dsp/cascade.hpp | 7cd56c6bc47ea34c8ea3762bdd905df320381696 | early unknown,exceptions/C ABI scope |

## 6. 외부 일차 자료 — 2026-10-08 확인

### S1

[SymPy Polynomials reference](https://docs.sympy.org/latest/modules/polys/reference.html): QQ polynomial, count_roots, exact root isolation 및 square-free tools의 공식 인터페이스 참고입니다. 문서의 API 존재는 우리의 구현 정확성 보증이 아닙니다.

### S2

[SciPy sosfilt](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfilt.html): SOS 처리·state·DF-II transposed realization의 공식 참고입니다. 현재 참조 페이지 버전과 과거 고정 benchmark 환경은 다를 수 있으며 이 문서 추가로 dependency를 올리지 않습니다.

### S3

[SciPy freqz_sos](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz_sos.html): 지정된 frequency points의 수치 응답 평가입니다. 수치 주파수 배열 검사를 수학적 full-band certificate라고 주장하지 않습니다.

### S4

[python-control frequency_response](https://python-control.readthedocs.io/en/latest/generated/control.frequency_response.html): 이산시간 시스템·시간축·frequency-response 계약 참고입니다. TF 변환 비용·conditioning·동일 SOS 계수 의미를 비교에서 공개합니다.

### S5

[GNU MPFR manual](https://www.mpfr.org/mpfr-current/mpfr.html): correctly rounded multiple-precision 연산과 directed rounding의 공식 설명입니다. Hz/roundoff 확장 설계의 후보이며 현재 core가 MPFR를 사용한다는 뜻이 아닙니다.

정수 Q 전개·Jury·Bernstein·stationary 식의 실제 논증은 [02](02_ALGORITHMS_AND_INVARIANTS.md)와 [10](10_EXTENSIONS_AND_ROUNDOFF.md), 기존 저장소 proof를 함께 검토합니다. 외부 문서와 테스트 성공은 제3자 수학적 감사를 대체하지 않습니다.
