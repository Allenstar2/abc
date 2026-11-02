"""R2-7：若真實製程 |Vthp| 比 PTM 高 ~0.15 V（PTM L=0.18 PMOS 定電流 Vth≈0.31 V；一般 1.8 V 0.18 µm 製程常見 0.4–0.5 V [H]），
REF-A 的 pass 要多寬才維持 100 mA@200 mV、補償與暫態怎麼變。只平移 PMOS Vth0，NMOS 不動。"""
import json, numpy as np
from common import run, RES
from ldo_ref import DEFAULT, loopgain, margins, load_step, header
from corners import variant
R = []
for dvp, Wp in ((0, 4000), (0.15, 4000), (0.15, 6000), (0.15, 8000)):
    m = variant(0, dvp, 1.0, tag=f"vp{dvp}")
    p = dict(DEFAULT, Wp=Wp, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3, model=m)
    pms = []
    for IL in (0, 1e-3, 10e-3, 100e-3):
        f, T, v = loopgain(p, IL, "r27"); mm = margins(f, T); pms.append(round(mm["pm"], 1))
        if IL == 100e-3: v100 = v["vout_op"]; pg100 = v["vpg_op"]; dc100 = mm["dc_db"]
        if IL == 0: v0 = v["vout_op"]
    u = {}
    for te in (1e-9, 100e-9):
        t, vo, vpg, ms = load_step(p, 0, 100e-3, te, "r27tr", thold=4e-6); u[f"{te*1e9:.0f}ns"] = round(ms["undershoot"] * 1e3, 1)
    row = dict(dVthp_V=dvp, Wp_um=Wp, pm_0_1_10_100mA=pms, vout_0=round(v0, 4), vout_100mA=round(v100, 4), vpg_100mA=round(pg100, 3),
               dc_db_100mA=round(dc100, 1), undershoot_0to100mA=u)
    R.append(row); print(row, flush=True)
json.dump(R, open(f"{RES}/r2_7_vth_real.json", "w"), indent=1)
