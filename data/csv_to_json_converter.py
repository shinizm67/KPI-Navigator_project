import csv
import json

# ファイルパス（data フォルダ内にある CSV と JSON）
csv_path = "data/past_actuals.csv"
json_path = "data/kpi-data.json"

actual_list = []

# CSV 読み込み
with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        actual_list.append({
            "open": int(row["営業日"]),
            "date": row["日付"],
            "sales": int(row["Daily売上額"]),
            "target_sales": int(row["日次目標売上額"]),
            "diff": int(row["差額"]),
            "rate": float(row["日次達成率"].replace('%','')) / 100,
            "monthly_target_total": int(row["月次累積目標額"]),
            "monthly_sales_total": int(row["月次累積売上額"]),
            "monthly_diff": int(row["月次差額"]),
            "monthly_rate": float(row["月次達成率"].replace('%','')) / 100,
            "yearly_target_total": int(row["年次累積目標額"]),
            "yearly_sales_total": int(row["年次累積売上額"]),
            "yearly_diff": int(row["年次差額"]),
            "yearly_rate": float(row["年次達成率"].replace('%','')) / 100
        })

# 最終 JSON データ構造
output = {
    "meta": {
        "store": "shin's dinner",
        "year": 2024
    },
    "actual": actual_list
}

# JSON 保存
with open(json_path, "w", encoding="utf-8") as jsonfile:
    json.dump(output, jsonfile, ensure_ascii=False, indent=2)

print("✅ JSONファイル出力完了: data/kpi-data.json")
