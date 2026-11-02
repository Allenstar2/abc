"""抽查 Seok 等人的 DLDO survey 資料集（https://github.com/mgseok/DLDO-survey, commit 68e94cc）。
資料集不放進 repo；請先 git clone 到 ldo-research/ext/DLDO-survey。"""
import os, json, pandas as pd
from common import RES
p = os.path.join(os.path.dirname(__file__), "..", "..", "ext", "DLDO-survey", "DLDO survey.xlsx")
df = pd.read_excel(p); df.columns = [c.strip() for c in df.columns]
e = pd.to_numeric(df["Edge time [ns]"], errors="coerce")
w = df[df["Author"].astype(str).str.contains("X. Wang")][["Title", "Venue", "Year", "Voltage droop [mV]", "Edge time [ns]"]]
out = dict(rows=len(df), edge_reported=int(e.notna().sum()), edge_min_ns=float(e.min()), edge_max_ns=float(e.max()),
           edge_median_ns=float(e.median()), psrr_reported=int(pd.to_numeric(df["PSRR [dB]"], errors="coerce").notna().sum()),
           hybridization=df["Digital Analog Hybridization"].astype(str).str.strip().value_counts().to_dict(),
           xwang_cicc2019=w.astype(str).values.tolist())
json.dump(out, open(f"{RES}/s7_dataset_stats.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
