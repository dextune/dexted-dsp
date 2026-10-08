# 06. 자원 예산·성능 목표·손실 없는 측정

[코어 명세 홈](README.md) · [상위 목표](../01_GOALS_AND_SCOPE.md) · [수치 계약](contracts/budgets.json)

## 1. 지표는 목표이며 측정 결과가 아닙니다

IND-04~06을 세분화합니다. baseline 성능을 확인한 뒤 G0에서 입력 집합·호스트·thread·빌드·비교 경계와 아래 목표를 승인·동결합니다. 미달 결과를 본 후 ordinary 집합을 줄이거나 실행 시간을 제외하지 않습니다. 정답과 속도를 맞바꾸지 않습니다.

## 2. 계산 규모별 목표

**Python verified prepared decision**은 미리 frozen된 계수에서 exact producer+필수 proof serialization+independent consumer까지의 warm wall time입니다. prepare/parser와 optional bounds는 별도 측정하되 전체 요청 지연에서도 보고합니다.

| SOS section 수 | f32 / f64 p95 목표(ms) | p99 목표(ms) | ordinary UNKNOWN 상한 | v1.0 적용 |
|---:|---:|---:|---:|---|
| 1 | 5 | 20 | 0.1% | 필수 |
| 2 | 25 | 100 | 0.1% | 필수 |
| 4 | 100 | 400 | 0.1% | 필수 |
| 8 | 250 | 1000 | 0.1% | 필수; IND-05 그대로 |
| 16 | 1000 | 4000 | 0.1% | 필수 |
| 17~32 | best effort, 미승인 | 미승인 | 목표 미지정, 전량 보고 | extended; 입력 지원과 SLO 구분 |

f32와 f64를 합산해 더 좋은 평균을 만들지 않습니다. native f32 predicate-only에는 초기 설계 목표를 따로 계측하고 Python verified 경로와 나누어 speedup을 계산하지 않습니다. native f64는 현재 unsupported입니다. optional full inspection은 별도 30초 확장 프로필을 명시적으로 요청해야 하며 자동 승격 금지입니다.

## 3. ordinary cohort 동결

고객/생성 lineage, m≤16, independent 안정성 여유·peak gap으로 ordinary 여부를 후보 코드 실행 **전에** 고정합니다. 초안 기준은 분모 pole modulus ≤0.98의 보수적 인증과 `|peak/γ-1|≥10^-3`의 독립 bracket입니다. peak bracket가 경계를 걸치거나 pole enclosure가 못 닫히면 해당 cohort label은 미확정이며 unresolved에 남깁니다. 전량 corpus에서 삭제하지 않습니다. high-Q/strict equality/extreme bit pattern은 별도 stress cohort입니다.

인증 가능한 정상 ordinary와 oracle rejected ordinary 양쪽에서 coverage를 측정합니다. UNKNOWN 분모는 oracle-resolved valid inputs이며 unique case를 기준으로 합니다. invalid·oracle unresolved·not_run을 성공 분모에 넣지 않습니다. UNKNOWN≤0.1%는 관측 목표입니다. 반복 30번은 독립 필터 30개가 아닙니다. 0 failures/n의 통계적 상한이 필요하면 iid 가정이 성립하는 범위에서만 별도 보고합니다.

## 4. 기본 hard policy

기본 worker: 전체 요청 5초, RSS 256MiB, 최대 nodes 50,000, depth 64, proof 4MiB, input 128KiB입니다. extended worker: 30초/1GiB, nodes≤100,000, depth≤128이며 caller opt-in만 허용합니다. 신규 intermediate integer cap은 262,144 bits, parser nesting 16, serialized cover leaves≤50,000을 초안으로 고정합니다. 이것은 기존 library max_depth=48/max_nodes=20000 default를 조용히 바꾸는 작업이 아닙니다.

모든 기본 stage 합계가 5초 안에 들어갑니다. producer가 4.9초를 쓰면 verifier에 또 5초를 줄 수 없습니다. 결과가 수학적으로 맞아도 verification time이 없으면 미검증으로 차단합니다. proof 4MiB는 **cap이지 반드시 그 크기의 proof를 처리한다는 latency 보장**이 아닙니다. 노드·정수·시간 한도는 모든 stage에서 함께 적용합니다.

soft deadline 이후 종료 유예 250ms, hard kill→reap 최대 750ms의 **운영 목표**를 둡니다. 이를 실시간 WCET proof로 광고하지 않습니다. child 실행 시간이 5초 이내일 것과 parent가 강제 종료한 것을 구분해 기록합니다. timeout budget에 큐 대기와 process cold start를 포함할지 분리할지는 request contract에 고정하며, end-to-end 지연에서는 둘 다 반드시 보고합니다.

## 5. OS별 enforcement

Linux는 격리 worker의 cgroup memory quota와 supervisor timeout을 사용하도록 설계합니다. Windows는 Job Object의 메모리/프로세스 종료 경계를 구현합니다. macOS는 RSS 감시·worker 종료 경계의 한계를 측정하며 정확한 hard RSS cap을 구현하지 못한 조합은 `HARDENED_RESOURCE_LIMIT_UNSUPPORTED`로 표시합니다. RLIMIT_AS를 RSS와 동일시하지 않습니다. quota 설치 실패 후 무제한 실행으로 fallback하지 않습니다.

이 조합들의 구현과 측정은 CW-06/CW-19의 결과가 있어야 확정됩니다. 미지원 OS를 '모든 플랫폼 hard bounded' 주장에 넣지 않습니다.

## 6. 측정 절차

고정 corpus·고정 coefficients·threshold에서 SciPy `freqz_sos`, python-control `frequency_response`, 각각+Dexted, Dexted prepared decision, full inspection을 분리합니다. order는 seeded shuffle, warmup 5회, case/method별 최소 30 untrimmed time observations입니다. 오라클 계산은 correctness lane에서 수행하여 latency에 섞지 않습니다. repeated calls 결과가 변하면 성능 계산 이전에 correctness failure입니다.

memory는 별도 isolated fresh process에서 minimum 30 observations, baseline RSS와 peak RSS·after-GC retained RSS·tracemalloc peak를 구분합니다. 동일 프로세스 lifetime high-water를 다음 method의 비용으로 귀속하지 않습니다. native buffers를 포함하는 RSS와 Python heap을 하나의 막대로 섞지 않습니다. 전체 요청·sampler setup·TF convolution·I/O 비용은 exclusions 표에 남깁니다.

9개 사례를 풀링한 과거 median은 역사적 수치로 유지합니다. 새 보고서는 family×section×precision별 quantile, within-case paired delta, process/session 간 분산을 보여줍니다. CI는 hardware-independent correctness를 검증하고 성능 SLO 판정은 동결된 기준 장비에서 합니다. bootstrap interval은 case/session 단위로 cluster resampling하며 30 trials를 독립 population으로 간주하지 않습니다.

## 7. censoring·failure 정책

작업 시작 전 예정 case IDs를 ledger에 씁니다. 각 case는 completed/invalid/unknown/timeout/error/cancelled/not_run 중 하나로 종결합니다. mismatch 발견 시 fail-fast 모드를 쓰더라도 나머지를 NOT_RUN으로 마감합니다. partial 파일을 성공 summary로 읽지 않습니다.

timeout을 5,000ms의 정상 관측값으로 위장하지 않습니다. censored time과 실제 deadline을 별도 필드에 저장합니다. p99를 계산할 충분한 uncensored 자료가 없으면 p99 미확정으로 두고 SLO 통과를 막습니다. 17~32 extended 결과·거대 integer·near-boundary 실패도 원시 결과에 전부 남깁니다.

## 8. 최적화 승인 조건

CW-10 최적화는 먼저 모든 mandatory correctness/legacy test를 통과합니다. 같은 input family에서 verified pipeline p95가 유의미하게 나아지고 p99·RSS·UNKNOWN이 악화되지 않아야 기본값으로 켭니다. 개선이 없으면 실험 flag로 남기거나 제거합니다. mathematically independent consumer를 생략한 fast mode를 표준 성능으로 발표하지 않습니다.
