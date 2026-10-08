# 10. 실행 런북 — 지금 가능한 것과 앞으로 구현할 것

[문서 홈](README.md) · [증거 설명](evidence/README.md)

## 1. 이번 제공 범위

산업용 요구·WBS·검증 protocol과 함께 독립된 계획용 toolkit을 제공합니다. `tooling/longrun.py`는 데이터 전량 스트리밍과 SciPy 참조 처리기 regression을 실행합니다. `tooling/test_longrun.py`는 generator/manifest·state negative control을 검사합니다. 정식 라이브러리의 runtime·API는 이 계획 작성으로 변경되지 않습니다.

명령은 저장소 루트에서 실행합니다. ZIP만 받은 경우에도 `docs/plan`이 있는 압축 해제 디렉터리에서 같은 명령을 사용합니다. 기존 라이브러리를 검사하려면 전체 repository와 Dexted 설치가 필요합니다.

## 2. 환경 준비

검증된 bootstrap 조합은 Python 3.13, NumPy 2.3.5, SciPy 1.17.0입니다. “현재 최신”이라는 의미가 아니라 재현을 위해 고정한 조합입니다. 장시간 raw를 저장하지 않으면 수백 MB 메모리·소량 결과 공간으로 실행할 수 있지만 실제 자원은 host에 따라 달라집니다.

```bash
python -m venv .venv
# POSIX: source .venv/bin/activate
# PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r docs/plan/tooling/requirements-tested.txt
python docs/plan/tooling/longrun.py validate
python -m unittest discover -s docs/plan/tooling -p 'test_*.py' -v
```

manifest 검증 예상: 24 records, 76 record-hours, 248 channel-hours, 93,081,600,000 uncompressed bytes. 이 단계는 실제 샘플 전량 검사가 아닙니다.

## 3. 빠른 smoke — 길이를 숨기지 않습니다

```bash
python docs/plan/tooling/longrun.py run --profile smoke --out validation/industrial/smoke-001
```

6개 시나리오를 각각 **2초**만 실행합니다. 결과에는 `profile=smoke`, 실제 `duration_seconds=2`, 원래 예정한 길이를 별도 기록합니다. smoke를 3시간 장시간 검증 결과로 계산하지 않습니다. output directory가 이미 있으면 거절합니다.

## 4. 실제 pilot — 6건 ×30분 전량 생성·검사

```bash
python docs/plan/tooling/longrun.py run --profile pilot --out validation/industrial/pilot-001
```

기본적으로 원시 파형을 보관하지 않고 모든 frame을 생성·처리·해시합니다. 예상 결과는 6 records, 3 record-hours, 1,036,800,000 scalar samples입니다. phase·counter noise는 전체 절대 인덱스를 사용하고 짧은 clip을 재사용하지 않습니다. 처리 시간은 signal duration보다 짧을 수 있으며 soak의 벽시계 시간이 아닙니다.

## 5. 설치된 Dexted의 계수 인증까지 연결

전체 repository checkout에서 다음처럼 실행합니다.

```bash
python -m pip install .
python docs/plan/tooling/longrun.py run --profile pilot --with-dexted --out validation/industrial/pilot-with-core-001
```

이 옵션은 각 record에 사용한 reference SOS를 `certify_cascade`로 인증하고 `verify_cascade`로 재검증합니다. 파형 처리는 여전히 SciPy입니다. current Dexted가 설치되어 있지 않으면 명확히 실패합니다. 이번 local pilot 증거가 이 옵션을 사용했는지는 summary의 `dexted_core_executed`로 확인합니다. false이면 “Dexted가 3시간 실자료 검증 완료”라고 보고할 수 없습니다.

인증이 reference filter에서 UNKNOWN/REJECTED라면 runner가 실패합니다. 이 작은 bootstrap은 대규모 coefficient corpus의 모든 UNKNOWN을 집계하는 benchmark runner가 아닙니다. 그 runner의 개선은 B01 작업입니다.

## 6. 원시 장시간 파일이 필요한 경우

```bash
python docs/plan/tooling/longrun.py run --profile pilot --retain-waveforms --out validation/industrial/pilot-materialized-001
```

총 약 4.1472GB의 little-endian interleaved float32 입력이 생성됩니다. 파일명은 `A01.f32le` 등이며 manifest의 sample rate/channel 수와 함께 해석해야 합니다. raw 자체에 오디오 container header는 없습니다. 무단 업로드하거나 불필요하게 Git history에 추가하지 않습니다.

SHA-256은 raw file bytes와 summary의 input_sha256을 비교합니다. 보관하지 않은 경우 같은 pinned generator/environment에서 다시 생성하여 비교합니다. 다른 OS/libm에서 미세한 바이트 차이가 있으면 동일 입력 비교에는 보관된 원본 raw를 사용합니다.

## 7. 전체 24건·76시간 profile

```bash
python docs/plan/tooling/longrun.py run --profile qualification --confirm-long-run --out validation/industrial/full-001
```

원시 파형 보관은 별도의 `--retain-waveforms` 옵션으로만 켭니다. 필요한 저장량을 계산한 뒤 실행합니다. 일부 record만 실행하려면 `--record C01 --record D01`처럼 선택하며 결과의 actual record count를 그대로 보고합니다. subset이 전체 qualification의 완료를 의미하지 않습니다.

## 8. 결과 확인과 오류 처리

각 `<record>.json`은 실제 frame 수, input/output hash, numerical engine, f32/f64 최대 오차, state partition 차이, core 실행 여부, 소요 시간, process-lifetime RSS를 갖습니다. summary는 모든 요청 record 완료 뒤에 생성됩니다. 중도 실패한 디렉터리는 partial evidence이며 완료한 것처럼 이름만 바꾸지 않습니다.

`status=passed`는 해당 reference-runtime 시험의 조건 통과입니다. 외부 자료·수학 감사·24h/72h 벽시계 soak·전체 산업용 승인은 별도 상태입니다. native/Dexted 비용이라고 해석할 수 없는 전체 프로세스 RSS가 포함되어 있음을 주의합니다.

## 9. 아직 구현하지 않은 운영 명령

대규모 100,000 coefficient corpus runner, 실제 고객 adapter, exact high-Q settling/dwell 자동화, isolated RSS benchmark, 장치 실시간 재생, 24h/72h worker soak orchestration, external dataset acquisition은 WBS의 구현 대상입니다. 동작하지 않는 가상의 CLI를 현재 예제로 제시하지 않습니다.

[CI 설계 template](templates/ci-lanes.md)는 PR/nightly/weekly/release의 실행 책임을 설명하는 문서입니다. 새로운 장시간 CI를 이 계획만으로 자동 활성화하지 않습니다. 운영비·runner·권한·보존 정책 승인 후 R03에서 workflow를 구현합니다.

## 10. 로컬 문서 패키지 감사

```bash
python docs/plan/tooling/audit_plan.py
```

목표·작업 의존성·long manifest 합계·내부 링크·증거 scope가 일치하는지 확인합니다. 이 감사는 산업용 알고리즘 정당성 proof가 아닙니다. GitHub 업로드 시 `docs/plan`의 전체 파일과 docs hub 링크를 한 원자적 tree/commit으로 반영하고, HEAD 변경이 있으면 덮어쓰기 없이 새 base에 다시 합칩니다.
