# 사용 가이드: 설치·API·프로젝트 연동

[English](../../en/getting-started/USER_GUIDE.md) · [한국어](USER_GUIDE.md) · [简体中文](../../zh-CN/getting-started/USER_GUIDE.md) · [日本語](../../ja/getting-started/USER_GUIDE.md)

[Dexted DSP](../README.md)

## 1. 먼저 적용 가능한 모델인지 확인하십시오

이 라이브러리는 **고정 계수·실수·정규화된 biquad** 또는 이러한 필터 1–32개의 직렬 연결을 다룹니다. 주어진 분모가 엄격히 안정하고 이상적인 선형 주파수 응답이 제한값보다 작은지 배포 전에 검사합니다. FLAMO·PyTorch 그래프, FAUST·VST·ONNX를 자동 분석하거나 계수를 고쳐주지는 않습니다.

정규화와 float32 변환을 포함한 **실제 최종 배포 계수**를 내보내야 합니다. 재생·배포 전에 오프라인으로 검사하십시오. 이 가이드의 명령은 소리를 재생하거나 하드웨어를 제어하지 않습니다.

## 2. 설치 방법

모든 명령은 `docs/ko/`가 아니라 압축을 푼 `dexted-dsp/` 루트에서 실행합니다.

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
python -m dexted_dsp --version
```

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install .
python -m dexted_dsp --version
```

예상 버전은 `0.1.0`입니다. 환경 활성화는 필수가 아닙니다. POSIX의 `.venv/bin/python`, Windows의 `.venv\Scripts\python.exe`를 직접 실행하면 PowerShell 실행 정책을 바꾸지 않아도 됩니다. 선언된 최소 버전은 Python 3.10이며, 실제 호스팅 OS·버전별 CI는 공개 후 별도 실행해야 합니다.

### 오프라인 wheel 또는 개발용 설치

```bash
python -m pip install build
python -m build
python -m pip install --no-deps dist/dexted_dsp-0.1.0-py3-none-any.whl
# 소스를 수정하는 경우의 대안. 빌드 도구 다운로드가 필요할 수 있습니다.
python -m pip install -e .
```

하나의 환경에서 설치 방법 **하나를 선택**하십시오. 미공개 프로젝트이므로 패키지 인덱스의 `pip install dexted-dsp`가 이 프로젝트를 가리킨다고 가정하면 안 됩니다. wheel은 Python 실행 코드이며 C++ 바이너리를 포함하지 않습니다. 문서·검사·그래프·소스는 ZIP·sdist에 있으므로 예제를 실행하려면 소스 트리를 보관하십시오. 빌드·배포 구조는 PyPA 문서를 참고했습니다 [PYPA].

## 3. 입력의 의미: 가장 중요한 계약

필터 정의는 다음과 같습니다.

$$H(z)=\frac{b_0+b_1z^{-1}+b_2z^{-2}}{1+a_1z^{-1}+a_2z^{-2}}.$$

| 입력 방법 | 필요한 순서 |
|---|---|
| `Biquad.from_coefficients()` | `[b0,b1,b2,a1,a2]` 다섯 값 |
| `Biquad(b=..., a=...)` | 분자 `(b0,b1,b2)`, 분모 `(1,a1,a2)` |
| `from_sos()` | SciPy 형식 `[b0,b1,b2,a0,a1,a2]`, `a0==1` 필수 |
| CLI `type="cascade"` | `sections`의 각 행은 SciPy의 여섯 값이 아닌 **다섯 값** |

`a0`를 자동 정규화하지 않습니다. 실제 배포 파이프라인에서 정규화·반올림한 후 결과값을 전달하십시오. 다른 도구의 계수 부호 관례를 확인하지 않으면 전혀 다른 필터를 검사할 수 있습니다.

Python·JSON의 십진수는 우선 유한 binary64로 변환됩니다. `precision="float32"`는 계수를 binary32로 명시적으로 다시 반올림하며 `float64`는 파싱된 값을 유지합니다. 이후 **그 이진 유리수 표현값**을 정확하게 인증합니다. 파싱 전 의도한 십진수에 대한 정확 연산은 아닙니다. float32 계수에서도 제한값은 binary64입니다. NaN·무한대·복소수·불리언·문자열·양수가 아닌 제한값은 거절합니다. float32 범위 초과는 오류이며 작은 값이 0이 되는 것은 명시한 변환의 결과입니다.

## 4. 단일 필터와 결과 해석

```python
from dexted_dsp import Biquad, certify, verify_biquad
f = Biquad.from_coefficients([0.25, 0, 0, -0.5, 0], precision="float32")
report = certify(f, max_gain=1.0)
print(report.status)
print(report.denominator_stable)
print(verify_biquad(report.as_dict(), f, max_gain=1.0))
```

예상 출력:

```text
certified
True
True
```

| 단일 필터 상태 | 의미 |
|---|---|
| `certified` | 이 입력에서 두 엄격한 조건 모두 만족 |
| `denominator_not_schur` | 분모가 엄격한 단위원 내부 안정성 조건 미충족 |
| `gain_limit_not_met` | 분모는 안정하지만 지정한 엄격한 이득 제한 미충족 |

`max_gain_limit`는 **요청한 제한값**입니다. 실제 최대 이득·임계 주파수·dB 여유·지각적 점수를 계산해 주지 않습니다. 상수 이득 1에 대한 `certify(Biquad.from_coefficients([1,0,0,0,0]),1.0)`은 `<1`을 만족하지 않으므로 거절됩니다.

사용 프로그램에서는 예외와 실패를 명시적으로 처리하십시오.

```python
from dexted_dsp import Biquad, certify

def accept_exported_filter(values):
    try:
        f = Biquad.from_coefficients(values, precision="float32")
        result = certify(f, max_gain=1.0)
    except (ValueError, TypeError):
        return False
    return result.certified
```

이 함수는 명시한 필터 모델의 검사 단계이지 주변 피드백 시스템 전체의 증명이 아닙니다.

## 5. 직렬 체인과 SciPy

```python
from dexted_dsp import from_sos, certify_cascade, verify_cascade
sections = from_sos([
    [1.0, -0.75, 0.0, 1.0, -0.125, 0.0],
    [0.75, -0.09375, 0.0, 1.0, -0.75, 0.0],
], precision="float32")
proof = certify_cascade(sections, max_gain=1.0)
assert proof["certified"]
assert verify_cascade(proof, sections, max_gain=1.0)
```

전체 전달함수는 정확히 0.75입니다. 합동 인증은 주파수별 보상을 유지하지만 개별 최대값만 곱하면 이를 놓칠 수 있습니다. `from_sos` 자체는 SciPy를 import하지 않습니다. 선택 예제 `examples/scipy_sos.py`는 설치한 SciPy로 Butterworth SOS를 설계하고 반올림한 필터를 제한값 1.01에서 검사합니다.

체인 상태는 `certified`, `denominator_not_schur`, `condition_failed`, `unknown`입니다. `condition_failed`에는 엄격한 이득 차이 다항식의 0 이하 값에 대한 정확한 근거가 있습니다. `unknown`은 예산 내에 증명을 만들지 못했다는 뜻이며 안정·불안정·배포 가능을 의미하지 않습니다. 다른 구간에서 극점이 상쇄되는 것처럼 보이더라도 개별 분모가 불안정하면 거절합니다.

기본 예산은 `max_depth=48`, `max_nodes=20000`입니다. 최대 깊이 128, 노드 100,000개, 필터 32개를 지원합니다. 예산을 늘리면 도움이 될 수 있지만 0에 가까운 고차 다항식을 빠르게 처리한다는 보장은 없습니다.

## 6. JSON CLI·인증서 저장·예상 실패

일반 입력 예제는 [safe.json](../../../examples/safe.json)입니다.

```json
{
  "type": "biquad",
  "precision": "float32",
  "max_gain": 1.0,
  "coefficients": [0.25, 0, 0, -0.5, 0]
}
```

```bash
python -m dexted_dsp check examples/safe.json --output certificate.json
python -m dexted_dsp verify examples/safe.json certificate.json
```

검사는 전체 JSON을, 재검사는 `{"verified": true}`를 출력합니다. `--output`으로 입력 파일을 덮어쓸 수 없습니다. 출력의 부모 디렉터리는 미리 만들어야 합니다. JSON은 최대 1 MiB이며 파일을 실행하거나 외부 서비스로 보내지 않습니다.

0이 아닌 종료 코드에서 멈추는 셸에서는 아래 부정 테스트를 별도로 실행하십시오.

```bash
python -m dexted_dsp check examples/hidden_peak.json
# 예상: gain_limit_not_met, 종료 코드 1
python -m dexted_dsp check examples/budget_limited.json --max-depth 0
# 예상: unknown, 종료 코드 3
python -m dexted_dsp check examples/budget_limited.json --max-depth 16
# 포함된 이 예제의 예상 결과: certified, 종료 코드 0
```

마지막 두 명령은 판정보류가 조건 위반의 증명이 아님을 보여줍니다. 상태·종료 코드를 확인하십시오. JSON에는 거짓인 `certified` 필드도 있으므로 문자열 검색만으로 합격 처리하면 안 됩니다. 성공한 인증서만 재검사할 수 있습니다. 원본 입력·제한값·인증서·버전을 함께 보관하십시오. 인증서는 서명되지 않으며 검사기가 수학적 조건과 입력 일치를 다시 확인합니다.

## 7. C++·C 연동

C++20 컴파일러, CMake 3.20 이상, Boost 1.74 이상 헤더가 필요합니다. Debian/Ubuntu 예시는 `sudo apt-get install g++ cmake libboost-dev`입니다. macOS는 사용하는 패키지 관리자로 컴파일러·CMake·Boost를 설치하고, Windows는 호환되는 CMake 도구와 Boost 경로를 구성하십시오. Python 핵심에는 이 도구들이 필요 없습니다.

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
cmake --install build --prefix ./local-install
```

```cpp
#include <dexted_dsp/biquad.hpp>
int main() {
    const float coefficients[5] = {0.25f, 0, 0, -0.5f, 0};
    const int verdict = dexted_dsp::certify_biquad_f32(coefficients, 1.0);
    return verdict == 1 ? 0 : 1;
}
```

반환값은 `1` 인증, `0` 조건 미충족, `-1` 잘못된 입력입니다. C ABI는 추가로 예외를 잡아 `-2`를 반환·기록합니다. **정수 결과를 그대로 bool로 바꾸지 마십시오.** 음수 오류 코드도 참이 됩니다. 헤더 API는 메모리 할당 예외를 던질 수 있습니다. fast-math를 사용하지 마십시오.

CMake 소비 프로젝트는 `find_package(DextedDSP CONFIG REQUIRED)` 후 `DextedDSP::dexted_dsp`에 링크하고 설치 경로를 `CMAKE_PREFIX_PATH`로 전달합니다. C++ 계수는 binary32 전용이고 제한값은 binary64입니다. 네이티브 체인 인증은 구현하지 않았습니다.

선택적 Python 네이티브 연결 검사, Linux 예시:

```bash
python tools/native_smoke.py "$PWD/build/libdexted_dsp.so"
```

래퍼는 신뢰할 수 있는 라이브러리의 명시적 절대 경로를 요구하며 조용한 계수 반올림을 거절합니다. macOS·Windows는 라이브러리 이름과 위치가 다릅니다. [API 계약](../../reference/API.md)을 참고하십시오.

## 8. 잘못된 기본값 없이 CI에 넣기

배포 전 단계에서 다음을 실행할 수 있습니다.

```bash
python -m dexted_dsp check examples/safe.json --output certificate.json
python -m dexted_dsp verify examples/safe.json certificate.json
```

예제 대신 실제 내보낸 계수를 사용하십시오. 3을 포함한 모든 비정상 종료 코드에서 CI가 멈추게 해야 합니다. 포함된 GitHub Actions는 Python·C++·빌드를 검사하지만 설정 파일이 존재한다고 실제 호스팅 검사까지 수행된 것은 아닙니다. 실제 저장소에서 성공하기 전에는 통과 배지를 공개하지 마십시오.

## 9. 문제 해결

| 증상 | 확인·대응 |
|---|---|
| `ModuleNotFoundError`, `dexted-dsp`를 찾지 못함 | 같은 환경에서 `python -m pip`와 `python -m dexted_dsp` 사용 |
| float32 범위 초과·계수 오류 | 실제 내보낸 유한 실수 값을 확인. 임의로 잘라낸 후 이전 인증서를 재사용하지 않음 |
| 이득 1 필터 거절 | 조건은 엄격함. 실제 이득보다 큰 타당한 제한값을 명시하며 숨은 허용오차를 넣지 않음 |
| `unknown` | 노드·깊이·조건 여유 확인. 공개 한도 안에서 예산을 늘리거나 배포 거절 |
| 이전 인증서 검증 실패 | 계수 순서·정규화·반올림·필터 순서·동일한 제한값 확인 |
| Boost를 찾지 못함 | 헤더 설치. 비표준 설치는 CMake 검색 경로 지정 |
| 네이티브 래퍼가 계수 거절 | 배포값을 명시적으로 float32로 변환 |
| 화면 없는 환경의 그래프 오류 | `MPLBACKEND=Agg`, 쓰기 가능한 `MPLCONFIGDIR` 설정 |
| 벤치마크 수치 차이 | 버전·입력·CPU 부하·플래그·스레드 설정 확인. 빠른 시간으로 정확성 근거를 대체하지 않음 |

버그 보고에는 최소 계수 JSON, 예상 조건과 실제 상태, 정확한 버전, OS·컴파일러와 로그를 포함하십시오. 허가 없이 비공개 음원·인증정보·독점 모델을 첨부하지 마십시오.

[OAI-README]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/README.md
[OAI-325]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex
[OAI-DFT]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex
[CP-2017]: https://arxiv.org/abs/1702.00668
[SCIPY-FREQZ]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html
[PYPA]: https://packaging.python.org/en/latest/tutorials/packaging-projects/
