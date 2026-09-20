# KPN Scrollbar UX Contract

更新日: 2026-09-20  
ステータス: **採用（Cross-Platform Overlay Scrollbar Standard）**

関連実装: [`js/kpi-overlay-scrollbar.js`](../js/kpi-overlay-scrollbar.js)  
PL 生成: [`scripts/build_pl_table_page.py`](../scripts/build_pl_table_page.py)（gutter / native track を出さない）

---

## 目的

Windows Chrome の native scrollbar rail がレイアウト幅を占有して
table / grid / modal を壊す問題を解消し、Mac Chrome の overlay 体験へ近づける。

## 契約（必須）

1. **scrollbar track がレイアウト領域を占有しない**
2. **scrollbar 出現/消失で table / cell / grid 幅が変化しない**（layout shift 0px）
3. **小さい thumb だけを overlay 表示**（track は原則 transparent / 非描画）
4. **scroll / pointer interaction 時のみ表示**
5. **操作終了後すぐ fade out**（目安 500–900ms、既定 700ms）
6. **Mac Chrome の既存 native overlay は壊さない**
7. **Windows Chrome でも Mac に近い使用感**
8. **KPN 内で scrollbar visual language を統一**

## Platform strategy

UA 文字列で OS 判定しない。

ランタイムで temporary scroll element を作り:

```
nativeScrollbarWidth = offsetWidth - clientWidth
```

| 測定 | 方針 |
|---|---|
| `nativeScrollbarWidth > 0` | non-overlay → `html.kpn-overlay-scroll` + custom overlay thumbs |
| `nativeScrollbarWidth == 0` | overlay 環境（典型 Mac Chrome）→ native を維持 |

強制検証（Windows headless 等で nativeWidth=0 のとき）:

- `window.__KPN_FORCE_OVERLAY_SCROLL = true` → custom overlay を有効化
- `window.__KPN_FORCE_OVERLAY_SCROLL = false` → Mac 相当（native 維持）を強制

## Shared implementation

| 資産 | 役割 |
|---|---|
| `js/kpi-overlay-scrollbar.js` | 測定・CSS 注入・host wrap・thumb sync / drag / auto-hide・selector 登録 |

対象 container は `KpiOverlayScrollbar.SELECTORS` に登録。
新規 scroll container は原則ここに追加するか `data-kpn-overlay-scroll` を付与。

## Visual tokens（Sci-Fi）

```css
--kpn-scroll-thumb: rgba(88, 225, 243, 0.75);
--kpn-scroll-thumb-hover: rgba(110, 235, 250, 0.95);
```

- track: 原則 transparent
- 白/gray native track: **禁止**（overlay mode 時）
- Office mode: 灰系 thumb（Sci-Fi cyan を流用しない）

Past Sales: purple shell + cyan/blue overlay thumb。

## Surface notes

### MEP（Monthly Edit）

| Container | 役割 |
|---|---|
| `.monthly-edit-float__scroll` | **primary** XY scroll（overlay thumb） |
| `.monthly-edit-float__labels` | Y slave（wheel は primary へ。overlay 時は native rail 非表示・非 enhance） |
| `.monthly-edit-float__date-rail-scroll` | X slave（同上） |
| `.monthly-edit-float__body` | `overflow:hidden` のみ。scroll 対象外 |

### PL Table

生成 HTML / generator 正本:

- `--pl-scrollbar-w: 0`
- frozen `padding-right: 0`（rail 幅予約なし）
- `scrollbar-gutter: auto`（`stable` 禁止）
- `overflow-y: auto`（常時 gutter の `scroll` 禁止）
- 自前 `::-webkit-scrollbar` track/thumb **描画しない**

Windows classic は overlay JS が thumb を出す。Mac は native overlay を維持。

### Annual Timeline Window（TW）

`.annual-daily-focus-scroll` 系は **共通 SELECTORS から除外**（2026-09-20 hotfix）。

理由: host wrap が `height:100%`（absolute clip 内）を content 高さへピン留めし、
`canY=false` / 縦スクロール不能 / 内容がクリップされて消えて見える。

Annual TW は native scroll（Mac overlay / Windows classic）を維持。
Windows classic rail が再発する場合は Annual 専用 hook で open 後 enhance を再設計する。

### First-open race

`[hidden]` / `display:none` 中、または `clientWidth|Height < 2` のときは enhance しない
（`data-kpn-osb-pending` + `ResizeObserver` / rAF×2 で監視）。

表示後に `refresh()` / MutationObserver（`hidden` / `class` / `aria-hidden`）→ rAF×2 / pending watcher で remeasure。
`style` 属性は監視しない（PL Insight の chart style 更新で refresh 連打 → 初回スクロール不能になるため）。

flex scroll child の host は `height:100%` 固定せず `flex` + `height:auto` で fill
（`height:100%` 連鎖で host が 0px になるのを防ぐ）。

absolute で `top`+`bottom`（Insight TW）の port は host に computed px 高さをコピーしない
（短い高さで固定され下部に空白が残るため。inset のみで fill）。

API: `KpiOverlayScrollbar.refresh()` / `remeasure()` / `destroyAnnualTwWrappers()`

## Accessibility

visual を隠しても:

- wheel / trackpad / keyboard / PageUp/Down / arrows / focus scroll / touch

を壊さない。

`prefers-reduced-motion: reduce` 時は fade を短縮。

## 禁止

- `scrollbar-gutter: stable` だけで「解決した」ことにする（常時領域予約は Mac-like 要件と不一致）
- Mac で track/thumb 常時表示や gutter 予約を新たに発生させること
- content layout / column widths / table architecture の redesign
- excel/ への干渉
- generator に旧 8px track / frozen padding / stable gutter を戻すこと

## 今後

新しい scroll container を追加するとき:

1. 可能なら shared selector / `data-kpn-overlay-scroll` へ載せる
2. Windows で layout shift 0px を確認
3. Mac で native overlay が悪化していないことを確認
4. PL を再生成するときは `build_pl_table_page.py` の gutter 契約を崩さない
