# GitHub 및 패키지 공개 가이드

[English](../../en/development/RELEASING.md) · [한국어](RELEASING.md) · [简体中文](../../zh-CN/development/RELEASING.md) · [日本語](../../ja/development/RELEASING.md)

[Dexted DSP](../README.md)

## 1. 공개 전 소유권과 범위 확인

저장소는 `https://github.com/dextune/dexted-dsp`이며 DEXTUNE이 Dexted DSP를 관리합니다. Git 커밋과 PyPI 게시는 다릅니다. 배포 전 패키지 이름 사용 가능 여부·메타데이터·기존 저작권·아래 검사를 확인하십시오. DOI·기관 보증·외부 감사·CI 상태를 꾸며내지 마십시오.

기본 README는 영어이며 한국어·중국어 간체·일본어판이 같은 측정 자료를 연결합니다. 연구용 alpha 표시, 엄격한 입력 조건, `unknown` 시 거절, OpenAI 참고 범위는 유지하십시오. 실행 코드는 Crouzeix 구현이나 청력·영상 품질의 안전 인증기가 아닙니다.

## 2. 로컬 릴리스 검사

압축을 푼 소스 루트의 적절한 환경에서 실행합니다.

```bash
python -m pip install '.[dev,bench]'
python -m unittest discover -s tests -v
python tools/documentation_smoke.py
python tools/check_documentation.py
python tools/check_links.py
python -m pip install -r benchmarks/requirements-bench-tested.txt
python tools/restore_fixtures.py
python tools/audit_benchmark.py --recheck-fixtures
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
```


원시 로그와 [이번 재검증 요약](../../../validation/docs_refresh/summary.json)을 확인하십시오. 테스트 통과는 릴리스 점검이지 외부의 독립 증명 감사가 아닙니다. 새 벤치마크가 반드시 더 빨라야 하는 것은 아닙니다. 실행 코드가 바뀌면 기존 해시를 수정하거나 유리한 실행을 고르는 대신 새로운 측정 버전을 남기십시오.

## 3. 기존 저장소에 변경 반영

별도의 Git 이력을 만드는 대신 관리 중인 저장소를 복제하십시오. 비공개 상태에서는 접근 권한이 필요합니다. 쓰기 권한이 없는 기여자는 포크와 풀 리퀘스트를 사용하십시오.

```bash
git clone https://github.com/dextune/dexted-dsp.git
cd dexted-dsp
git switch -c improve-dexted-dsp
# Edit files, run the documented checks, then review the diff.
git status --short
git diff --check
git add .
git commit -m "Improve Dexted DSP"
git push -u origin HEAD
```

커밋 전에 위 릴리스 검사를 실행하십시오. 작업 브랜치를 올린 뒤 GitHub의 변경 내용과 CI 결과를 검토하고 통상적인 리뷰 절차로 병합하십시오. main 브랜치에 강제 푸시하지 마십시오. `dist/`의 빌드 결과는 로컬 산출물이며 소스 커밋에 포함하지 않습니다.

## 4. 실제 배포 파일 빌드·검사

```bash
python -m build
python -m twine check dist/*
python -m venv .wheel-test
# POSIX; Windows: .wheel-test\Scripts\python.exe
.wheel-test/bin/python -m pip install --no-index --no-deps dist/dexted_dsp-0.1.0-py3-none-any.whl
.wheel-test/bin/python -m unittest discover -s tests -v
.wheel-test/bin/python tools/documentation_smoke.py
```


wheel 테스트에는 `PYTHONPATH=src`를 설정하지 마십시오. wheel은 순수 Python이며 네이티브 공유 라이브러리를 포함하지 않습니다. 네이티브 사용자는 CMake를 이용합니다. 소스 배포본에는 코드·예제·문서·벤치마크 근거 자료가 포함됩니다.

일반적인 빌드·검사 명령은 선택적 도구를 내려받을 수 있습니다. 이번 환경에서는 네트워크로 `build`·`twine`을 설치할 수 없어 이미 설치된 setuptools 백엔드로 로컬 빌드했습니다. 실제 실행한 검사는 재검증 요약을 확인하십시오. 문서에 명령을 적었다고 그 명령을 모두 실행했다는 의미는 아닙니다.

이미 공개한 버전의 파일을 바꿀 때에는 버전을 올리십시오. 이번 산출물은 **아직 게시하지 않은** 0.1.0 패키지의 README·문서를 갱신합니다. 실제 공개 전에 공개 URL을 설정하고 PyPI 메타데이터의 상대 그림 링크를 검토하며 4개 언어 문서를 동기화하십시오. PyPI에는 절대 그림 URL이나 전용 짧은 README가 필요할 수 있습니다.

## 5. 검토 완료 후 게시

로컬·호스팅 검사와 권한 검토 후 의도한 버전 태그를 생성하고 GitHub Release에 소스 ZIP·wheel·sdist·체크섬을 첨부하십시오. PyPI는 선택 사항입니다. 이름을 확보하고 TestPyPI로 확인한 뒤 승인된 게시 방법을 설정하십시오. 토큰·암호·자동 업로드 코드는 들어 있지 않습니다.

인덱스의 이름과 배포 파일을 실제로 확보하기 전에는 `pip install dexted-dsp`가 이 프로젝트를 설치한다고 홍보하지 마십시오. 빌드와 업로드는 별개입니다. [PyPA 공식 패키징 가이드](https://packaging.python.org/en/latest/tutorials/packaging-projects/)를 참고하십시오.

## 6. 유지관리

동작·인증서 스키마를 바꾸면 버전과 회귀 테스트를 갱신하고 공정하게 다시 측정한 후 4개 언어를 업데이트하십시오. `MANIFEST.sha256`과 체크섬은 바이트 무결성 기록이지 수학의 정확성을 증명하지 않습니다. 검사 속도 우위를 지각적 품질이나 의료적 안전성 주장으로 바꾸지 마십시오.

[OpenAI source revision](https://github.com/openai/math/tree/adc7f1241b42e322a6451854ab7e4b4c146bf78a)
