# 04. 계수 데이터와 다수의 장시간 자료 구성

[문서 홈](README.md) · [매니페스트](manifests/long-signals-v1.json) · [실행 도구](tooling/longrun.py)

## 1. 짧은 테스트만으로 끝내지 않는 데이터 전략

하나의 hidden-peak 예제와 몇 개의 필터에 대한 결과를 산업용 일반 성능으로 확대하지 않습니다. 데이터는 **계수 corpus**, **장시간 파형 corpus**, **운영 event trace** 세 종류로 구성합니다. 첫 종류는 수학적 판단의 정확성을 검증하고, 두 번째는 실제 엔진의 연속 상태·수치·I/O를 검증하고, 세 번째는 배포 도구의 장기 신뢰성을 검증합니다.

세 종류는 같은 run ID 아래 연결할 수 있지만 건수·시간·정답의 분모를 합치지 않습니다. 같은 계수를 1,000시간 검사해도 독립적인 계수 1,000개가 아닙니다. 1분 파일을 1,440회 반복한 것은 새로운 24시간 현장 기록이 아닙니다.

## 2. 계수 corpus — 목표 100,000 합성 + 3,000 실제 export

아래는 확보·생성 목표이며 이미 보유한 자료 수가 아닙니다. 현재의 9-case 경쟁 비교, 25-case 설계 pilot, 1,200-case EQ catalog는 그대로 보존하고 신규 corpus와 분리합니다.

| 집합 | 목표 수 | 주요 범위 | 정답 생성·주의점 |
|---|---:|---|---|
| C-ORD | 40,000 | Butterworth/Chebyshev/elliptic/EQ/notch, 1~16 SOS 중심 | 독립 exact oracle; margin bin 사전 고정 |
| C-HQ | 20,000 | 높은 Q, pole 반경이 1에 접근, 매우 좁은 peak | grid 오라클 금지; Fs/2 부근 포함 |
| C-BOUND | 20,000 | gamma 근방, equality, 1 ULP 상하, 끝점/중복근 | exact constant/rational 사례 + 독립 peak enclosure |
| C-ADV | 10,000 | section 보상, pole-zero cancellation, 큰 중간 이득, 17~32 SOS | 내부 안정성 정책과 전체 응답 구별 |
| C-INVALID | 10,000 | NaN/Inf/complex/nonunit a0/초대형 입력/형식 오류 | invalid 정답표; 수학적 truth 분모와 분리 |
| C-REAL | ≥3,000 | 최소 3개 실제 제품 프로젝트의 최종 배포 계수 | 사용·보존 권한, 고정 holdout ≥1,000 |

유효 합성 90,000건에서는 f32/f64를 균형 배치하고 section 수 1,2,4,8,16,32를 층화합니다. 32-section 예산 한계는 정상적으로 UNKNOWN을 만들 수 있으므로 별도 집합으로 공개합니다. 모든 행에 원 family, design parameters, normalized coefficients, deployed hex, precision, gamma, generator version, oracle outcome을 저장합니다.

임계 gamma를 Dexted 자신이 만든 peak 추정으로만 결정하지 않습니다. 독립 rational/interval 기준으로 임계값을 생성하고 exact equality를 구성할 수 있는 filter family를 별도 사용합니다. 어떤 case가 실패하는지 본 뒤 fixture를 제거하지 않습니다.

## 3. 장시간 합성 corpus — 이번에 구성한 24건

[JSON 매니페스트](manifests/long-signals-v1.json)가 길이·채널·seed·generator의 기준입니다. 자료는 절대 샘플 인덱스에서 생성하여 chunk마다 phase/RNG를 초기화하지 않습니다. 반복되는 짧은 파일을 이어 붙이지 않습니다.

| 그룹 | 개수 × 개별 길이 | sampling / channel | record-hours | 주요 목적 |
|---|---|---|---:|---|
| A01~A12 | 12 × 30분 | 48kHz / stereo | 6 | 일반 audio export·state 경계·노이즈·과도 응답 |
| B01~B06 | 6 × 60분 | 96kHz / stereo | 6 | 고 sample-rate에서 메모리·긴 누적 인덱스 |
| C01~C04 | 4 × 4시간 | 1kHz / 8ch | 16 | 저속 계측·다채널 drift·시계·state 분리 |
| D01~D02 | 2 × 24시간 | 48kHz / stereo | 48 | 긴 가상 입력, 재시작/복구 시험 기반 |
| 합계 | 24건 | mixed | **76** | **248 channel-hours** |

모든 값을 f32 raw로 저장하면 **23,270,400,000 scalar samples = 93,081,600,000 bytes ≈86.689GiB**입니다. 계산은 `duration × fs × channels × 4`이며 압축률을 가정하지 않습니다. 입력 1본+비교 출력 2본+임시 파일/증거를 보존할 경우 최소 수백 GB의 별도 저장 공간을 계획합니다. Git에는 바이너리를 올리지 않고 manifest·generator·hash·요약을 올립니다.

A01~A06은 실행 가능한 pilot입니다. **6 × 30분 = 3 record-hours**, stereo 48kHz이므로 1,036,800,000 scalar samples입니다. A07~A12는 같은 6개 파형 family에 다른 seed를 적용한 추가 기록입니다. 이를 12개의 완전히 다른 실제 산업 환경이라고 부르지 않습니다.

### 이번 generator에 실제 구현된 여섯 family

| family | 구성 | 장시간 확인할 항목 |
|---|---|---|
| sweep | 전 길이에 걸친 log sweep + 비반복 counter noise | phase 연속, 샘플 인덱스, 고주파 및 저주파 구간 |
| multitone | 서로 다른 주파수의 tone 3개 + channel phase + noise | 지속 여기, 채널 분리, amplitude·state 추적 |
| wideband | 시간에 따른 noise amplitude 변화 + 저주파 성분 | 통계 변화, 긴 누적 오차, 전 구간 처리 여부 |
| transients | 드문 impulse-like 사건 + noise | chunk에 걸친 transient, 상태 reset 감지 |
| silence_recovery | 서로 다른 길이의 활성·무음 구간 | 재시작, tail, 작은 값·무음 후 상태 |
| drift | 긴 주파수 drift + 느린 DC 변화 + noise | 정상/비정상 구간, 장시간 state 및 추세 |

각 기록 말미의 최대 60초는 zero-input tail이며, 명시된 총 길이에 포함됩니다. 이는 임의의 high-Q 필터에 충분한 settling time이라고 주장하지 않습니다. 산업용 adapter에서는 pole/interval state bound와 고객 허용 오차로 tail 길이를 별도로 산출해야 합니다.

## 4. 장시간 자료의 다음 확장

실제품용 qualification에는 단순한 6-family bootstrap보다 강한 자극이 필요합니다. 아래는 WBS에서 구현할 추가 항목입니다.

**공진 dwell:** 독립적으로 격리한 peak 영역의 대표 주파수와 양쪽 detuning에서 충분한 길이로 excitation합니다. 짧은 sweep가 high-Q peak에서 충분히 머물지 못하는 문제를 보완합니다. 정확한 peak 위치를 근사 Hz로 변환한 경우 입력 생성은 근사이고, 그 신호가 전체 상한의 증명은 아닙니다.

**극단 동작:** impulse polarity, DC step, near-Nyquist, 매우 작은 값/subnormal, 단계적 gain, 고 crest factor, 채널별 위상·상관 차이를 추가합니다. full scale saturation이나 비선형 limiter를 포함하면 LTI 모델과 분리합니다.

**I/O·상태 사건:** sample gap/duplicate/out-of-order, 127·128·129·255·256·257·4093 frame block, 한 샘플 단위 시작/끝, 저장·복원, 취소, 장치 바꿈, coefficient change를 event trace로 기록합니다. 계수 전환 전후 인증만으로 전체 time-varying 경로가 인증되는 것은 아닙니다.

## 5. 실제 장시간 자료 — 최소 20건, 각 30분 이상

[외부 자료 등록부](manifests/external-sources-v1.json)는 현재 acquisition 상태를 PENDING으로 둡니다. 확보하지 않은 경로·SHA를 가짜 값으로 채우지 않습니다.

| 실제 자료 부류 | 목표 | 권한·조건 | 산업용 의미 |
|---|---|---|---|
| 파트너 audio export / 사용 세션 | ≥8건 × ≥30분 | 실제 녹음/재생 pipeline 출처, permission, privacy 검토 | 실제 제품 동작 검증 |
| 파트너 센서/계측 연속 trace | ≥6건 × ≥4시간 | 장비·calibration·timestamp·단위·gap 메타데이터 | 합성 drift를 실제 장기 변동과 대조 |
| 공개 오디오 derived long session | ≥6건 × ≥60분 | 원본 출처·라이선스·편집 순서·offset 보존 | 다양한 실제 소리의 처리; 현장 연속 기록은 아님 |

MUSAN은 music/speech/noise 원자료 후보이고, LibriSpeech는 음성 후보입니다([S05](11_SOURCES_AND_BASELINE.md#s05), [S06](11_SOURCES_AND_BASELINE.md#s06)). 둘을 다운로드했다고 “실제 산업용 filter coefficient data”를 확보한 것은 아닙니다. 파편을 연결했다면 `source_kind=derived_real_composite`, `continuous_capture=false`와 모든 splice 정보를 남깁니다. 인위적 resample·upmix를 새로운 센서 측정으로 집계하지 않습니다.

상용 고객 자료는 기본 비공개입니다. 라이브러리 MIT 라이선스와 데이터 권리는 독립적입니다. 다운로드 가능 여부, 수정/재배포/상업 사용 조건, attribution, 지역·개인정보 제한, 보존 기한을 승인받아야 합니다. 데이터 파일 자체를 repo/ZIP에 포함하는 행위는 권한 확인 이후에만 합니다.

## 6. 매니페스트의 최소 필드

모든 실제 자료는 dataset_id, record_id, source_kind, original_source_uri, acquisition_status, rights_owner, permission_reference, license, attribution, continuous_capture, duration_seconds, sample_rate_hz, channels, dtype, unit, timezone/timebase, dropped_frames, original_sha256, transformed_sha256, transformation_recipe, parent_session_id, split_group, consent/privacy_state를 가져야 합니다.

계수 자료에는 product/design lineage, exported_coefficients_hex, a0 normalization recipe, precision, section order, sample rate, policy gamma, source commit, transformation history를 추가합니다. 알고리즘에 사용되는 값과 표시용 메타데이터를 분리합니다. origin checksum과 decoded waveform checksum 둘 다 있으면 format transcoding의 영향을 추적할 수 있습니다.

## 7. 데이터 분할과 누수 방지

유사한 설계 파라미터나 같은 제품의 계수 변형을 train/development와 holdout에 흩뿌리지 않습니다. product/design-template/seed-lineage 및 녹음 session 단위로 묶어 60/20/20 개발·검증·holdout을 분할합니다. 실제 계수 holdout 최소 1,000건 조건은 비율보다 우선합니다. 데이터 규모가 부족하면 미달을 보고합니다.

동일 audio의 crop, gain 변환, channel duplicate, sample rate 변경은 같은 parent group입니다. ID가 달라도 파형이 같을 수 있으므로 content hash와 특징 기반 유사도 검사를 병행합니다. 합성 family가 같고 seed만 다른 기록은 독립적인 실제 환경 표본처럼 확률 해석하지 않습니다.

holdout 결과를 보고 알고리즘을 수정하면 그 holdout은 더 이상 완전한 blind set이 아닙니다. 수정 내역을 남기고 외부 평가용 새 holdout을 확보합니다. 기존 결과를 지우지는 않습니다.

## 8. 길이·고유성·파일 무결성 승인

header의 길이만 믿지 않고 실제 디코딩한 frames를 계산합니다. 기대 sample count와 read count가 달라지면 TRUNCATED로 실패합니다. 샘플링한 첫 10초만 확인한 실행은 full-run으로 표시할 수 없습니다. 각 stream은 처음부터 끝까지 SHA-256에 반영하고 실제 처리 프레임 수를 기록합니다.

긴 자료를 전체 RAM에 적재하지 않습니다. chunk 단위로 처리하고 필터 state를 이어받습니다. 큰 WAV의 format 한계·container semantics는 별도 adapter가 담당하며 bootstrap은 명시된 endian의 `.f32le` raw 출력을 제공합니다. raw에는 header가 없으므로 manifest와 분리해 배포하지 않습니다.

파일 생성 여부와 입력 처리 여부를 구별합니다. `waveform_retained=false`는 모든 샘플을 생성·검사했지만 원시 파형 파일은 보관하지 않았다는 뜻입니다. 재현은 같은 manifest와 generator/environment로 수행하며, 다른 libm의 bit identity를 무조건 보장하지 않습니다. 외부 재현의 동일 입력이 중요하면 동일한 저장된 raw artifact를 전달합니다.

## 9. 자료 확보 실패 시 대안

고객 자료 권한이 없으면 합성 시험을 진행할 수 있지만 G3/G6 실자료·외부 도입 조건은 BLOCKED로 남깁니다. “산업형 합성”이라는 이름으로 현장 자료 조건을 충족했다고 처리하지 않습니다. 공개 자료는 알고리즘의 성능 평가에 보탬이 되지만 특정 제품의 현장 대표성을 증명하지 않습니다.

## 10. 이번 작성 시점의 상태

24건은 manifest와 generator로 구성되었습니다. 6건 pilot의 샘플 전량 스트리밍 검사 증거는 [evidence](evidence/README.md)에 있습니다. 24건 전체, 실제 자료 20건, 실제 제품 계수 3,000건, 24/72h 벽시계 soak는 아직 완료 결과가 아닙니다. 산업용 PASS라는 문구를 이 bootstrap 결과에 붙이지 않습니다.
