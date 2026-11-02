"""literature.csv → ../REFERENCES.md（完整參考文獻清單，含全文狀態與 DOI/URL）。"""
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, "..", "literature.csv"), encoding="utf-8")))
L = ["# 參考文獻（完整清單，由 lit_raw/make_refs.py 從 literature.csv 產生）", "",
     "> 全文狀態：除 X01（GitHub 資料集）外，**全部只讀到搜尋摘錄（僅摘要）**；網路政策擋下學術網站（DECISIONS D-009）。",
     "> DOI 欄：「已填」者是 subagent 以 DOI 字串比對到出版社/典藏記錄（間接驗證），**沒有經 doi.org 解析**；「資料集 DOI」取自 Seok DLDO survey，未驗證。", ""]
for r in rows:
    doi = r["doi"].strip()
    link = f"https://doi.org/{doi}" if doi else r["url"].strip()
    extra = []
    if r.get("doi_from_dataset"): extra.append(f"資料集 DOI：{r['doi_from_dataset']}")
    if r.get("oa_reported"): extra.append(f"搜尋顯示可能有開放版本（未開啟）：{r['oa_reported']}")
    if r.get("dup_of"): extra.append(f"另一 agent 重複收錄：{r['dup_of']}")
    L.append(f"- **[{r['id']}]** {r['authors_short'] or r['first_author']}, “{r['title']}”, {r['venue']}, {r['year']}. "
             f"{('DOI ' + doi + ' — ') if doi else ''}<{link}> — 全文狀態：{r['fulltext_status']}；類別 {r['arch_class']}。"
             + (" " + "；".join(extra) if extra else ""))
open(os.path.join(HERE, "..", "REFERENCES.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print(len(rows), "refs written")
