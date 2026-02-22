# .specstory を 2台の Mac で共有する手順

目的: どちらの Mac で作業しても、同じ議事録・仕様の続きで進められるようにする。

## 初回セットアップ（1台目で 1回だけ）

1. 1台目（家の MacBook Pro）で、ターミナルを開きプロジェクトフォルダへ移動:
   ```bash
   cd /Users/shinmatsushita/Desktop/kpi-navigator
   ```

2. .specstory を git に追加（履歴だけ。project.json / what-is-this.md は .specstory/.gitignore で除外済み）:
   ```bash
   git add .specstory/
   git status   # .specstory/.gitignore と .specstory/history/*.md が追加されることを確認
   ```

3. コミットして push:
   ```bash
   git commit -m "Add .specstory history for sharing between machines"
   git push
   ```

## 2台目で初めて使うとき

1. 2台目でプロジェクトを clone している場合、最新を取得:
   ```bash
   cd /Users/shinmatsushita/Desktop/kpi-navigator
   git pull
   ```

2. これで `.specstory/history/` に議事録が入り、2台目でも「同じページ」で作業できます。

## 普段の運用（常に同じページで進める）

- **作業を始めるとき（どちらの Mac でも）**
  ```bash
  git pull
  ```
  → もう一方の Mac で追加された議事録・コードを必ず取り込む。

- **作業が一段落したら（どちらの Mac でも）**
  ```bash
  git add .
  git status   # .specstory/history/ の変更も含まれるか確認
  git commit -m "作業内容の説明（例: Office Mode 対応など）"
  git push
  ```

- **もう一方の Mac に戻ったら**
  ```bash
  git pull
  ```
  → 最新の議事録とコードで続きから作業。

## 注意

- `.specstory/project.json` と `.specstory/what-is-this.md` は git に含めていません（.specstory/.gitignore で除外）。これらは各 Mac ごとに Cursor が自動生成するため、共有しなくても問題ありません。
- 共有されるのは `.specstory/history/*.md`（議事録）と `.specstory/.gitignore` だけです。これで「進め具合・仕様・決め事」を両方の Mac で参照できます。
