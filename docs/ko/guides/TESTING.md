# 테스트 실행 및 결과 판독 가이드

[English](../../en/guides/TESTING.md) · [한국어](TESTING.md) · [简体中文](../../zh-CN/guides/TESTING.md) · [日本語](../../ja/guides/TESTING.md)

[Dexted DSP](../README.md)

## 1. “몇 개 통과”보다 검증 계층을 구분하십시오

| 계층 | 명령·자료 | 의미 |
|---|---|---|
| 핵심 회귀검사 | unittest 메서드 35개 | API·정확 판정·제한·인증서·CLI |
| 문서 시나리오 | `documentation_smoke.py` 12개 검사 | 이 가이드의 예제와 종료 코드 계약 |
| 네이티브 실행 파일 | 여러 assertion이 있는 CTest 항목 1개 | C++ 헤더·C ABI의 고정 경계 사례 |
| 네이티브 래퍼 점검 | 시드가 고정된 필터 256개 | ctypes 연결 및 숨은 float32 변경 거절 |
| 저장된 전체 벤치마크 | 필터 4,096개 및 별도 비트 패턴 2,048개 | 기존 비교 결과와 네이티브 비트 해석 검사 |
| 문서 개정용 작은 벤치마크 | 4 × 32개 필터, 3회 반복 | 명령 실행 점검이며 공개 시간표의 근거는 아님 |

한 테스트 메서드에 많은 무작위 사례가 들어갈 수 있습니다. 35개의 독립 실험, 외부 감사 또는 Lean 검증을 의미하지 않습니다. 원본 로그는 `validation/`, 이번 개정의 별도 로그는 `validation/docs_refresh/`에 있습니다.

## 2. 벤치마크 의존성 없이 최소 검사

[사용 가이드](../getting-started/USER_GUIDE.md)대로 설치한 후 소스 루트에서 실행합니다.

```bash
python -m unittest discover -s tests -v
python tools/documentation_smoke.py
python examples/basic.py
python examples/cascade.py
```

핵심 예상 요약은 `Ran 35 tests ... OK`입니다. 문서 검사기는 `"status": "passed"`, `"checks": 12`를 포함한 JSON을 반환합니다. 기본 예제는 `certified`와 유리수 재검사 성공을 출력합니다. 체인 예제는 개별 필터의 실패와 전체 `certified`를 출력합니다.

등호 경계, 숨은 공진, 분모 경계 극점, 불안정 극점 상쇄, 명시적 float32 변환, 극단적인 유한값, 복소수·잘못된 입력, 정수·유리수 무작위 대조, 위조된 합격 상태, 잘못된 덮개, 자원 부족 및 CLI 입력 보존을 검사합니다.

핵심 파일 내부에는 시드 기반 2,500개 대조, 임의 비트 패턴 최대 1,200회 시도에서 유한값만 검사, 보상형 체인 후보 100개 검사가 있습니다. 벤치마크의 4,096개·2,048개와는 다른 데이터입니다.

특정 회귀검사만 실행할 수도 있습니다.

```bash
python -m unittest discover -s tests -p test_dexted_dsp.py -k hidden_peak -v
python -m unittest discover -s tests -p test_dexted_dsp.py -k unknown -v
python -m unittest discover -s tests -p test_dexted_dsp.py -k tampering -v
```

각 명령은 테스트 하나를 선택해 통과해야 합니다. 부정 테스트는 수학적 주장을 올바르게 거절하거나 보류하면 성공입니다.

## 3. 모든 CLI 종료 경로 확인

| 입력·행동 | 예상 상태 | 종료 코드 |
|---|---|---|
| `safe.json` | `certified` | 0 |
| `hidden_peak.json` | `gain_limit_not_met` | 1 |
| `budget_limited.json --max-depth 0` | `unknown` | 3 |
| 같은 예제, `--max-depth 16` | `certified` | 0 |
| 잘못된 JSON·지원하지 않는 타입 | `invalid_input` | 2 |
| 다른 계수에 대해 기존 인증서 재검사 | `verified: false` | 1 |

`python tools/documentation_smoke.py`가 이 경우와 종료 코드를 자동 확인합니다. POSIX에서는 실행 직후 `echo $?`, PowerShell에서는 `$LASTEXITCODE`로 볼 수 있습니다. 예상 실패 명령을 처리 없이 `set -e` 블록에 넣지 마십시오.

예산을 늘려 나중에 통과하더라도 `unknown`이 반환된 현재 판정은 배포를 거절해야 합니다. 이득 제한 미충족은 일반적인 피드백 불안정 증명이 아닙니다.

## 4. C++·C ABI·연결 검사

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
# Linux 공유 라이브러리 예시:
python tools/native_smoke.py "$PWD/build/libdexted_dsp.so"
```

예상 출력에 `native tests: PASS`가 있고 CTest 항목 하나가 통과합니다. 래퍼는 256개·불일치 0·`implicit_rounding_rejected: true`를 출력합니다. 다른 플랫폼은 실제 라이브러리 절대 경로를 사용하십시오. 네이티브 벤치마크는 별도 빌드이며 이 인터페이스 검사를 대체하지 않습니다.

컴파일 경고는 보존해야 합니다. 원본 GCC·Boost 인라인 경고 및 sanitizer 근거는 [벤치마크 상세](../benchmarks/BENCHMARKS.md)에 설명했습니다. CTest 통과가 모든 경고의 무해함을 증명하는 것은 아닙니다.

## 5. 새 시간 측정 없이 저장 자료 감사

```bash
python tools/audit_benchmark.py
# 프로젝트 및 NumPy 설치 필요:
python tools/audit_benchmark.py --recheck-fixtures
```

첫 명령은 NPZ 해시, 측정 소스 파일 12개 해시, 반복 개수, 중앙값, 반복별 비율과 건수의 일관성을 검사합니다. 두 번째는 `allow_pickle=False`로 저장 배열을 읽고 **4,096개 전체**를 정수·Fraction으로 재계산해 시험군별 합격 수를 확인합니다.

예상 필드는 `status: passed`, `fixture_rows: 4096`이며 재검사를 사용하면 `exact_recheck_rows: 4096`입니다. 과거 네이티브 시간이나 모든 기준선의 과거 오판 건수를 독립 재측정하는 것은 아닙니다. 아카이브 일관성과 현재 정확 판정을 검사합니다.

측정한 소스의 해시가 바뀌면 실패하는 것이 유용한 동작입니다. 해당 실행을 감사하려면 원본 코드를 복원하고 새 코드를 평가하려면 새 벤치마크를 생성하십시오. 과거 해시를 편집해 억지로 통과시키지 마십시오.

## 6. 벤치마크 재실행과 그래프 생성

```bash
python -m pip install '.[bench]'
python benchmarks/run.py --n 32 --trials 3 --out validation/my-smoke
python benchmarks/run.py --n 1024 --trials 9 --seed 20261007 --out validation/my-run
python benchmarks/plot.py --results validation/my-run/benchmark.json --out validation/my-run/figures
```

기록된 설정을 재현할 때 OpenBLAS·OMP는 한 스레드를 사용하십시오. 네이티브 측정에는 C++ 컴파일러·Boost가 필요하며 Windows는 WSL을 사용합니다. 정확한 분포·제외 비용·버전은 [BENCHMARKS.md](../benchmarks/BENCHMARKS.md)를 참고하십시오.

재현 성공은 정확 참조와 불일치가 없고, 결과 파일이 유효하며, 환경이 사실대로 기록됐다는 의미입니다. **더 빨라야 한다는 뜻은 아닙니다.** 원하는 수치가 나올 때까지 느린 실행을 버리지 말고 같은 입력과 코드 버전으로 전후 자료를 보존하십시오.

원본 실험을 다시 돌리지 않고 그림만 재생성할 수 있습니다.

```bash
python benchmarks/plot.py --results benchmarks/results/benchmark.json --out validation/redrawn-figures
```

## 7. 개발 소스가 아닌 배포 파일 검사

소스 루트에서 별도 환경을 만들고 이 소스에서 빌드한 wheel을 설치합니다.

```bash
python -m pip install build
python -m build
python -m venv .wheel-test
# POSIX:
.wheel-test/bin/python -m pip install --no-deps dist/dexted_dsp-0.1.0-py3-none-any.whl
.wheel-test/bin/python -m unittest discover -s tests -v
.wheel-test/bin/python tools/documentation_smoke.py
# Windows는 .wheel-test/bin/python 대신 .wheel-test\Scripts\python.exe 사용
```

이 검사에서는 `PYTHONPATH=src`를 설정하지 마십시오. 그러면 wheel에서 빠진 파일을 개발 소스가 대신 제공할 수 있습니다. 재빌드는 선택 개발 도구 설치 후 `python -m build`, `python -m twine check dist/*`를 사용합니다. 빌드·검사는 게시가 아닙니다. README 메타데이터를 바꿨으면 wheel도 다시 빌드하십시오.

## 8. 문서·공개 전 검사

```bash
python tools/check_links.py
python tools/check_documentation.py
python tools/audit_benchmark.py
```

로컬 링크, 4개 언어별 필수 문서, 공통 벤치마크 식별자, 필수 결과표와 소스 일관성을 확인합니다. 번역의 모든 뉘앙스를 검증하거나 수학을 증명하는 도구는 아닙니다. GitHub Actions의 실제 호스팅 실행이나 외부 감사도 의미하지 않습니다.

공개 전 [validation/docs_refresh/summary.json](../../../validation/docs_refresh/summary.json)을 확인하고 원시 로그를 보존하십시오. README의 수치가 의도한 실행을 가리키는지 확인하고 배포 메타데이터를 재빌드한 후 [공개 절차](../development/RELEASING.md)를 진행합니다. ZIP 체크섬과 `MANIFEST.sha256`은 파일 식별용이며 수학적 정확성의 증명은 아닙니다.

[OAI-README]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/README.md
[OAI-325]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex
[OAI-DFT]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex
[CP-2017]: https://arxiv.org/abs/1702.00668
[SCIPY-FREQZ]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html
[PYPA]: https://packaging.python.org/en/latest/tutorials/packaging-projects/
