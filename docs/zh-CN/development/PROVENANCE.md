# 研究来源、过程与 OpenAI 归属说明

[English](../../en/development/PROVENANCE.md) · [한국어](../../ko/development/PROVENANCE.md) · [简体中文](PROVENANCE.md) · [日本語](../../ja/development/PROVENANCE.md)

[Dexted DSP](../README.md)

## 1. 区分三种“参考 OpenAI”

**研究资料：**从 [`openai/math` 手稿集][OAI-README]寻找信号处理相关方向。**条件性定理：**在独立研究说明中，采用某篇 Crouzeix 手稿的结论作为假设。**AI 辅助工程：**通过交互式研究和编程形成当前仓库。三者不同；它们并不意味着运行库来自 OpenAI、受到 OpenAI 审计，或测得的优化属于新的 OpenAI 数学定理。

上游明确说明各手稿验证程度不同。手稿出现在该仓库中，并不足以证明下游 DSP 软件已经形式化验证 [OAI-README]。

## 2. 固定版本与具体位置

| ID | 原文和位置 | 用途 |
|---|---|---|
| OAI-README | 提交 `adc7f1241b42e322a6451854ab7e4b4c146bf78a` 中的 `README.md` | 资料来源和验证状态说明 |
| OAI-325 | *A direct proof of the complete Crouzeix inequality*，2026-09-26；`build/main.tex` §1、标签 `thm:main`，以及 `W(A)`、`P[A]` 定义 | 条件性采用矩阵值多项式的完全常数 2 不等式 |
| OAI-DFT | *An explicit power saving for the exact discrete Fourier transform*，2026-09-25；`build/sections/introduction.tex` 计算模型与 `cor:decimal` 后的限制 | 范围筛选，不用于浮点 FFT 实现或性能测量 |

完整固定链接和 Git blob 哈希位于 [sources.json](../../research/provenance/sources.json)。本次查看的是 LaTeX 定理源码，没有运行 Lean 内核。日期指所引用手稿，并非宣称掌握之后的最新修订。

[OpenAI 主定理原文][OAI-325] · [OpenAI DFT 模型与局限][OAI-DFT]

采用的 Crouzeix 假设为：

$$\|P[A]\|_2\le 2\max_{z\in W(A)}\|P(z)\|_2,\qquad P[A]=\sum_k A^k\otimes B_k.$$

这里的**矩阵值/完全型**性质很重要，因为通道系数矩阵可以不交换。比较依据是 Crouzeix–Palencia 2017 年的完全常数 `1+sqrt(2)` [CP-2017]。这里没有独立复核 OpenAI 的一般常数 2 原证明。

## 3. 代码究竟依赖什么？

| 组件 | 数学依据 | 状态 |
|---|---|---|
| `src/dexted_dsp/biquad.py`、`cpp/include/dexted_dsp/biquad.hpp` | 基本 Schur/Jury 条件、二次多项式正性、精确二进制有理数 | 可执行，与 OpenAI 新定理无关 |
| `src/dexted_dsp/cascade.py` | 模平方多项式乘积、Bernstein 正性与细分 | Python 可执行；有资源限制的充分认证程序 |
| `reference.py`、`verify.py` | 独立表达的有理数公式与区间覆盖检查 | 复核，不是外部机构认证 |
| `benchmarks/kernels.cpp` | 整数判定、采样响应、float64 代数基线 | 被测代码，没有 Crouzeix 依赖 |
| [条件性研究说明](../../research/proofs/crouzeix.md) | 对一般基矩阵假设 OAI-325 成立 | 仅文档，无生产 API |

经典方法不是本项目发明。工程贡献在于：明确部署值语义、实现精确整数判定、提供可检查证书和独立表达的复核器、建立接口及可复现比较。

## 4. 开发步骤与证据

下表描述可检查的工作产物，不宣称没有记录的“无限优化”次数。

| 阶段 | 决策或实现 | 本包中的证据 |
|---|---|---|
| 范围筛选 | 探索手稿与信号处理的关联，区分渐近理论与可部署算法 | 固定来源清单、本说明 |
| 假设隔离 | 将一般 Crouzeix 推论保留为条件性文档，不放入生产引擎 | `docs/research/proofs/crouzeix.md`、代码依赖 |
| 固定问题契约 | 固定实系数二阶节、显式部署精度、严格增益上限 | `model.py`、数学文档 |
| 精确实现 | 将二进制有理数化为整数，检查稳定性、端点和必要的内部最小值 | `biquad.py`、原生头文件 |
| 扩展级联 | 保留频率补偿，对整条链的多项式证明正性 | `cascade.py`、`verify.py` |
| 独立表达对照 | 与 `Fraction` 比较，绑定原始输入，拒绝篡改与未知结论 | `tests/test_dexted_dsp.py` |
| 公平性审查 | 保留快速 float64 基线、预热网格、允许提前退出、检查输入 | `run.py`、`kernels.cpp`、`protocol.json` |
| 保留中间记录 | 不只保留快的结果，保存审查前后和输入校验前后的测量 | `validation/runs/v0.1.0/benchmark_before_review*`、`benchmark_before_input_validation*` |
| 打包 | Python/C++/CLI、安装验证、实际本地日志 | 原 `validation/runs/v0.1.0/summary.json`、构建日志 |
| 文档修订 | 四语文档、来源追踪、已保存测量审计、示例重跑、小规模冒烟测试 | `validation/docs_refresh/`；被测源码哈希未变 |

历史压缩包哈希见 [sources.json](../../research/provenance/sources.json)。前面对话中的其他性能数字、媒体实验或旧基准修订**没有作为当前测量结果重新引用**。当前 README 数字仅来自 `benchmarks/results/benchmark.json`。

## 5. 条件性推论的意义与限制

假设 OAI-325 成立，对独立张量轴中的 `r` 个非正规轴，可得系数 `2^r`；正规轴的系数为 1。对于共同固定基矩阵、仅通道多项式随时间变化的系统，乘积界是 `2 q^T`，而不是 `(2q)^T`。加入相对状态扰动 `epsilon` 后，可得到充分衰减条件 `q+2 epsilon<1`。

相对于同一论证采用 `1+sqrt(2)`，可认证的充分扰动半径增加 `(1+sqrt(2))/2-1`，约 **20.71%**。这是两个充分条件的代数比较，不是实测音质、画质、真正最大鲁棒性，或任意时变系统的通用认证。详细假设和证明见[研究说明](../../research/proofs/crouzeix.md)。

## 6. 署名、复用和验证边界

包内没有上游 OpenAI/ADAC 实现、手稿源码、第三方媒体、权重或私密凭据。链接表示引用，不表示背书。此前实现的 MIT 声明保留于 [LICENSE](../../../LICENSE) 和 [NOTICE](../../legal/NOTICE.md)。Boost 是外部原生构建依赖，NumPy/SciPy/Matplotlib 是可选基准工具。

没有独立审计一般 Crouzeix 原证明、所有编译器优化的正确性或物理设备行为。即使删除条件性研究说明，精确 biquad/级联引擎及其基准结果的数学依据也不会改变。

[OAI-README]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/README.md
[OAI-325]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex
[OAI-DFT]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex
[CP-2017]: https://arxiv.org/abs/1702.00668
[SCIPY-FREQZ]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html
[PYPA]: https://packaging.python.org/en/latest/tutorials/packaging-projects/
