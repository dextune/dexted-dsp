# 数学推导与实现边界

[English](../en/MATHEMATICS.md) · [한국어](../ko/MATHEMATICS.md) · [简体中文](../zh-CN/MATHEMATICS.md) · [日本語](../ja/MATHEMATICS.md)

[Dexted DSP](../../README.zh-CN.md)

## 1. 运行库实际判定的命题

对固定实系数和正阈值，

$$H(z)=\frac{b_0+b_1z^{-1}+b_2z^{-2}}{1+a_1z^{-1}+a_2z^{-2}},\quad \gamma>0,$$

验证分母严格稳定且 `sup |H| < gamma`。实系数的共轭对称使 `[0,pi]` 足够覆盖问题。即使传递函数形式上消去不稳定极点，提供了不稳定分母的非最小实现仍会被拒绝。

精确处理的是显式部署转换后的有限二进制有理数，不是理想十进制原值、未知系数区间或处理每个样本时的所有舍入误差。

## 2. 分母稳定性

实首一二次式 `z²+a1 z+a2` 的根严格位于单位圆内，当且仅当：

$$|a_2|<1,\qquad 1+a_1+a_2>0,\qquad 1-a_1+a_2>0.$$

充分性可用 `z=(1+s)/(1-s)` 并乘以 `(1-s)²`：

$$(1-a_1+a_2)s^2+2(1-a_2)s+(1+a_1+a_2).$$

三个系数均为正，因此根在开左半平面，原根在单位圆内。必要性来自根的乘积及 `z=±1` 处的正多项式值。严格不等式排除边界根。这是经典二阶 Schur/Jury 推理，不是 OpenAI 定理。

## 3. 增益化为二次式符号

实数 `x,y,z`、`c=cos(omega)` 满足：

$$|x+ye^{-i\omega}+ze^{-2i\omega}|^2=(x-z)^2+y^2+2y(x+z)c+4xz c^2.$$

对分子和分母分别得到 `N(c)`、`D(c)`。分母稳定保证 `D(c)>0`，所以增益条件等价于：

$$Q(c)=\gamma^2D(c)-N(c)>0\quad\text{for all }c\in[-1,1].$$

连续性与紧区间保证这里的逐点严格正性等价于严格的全局上确界界限。令 `Q(c)=Ac²+Bc+C`，检查端点 `A-B+C>0`、`A+B+C>0`。只有在 `A>0` 且 `-2A<B<2A` 时需要内部顶点，条件化为：

$$4AC-B^2>0.$$

有限浮点数是整数除以二的幂；乘以**正的**公分母可保持符号并清除分数。Python 大整数与 Boost `cpp_int` 精确计算符号，避免相消舍入错误。但复杂度不是与输入位数无关的常数。

完整推导见 [biquad.md](../math/biquad.md)；实现为 `biquad.py` 与原生头文件，独立表达的参考为 `reference.py`。

## 4. 级联与未知结果

稳定节的总增益条件等价于：

$$Q(c)=\gamma^2\prod_j D_j(c)-\prod_j N_j(c)>0,\quad c\in[-1,1].$$

这保留频率补偿，而各节上确界相乘往往更保守。在同一频率相乘响应的网格方法也保留补偿，但依然只采样。

令 `t=(c+1)/2`，用 Bernstein 形式：

$$Q(2t-1)=\sum_{i=0}^n\beta_i {n\choose i}t^i(1-t)^{n-i}.$$

基函数非负且和为 1，因此所有 `beta_i>0` 足以证明该区间正性。某个系数非正本身**不能**证明失败，应在中点精确细分。非正端点值才是严格正性失败的精确证据；预算耗尽则返回 `unknown`。

成功证书包含二进制有理区间覆盖。`verify_cascade()` 重建有理多项式、绑定原输入及阈值、验证覆盖无缺口/重叠，并检查每个子区间的 Bernstein 系数为正，不盲信生成器标志。它是资源受限的充分认证程序，不是任意次数实根问题的完备求解器。详见 [cascade.md](../math/cascade.md)。

## 5. OpenAI 条件性扩展，与运行库分开

OpenAI 原文 [OAI-325] 提出矩阵值多项式的完全型不等式：

$$\|P[A]\|_2\le2\sup_{z\in W(A)}\|P(z)\|_2.$$

假设一般定理成立，独立张量轴中 `r` 个非正规轴的系数为 `2^r`，正规轴为 1。若共同基矩阵固定，每个时刻的通道多项式在同一数值域上被 `q<1` 限制，则 `||H_(T-1)...H_0|| <= 2 q^T`。

对相对状态扰动 `||e_t(x)||<=epsilon||x||`，常数变易与归纳可得：

$$\|x_T\|\le2(q+2\epsilon)^T\|x_0\|.$$

将既有完全常数 `1+sqrt(2)` [CP-2017] 替换为 2，使充分扰动半径增加约 20.71%。这并不求得真正最大半径，也不证明通用音质/画质提升。基矩阵任意变化或任意反馈图不自动满足共同基条件。

一般 OpenAI 定理仍是外部假设。精确 biquad/级联引擎和全部公开基准柱状图**没有使用它**。固定版本和通用认证器尚缺的工作见[来源说明](PROVENANCE.md)及[完整条件性研究](../math/crouzeix.md)。

## 6. 本仓库中“验证”的含义

精确算术验证规定输入模型中的符号；测试一致性验证实现之间的相容性；有理数检查器核验证书与预期输入。它们不同于证明助理形式化验证、外部安全审计、全部运行算术正确性或物理安全认证，也不暗示已完成这些工作。

[OAI-README]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/README.md
[OAI-325]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex
[OAI-DFT]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex
[CP-2017]: https://arxiv.org/abs/1702.00668
[SCIPY-FREQZ]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html
[PYPA]: https://packaging.python.org/en/latest/tutorials/packaging-projects/
