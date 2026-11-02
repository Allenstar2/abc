"""R2-5h：EA 輸入對 gm1 在各條件下的值 → 平台迴路增益 β·gm1·Rz 的推導檢查。"""
import json
from common import run, RES
from ldo_ref import DEFAULT, header
from corners import corner
R = {}
for tag, kw in (("TT27", {}), ("FF-40_Ibias+30%", dict(model=corner("FF"), temp=-40, Ibias=13e-6)), ("SS125_Ibias-30%", dict(model=corner("SS"), temp=125, Ibias=7e-6))):
    p = dict(DEFAULT, R1=4e3, R2=4e3, CL=1e-9, Cc=8e-12, Rz=10e3); p.update(kw)
    net = header(p, "r25h") + f"\nVIN vin 0 DC 1.8\nVREF vref 0 0.8\nX1 vin vout vref fb fb ldoA\nIL vout 0 DC 10m\n.control\nop\nprint @m.x1.m1[gm] @m.x1.m2[gm]\nquit\n.endc\n.end\n"
    out = run(net, "r25h")
    gm = [float(l.split("=")[1]) for l in out.splitlines() if "[gm]" in l and "=" in l]
    R[tag] = dict(gm1_uS=round(gm[0] * 1e6, 1), beta_gm1_Rz10k=round(0.5 * gm[0] * 1e4, 2), beta_gm1_Rz3k=round(0.5 * gm[0] * 3e3, 2),
                  GM_pred_Rz10k_dB=round(-20 * __import__("math").log10(0.5 * gm[0] * 1e4), 1), GM_pred_Rz3k_dB=round(-20 * __import__("math").log10(0.5 * gm[0] * 3e3), 1))
    print(tag, R[tag])
R["ring_pred_MHz_Rz10k_Cp0.8p"] = round(1 / (2 * 3.14159 * 10e3 * 0.8e-12) / 1e6, 1)
json.dump(R, open("res/r2_5h_gm1.json", "w"), indent=1)
print(R["ring_pred_MHz_Rz10k_Cp0.8p"])
