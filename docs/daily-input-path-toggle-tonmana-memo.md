# Annual / Monthly 入力経路トグル — トンマナ差分メモ

更新日: 2026-06-17

Phase 5（`dailySalesInputPath` 排他）で追加した **Annual / Monthly 切替トグル**（`.kpi-daily-input-path`）と、グローバルヘッダーの **Sci-Fi / Office 切替トグル**（`.si-fi.profile-page .btn-mode`）の見た目が異なる理由・数値差分・将来揃える場合の注意点をまとめる。

**現状方針（2026-06-17）**: トンマナは **このまま維持**。後日、Sci-Fi / Office トグルに寄せる可能性あり。

---

## 1. 2 種類のトグルが存在する

| 名称 | 役割 | 表示場所 | 主な CSS / HTML |
|------|------|----------|-----------------|
| **Sci-Fi / Office** | UI テーマ（`body.office-mode`） | グローバルヘッダー右（歯車の左） | `en/setting/style.css` — `.si-fi.profile-page .btn-mode` |
| **Annual / Monthly** | 日次売上の編集経路（`KpiYearStore.dailySalesInputPath`） | Sales Data モーダル内・MEP 内・**PL 表ツールバー（表示のみ）**（Pro） | `scripts/kpi_phase5_client.py` — `PHASE5_TOGGLE_CSS` / `.kpi-daily-input-path` |

月次・年次・MEP ページは `body` に `profile-page` があり `en/setting/style.css` を読み込むため、**ヘッダーには Sci-Fi / Office トグルが出る**。一方 Annual / Monthly トグルは **モーダル／MEP パネル内の別コンポーネント** で、ヘッダートグルとは無関係に動作する。**PL 表**（2026-07-20）は MEP と同じ見た目の **read-only インジケータ**（`.kpi-daily-input-path--pl-readonly`）を年度セレクタ横に表示。切替は MEP / Sales Data で行う。

### PL 表（表示のみ・Option A）

- 実装: `scripts/pl_sales_input_path_indicator_client.py` + `build_pl_table_page.py`
- Pro のみ表示（Standard は他画面と同様非表示）
- `kpi:dailySalesInputPathChanged` / `localStorage` 更新で同期
- ツールチップ: 「切替は MEP または Sales Data で」

---

## 2. なぜトンマナが違うか

1. **別コンポーネント・別実装タイミング**
   - Sci-Fi / Office: Profile 系ページ向けヘッダー UI（`btn-mode` を CSS でピル型トグルに再解釈）。
   - Annual / Monthly: Phase 5 で **Figma / tutorial-toggle 系**を参考に新規追加（`kpi_phase5_client.py` 先頭コメント: *Mirrors tutorial-toggle pill switch*）。

2. **色の役割分担が異なる**
   - Sci-Fi / Office: **ラベル＝シアン**（`var(--si-fi-cyan)` / `#58e1f3`）、**スイッチ＝緑**（`#0f9403`）。
   - Annual / Monthly: **ラベル・スイッチとも緑**（`#0db13a`）。tutorial-toggle（画面左下 `Tutorial on/off`）と同系統。

3. **ノブ形状**
   - Sci-Fi / Office: **24×13px の横長ピル**（`#btn-mode-text::before`）。
   - Annual / Monthly: **13×13px の円形ノブ**（`.kpi-daily-input-path__knob`）。

4. **意味・ラベル**
   - Sci-Fi / Office: タイトル `Mode`、左右 `Sci-Fi` / `Office`（疑似要素で描画）。
   - Annual / Monthly: タイトル `Edit`（EN）/ `編集`（JA）、左右 `Annual` / `Monthly`（HTML `span` + `is-active` / `is-inactive`）。

---

## 3. 数値比較（Sci-Fi モード基準）

| 項目 | Sci-Fi / Office（ヘッダー） | Annual / Monthly（Phase 5） |
|------|------------------------------|-----------------------------|
| トラック | 52×17px | 52×17px（**同じ**） |
| トラック枠 | 1px `#0f9403` | 1.5px `#0db13a` |
| トラック背景 | `rgba(15, 148, 3, 0.1)` | `rgba(0, 0, 0, 0.2)` |
| ノブ | 24×13px ピル、`#0f9403` | 13×13px 円、`#0db13a` |
| ノブ移動 | `left` 0.18s ease | `transform: translateX(31px)` 0.2s |
| タイトル | 12px シアン（`Mode`） | 11px 緑（`Edit` / `編集`） |
| サイドラベル | 12px シアン | 10px 緑 |
| 横レイアウト | `grid: auto 52px auto`、`gap: 4px`、2 行（タイトル＋行） | `grid: auto 52px auto`、`gap: 6px`、`min-width: 172px` |
| 非アクティブ側 | Office 側 `rgba(88,225,243,0.45)` 等 | `opacity: 0.34`（`is-inactive`） |
| Office 時 | 白/グレー系（`en/setting/style.css` 849行付近） | グレー系（`PHASE5_TOGGLE_CSS` 内 `body.office-mode`） |

### 参考: tutorial-toggle（左下フロート）

`app/monthly/index.html` 等の `.tutorial-toggle-float` も Phase 5 の近い祖先:

- トラック 52×17、緑 `#0db13a`
- ノブ **24×13 ピル**（Annual / Monthly より Sci-Fi / Office に近い）
- ラベル `on` / `off`、9px、列幅 13px 固定

→ Annual / Monthly は **tutorial の緑色＋円形ノブ**、Sci-Fi / Office は **シアンラベル＋緑ピル** という中間関係。

---

## 4. 配置（現状・2026-06-17 時点）

### Sales Data モーダル（`.kpi-daily-input-path--sales-data`）

```css
position: absolute;
top: calc(var(--sdm-tab-top) - 30px);  /* Input/Analyze タブより 30px 上 */
right: 22px;
z-index: 7;
```

- パネル `--sdm-panel-w: 1100px`、内幅 `--sdm-inner-w: 1020px`
- テーブル上端は `--sdm-body-top`（タブ行の下）
- `-30px` は Sales Data テーブルへの食い込み回避用（2026-06-17 調整済み）

### MEP（`.kpi-daily-input-path--mep`）

```css
position: absolute;
top: 8px;
left: calc(
  var(--mef-toolbar-pad) + var(--mef-page-inset, 0px) + var(--mef-summary-toggle-w) +
    var(--mef-nav-gap) + var(--mef-today-shift) + 106px
);
```

- `106px` は Today ボタン（`本日` / `Today`）との重なり回避用（当初 56px → +50px）
- MEP 配置はユーザー確認済み「完璧」状態（2026-06-17）

---

## 5. 将来 Sci-Fi / Office トンマナに揃えた場合のレイアウト検証

実装は未着手。コード・寸法からの見込み。

### 横方向

Orbitron 12px 時のラベル行幅の目安:

| ラベル組 | おおよその行幅（52px トラック + gap 込み） |
|----------|---------------------------------------------|
| Sci-Fi + Office | ~147px |
| Annual + Monthly | ~158px（Monthly が 1 文字分長い） |

現状 `min-width: 172px` は上記より広い。**12px 化しても横は縮むか同等**で、はみ出しリスクは低い。

| 配置 | リスク |
|------|--------|
| Sales Data（右上） | **低** — パネル右端から 22px、十分な余白 |
| MEP（Today 横） | **低〜中** — 幅が ~172→~165px 程度なら Today（右端 ~136px）との隙間 ~56px は維持。極端に gap / フォントを広げた場合のみ再オフセット検討 |

### 縦方向

- ヘッダートグル cluster の `min-height` 参考値: `.annual-tw-toggle-cluster` で 47px
- Annual / Monthly もタイトル + 1 行で **35〜47px 前後**
- **スタイルのみ変更**（`top` 不変）なら Sales Data テーブルへの食い込みは悪化しにくい

### 揃えるときの推奨手順（メモ）

1. **見た目だけ**寄せる（色: シアンラベル + `#0f9403` ピルノブ、12px ラベル）。配置定数は触らない。
2. `scripts/kpi_phase5_client.py` の `PHASE5_TOGGLE_CSS` を単一ソースにし、`python3 scripts/apply_kpi_phase5.py` で 4 ページ反映。
3. Office モードは `en/setting/style.css` の `.office-mode.profile-page .btn-mode` と **視覚的整合**を確認（白ノブ・白枠等）。
4. MEP で Today との距離を実機確認。必要なら `106px` のみ微調整。
5. タイトル文言は **Edit / 編集のまま**が UX 的には自然（`Mode` にしない）。

共通化案（将来）:

- オプション A: `.kpi-daily-input-path` に Profile トグルと同じトークン（`--si-fi-cyan`, `#0f9403`）を適用。
- オプション B: 共通クラス例 `.kpi-pill-toggle` を切り出し、ヘッダー・Phase5 の両方から参照（影響範囲大のため要検討）。

---

## 6. 関連ファイル

| 用途 | パス |
|------|------|
| Phase 5 CSS / HTML / JS 定義 | `scripts/kpi_phase5_client.py` |
| HTML 反映 | `scripts/apply_kpi_phase5.py` |
| 対象ページ | `app/annual/index.html`, `en/app/annual/index.html`, `app/monthly/edit/index.html`, `en/app/monthly/edit/index.html` |
| Sci-Fi / Office ヘッダートグル | `en/setting/style.css`（`.si-fi.profile-page .btn-mode`、28行目〜） |
| tutorial-toggle 参考 | `app/monthly/index.html` — `.tutorial-toggle-float` |
| 年次データ・アーキテクチャ | `docs/year-rollover-data-architecture.md`（Phase 5 参照） |

---

## 7. 変更履歴（トグル UI のみ）

| 日付 | 内容 |
|------|------|
| 2026-06-17 | 初版。トンマナ差分の整理。現状維持を決定。 |
| 2026-06-17 | MEP: 左オフセット 106px、全文 Annual/Monthly、非アクティブ dim、言語別 Edit/編集 |
| 2026-06-17 | Sales Data: `top: calc(var(--sdm-tab-top) - 30px)` でテーブル食い込み回避 |
