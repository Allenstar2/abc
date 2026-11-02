"""粗略「corner」趨勢檢查（不是真的 corner！）：Vth0 ±50 mV、Tox ±5%、溫度 −40/27/125 °C。
只看趨勢：最差 PM、DC 迴路增益、0→100 mA (1 µs) undershoot、dropout 方向。"""
import os, re, json, itertools, numpy as np
from ldo_ref import DEFAULT, loopgain, margins, load_step
from common import MODEL, RES

os.makedirs(f"{RES}/tmp", exist_ok=True)
base = open(MODEL).read()

def variant(dvthn, dvthp, tox_scale, tag):
    s = base
    s = s.replace("Vth0 = 0.3999", f"Vth0 = {0.3999 + dvthn:.4f}")
    s = s.replace("Vth0 = -0.42", f"Vth0 = {-0.42 - dvthp:.4f}")  # dvthp>0 → |Vthp| 變大（slow）
    s = s.replace("Tox = 4.e-09", f"Tox = {4e-9 * tox_scale:.4e}").replace("Tox = 4.2e-09", f"Tox = {4.2e-9 * tox_scale:.4e}")
    path = f"{RES}/tmp/model_{tag}.pm"; open(path, "w").write(s); return path

cases = {"TT-like(原模型)": (0, 0, 1.0), "SS-like(|Vth|+50mV,Tox+5%)": (0.05, 0.05, 1.05),
         "FF-like(|Vth|-50mV,Tox-5%)": (-0.05, -0.05, 0.95), "SF-like(Vthn+50,|Vthp|-50)": (0.05, -0.05, 1.0),
         "FS-like(Vthn-50,|Vthp|+50)": (-0.05, 0.05, 1.0)}
rows = []
for (cn, (dn, dp, tx)), temp in itertools.product(cases.items(), (-40, 27, 125)):
    mp = variant(dn, dp, tx, re.sub(r"\W", "", cn))
    for cl, cc in ((100e-12, 5e-12), (1e-9, 20e-12)):
        p = dict(DEFAULT, CL=cl, Cc=cc, R1=4e3, R2=4e3, model=mp, temp=temp)
        pms, dcs, vouts = [], [], []
        for IL in (0, 1e-3, 100e-3):
            f, T, v = loopgain(p, IL, "cr_tmp"); m = margins(f, T)
            pms.append(m["pm"]); dcs.append(m["dc_db"]); vouts.append(v.get("vout_op", np.nan))
        t, vo, vpg, ms = load_step(p, 0, 100e-3, 1e-6, "cr_tr", thold=6e-6)
        rows.append(dict(case=cn, temp=temp, CL_pF=cl * 1e12, pm_min=round(min(pms), 1), pm_list=[round(x, 1) for x in pms],
                         dc_db_fullload=round(dcs[-1], 1), vout_0=round(vouts[0], 4), vout_full=round(vouts[-1], 4),
                         undershoot_1us_mV=round(ms["undershoot"] * 1e3, 1)))
        print(rows[-1], flush=True)
json.dump(rows, open(f"{RES}/s6_corners.json", "w"), indent=1, ensure_ascii=False)
