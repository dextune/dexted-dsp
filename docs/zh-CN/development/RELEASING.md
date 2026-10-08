# GitHub 与软件包发布指南

[English](../../en/development/RELEASING.md) · [한국어](../../ko/development/RELEASING.md) · [简体中文](RELEASING.md) · [日本語](../../ja/development/RELEASING.md)

[Dexted DSP](../README.md)

## 1. 发布前确认归属与范围

仓库为 `https://github.com/dextune/dexted-dsp`，由 DEXTUNE 维护。Git 提交不等于 PyPI 发布。分发前请核对包名可用性、元数据、已有版权和下列检查。不要虚构 DOI、机构背书、外部审计或 CI 状态。

默认 README 为英语，韩语、简体中文和日语版本引用同一数据。请保留研究 alpha 标识、严格输入约定、对 `unknown` 的拒绝策略，以及 OpenAI 引用的边界。当前可执行代码不是 Crouzeix 实现，也不是听力或视频质量的安全认证工具。

## 2. 本地发布检查

在解压后的源码根目录和适当环境中运行：

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


审查原始日志与[本次复核摘要](../../../validation/docs_refresh/summary.json)。测试通过属于发布检查，不代表独立的外部证明审计。新基准不必更快。修改运行代码后，应保存新测量版本，不要重写旧哈希或只选择有利的运行结果。

## 3. 向现有仓库提交修改

请克隆维护中的仓库，不要创建无关的 Git 历史。私有仓库需要访问权限。没有写入权限的贡献者应通过 fork 和 pull request 提交。

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

提交前执行上述发布检查。推送工作分支，检查 GitHub diff 和实际 CI 结果，再按正常评审流程合并。不要强制推送 main。`dist/` 中的构建产物不属于应提交的源码。

## 4. 构建并检查实际分发文件

```bash
python -m build
python -m twine check dist/*
python -m venv .wheel-test
# POSIX; Windows: .wheel-test\Scripts\python.exe
.wheel-test/bin/python -m pip install --no-index --no-deps dist/dexted_dsp-0.1.0-py3-none-any.whl
.wheel-test/bin/python -m unittest discover -s tests -v
.wheel-test/bin/python tools/documentation_smoke.py
```


wheel 测试中不要设置 `PYTHONPATH=src`。wheel 是纯 Python 包，不含原生共享库；原生用户通过 CMake 构建。源码分发包包含源码、示例、文档和基准证据。

常规构建与检查命令可能下载可选工具。本次环境无法联网安装 `build` 和 `twine`，因此使用已安装的 setuptools 后端完成本地打包。实际执行了哪些检查，以验证摘要为准；文档列出命令不等于声称已执行每条命令。

修改已发布版本的文件时必须提升版本。本交付包只更新**尚未发布的** 0.1.0 包的 README 和文档。正式发布前，请设置真实公开 URL，检查 PyPI 元数据中的相对图片链接，并同步四种语言。PyPI 可能需要绝对图片 URL 或专用简短 README。

## 5. 审查后再发布

完成本地、托管检查及权限审查后，创建计划版本标签，并把源码 ZIP、wheel、sdist 和校验和附加到 GitHub Release。PyPI 发布是可选项：确认包名，使用 TestPyPI 试装，再配置获准的发布方式。本包不含令牌、密码或自动上传代码。

在真正拥有索引中的名称和文件之前，不要宣传 `pip install dexted-dsp` 会安装本项目。构建与上传是不同步骤。参考 [PyPA 官方打包指南](https://packaging.python.org/en/latest/tutorials/packaging-projects/)。

## 6. 维护

行为或证书格式变更时，请更新版本、添加回归测试、公平重测并更新四种语言。`MANIFEST.sha256` 与发布校验和只记录字节完整性，并不证明数学正确性。不要把检查速度优势表述为感知质量或医疗安全提升。

[OpenAI source revision](https://github.com/openai/math/tree/adc7f1241b42e322a6451854ab7e4b4c146bf78a)
