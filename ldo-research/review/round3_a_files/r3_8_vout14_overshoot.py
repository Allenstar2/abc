"""第 3 輪 (a)：REPORT 推薦的替代規格 Vout 1.4 V（s17）沒有量卸載過衝。
PMOS pass 不能吸電流，卸載過衝在 1.6 V 時被 Vin（1.8 V）夾在 ~200 mV；Vout 降低後夾限變成 Vin−Vout。
REF-A 拓樸，CL=100 pF，Cc=5 pF，R1+R2=8 kΩ（與 s17 相同），0→100 mA→0。"""
import json
from ldo_ref import DEFAULT, load_step
R = []
for vout in (1.6, 1.4, 1.2):
    R2 = 8e3 * 0.8 / vout
    p = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=8e3 - R2, R2=R2)
    for te in (1e-9, 10e-9, 100e-9, 1e-6):
        t, vo, vpg, m = load_step(p, 0, 0.1, te, "r3v14", thold=8e-6)
        r = dict(Vout=vout, edge_ns=te * 1e9, undershoot_mV=round(m["undershoot"] * 1e3, 1), overshoot_mV=round(m["overshoot"] * 1e3, 1),
                 overshoot_pct=round(m["overshoot"] / vout * 100, 1), v_peak=round(float(vo[t > 2e-6 + te + 8e-6].max()), 3))
        R.append(r); print(r, flush=True)
json.dump(R, open("res/r3_8_vout14_overshoot.json", "w"), indent=1)
