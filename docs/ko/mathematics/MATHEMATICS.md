# 수학적 유도와 구현의 적용 범위

[English](../../en/mathematics/MATHEMATICS.md) · [한국어](MATHEMATICS.md) · [简体中文](../../zh-CN/mathematics/MATHEMATICS.md) · [日本語](../../ja/mathematics/MATHEMATICS.md)

[Dexted DSP](../README.md)

## 1. 실행 엔진이 판정하는 명제

고정 실수 계수와 양의 제한값에 대해

$$H(z)=\frac{b_0+b_1z^{-1}+b_2z^{-2}}{1+a_1z^{-1}+a_2z^{-2}},\quad \gamma>0$$

의 분모가 엄격히 안정하고 `sup |H| < gamma`인지 판정합니다. 실수 계수의 공액 대칭 때문에 `[0,pi]`만 다루면 됩니다. 전달함수에서 불안정한 분모가 약분되는 비최소 표현도 거절합니다.

정확하게 취급하는 값은 명시한 배포 변환 후의 유한 이진 유리수입니다. 의도한 십진수 원값·알 수 없는 계수 오차 구간·샘플 처리 중 모든 반올림에 대한 증명이 아닙니다.

## 2. 분모 안정성

실수 일계수 이차식 `z²+a1 z+a2`의 근이 단위원 내부에 엄격히 포함될 필요충분조건은 다음과 같습니다.

$$|a_2|<1,\qquad 1+a_1+a_2>0,\qquad 1-a_1+a_2>0.$$

충분성은 `z=(1+s)/(1-s)`를 대입하고 `(1-s)²`를 곱해 확인할 수 있습니다.

$$(1-a_1+a_2)s^2+2(1-a_2)s+(1+a_1+a_2).$$

세 계수가 모두 양수이므로 두 근이 열린 좌반평면에 있고 원래 근은 단위원 내부에 있습니다. 필요성은 근의 곱과 `z=±1`에서 양의 다항식 값을 이용합니다. 엄격한 부등호는 경계 근을 제외합니다. 이는 고전적인 2차 Schur/Jury 논리이며 OpenAI 정리가 아닙니다.

## 3. 주파수 이득을 이차식 부호 검사로 바꾸기

실수 `x,y,z`, `c=cos(omega)`에 대해 전개하면 다음을 얻습니다.

$$|x+ye^{-i\omega}+ze^{-2i\omega}|^2=(x-z)^2+y^2+2y(x+z)c+4xz c^2.$$

분자와 분모에 적용한 다항식을 각각 `N(c)`, `D(c)`라고 하겠습니다. 안정한 분모이면 `D(c)>0`이므로 이득 조건은 다음과 동치입니다.

$$Q(c)=\gamma^2D(c)-N(c)>0\quad\text{for all }c\in[-1,1].$$

연속성과 닫힌 유계 구간의 성질 때문에 이 경우 점별 엄격한 양수성과 전역 최대 이득의 엄격한 제한이 동치입니다. `Q(c)=Ac²+Bc+C`라 두고 양 끝점의 `A-B+C>0`, `A+B+C>0`을 검사합니다. `A>0`, `-2A<B<2A`인 경우에만 내부 꼭짓점을 추가 검사하며 다음 부호로 충분합니다.

$$4AC-B^2>0.$$

유한 이진 부동소수점 값은 정수를 2의 거듭제곱으로 나눈 수입니다. **양의** 공통 분모를 곱해 부호를 보존하며 정수식으로 변환합니다. Python 정수와 Boost `cpp_int`는 상쇄 반올림 오차 없이 이 부호를 계산합니다. 입력 비트 길이와 무관한 상수 시간이라는 뜻은 아닙니다.

전체 유도와 경계 조건은 [biquad.md](../../research/proofs/biquad.md), 구현은 `biquad.py`와 C++ 헤더, 별도 참조는 `reference.py`에 있습니다.

## 4. 직렬 연결과 UNKNOWN이 필요한 이유

안정한 필터들의 체인은 다음 다항식의 양수성과 동치입니다.

$$Q(c)=\gamma^2\prod_j D_j(c)-\prod_j N_j(c)>0,\quad c\in[-1,1].$$

주파수별 보상을 유지하며 개별 최대값 곱보다 덜 보수적일 수 있습니다. 같은 주파수에서 응답을 곱하는 격자 방식도 보상을 유지하지만 여전히 구간을 샘플링할 뿐입니다.

`t=(c+1)/2`로 변환하여 Bernstein 기저로 표현합니다.

$$Q(2t-1)=\sum_{i=0}^n\beta_i {n\choose i}t^i(1-t)^{n-i}.$$

기저 함수들은 음이 아니고 합이 1입니다. 모든 `beta_i>0`이면 해당 구간에서 양수입니다. 반면 0 이하인 계수가 하나 있다는 것만으로 실패를 증명하지는 못하므로 중간점에서 정확히 분할합니다. 끝점 값이 0 이하이면 엄격한 양수성의 실패 근거가 됩니다. 더 분할할 예산이 없으면 `unknown`을 반환합니다.

성공 인증서는 이진 유리수 구간 덮개입니다. `verify_cascade()`는 유리수 다항식을 재구성하고 원본 입력·제한값, 틈·중복 없는 덮개, 각 구간의 Bernstein 계수 양수성을 확인합니다. 생성기의 합격 플래그를 그대로 믿지 않습니다. 자원 제한이 있는 충분조건 절차이며 임의 차수의 완전한 실근 판정기가 아닙니다. 상세는 [cascade.md](../../research/proofs/cascade.md)입니다.

## 5. OpenAI와의 조건부 연결: 실행 엔진과 구분

OpenAI 원문 [OAI-325]은 행렬 계수에 대한 완전형 부등식을 제시합니다.

$$\|P[A]\|_2\le2\sup_{z\in W(A)}\|P(z)\|_2.$$

이 일반 정리를 가정하면 독립 텐서 축 중 비정규 축 `r`개에 `2^r`을 적용하고 정규 축에는 1을 사용합니다. 공통 고정 기저에서 각 시각의 채널 다항식이 동일한 수치범위 위에서 `q<1`로 제한되면 `||H_(T-1)...H_0|| <= 2 q^T`를 얻습니다.

상대 상태 교란 `||e_t(x)||<=epsilon||x||`에 대해서는 상수변화법과 귀납법으로 다음을 얻습니다.

$$\|x_T\|\le2(q+2\epsilon)^T\|x_0\|.$$

기존 완전형 상수 `1+sqrt(2)` [CP-2017]를 2로 바꾸면 교란 반경의 충분조건이 약 20.71% 넓어집니다. 실제 최대 반경을 찾은 것이 아니며 일반적인 음질·화질 우위를 증명하지 않습니다. 기저가 임의로 바뀌거나 임의 피드백 그래프인 경우 공통 기저 가정을 자동 충족하지 않습니다.

OpenAI의 일반 정리는 여기서 외부 가정입니다. 정확 biquad·체인 실행 코드와 공개된 모든 벤치마크 막대는 **이를 사용하지 않습니다.** 버전과 구현되지 않은 일반 인증기의 과제는 [출처](../development/PROVENANCE.md) 및 [전체 조건부 문서](../../research/proofs/crouzeix.md)에 적었습니다.

## 6. 이 저장소에서 “검증”의 의미

정확 연산은 명시한 유한 입력 모델의 부호를 확인합니다. 테스트 일치는 구현 사이의 일관성을 확인합니다. 유리수 재검사기는 인증서를 예상 입력과 대조합니다. 증명 보조기 형식 검증, 외부 보안 감사, 모든 실행 산술의 정확성, 물리적 안전 인증과는 서로 다르며 그러한 결과를 암시하지 않습니다.

[OAI-README]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/README.md
[OAI-325]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex
[OAI-DFT]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex
[CP-2017]: https://arxiv.org/abs/1702.00668
[SCIPY-FREQZ]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html
[PYPA]: https://packaging.python.org/en/latest/tutorials/packaging-projects/
