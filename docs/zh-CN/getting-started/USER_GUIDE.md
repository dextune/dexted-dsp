# 使用指南：安装、API 与集成

[English](../../en/getting-started/USER_GUIDE.md) · [한국어](../../ko/getting-started/USER_GUIDE.md) · [简体中文](USER_GUIDE.md) · [日本語](../../ja/getting-started/USER_GUIDE.md)

[Dexted DSP](../README.md)

## 1. 先确认模型适用

本库处理**固定、实系数、已归一化的 biquad**，或 1–32 个这样的节组成的串联链。验证的是给定分母的严格稳定性和理想线性频率响应上限，不会自动分析 FLAMO/PyTorch 图、解析 FAUST/VST/ONNX 或修改系数。

必须导出包括归一化及 float32 转换在内的**最终部署系数**。在播放或部署之前离线验证。本指南不会播放声音或控制硬件。

## 2. 安装选项

所有命令均从解压后的 `dexted-dsp/` 根目录执行，而不是 `docs/zh-CN/`。

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
python -m dexted_dsp --version
```

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install .
python -m dexted_dsp --version
```

预期版本为 `0.1.0`。也可以不激活环境，直接调用 POSIX 的 `.venv/bin/python` 或 Windows 的 `.venv\Scripts\python.exe`，从而无需修改 PowerShell 执行策略。声明支持 Python >=3.10；各托管 OS/版本的 CI 仍需公开后实际运行。

### 离线 wheel / 开发安装

```bash
python -m pip install build
python -m build
python -m pip install --no-deps dist/dexted_dsp-0.1.0-py3-none-any.whl
# 开发修改的另一种方式，可能需要下载构建工具：
python -m pip install -e .
```

每个环境选择**一种**安装方式。不要假定索引上的 `pip install dexted-dsp` 对应这个未发布项目。wheel 只有 Python 运行库，没有编译的原生库。源码、文档、图表、测试在 ZIP/sdist 中，运行以下示例时请保留源码树。打包结构参考 PyPA [PYPA]。

## 3. 输入语义与精度

$$H(z)=\frac{b_0+b_1z^{-1}+b_2z^{-2}}{1+a_1z^{-1}+a_2z^{-2}}.$$

| 入口 | 系数顺序 |
|---|---|
| `Biquad.from_coefficients()` | `[b0,b1,b2,a1,a2]`，五个值 |
| `Biquad(b=..., a=...)` | `(b0,b1,b2)` 与 `(1,a1,a2)` |
| `from_sos()` | SciPy 的 `[b0,b1,b2,a0,a1,a2]`，必须 `a0==1` |
| CLI `type="cascade"` | 每个 `sections` 行是**五个值**，不是 SciPy 的六个 |

库不会自动归一化 `a0`。请在真实部署流水线中归一化和舍入，然后传入最终值。其他工具的分母符号约定可能不同，必须先确认。

Python/JSON 十进制数首先被解析为有限 binary64；`precision="float32"` 再显式舍入到 binary32，`float64` 保留已解析值。之后精确验证的是**这些二进制有理数表示值**，不是解析前的理想十进制数。即使系数是 float32，阈值仍是 binary64。NaN、无穷、复数、布尔、字符串及非正阈值均被拒绝。float32 溢出是错误，极小值舍入为零则属于明确请求的转换。

## 4. 单滤波器 API 与结果

```python
from dexted_dsp import Biquad, certify, verify_biquad
f = Biquad.from_coefficients([0.25, 0, 0, -0.5, 0], precision="float32")
report = certify(f, max_gain=1.0)
print(report.status)
print(report.denominator_stable)
print(verify_biquad(report.as_dict(), f, max_gain=1.0))
```

预期输出：

```text
certified
True
True
```

| 状态 | 含义 |
|---|---|
| `certified` | 两个严格条件都成立 |
| `denominator_not_schur` | 分母不满足严格单位圆内稳定性 |
| `gain_limit_not_met` | 分母稳定，但严格增益上限不成立 |

`max_gain_limit` 保存**请求的阈值**。接口不返回真实最大增益、峰值频率、dB 余量或感知评分。常数增益恰为 1 时，`certify(Biquad.from_coefficients([1,0,0,0,0]),1.0)` 会拒绝，因为不满足 `<1`。

应用中应明确处理错误：

```python
from dexted_dsp import Biquad, certify

def accept_exported_filter(values):
    try:
        f = Biquad.from_coefficients(values, precision="float32")
        result = certify(f, max_gain=1.0)
    except (ValueError, TypeError):
        return False
    return result.certified
```

这是所述滤波器模型的部署检查，不是周围反馈系统的完整证明。

## 5. 级联与 SciPy 输入

```python
from dexted_dsp import from_sos, certify_cascade, verify_cascade
sections = from_sos([
    [1.0, -0.75, 0.0, 1.0, -0.125, 0.0],
    [0.75, -0.09375, 0.0, 1.0, -0.75, 0.0],
], precision="float32")
proof = certify_cascade(sections, max_gain=1.0)
assert proof["certified"]
assert verify_cascade(proof, sections, max_gain=1.0)
```

该例总传递函数精确为 0.75。联合验证保留频率补偿，单独最大值相乘可能丢失补偿。`from_sos` 不需要导入 SciPy；可选的 `examples/scipy_sos.py` 用 SciPy 设计 Butterworth SOS，并在转换为部署精度后按阈值 1.01 检查。

级联状态为 `certified`、`denominator_not_schur`、`condition_failed`、`unknown`。`condition_failed` 表示找到严格增益差多项式的精确非正值；`unknown` 只是预算不足，既不表示稳定，也不表示不稳定或可以部署。即使似乎可以代数消去极点，不稳定的单节分母仍被拒绝。

默认 `max_depth=48`、`max_nodes=20000`；公开上限为深度 128、100,000 个节点、32 个节。增加预算可能有帮助，但接近零的高次多项式不保证快速完成。

## 6. JSON 命令行与证书

输入示例 [safe.json](../../../examples/safe.json)：

```json
{
  "type": "biquad",
  "precision": "float32",
  "max_gain": 1.0,
  "coefficients": [0.25, 0, 0, -0.5, 0]
}
```

```bash
python -m dexted_dsp check examples/safe.json --output certificate.json
python -m dexted_dsp verify examples/safe.json certificate.json
```

检查输出完整 JSON，复核输出 `{"verified": true}`。`--output` 不能覆盖输入路径；请事先创建输出目录。JSON 最大 1 MiB，文件不会被执行或发送到服务。

下面的预期失败命令应与遇非零状态就停止的 shell 脚本分开运行：

```bash
python -m dexted_dsp check examples/hidden_peak.json
# 预期 gain_limit_not_met，退出码 1。
python -m dexted_dsp check examples/budget_limited.json --max-depth 0
# 预期 unknown，退出码 3。
python -m dexted_dsp check examples/budget_limited.json --max-depth 16
# 对附带的这个例子，预期 certified，退出码 0。
```

最后两个命令说明未知结论并不是失败证明。必须查看状态和退出码，不要只搜索“certified”字符串，因为它也可能是值为 false 的字段。只有通过的证书可以复核。保留原输入、阈值、证书和版本；证书没有签名，复核器会重新计算数学条件并检查输入绑定。

## 7. C++ 与 C 接口

需要 C++20 编译器、CMake >=3.20、Boost >=1.74 头文件。Debian/Ubuntu 示例：`sudo apt-get install g++ cmake libboost-dev`。macOS 请用常用包管理器安装相应工具；Windows 配置兼容工具链与 Boost。Python 核心不需要这些依赖。

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
cmake --install build --prefix ./local-install
```

```cpp
#include <dexted_dsp/biquad.hpp>
int main() {
    const float coefficients[5] = {0.25f, 0, 0, -0.5f, 0};
    const int verdict = dexted_dsp::certify_biquad_f32(coefficients, 1.0);
    return verdict == 1 ? 0 : 1;
}
```

返回码：`1` 通过，`0` 不通过，`-1` 输入无效。C ABI 还捕获内部异常并返回或写入 `-2`。**不可直接转换成 bool**，负错误码也会变成 true。头文件 API 可能抛出内存分配异常。不要启用 fast-math。

CMake 使用方调用 `find_package(DextedDSP CONFIG REQUIRED)`，链接 `DextedDSP::dexted_dsp`，并通过 `CMAKE_PREFIX_PATH` 传入安装前缀。原生系数仅支持 binary32，阈值为 binary64。原生级联认证尚未实现。

可选 Python 原生连接测试，Linux 示例：

```bash
python tools/native_smoke.py "$PWD/build/libdexted_dsp.so"
```

加载器要求明确、可信的绝对库路径，并拒绝隐式改变系数精度。macOS/Windows 的库名和目录不同，详见 [API 契约](../../reference/API.md)。

## 8. CI 集成

```bash
python -m dexted_dsp check examples/safe.json --output certificate.json
python -m dexted_dsp verify examples/safe.json certificate.json
```

将示例替换为实际导出的系数；所有非零退出码，包括 3，都应阻止部署。附带 GitHub Actions 测试 Python、C++ 和构建，但有配置不等于实际托管任务已经执行。仓库工作流真正通过前，不应展示已通过徽章。

## 9. 常见问题

| 问题 | 排查 |
|---|---|
| 找不到模块或 `dexted-dsp` | 同一环境中使用 `python -m pip` 和 `python -m dexted_dsp` |
| float32 溢出或输入无效 | 检查最终有限实数系数；不要静默裁剪后复用旧证书 |
| 单位增益被拒绝 | 条件严格；使用有依据且明确的更大阈值，不要隐藏容差 |
| `unknown` | 检查节点、深度和裕度；在上限内增加预算或拒绝部署 |
| 旧证书无法复核 | 检查顺序、归一化、舍入、节顺序及完全相同的阈值 |
| 找不到 Boost | 安装头文件，非标准安装需配置 CMake 搜索前缀 |
| 原生加载器拒绝系数 | 在导出流程明确转换为 float32 |
| 无显示环境绘图失败 | 设置 `MPLBACKEND=Agg` 和可写 `MPLCONFIGDIR` |
| 性能数字不同 | 核对版本、输入、CPU 负载、标志、线程；速度不能替代正确性 |

报告问题时提供最小系数 JSON、预期条件、实际状态、版本、OS/编译器和日志。未经授权不要附带私有音频、凭据或专有模型。

[OAI-README]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/README.md
[OAI-325]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-direct-proof-of-the-complete-Crouzeix-inequality-September-26-2026/build/main.tex
[OAI-DFT]: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex
[CP-2017]: https://arxiv.org/abs/1702.00668
[SCIPY-FREQZ]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html
[PYPA]: https://packaging.python.org/en/latest/tutorials/packaging-projects/
