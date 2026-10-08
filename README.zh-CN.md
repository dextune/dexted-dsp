<div align="center">

# Dexted DSP

**Exact filter checks. Inspectable evidence.**

Offline verification for fixed digital filters · Python & C++20

[![CI](https://github.com/dextune/dexted-dsp/actions/workflows/ci.yml/badge.svg)](https://github.com/dextune/dexted-dsp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![C++20](https://img.shields.io/badge/C%2B%2B-20-blue.svg)](CMakeLists.txt)
[![Research alpha](https://img.shields.io/badge/status-research%20alpha-orange.svg)](CHANGELOG.md)

[English](README.md) · [한국어](README.ko.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md)

[Documentation](docs/README.md) · [Contributing](CONTRIBUTING.md)

</div>

---

**验证固定数字滤波器在整个频率区间内是否满足增益上限，而不是仅靠若干采样点寻找峰值。**

Python · C++20 · 命令行 · 精确整数运算 · 可复核证书 · 可复现实验

**v0.1.0 · 研究型 Alpha。** 这是由 [dextune/dexted-dsp](https://github.com/dextune/dexted-dsp) 维护的 AI 辅助独立项目，不是 OpenAI 产品、官方集成或经过外部审计的安全认证工具。请从本仓库源码安装；不表示已在 PyPI 发布。

## 当前可用的功能

运行库支持**固定实系数 biquad（二阶滤波器）**，Python 版本还支持它们的**串联级联**。验证内容是各分母的严格稳定性，以及指定的严格全频段增益上限。请先把系数转换为实际部署精度，再离线验证。它不会播放音频、自动优化滤波器、分析任意神经网络或证明物理设备安全。

对视频中每个像素独立使用同一个固定时间滤波器时，可以采用这个模型；一般的视频修复网络并不自动满足这些条件。精确整数运算需要动态内存，因此不要在实时音频回调中运行验证器。

## 安装与快速使用

请克隆仓库后从源码安装。仓库处于私有状态时需要 GitHub 访问权限。

```bash
git clone https://github.com/dextune/dexted-dsp.git
cd dexted-dsp
python -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows PowerShell 请改用：.venv\Scripts\Activate.ps1
python -m pip install .
python examples/basic.py
python tools/documentation_smoke.py
```

需要 Python 3.10 或更新版本，**核心运行库**没有第三方运行时依赖。源码安装可能下载构建工具。离线使用前请按[发布指南](docs/zh-CN/RELEASING.md)构建 wheel；`dist/` 不纳入 Git。

```python
from dexted_dsp import Biquad, certify, verify_biquad

f = Biquad.from_coefficients(
    [0.25, 0.0, 0.0, -0.5, 0.0],  # b0, b1, b2, a1, a2；a0 = 1
    precision="float32",
)
report = certify(f, max_gain=1.0)
assert report.certified
assert verify_biquad(report.as_dict(), f, max_gain=1.0)
print(report.status)  # certified
```

`max_gain` 是输入的**验证阈值**，不是计算得到的最大增益。条件是 `<`，不是 `<=`。修改系数或阈值后，原证书的输入绑定将不再匹配。

```bash
python -m dexted_dsp check examples/safe.json --output certificate.json
python -m dexted_dsp verify examples/safe.json certificate.json
python -m dexted_dsp check examples/hidden_peak.json
# 最后一条命令预期返回退出码 1，是正确拒绝反例的负向测试。
```

退出码：`0` 认证或复核成功，`1` 条件不满足或证书无效，`2` 输入错误，`3` 资源预算不足而**无法判定**。部署检查只能接受 0。安装后的 `dexted-dsp` 命令具有同样的功能。

## 具体参考了 OpenAI 的什么内容？

研究起点是 [`openai/math` 数学手稿集][OAI-README]。本项目把参考版本固定为提交 **`adc7f1241b42e322a6451854ab7e4b4c146bf78a`**，而不是默默跟随主分支更新。上游 README 明确指出，不同手稿的验证程度并不相同。

| 来源或数学方法 | 在本项目中的用途 | 用于本基准测试吗？ |
|---|---|---|
| OpenAI 结果族 325，*A direct proof of the complete Crouzeix inequality*，§1 主定理 [OAI-325] | 矩阵多项式误差及受限时变系统的条件性研究扩展 | **没有** |
| OpenAI 精确 DFT 论文的引言、计算模型与限制 [OAI-DFT] | 研究范围筛选；不能将渐近精确算术结果当成实际浮点 FFT 加速 | **没有** |
| 经典二阶 Schur/Jury 条件与 `cos(omega)` 二次多项式 | 可执行的精确 biquad 判定 | **有** |
| 经典 Bernstein 正性及精确细分 | Python 级联证书与有理数复核 | 用于级联示例，**不属于 C++ 延迟柱状图** |

**测得的加速不是由 Crouzeix 定理带来的。** 运行库没有复制 OpenAI 的证明代码或 DSP 源码。这里没有独立验证一般形式的常数 2 原定理，也没有提供 `crouzeix_certify()` API。OpenAI 生成原手稿的过程，与本项目的 AI 辅助工程过程是两回事。

开发顺序为：筛选数学候选 → 区分理论假设与可执行方法 → 实现精确判定 → 用独立表达的有理数运算对照 → 移植 C++ → 保留强数值基线比较 → 保存失败与修改记录 → 打包和文档化。阶段和证据对应关系见[研究来源与过程](docs/zh-CN/PROVENANCE.md)。

## 基准测试测量了什么？

以下使用**原 v0.1.0 保存的测量值**，不是在翻译时重新挑选更有利的数据。本次文档修订复核了哈希与精确判定；另行执行的小规模冒烟测试没有替换原始数据。

| 配置项 | 记录值 |
|---|---|
| 输入 | 4 组人工合成数据 × 1,024 个 binary32 滤波器，共 **4,096 个** |
| 阈值与随机性 | binary64 `max_gain=0.9999`；输入种子 `20261007`；方法顺序种子 `932851` |
| 计时 | 9 轮；每轮计时包含 4 次原生批处理；`perf_counter_ns` |
| C++ 编译 | GCC 14.2.0；`-O3 -std=c++20 -ffp-contract=off`；禁用 fast-math |
| 主机 | 共享 Linux x86-64 主机报告 AMD EPYC 9V74、5 个可见逻辑 CPU；未绑定 CPU |
| Python 环境 | Python 3.13.5、NumPy 2.3.5、SciPy 1.17.0；图表依赖记录为 Matplotlib 3.10.8 |

原生时间单位为 **µs/滤波器，9 轮中位数**。四种方法都检查输入有效性与分母。网格方法使用已预热的三角函数缓存，并允许发现违规后提前退出；缓存构造时间不计入。

| 数据组 | 精确整数判定 | 1,024 点网格 | 16,384 点网格 | Float64 代数判定 | 网格 1,024 / 整数¹ |
| --- | --- | --- | --- | --- | --- |
| 普通滤波器 | 0.564106 | 1.686392 | 27.877729 | 0.011137 | 2.989× |
| 高 Q 值压力测试 | 0.599275 | 2.161358 | 33.816509 | 0.012064 | 3.607× |
| 接近增益阈值 | 0.377707 | 0.932293 | 16.152820 | 0.011086 | 2.468× |
| 不稳定分母 | 0.008509 | 0.006741 | 0.007093 | 0.006717 | 0.792× |

¹ 最后一列为**两个中位数之比**，并非每轮配对比值的中位数。两种统计量、观测最小/最大值及计时边界均列于[基准测试详情](docs/zh-CN/BENCHMARKS.md)。

![四种 C++ 方法在四组数据上的验证延迟](benchmarks/figures/native_latency.svg)

整数方法在前三组数据上快于 1,024 点网格，但在立即拒绝不稳定分母时更慢。**Float64 代数方法快得多。** 即使其判定会受到舍入影响，我们也保留了这一强基线。这是部署前验证延迟，不是音频处理吞吐量或音质改善。

### 正确性与 Python 调用成本是不同的问题

高 Q 数据中，有理数参考判定通过 539 个、拒绝 485 个。下表是案例数量，不是产品总体故障率估计。

| 方法 | 错误接受 / 485 个参考不通过样本 | 错误拒绝 / 539 个参考通过样本 |
| --- | --- | --- |
| 精确整数判定 | 0 | 0 |
| 1,024 点网格 | 356 | 0 |
| 16,384 点网格 | 213 | 0 |
| Float64 代数判定 | 2 | 5 |

其他三组数据的四种原生方法均记录为零分歧。错误接受表示将**不满足数学条件的输入**判为通过，并不自动证明任意反馈网络必然发散。

![高 Q 数据相对有理数参考判定的错误数量](benchmarks/figures/high_q_correctness.svg)

![包含逐次调用成本的 Python API 比较](benchmarks/figures/python_latency.svg)

Python 图使用 128 个高 Q 滤波器，并直接调用已安装 SciPy 的 `signal.freqz`。该函数计算指定频率上的响应，并非宣称提供精确证书的接口 [SCIPY-FREQZ]。不要把 Python API 延迟与原生批量内核延迟混为一谈。

![采样点之间存在的解析已知窄峰](benchmarks/figures/hidden_peak.svg)

窄峰示例在 `omega=pi/2` 的增益精确等于 2。图形只是展示这一代数事实；密集绘制的曲线本身不是证明。

### 原始证据与复现

[JSON 与每轮时间](benchmarks/results/benchmark.json) · [CSV 摘要](benchmarks/results/summary.csv) · [系数数组](tools/restore_fixtures.py) · [实验协议与源码哈希](benchmarks/results/protocol.json) · [环境](benchmarks/results/environment.json) · [原运行日志](validation/benchmark_run.log)

```bash
python -m pip install '.[bench]'
python -m pip install -r requirements-bench-tested.txt
python tools/restore_fixtures.py
python tools/audit_benchmark.py --recheck-fixtures
# 小规模命令路径检查，不是公开基准数据：
python benchmarks/run.py --n 32 --trials 3 --out validation/my-smoke
# 单独保存新测量，不覆盖原始结果：
python benchmarks/run.py --n 1024 --trials 9 --seed 20261007 --out validation/my-run
python benchmarks/plot.py --results validation/my-run/benchmark.json --out validation/my-run/figures
```

原生基准脚本面向 Linux/macOS 的 GNU/Clang 工具链；Windows 请使用 WSL。图内保留共用英文标签，各语言指南提供对应说明与图例解读。

## 测试与集成

```bash
python -m unittest discover -s tests -v
python tools/documentation_smoke.py
python examples/cascade.py
# 可选 C++：需要 C++20、CMake >=3.20、Boost >=1.74 头文件
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
```

核心套件包含 **35 个 unittest 方法**，其中部分方法内部运行随机案例。文档冒烟脚本另外检查 **12 个场景**。历史基准保存了 4,096 个部署系数样本及另外 2,048 行位模式测试。这些是不同测试层次，不代表外部独立审计次数。[测试指南](docs/zh-CN/TESTING.md)给出了预期失败、预算耗尽、wheel 安装检查和排错步骤。

## 文档与限制

| 文档 | 内容 |
|---|---|
| [使用指南](docs/zh-CN/USER_GUIDE.md) | 安装、输入语义、Python/SOS/CLI、预算、C++、CI、排错 |
| [测试指南](docs/zh-CN/TESTING.md) | 预期输出、通过/拒绝/未知、回归检查与复现 |
| [基准测试报告](docs/zh-CN/BENCHMARKS.md) | 数据分布、比较方法、计时边界、原始字段、局限 |
| [研究来源与过程](docs/zh-CN/PROVENANCE.md) | OpenAI 引用位置、依赖边界、开发证据 |
| [数学说明](docs/zh-CN/MATHEMATICS.md) | 推导、证书含义、条件性扩展 |
| [API 契约](docs/API.md) / [发布指南](docs/zh-CN/RELEASING.md) | 底层接口与仓库/包发布流程 |

证书只涉及给定部署系数的理想固定线性系统。它不证明所有运行时舍入、溢出、极限环、任意调制、反馈拓扑、AI 行为、听力保护，或 PSNR/STOI/PESQ 提升。`unknown` 必须阻止部署。JSON 证书不是数字签名，也不是用于恶意输入的安全沙箱。

[MIT 许可证](LICENSE) · [声明](NOTICE.md) · [安全](SECURITY.md) · [问题反馈](https://github.com/dextune/dexted-dsp/issues)。不声称发明新数学、获得外部独立审计或物理设备安全认证。CI 徽章动态显示 GitHub Actions 状态；[本地验证记录](validation/rebrand/)是另一类证据。

[OAI-README]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/README.md
[OAI-325]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex
[OAI-DFT]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex
[CP-2017]: https://arxiv.org/abs/1702.00668
[SCIPY-FREQZ]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html
[PYPA]: https://packaging.python.org/en/latest/tutorials/packaging-projects/

**测量来源。** 表中数据以原研究名称 **CertifiedDSP** 记录。Dexted DSP 更名只修改名称、命名空间、CLI 和证书模式，不改变代数判定式。保留原始测量与当时的源码。[迁移与复现](docs/REBRANDING.md) · [源码映射](benchmarks/results/rebrand-map.json)。

**源码检出数据：** NPZ 不存入 Git，而是按需重建。安装锁定的基准依赖后运行 `python tools/restore_fixtures.py`。重建必须匹配原始 SHA-256，不会替换测量值。

<!-- benchmark-sha256: 0332cbc6a22ebf2da482a043b3f206ae175bcab5d71f640417c96c46c7ac99a0 -->
