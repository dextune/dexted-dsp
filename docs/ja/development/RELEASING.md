# GitHub・パッケージ公開ガイド

[English](../../en/development/RELEASING.md) · [한국어](../../ko/development/RELEASING.md) · [简体中文](../../zh-CN/development/RELEASING.md) · [日本語](RELEASING.md)

[Dexted DSP](../README.md)

## 1. 公開前に所有者と適用範囲を確認

リポジトリは `https://github.com/dextune/dexted-dsp`、保守担当は DEXTUNE です。Git commit と PyPI 公開は別です。配布前にパッケージ名・メタデータ・既存著作権と以下の検査を確認してください。DOI・推薦・外部監査・CI 状態を捏造しないでください。

既定の README は英語で、韓国語・簡体字中国語・日本語版も同じデータを参照します。研究用 alpha 表示、厳密な入力条件、`unknown` の拒否、OpenAI 参照の範囲を維持してください。実行コードは Crouzeix の実装でも、聴覚・動画品質の安全認証ツールでもありません。

## 2. ローカル公開前チェック

展開したソースのルートで、適切な環境を用いて実行します。

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


生ログと[今回の再確認サマリー](../../../validation/docs_refresh/summary.json)を確認してください。テスト成功は公開前の点検であり、独立した外部の証明監査ではありません。新しいベンチマークが必ず高速になる必要はありません。実行コードを変更した場合は、過去のハッシュを書き換えたり有利な試行だけを選んだりせず、新たな測定版を保存してください。

## 3. 既存リポジトリに変更を反映する

無関係な Git 履歴を作らず、管理中のリポジトリを clone してください。非公開中はアクセス権が必要です。書き込み権限のない貢献者は fork と pull request を利用してください。

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

コミット前に上記のリリース検査を実行します。作業ブランチを push し、GitHub の差分と実際の CI 結果を確認してから通常のレビュー手順でマージしてください。main への強制 push は避けてください。`dist/` のビルド成果物はソースとしてコミットしません。

## 4. 実際の配布物をビルド・確認

```bash
python -m build
python -m twine check dist/*
python -m venv .wheel-test
# POSIX; Windows: .wheel-test\Scripts\python.exe
.wheel-test/bin/python -m pip install --no-index --no-deps dist/dexted_dsp-0.1.0-py3-none-any.whl
.wheel-test/bin/python -m unittest discover -s tests -v
.wheel-test/bin/python tools/documentation_smoke.py
```


wheel のテストでは `PYTHONPATH=src` を設定しないでください。wheel は純粋な Python パッケージで、ネイティブ共有ライブラリは含みません。ネイティブ利用者は CMake を使用します。ソース配布物にはコード、例、文書、測定の根拠資料を含めます。

通常のビルド・確認コマンドは追加ツールをダウンロードする場合があります。今回の環境では `build` と `twine` をネットワーク経由でインストールできず、インストール済みの setuptools バックエンドでローカルの配布物を作成しました。実行済みの確認内容はサマリーを参照してください。コマンドの掲載は、そのすべてを実行したという意味ではありません。

公開済みの配布ファイルを変更する場合はバージョンを上げてください。今回は**未公開の** 0.1.0 パッケージの README・文書のみを更新しています。正式公開前に実際の公開 URL を設定し、PyPI メタデータの相対画像リンクを確認し、4 言語を同期してください。PyPI には絶対画像 URL または専用の短い README が必要な場合があります。

## 5. 確認が完了してから公開

ローカル・ホスト型のチェックと権限確認後、予定したバージョンのタグを作成し、ソース ZIP、wheel、sdist、チェックサムを GitHub Release に添付してください。PyPI 公開は任意です。名前を確認し、TestPyPI で試してから承認された公開方法を設定します。トークン、パスワード、自動アップロードコードは含めていません。

インデックス上の名称・配布ファイルを実際に所有するまでは、`pip install dexted-dsp` がこのプロジェクトをインストールすると宣伝しないでください。ビルドとアップロードは別の操作です。[PyPA 公式ガイド](https://packaging.python.org/en/latest/tutorials/packaging-projects/)を参照してください。

## 6. 保守

動作や証明書形式を変えるときは、版を更新し、回帰テストを追加し、公平に再測定して 4 言語も更新してください。`MANIFEST.sha256` とチェックサムはバイトの整合性の記録であり、数学の正しさの証明ではありません。判定速度の優位性を知覚的品質や医療上の安全性の主張へ置き換えないでください。

[OpenAI source revision](https://github.com/openai/math/tree/adc7f1241b42e322a6451854ab7e4b4c146bf78a)
