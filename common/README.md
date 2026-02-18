# 共通アセット（common）

プロジェクト全体で使う CSS / JS を置くフォルダです。

## 使い方（各 HTML から読み込む）

**共通だけ使う場合:**
```html
<link rel="stylesheet" href="../common/global.css">
<script src="../common/global.js"></script>
```

**共通 ＋ そのページ用を両方使う場合（推奨）:**
```html
<!-- 先に共通 → あとでページ用が上書きできる -->
<link rel="stylesheet" href="../common/global.css">
<link rel="stylesheet" href="style.css">
<script src="../common/global.js"></script>
<script src="script.js"></script>
```

- 同じ種類のタグを複数書けば、すべて読み込まれます。
- CSS は後に書いた方が優先、JS は順番に実行されます。
- 階層に応じて `../` の数だけ変えてください（例: register/ からは `../common/`、register/registration_si-fi_jp/ からは `../../common/`）。
