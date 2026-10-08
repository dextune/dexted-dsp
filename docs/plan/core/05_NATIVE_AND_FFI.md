# 05. C++ 코어·C ABI·Python FFI 구현 명세

[코어 명세 홈](README.md) · [현행 C++ API](../../reference/cpp-api.md)

## 1. v1.0 필수 범위

현행 `certify_cascade_f32`와 C 함수 `dexted_dsp_cascade_f32`, `NativeCascade.check`의 정확한 binary32 semantics, 반환 코드, 예외·할당 정책을 안정화합니다. native certificate serialization·binary64 native path·실시간 오디오 처리기는 이번 필수 범위에 추가하지 않습니다. Python producer+consumer가 필수 증거 경로입니다.

## 2. 함수별 구현 계약

| 현존 함수 | 추가 명세·개발 | 테스트 |
|---|---|---|
| `decode_float`, `positive_double_ratio` | raw bits→정확한 dyadic, signed zero/subnormal/maxfinite/NaN 범위 표 | CT-03,24 |
| `detail::multiply`, `bernstein_scaled`, `split_scaled` | degree·size overflow 검사, positive scaling, budget checkpoint를 신규 context 경로로 추가 | CT-08~13,25 |
| `detail::positive_over_interval` | stage/reason telemetry, default depth-first 순서, unknown 의미 고정 | CT-25 |
| `certify_cascade_f32` | count 1..32, finite γ/coeffs, full request resource wrapper | CT-24~26 |
| `dexted_dsp_cascade_f32` | 모든 C++ exception catch, -2 유지, caller-visible buffer lifetime 명시 | CT-26 |
| `NativeCascade.check` | bounded section input, explicit f32 equivalence, unknown code를 internal error로 변환 | CT-02,24~26 |

## 3. 상태 코드와 탐색 차이

기존 `1=certified`, `0=condition_failed`, `-1=invalid`, `-2=internal/allocation error`, `-3=unknown`을 보존합니다. `if(code)`는 -3도 참이므로 금지합니다. 새 wrapper는 `code==1`만 positive 후보로 봅니다. 0은 안정성 또는 이득 실패의 구별을 잃는 legacy predicate이므로 새 telemetry API를 추가해야 reason을 구별할 수 있습니다.

현행 C++은 한 leaf가 depth limit에 걸리면 즉시 unknown을 반환하지만 Python은 다른 leaf 탐색 후 반례를 찾을 수 있습니다. 같은 예산의 Python rejection과 native unknown은 그 자체로 수학 오류가 아닙니다. 완결 판정끼리 충돌하면 오류입니다. budget-parity 회귀는 동일 정책·순서로 구현했을 때만 status 동등을 요구합니다. 수학적 일치와 solver coverage를 따로 기록합니다.

## 4. 메모리·소유권·재진입

caller가 넘기는 `float*`는 최소 `5*count`개의 유효한 float 객체를 가리켜야 합니다. count 검사는 잘못된 arbitrary pointer를 안전하게 만들지 못합니다. C API를 hostile raw memory의 sandbox라고 광고하지 않습니다. 데이터는 호출 동안 immutable이며 caller가 소유합니다. library는 pointer를 보관하거나 해제하지 않습니다.

thread별 budget/context와 output 객체를 사용합니다. 공유 mutable last_error buffer, request 간 polynomial scratch 재사용, process-wide rounding mode 변경은 금지합니다. binomial cache는 immutable table만 허용하고 allocator·cache peak를 계측합니다. f32 binary parser에서 산술 변환으로 subnormal을 잃지 않도록 bit decode를 사용합니다.

native result 구조 확장이 필요하면 새 suffix symbol과 `struct_size`, `abi_version`, reserved zero fields를 둡니다. 기존 exported symbol signature를 바꾸지 않습니다. future unknown ABI는 실패합니다. Python ctypes는 argtypes/restype와 구조체 alignment를 명시하고 canary buffers를 시험합니다.

## 5. 빌드/실행 조건

GCC/Clang/MSVC, Linux x86-64, macOS ARM64, Windows x86-64의 지원 표를 compiler version·Boost version과 함께 고정합니다. '다른 세 OS'만으로 세 독립 조직 검증을 대체하지 않습니다. little/big endian raw import가 있으면 별도 변환 함수와 fixture를 둡니다.

정확성 빌드는 `-ffast-math` 등 NaN/finite 의미를 바꾸는 옵션을 허용하지 않습니다. debug/release, ASan/UBSan 및 지원되는 sanitizer lane을 구별합니다. sanitizer 미지원 Windows 조합을 passed로 만들지 않고 unsupported로 보고합니다. malloc failure injection·sized container overflow는 isolated harness에서 수행합니다.

## 6. 시간 제한과 무중단 주장 금지

Boost arbitrary-precision 연산은 할당·예외·입력 의존 실행 시간이 있습니다. in-process에서 'hard 5초'를 보장하지 않습니다. native 작업도 process supervisor 하에 실행해야 산업용 hard budget 계약을 적용합니다. worker kill은 parent library 소비자를 살려야 하며 stale positive output을 남기면 안 됩니다.

## 7. 후속 native proof export 설계

후속 CW-23은 producer가 dyadic cover를 vector로 만든 뒤 크기 조회→caller buffer 채우기의 two-call C API를 제안합니다. 부족한 buffer는 required length와 dedicated error를 주고 partial valid certificate를 반환하지 않습니다. 1차 길이 조회와 2차 call의 input/policy identity가 달라지면 거절합니다. Python 독립 consumer가 native proof를 재검증한 뒤만 실사용 gate에 합류합니다. 이 기능은 v1.0 완료 조건이 아닙니다.
