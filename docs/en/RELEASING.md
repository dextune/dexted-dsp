# GitHub and package release guide

[English](../en/RELEASING.md) · [한국어](../ko/RELEASING.md) · [简体中文](../zh-CN/RELEASING.md) · [日本語](../ja/RELEASING.md)

[Dexted DSP](../../README.md)

## 1. Ownership and scope before publication

Repository: `https://github.com/dextune/dexted-dsp`. DEXTUNE maintains Dexted DSP. A Git commit is not a PyPI release. Review package-name availability, metadata, inherited copyright and the checks below before publishing any distribution. Do not invent a DOI, endorsement, external audit or CI status.

The default README is English; the Korean, Simplified Chinese and Japanese variants link to the same data. Keep the research-alpha label, strict input contract, fail-closed `unknown`, and OpenAI dependency boundaries. The current runnable code is not a Crouzeix implementation or a hearing/video-quality safety certificate.

## 2. Local release gate

From the extracted source root, in a suitable environment:

```bash
python -m pip install '.[dev,bench]'
python -m unittest discover -s tests -v
python tools/documentation_smoke.py
python tools/check_documentation.py
python tools/check_links.py
python -m pip install -r requirements-bench-tested.txt
python tools/restore_fixtures.py
python tools/audit_benchmark.py --recheck-fixtures
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
```


Review raw logs and [the refresh summary](../../validation/docs_refresh/summary.json). Passing tests is a release check, not an independent proof audit. Benchmark runs need not become faster. If runtime code changes, create a new measured revision rather than rewriting archived hashes or selecting favorable runs.

## 3. Contribute to the existing repository

Clone the maintained repository rather than initializing an unrelated history. You need repository access while it is private. Contributors without write permission should use a fork and a pull request.

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

Run the release checks above before committing. Push a topic branch, review the GitHub diff and CI results, then merge through your normal review process. Do not force-push the main branch. Build outputs in `dist/` are local artifacts, not source files to commit.

## 4. Build and check the real distribution

```bash
python -m build
python -m twine check dist/*
python -m venv .wheel-test
# POSIX; Windows: .wheel-test\Scripts\python.exe
.wheel-test/bin/python -m pip install --no-index --no-deps dist/dexted_dsp-0.1.0-py3-none-any.whl
.wheel-test/bin/python -m unittest discover -s tests -v
.wheel-test/bin/python tools/documentation_smoke.py
```


Do not set `PYTHONPATH=src` during the wheel test. The wheel is pure Python and excludes the native shared library. Native consumers use CMake. The source distribution includes source, examples, docs and benchmark evidence.

The usual build/test commands can download optional tooling. This refresh could not fetch `build`/`twine` from the network; local packaging used the already installed setuptools backend instead. Consult the validation summary for which checks actually ran; a documented command is not an execution claim.

For an existing published release, bump the version before publishing changed artifacts. This bundle only revises the README/docs of an **unpublished** 0.1.0 package. Before a real release, set real public project URLs, review relative image links in PyPI metadata, and synchronize all language versions. PyPI may need absolute image URLs or a package-specific short README.

## 5. Publish only after review

After local/hosted checks and permissions review, create the intended version tag and attach the source ZIP, wheel, sdist and checksum to GitHub Releases. PyPI publication is optional: verify the name, test with TestPyPI, and configure an approved publishing method. No tokens, passwords or automatic upload code are bundled.

Do not advertise `pip install dexted-dsp` from an index as this project's installation until the name and published files are actually yours. Building and uploading are different steps. See [PyPA's official packaging tutorial](https://packaging.python.org/en/latest/tutorials/packaging-projects/).

## 6. Maintenance

For behavior or certificate-schema changes, version the change, add regression tests, remeasure fairly and update the four language sets. Use `MANIFEST.sha256` and release checksums as byte-integrity records; they do not prove the mathematics. Do not convert a timing advantage into a claim of perceptual or medical safety.

[OpenAI source revision](https://github.com/openai/math/tree/adc7f1241b42e322a6451854ab7e4b4c146bf78a)
