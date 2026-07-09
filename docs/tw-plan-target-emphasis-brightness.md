# TW — Plan Target Sales 強調（明度ベースライン）

> 適用: Annual TW（Daily / Monthly / Annual 列）、Monthly TW（Income グループ Target Sales 行）、各 Focus Bar  
> 実装: `scripts/tw_daily_target_emphasis_client.py`, `scripts/monthly_tw_plan_target_emphasis_client.py`

## Sci-Fi モード（確定値・2026-07-05）

| 用途 | 背景 | 文字色 | 備考 |
|------|------|--------|------|
| TW セル（Annual 行 / Monthly Income 行） | `rgba(88, 225, 243, 0.20)` | `#a8e8f5` | 太字 700、TW フォント +1px |
| Focus Bar 下段（値セル） | `rgba(88, 225, 243, 0.24)` | `#a8e8f5` | 太字 700、16px |
| Focus Bar 上段（ヘッダー） | なし | `#a8e8f5` | 太字 700 のみ |

初回案（0.28 / 0.34 / `#b8f4ff`）より **約 30% 暗め**。ユーザー確認済みでこの値を標準とする。

## Office モード

| 用途 | 背景 | 文字色 |
|------|------|--------|
| TW セル | `#c5dce8` | `#0a3d7a` |
| Focus Bar 下段 | `#c5dce8` | `#0a3d7a` |
| Focus Bar 上段 | なし | `#1256a8` |

## OFF / 非アクティブ行

- 背景: `transparent`
- 字色: 継承（他列と同程度）
- 太字: 600、フォントサイズは通常に戻す

## Monthly 専用 vFocus（Income グリッド）

中央レーンの `.monthly-vfocus-cell` に `#35686f` が一括指定されていたため、Target 強調が効かない。  
`KPI-MONTHLY-TW-PLAN-TARGET-EMPHASIS` 内で **中央レーン + `:not(.monthly-vfocus-cell--plan-target)`** を上書きする。

| セル | 背景 |
|------|------|
| 非 Target | `rgba(114, 117, 117, 0.12)` |
| Target（Income 4 行目） | `rgba(88, 225, 243, 0.24)` + 太字 16px |

## 再適用

```bash
python3 scripts/apply_tw_daily_target_emphasis.py      # Annual + Monthly index（annual-daily TW）
python3 scripts/apply_monthly_tw_plan_target_emphasis.py  # Monthly 専用 TW（Income グリッド）
```
