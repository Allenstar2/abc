import json, numpy as np
from ldo_ref import DEFAULT, loopgain, margins, load_step
loads = (0, 50e-6, 0.2e-3, 0.5e-3, 1e-3, 2e-3, 5e-3, 10e-3, 20e-3, 50e-3, 100e-3)
R = []
for CL, Cc, Rz in ((1e-9, 8e-12, 10e3), (1e-9, 8e-12, 7e3), (1e-9, 10e-12, 10e3), (100e-12, 5e-12, 0), (100e-12, 5e-12, 3e3), (100e-12, 3e-12, 5e3), (100e-12, 3e-12, 10e3), (100e-12, 2e-12, 10e3)):
    p = dict(DEFAULT, R1=4e3, R2=4e3, CL=CL, Cc=Cc, Rz=Rz)
    pms, gms = [], []
    for IL in loads:
        f, T, v = loopgain(p, IL, "r4c_lg"); m = margins(f, T)
        pms.append(round(m["pm"], 1)); gms.append(round(m["gm_db"], 1))
    r = dict(CL_pF=CL*1e12, Cc_pF=Cc*1e12, Rz_k=Rz/1e3, pm_min=min(pms), gm_min=min(gms), pm=pms)
    if min(pms) > 45 and min(gms) > 6:
        for te in (1e-9, 100e-9, 1e-6):
            t, vo, vpg, ms = load_step(p, 0, 100e-3, te, "r4c_tr", thold=6e-6)
            r[f"us_{te*1e9:g}ns"] = round(ms["undershoot"]*1e3, 1)
            if te == 100e-9:
                # 振鈴檢查：負載 100 mA 平台最後 3 µs 的 p-p
                w = (t > 2e-6+te+3e-6) & (t < 2e-6+te+6e-6)
                r["pp_plateau_mV"] = round(float((vo[w].max()-vo[w].min())*1e3), 3)
        # 輕載小步階 0→1 mA 100 ns 的 settling（看 doublet 長尾）
        t, vo, vpg, ms = load_step(p, 0, 1e-3, 100e-9, "r4c_sm", thold=6e-6)
        r["us_0to1mA_mV"] = round(ms["undershoot"]*1e3, 1)
    R.append(r); print(r, flush=True)
json.dump(R, open("res/r4c_rz_fine.json", "w"), indent=1)
