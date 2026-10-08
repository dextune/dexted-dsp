# 11. 공식 근거, 기준 소스, 현재 상태

[문서 홈](README.md)

## 1. 기준 소스와 확인 범위

계획의 출발점은 private repository `dextune/dexted-dsp`, `main` commit `0a2c1c4e87fa868c166953e9527a3ac721fe01c3`입니다. source tree는 `ae736013c0babab3c59297cbd9fb8e0627e9a1d3`입니다. 후속 구현 때 HEAD가 바뀌면 baseline inventory를 새로 생성합니다.

| 확인 항목 | 기준 파일·근거 | 현재 해석 |
|---|---|---|
| maturity/미달 gate | [implementation-status](../product/implementation-status.md) | research alpha, 실제 자료·외부 검토 미완료 |
| math contract | [cascade.py](../../src/dexted_dsp/cascade.py) | max 32 SOS, exact Bernstein 충분조건, UNKNOWN 가능 |
| competitor pilot | [run.py](../../benchmarks/competitive/run.py) | SciPy/control 실제 호출, UNKNOWN bool 축약 개선 필요 |
| measured evidence | [동결 JSON](../../benchmarks/competitive/results/run-20261008.json) | 선택한 합성 9건, 반복 30회, field prevalence 아님 |
| API scope | [inspection](../product/inspection.md) | 표현 계수 인증, runtime roundoff 별도 |
| existing host CI | main의 Actions run `37731767577` | 확인 시 completed/success |
| existing competitive CI | main의 Actions run `37731767584` | 확인 시 completed/success |

이 CI 결과는 계획을 올리기 전 기준 source의 결과입니다. 새 계획 commit이 성공했는지, 그 commit의 CI가 끝났는지는 별도로 확인합니다. 기존 CI 성공으로 새 long/real/soak 계획을 이미 실행했다고 주장하지 않습니다.

현재 1,200 EQ reference-only 계산과 64-case actual producer 비교를 구분합니다. “1,200개 정답을 계산했다”와 “라이브러리를 1,200개 모두 검증했다”는 같은 문장이 아닙니다. 기존 9-case 시간 반복 270개 역시 270개의 독립 계수 사례가 아닙니다.

## 2. 외부 공식 자료 — 열람 기준 2026-10-08

외부 문서는 아래 특정 URL/버전의 기술 근거입니다. 목표 숫자·일정·표본 수는 이 프로젝트의 제안값이며 외부 기관이 보증한 규격이 아닙니다. 법률·안전 적합성을 자동 보장하지 않습니다.

### S01

**SciPy `signal.freqz_sos` 공식 문서**  
https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz_sos.html

SOS 계수의 numerical frequency response, 명시한 주파수의 단위·endpoint·representation 의미를 확인했습니다. 열람 페이지는 SciPy 1.18.0 문서였으나 기존 벤치마크와 이번 bootstrap은 1.17.0으로 고정합니다. 서로 다른 버전을 최신이라는 이름으로 섞지 않습니다.

### S02

**SciPy `signal.sosfilt` 공식 문서**  
https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfilt.html

SOS 기반 IIR 처리, `zi` 초기 상태와 `zf` 최종 상태, direct-form II transposed 구현 경계를 확인했습니다. 두 block partition에 같은 함수를 적용하는 시험은 state regression이며 독립 수학 오라클이 아닙니다.

### S03

**python-control `frequency_response` 공식 문서**  
https://python-control.readthedocs.io/en/latest/generated/control.frequency_response.html

이산시간 `G(exp(j*omega*dt))`, rad/s 입력, response magnitude 의미를 확인했습니다. numerical estimate와 Dexted proof를 기능적으로 같은 것으로 비교하지 않는 근거입니다.

### S04

**SymPy polynomial reference**  
https://docs.sympy.org/latest/modules/polys/reference.html

exact polynomial domain·root counting/격리 검증 도구의 API 근거입니다. 특정 root solver를 호출했다는 사실만으로 프로젝트 전체가 formal verification된 것은 아닙니다. oracle resource exhaustion·독립 구현 검토가 필요합니다.

### S05

**OpenSLR MUSAN / SLR17**  
https://www.openslr.org/17/

music/speech/noise corpus이며 공식 페이지가 CC BY 4.0을 표기한 원자료 후보입니다. 이번 계획 작성 중 실제 파일을 다운로드하거나 권한별 파생자료를 배포하지 않았습니다. 개별 metadata·attribution·원본 라이선스 범위를 acquisition 시 다시 확인합니다.

### S06

**OpenSLR LibriSpeech / SLR12**  
https://www.openslr.org/12/

공식 페이지의 읽기 음성 corpus와 CC BY 4.0 표기를 확인했습니다. segmented speech를 이어붙이면 derived composite이며 새로운 현장 연속 녹음이 아닙니다. 산업 filter coefficients와도 다른 종류의 자료입니다.

### S07

**NIST SP 800-218, SSDF v1.1 (2022 final)**  
https://csrc.nist.gov/pubs/sp/800/218/final

안전한 개발·보호·검증·취약점 대응 프로세스의 참고 기준으로 사용합니다. 본 프로젝트의 NIST 인증이나 법규 적합성을 의미하지 않습니다. 실제 조직 적용 시 최신 관련 보완 문서와 조직 요구를 재검토합니다.

### S08

**SLSA specification v1.2**  
https://slsa.dev/spec/v1.2/

source/build 출처와 점진적 공급망 보증의 참고 체계입니다. 열람 시 v1.2는 approved로 표시되었습니다. 실제 달성 수준은 builder·권한·attestation 검증 후 판단하며, 이 문서는 level 달성 선언이 아닙니다.

### S09

**PyPI Trusted Publishers 공식 문서**  
https://docs.pypi.org/trusted-publishers/

OIDC 기반의 짧은 수명 credential을 사용하는 배포 방식의 근거입니다. 실제 publish 설정·namespace·권한 승인은 별도 작업이며 자동으로 공개 출시하지 않습니다.

### S10

**W3C Audio EQ Cookbook, 2021 Working Group Note**  
https://www.w3.org/TR/2021/NOTE-audio-eq-cookbook-20210608/

오디오 biquad 설계식의 기준 자료입니다. 이 공식으로 설계한 계수는 “표준 설계식으로 만든 합성 데이터”이며 실제 현장 export라는 뜻이 아닙니다. W3C가 Dexted를 보증한다는 표현을 사용하지 않습니다.

## 3. 주장 관리

현재 사실, 이번에 만든 실행 도구, 이번 실제 실행 결과, 앞으로의 요구 목표를 문서마다 구별합니다. 증거가 없는 값에 `measured`, `certified`, `industry-proven`를 붙이지 않습니다. 특히 실제 제품 계수 3,000건·실자료 20건·76h 전체·24/72h soak·외부 reviewer 서명은 아직 완료되지 않은 목표입니다.

출처 URL만 있다는 이유로 자료를 확보했다고 처리하지 않습니다. 실제 acquisition의 content SHA·license review·원본 보존·변환 recipe가 채워져야 합니다. 재현성을 위해 문서 URL과 dependency version을 함께 고정합니다.
