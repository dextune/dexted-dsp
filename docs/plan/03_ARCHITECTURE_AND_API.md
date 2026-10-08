# 03. 제품 구조, API 계약, 인증서·배포 바인딩

[문서 홈](README.md) · [코어 증명 의무](02_MATHEMATICS_AND_CORE.md)

## 1. 권장 아키텍처

```text
고객 설계기 / 외부 DSP 라이브러리
  → export adapter: 정규화·양자화·section 순서 확정
  → immutable coefficient artifact + 제품 정책
  → 입력 검증 → 격리된 exact core worker
  → 독립 proof verifier → 정책 결정
  → proof + diagnostic report + provenance를 원자적으로 저장
  → 배포 직전 byte/hash 확인 → 기존 처리기에 계수 전달
```

범용 신호 처리는 고객의 기존 SciPy/native/임베디드 엔진에 남깁니다. Dexted는 계수 승인 경로에만 참여합니다. 이 구조에서 오디오 파일 길이가 늘었다고 같은 계수를 매 샘플마다 다시 인증할 필요는 없습니다. 계수·정책·인증 구현 버전·모델 범위가 바뀔 때 재인증합니다.

## 2. 모듈 경계와 구현 작업

| 영역 | 현행 근거 | 필요한 산업용 작업 | 허용하지 않을 의존 |
|---|---|---|---|
| coefficient model | `model.py`, `from_sos` | bounded iterable, 정규화 계약, 직렬화 round-trip | 오라클을 런타임 필수 의존으로 추가 |
| exact predicate | `biquad.py`, `cascade.py` | 상태·예산 telemetry, cancellation wrapper | numerical grid로 긍정 판정 |
| proof consumer | `verify.py`, inspection verifier | 외부 입력 상한, 변경 감지, 독립 review | producer 내부 success flag만 신뢰 |
| inspection/report | `inspection.py`, CLI | 핵심 verdict와 optional gain-bound 계산 분리 | 표시 값 변경으로 verdict 수정 |
| native facade | `cpp/include`, C ABI | ABI·오류·allocation·thread 계약, 산출물 검사 | C++ exception을 C 경계 밖으로 전파 |
| integration adapter | 새 work package | 제품 export 변환과 최종 바이트 바인딩 | 사용자의 필터를 묵시적 수정 |
| evidence store | 새 work package | content-addressed immutable 저장·보존 정책 | 민감한 고객 원자료 무단 업로드 |

새 디렉터리 이름은 WBS 구현 시 확정합니다. 표의 새 영역은 이미 존재하는 API라는 뜻이 아닙니다.

## 3. 공개 상태 모델

기존 `certified/rejected/unknown` 및 CLI exit 0/1/2/3을 유지하면서, 확장 보고서에 machine-readable reason을 추가합니다. v1 certificate의 기존 의미를 바꾸지 않습니다.

| 수학/실행 상태 | 배포 허용 | 사용자에게 설명할 내용 |
|---|---|---|
| CERTIFIED + VERIFIED + INPUT_MATCH | 제품 정책이 승인할 때만 가능 | 주어진 표현 계수와 명제 범위에서만 인증 |
| REJECTED_GAIN | 불가 | strict gain 조건을 만족하지 않음, 가능한 경우 정확한 witness |
| REJECTED_STABILITY | 불가 | 어떤 section의 분모가 안정성 정책을 위반했는지 |
| UNKNOWN_RESOURCE_LIMIT | 불가 | 시간/노드/깊이/메모리 중 어떤 자원이 부족했는지 |
| INVALID_INPUT / UNSUPPORTED_POLICY | 불가 | 입력 형식이나 지원 계약 불일치; 수학적 FAIL과 다름 |
| INVALID_CERTIFICATE / INPUT_MISMATCH | 불가 | 인증서가 잘못되었거나 배포 대상과 다른 계수임 |
| INTERNAL_ERROR / CANCELLED | 불가 | 실패 파일 저장, 재현 ID, 예외·취소 경계 |

`if report:`처럼 객체의 truthiness로 통과시키는 예제를 만들지 않습니다. 상위 gate는 `certified is True`, verifier true, 정책 일치, payload hash 일치를 모두 명시적으로 검사합니다. UNKNOWN을 “필터가 잘못되었다”로 단정하지 않습니다.

## 4. 입력·출력 계약

입력은 section 수, 계수 순서 `[b0,b1,b2,a0,a1,a2]`, deployment precision, sampling rate 메타데이터, strict gain threshold, 안정성 정책, 예산 프로필, 제품 artifact 식별자로 구성합니다. finite 값인지 확인하고 최종 배포 binary 표현을 보존합니다. fs는 주파수 단위를 해석하고 report에 바인딩하는 메타데이터이며, 같은 정규화 전달함수의 전 대역 이득을 바꾸는 입력은 아닙니다.

출력은 schema_version, input_digest, coefficient artifact hash, verdict/reason, producer/verifier build identity, proof, optional bounds, resource telemetry, scope exclusions, timings를 포함합니다. 기존 certificate에 새 필드를 덧붙일 경우 verifier의 허용/거절 정책을 먼저 결정합니다. 미지원 미래 schema는 보수적으로 거절합니다.

단위는 gain linear와 dB를 구별합니다. CLI 사용자가 `6`을 6dB로 해석할 수 없도록 옵션 이름과 report 단위를 명시합니다. dB를 linear로 변환하여 인증할 때는 float로 변환된 실제 threshold와 원 요청을 모두 보존하고 경계 의미를 설명합니다. 반올림을 근거 없이 유리한 방향으로 적용하지 않습니다.

## 5. 인증서와 서명의 차이

`input_digest`는 데이터 결속을 위한 해시입니다. 누구나 해시를 다시 계산할 수 있으므로 발행자 신원을 보장하지 않습니다. 수학적 proof 검사, 파일 무결성, 배포 공급망의 서명/attestation은 각각 별도 계층입니다.

proof를 통과해도 제품 정책의 gain limit을 인증서에서 읽어 믿으면 안 됩니다. 소비자는 자신이 승인하려는 임계값·배포 계수·precision을 독립적으로 제공해야 합니다. 보고서에 “검증 성공”이라고 적혀 있다는 이유로 pass하지 않습니다.

## 6. 원자적 배포와 TOCTOU 방어

1. 최종 계수 payload를 freeze하고 raw-byte SHA-256을 계산합니다.
2. 인증 대상은 그 payload에서 디코딩한 실제 값입니다. 독립 verifier에 동일한 외부 입력을 제공합니다.
3. proof·policy·artifact identity를 임시 경로에 저장하고 성공 시 rename/commit합니다.
4. 배포 도구는 실제 firmware/preset 안에서 계수를 다시 읽어 hash를 비교합니다.
5. 캐시된 proof의 계산 명제·정밀도·정책·core build가 모두 같을 때만 재사용합니다.
6. 교체·정렬·정규화·rounding이 발생하면 proof를 폐기하고 재인증합니다.

동시에 여러 작업이 같은 파일 이름을 쓰는 경우 last-writer-wins로 처리하지 않습니다. run ID·제품 ID·hash를 조합해 경로를 분리합니다. 프로세스가 중단되면 incomplete marker만 남고 successful release marker가 생기지 않아야 합니다.

## 7. C++ 및 임베디드 경계

지원 compiler, architecture, endianness, exception 설정, ABI version, float32 layout을 표로 고정합니다. 분모 안정성 정책이 Python과 다르지 않은지 교차검증합니다. native API의 `-1/-2/-3/0/1`처럼 기존 코드가 쓰는 상태를 wrapper에서 손실 없이 보존합니다.

f32 native predicate와 f64 Python API를 같은 정확도·성능 계약으로 광고하지 않습니다. native batch와 Python one-shot도 같은 timing으로 나누어 speedup을 계산하지 않습니다. “실시간 안전 API”를 주장하기 전에는 allocation-free, bounded execution, locks, worst-case latency를 별도로 증명/측정해야 하며 첫 버전의 인증 worker는 이 주장을 하지 않습니다.

native proof serialization은 후속 목표입니다. v1.0에서는 Python에서 인증서 생성·검증을 수행하고 실제 배포 f32 byte가 같은지 확인하는 워크플로로 제품 가치를 완성할 수 있습니다.

## 8. 테스트 어댑터의 계약

장시간 신호 처리 어댑터는 별도 모듈로 `prepare(coefficients, precision)`, `process_block(input, state)`, `flush_tail`, `export_state`, `implementation_identity`를 갖추도록 설계합니다. 이들은 **제안된 인터페이스**이며 현재 라이브러리 API로 오해하지 않도록 문서와 코드 위치를 분리합니다.

고객 엔진을 붙이면 output hashes, state extrema, NaN/Inf count, chunk boundary difference, cancellation, coefficient transition events를 기록합니다. 상태를 매 블록 초기화하는 잘못된 adapter를 negative control로 넣습니다. `scipy.sosfilt`를 두 번 호출하는 것은 상태 경계 regression 확인이지 독립 algorithm 검증이 아닙니다([S02](11_SOURCES_AND_BASELINE.md#s02)).

## 9. 운영 관측 필드

request_id, coefficient_hash, policy_hash, library_build, elapsed_core_ms, elapsed_verify_ms, nodes, depth, proof_bytes, worker_peak_rss, verdict, reason, retry_count를 수집합니다. 원래 음성 데이터·고객 설계 파라미터 전체를 기본 telemetry로 보내지 않습니다. 작업 취소 후 CPU 사용이 실제로 멎었는지도 검사합니다.

## 10. 완료 정의

각 공개 진입점의 타입·예외·상태·상한·호환성 테스트가 있어야 합니다. clean-install된 실제 배포 아티팩트에서 example→certificate→verify→deploy-hash 시나리오가 통과해야 하며, 소스 디렉터리가 우연히 import되는 검증을 금지합니다.
