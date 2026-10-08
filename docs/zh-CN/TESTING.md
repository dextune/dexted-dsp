# 测试指南与预期结果

[English](../en/TESTING.md) · [한국어](../ko/TESTING.md) · [简体中文](../zh-CN/TESTING.md) · [日本語](../ja/TESTING.md)

[Dexted DSP](../../README.zh-CN.md)

## 1. 区分测试层次

| 层次 | 命令或数据 | 含义 |
|---|---|---|
| 核心回归 | 35 个 unittest 方法 | API、精确判定、限制、证书、CLI |
| 文档场景 | `documentation_smoke.py` 的 12 项检查 | 示例与退出码契约 |
| 原生测试 | 1 个 CTest 项，包含多个断言 | C++ 头文件与 C ABI 边界案例 |
| 原生加载器 | 256 个固定种子样本 | ctypes 集成及拒绝隐式 float32 转换 |
| 保存的完整基准 | 4,096 个滤波器，另有 2,048 行位模式 | 原算法比较与解码检查 |
| 文档修订冒烟基准 | 4 × 32 个滤波器，3 轮 | 命令路径检查，不是公开速度表 |

一个测试方法可能包含大量随机输入。35 个方法不是 35 个独立实验，也不是外部审计或 Lean 证明。原记录位于 `validation/`，本次修订单独记录于 `validation/docs_refresh/`。

## 2. 不安装基准依赖的最小测试

按照[使用指南](USER_GUIDE.md)安装后，从源码根目录执行：

```bash
python -m unittest discover -s tests -v
python tools/documentation_smoke.py
python examples/basic.py
python examples/cascade.py
```

核心预期摘要为 `Ran 35 tests ... OK`。文档脚本输出含 `"status": "passed"`、`"checks": 12` 的 JSON。基本例子打印 `certified` 与有理数复核成功；级联例子显示单节不通过而整体 `certified`。

覆盖内容包括严格等号、隐蔽共振、分母边界极点、不稳定极零抵消、显式 float32 转换、极端有限值、非法/复数输入、整数与 Fraction 随机对照、伪造通过标志、错误区间覆盖、预算耗尽和 CLI 输入保护。

核心文件内有 2,500 个固定种子对照案例、最多 1,200 次位模式尝试（跳过非有限行）、100 个补偿级联候选。这些与基准的 4,096/2,048 数据不同。

定向运行：

```bash
python -m unittest discover -s tests -p test_dexted_dsp.py -k hidden_peak -v
python -m unittest discover -s tests -p test_dexted_dsp.py -k unknown -v
python -m unittest discover -s tests -p test_dexted_dsp.py -k tampering -v
```

每条应选中一个测试并通过。负向测试的成功，正是正确拒绝或推迟一个数学断言。

## 3. 检查 CLI 的全部退出路径

| 输入或操作 | 预期状态 | 退出码 |
|---|---|---|
| `safe.json` | `certified` | 0 |
| `hidden_peak.json` | `gain_limit_not_met` | 1 |
| `budget_limited.json --max-depth 0` | `unknown` | 3 |
| 同一输入，`--max-depth 16` | `certified` | 0 |
| 非法 JSON 或不支持的类型 | `invalid_input` | 2 |
| 使用不匹配系数复核旧证书 | `verified: false` | 1 |

`python tools/documentation_smoke.py` 自动断言这些退出码。手工检查时，POSIX 在命令后立即运行 `echo $?`；PowerShell 使用 `$LASTEXITCODE`。不要把预期失败命令直接放进未处理的 `set -e` 区块。

即使增大预算后通过，当前的 `unknown` 也必须阻止部署。增益限制失败不是一般反馈不稳定证明。

## 4. 原生构建与接口检查

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
# Linux 库路径示例：
python tools/native_smoke.py "$PWD/build/libdexted_dsp.so"
```

原生输出应包含 `native tests: PASS`，CTest 为 1 项通过。加载器输出 256 个样本、零分歧、`implicit_rounding_rejected: true`。其他平台需传入实际绝对库路径。原生基准是另一条构建路径，不替代接口检查。

请保留编译警告。原 GCC/Boost 内联警告和历史 sanitizer 记录见[基准报告](BENCHMARKS.md)。CTest 通过不等于证明所有警告无害。

## 5. 不计时的存档审计

```bash
python tools/audit_benchmark.py
# 需要已安装项目和 NumPy：
python tools/audit_benchmark.py --recheck-fixtures
```

前者核对 NPZ 哈希、12 个被测源码哈希、轮次数、中位数、配对比率和计数一致性；后者使用 `allow_pickle=False` 读取保存数据，以整数与 Fraction 重新计算**全部 4,096 个判定**并核对各组通过数。

预期字段包括 `status: passed`、`fixture_rows: 4096`；启用复核后有 `exact_recheck_rows: 4096`。这并非重新测量历史原生时间或重新计算所有数值基线的历史错误数量，只验证存档一致性与当前精确判定。

被测源码变化后审计失败是有用的保护。复核旧运行请恢复原代码；测试新算法请创建新基准，不能修改旧哈希来伪装通过。

## 6. 重新测量与画图

```bash
python -m pip install '.[bench]'
python benchmarks/run.py --n 32 --trials 3 --out validation/my-smoke
python benchmarks/run.py --n 1024 --trials 9 --seed 20261007 --out validation/my-run
python benchmarks/plot.py --results validation/my-run/benchmark.json --out validation/my-run/figures
```

复现记录配置时，将 OpenBLAS/OMP 设为单线程。原生测量需要支持的编译器和 Boost；Windows 使用 WSL。分布、计时排除项及版本详见 [BENCHMARKS.md](BENCHMARKS.md)。

成功复现意味着精确参考无分歧、文件有效、环境如实记录，**不要求结果更快**。不要丢弃慢的运行直到出现想要的标题；保留前后结果并使用相同系数值和源码版本。

只重绘原图：

```bash
python benchmarks/plot.py --results benchmarks/results/benchmark.json --out validation/redrawn-figures
```

## 7. 测试发布包而非开发源码

在根目录创建独立环境：

```bash
python -m pip install build
python -m build
python -m venv .wheel-test
# POSIX:
.wheel-test/bin/python -m pip install --no-deps dist/dexted_dsp-0.1.0-py3-none-any.whl
.wheel-test/bin/python -m unittest discover -s tests -v
.wheel-test/bin/python tools/documentation_smoke.py
# Windows 改用 .wheel-test\Scripts\python.exe
```

不要设置 `PYTHONPATH=src`，否则源码可能掩盖 wheel 缺失的文件。重建时安装开发构建工具并运行 `python -m build`、`python -m twine check dist/*`。构建和检查不等于发布。README 元数据变化后应重新生成 wheel。

## 8. 文档与发布前检查

```bash
python tools/check_links.py
python tools/check_documentation.py
python tools/audit_benchmark.py
```

检查本地链接、四语必需文档、共同基准身份、必需表格和被测源码一致性；并不验证全部翻译语义或数学证明，也不代表 GitHub 托管工作流或外部审计。

公开前阅读 [validation/docs_refresh/summary.json](../../validation/docs_refresh/summary.json)，保留日志、确认 README 对应预期数据、重建元数据，再按[发布流程](RELEASING.md)操作。ZIP 校验值及 `MANIFEST.sha256` 识别交付文件；哈希不证明数学正确性。

[OAI-README]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/README.md
[OAI-325]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex
[OAI-DFT]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex
[CP-2017]: https://arxiv.org/abs/1702.00668
[SCIPY-FREQZ]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html
[PYPA]: https://packaging.python.org/en/latest/tutorials/packaging-projects/
