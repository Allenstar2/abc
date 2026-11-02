"""合併 4 個 subagent 的 CSV → ../literature.csv。
- 去重（同一篇被兩個 agent 收錄者保留一筆，dup_of 記錄另一個 id）
- fulltext_status 改為實際閱讀狀態：本次全部「僅摘要（搜尋摘錄）」；原值移到 oa_reported（D-012）
- 加 2 筆一手資料集/背景：DLDO survey dataset（GitHub，本次實際開啟）
"""
import csv, glob, os
HERE = os.path.dirname(os.path.abspath(__file__))
dups = {"D07": "H06", "D04": "H08", "D09": "A12", "D11": "A14", "F01": "A05", "F14": "A07"}
rows, seen = [], {}
for f in sorted(glob.glob(os.path.join(HERE, "agent*.csv"))):
    for r in csv.DictReader(open(f, encoding="utf-8")):
        if r["id"] in dups:
            seen.setdefault(dups[r["id"]], []).append(r["id"]); continue
        rows.append(r)
out = []
for r in rows:
    r = dict(r)
    r["oa_reported"] = r["fulltext_status"] if r["fulltext_status"] != "僅摘要" else ""
    r["fulltext_status"] = "僅摘要（搜尋摘錄，未開啟全文）"
    r["dup_of"] = ";".join(seen.get(r["id"], []))
    r["source_agent"] = {"H": "agent1", "A": "agent2", "D": "agent3", "F": "agent4"}[r["id"][0]]
    out.append(r)
out.append(dict(id="X01", first_author="M. Seok; Z. Wang; S. J. Kim", authors_short="Seok, Wang, Kim",
                title="Digital Low-Dropout Voltage Regulator (DLDO) Survey (dataset, 58 rows, 2010–2020)",
                venue="GitHub dataset (companion of Wang et al. review, D08)", year="2021", doi="",
                url="https://github.com/mgseok/DLDO-survey", fulltext_status="全文-開放（本次實際開啟，commit 68e94cc）",
                fulltext_url="https://github.com/mgseok/DLDO-survey", arch_class="R",
                numbers_source="資料集（作者群整理之 reported/estimated 值，非原論文）", result_type="M(多數)",
                relevance="高：edge time 分佈、PSRR 報告率、0.18µm DLDO 例子",
                notes="本次以 pandas 讀取：58 列；46 列有 edge time，範圍 0.015–4000 ns，中位數 2 ns；僅 8 列有 PSRR。"
                      "X. Wang CICC 2019 同晶片：1 ns 邊沿 droop 185 mV、10 ns 邊沿 88 mV。180 nm 只有 2 列（ESSCIRC 2018 pseudo-digital 0.7→0.6 V 100 mA 30 pF droop 106 mV @150 ns；VLSI 2018 quasi-digital）。",
                oa_reported="", dup_of="", source_agent="main"))
fields = list(out[0].keys())
for extra in ("oa_reported", "dup_of", "source_agent"):
    if extra not in fields: fields.append(extra)
with open(os.path.join(HERE, "..", "literature.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
    for r in out: w.writerow({k: r.get(k, "") for k in fields})
print(len(out), "rows; years:", sorted(set(r["year"] for r in out)))
import collections
print(collections.Counter(r["arch_class"] for r in out))
print("2014+:", sum(1 for r in out if r["year"][:4].isdigit() and int(r["year"][:4]) >= 2014))
