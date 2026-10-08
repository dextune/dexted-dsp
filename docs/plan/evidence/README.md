# 이번 문서 패키지의 실행 증거

[문서 홈](../README.md) · [실행 런북](../10_EXECUTION_RUNBOOK.md)

## 실행한 것

고정 매니페스트의 A01~A06, 각각 30분 stereo 48kHz 합성 입력을 **전량 생성·스트리밍 처리**했습니다. 합계 **3 record-hours, 1,036,800,000 scalar samples, 4,147,200,000 input bytes**입니다. 원시 파형은 보관하지 않고 전체 입력·출력의 SHA-256과 실제 처리한 frame 수를 남겼습니다. 같은 pinned 환경에서 재생성하거나 `--retain-waveforms`로 실제 긴 파일을 만들 수 있습니다.

[원시 record별 요약 JSON](bootstrap-pilot.json) · [실행 로그](bootstrap-pilot.log) · [16개 toolkit 회귀 테스트](tooling-tests.log)

| ID | family | 실제 데이터 길이(초) | 처리 frames | block partition 최대 차이 | f32 대 f64 최대 절대 오차 |
|---|---|---:|---:|---:|---:|
| A01 | sweep | 1800 | 86,400,000 | 0 | 3.81707378e-08 |
| A02 | multitone | 1800 | 86,400,000 | 0 | 2.32887661e-08 |
| A03 | wideband | 1800 | 86,400,000 | 0 | 3.16918552e-08 |
| A04 | transients | 1800 | 86,400,000 | 0 | 2.74896784e-08 |
| A05 | silence_recovery | 1800 | 86,400,000 | 0 | 3.39172466e-08 |
| A06 | drift | 1800 | 86,400,000 | 0 | 3.65359665e-08 |

최대 관측 오차는 **3.81707378483e-08**입니다. 이 값은 제공한 2-section dyadic **참조 필터에 대한 수치 회귀 검사**의 결과입니다. 입력·필터·엔진이 바뀐 일반 산업용 정확도 규격으로 사용하지 않습니다. 허용오차 `3e-6`은 실행 전에 정한 이 참조 필터용 상한입니다.

## 실행하지 않은 것

**이 local pilot에는 Dexted core를 호출하지 않았습니다**(`dexted_core_executed=false`). 파형 처리는 SciPy `sosfilt`이며 같은 엔진의 block 분할을 바꾸어 상태 연속성을 확인했습니다. 이것은 독립적인 mathematical oracle가 아닙니다.

실제 산업용 자료, 전체 24건·76시간 profile, 24h/72h 벽시계 soak, 고객 하드웨어, 외부 reviewer 평가는 이번 결과가 아닙니다. coefficient corpus 100,000건과 real exports 3,000건도 계획 목표입니다. `--with-dexted`로 설치된 라이브러리의 계수 인증을 연결하는 명령은 제공하지만, 그 모드의 실행 증거와 이번 local 결과를 혼합하지 않습니다.

## 소요 시간과 메모리의 해석

signal duration은 3시간이고, 이 환경의 record 실행 시간 합계는 약 95.301초입니다. synthesis·hashing·3개 numerical lane·결과 계산을 포함한 전체 toolkit 시간입니다. Dexted의 latency나 오디오 real-time throughput 벤치마크로 해석하지 않습니다.

RSS는 Python·NumPy·SciPy와 모든 lane을 포함한 process-lifetime high-water입니다. Dexted 고유의 incremental/native memory 비용이 아닙니다. 상세 환경, runner·manifest hash는 JSON에 보존했습니다.

## 재검증

```bash
python -m unittest discover -s docs/plan/tooling -p 'test_*.py' -v
python docs/plan/tooling/audit_plan.py
python docs/plan/tooling/longrun.py run --profile pilot --out validation/industrial/pilot-reproduction-001
```

실행 디렉터리는 새 이름을 사용합니다. 다른 OS/libm에서는 raw hash가 달라질 수 있으므로 같은 입력의 외부 비교가 필요하면 이미 생성된 원본 raw와 그 hash를 전달합니다.
