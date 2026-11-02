"""實驗 X2：同一顆 REF-A，量到的 undershoot 隨負載邊沿時間與起始電流改變多少。
目的：驗證「不同論文的 ΔV/FoM 不能直接比較」這個主張。"""
import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ldo_ref import DEFAULT, load_step
from common import RES, FIG

designs = {"CL=100pF,Cc=5pF": dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3),
           "CL=1nF,Cc=20pF": dict(DEFAULT, CL=1e-9, Cc=20e-12, R1=4e3, R2=4e3)}
edges = [0.1e-9, 1e-9, 10e-9, 100e-9, 1e-6]
rows = []
fig, ax = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
for j, (dn, p) in enumerate(designs.items()):
    for I1 in (0, 1e-3, 10e-3):
        us = []
        for te in edges:
            t, vo, vpg, m = load_step(p, I1, 100e-3, te, "x2_tmp", thold=6e-6)
            us.append(m["undershoot"] * 1e3)
            rows.append(dict(design=dn, I1_mA=I1*1e3, I2_mA=100, edge_ns=te*1e9,
                             undershoot_mV=m["undershoot"]*1e3, overshoot_mV=m["overshoot"]*1e3))
        ax[j].semilogx(np.array(edges)*1e9, us, "o-", label=f"I1={I1*1e3:g} mA → 100 mA")
    ax[j].set_title(dn); ax[j].set_xlabel("load edge time [ns]"); ax[j].grid(True, which="both", alpha=.3); ax[j].legend()
ax[0].set_ylabel("undershoot ΔV [mV]")
plt.suptitle("Same REF-A circuit: measured undershoot depends on edge time and start current")
plt.tight_layout(); plt.savefig(f"{FIG}/x2_edge_time.png", dpi=110)
json.dump(rows, open(f"{RES}/x2_edge_time.json", "w"), indent=1)
for r in rows:
    print(f"{r['design']:16s} I1={r['I1_mA']:4.0f}mA edge={r['edge_ns']:7.1f}ns  ΔV-={r['undershoot_mV']:6.0f} mV  ΔV+={r['overshoot_mV']:5.0f} mV")
