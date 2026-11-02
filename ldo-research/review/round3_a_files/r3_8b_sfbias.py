"""第 3 輪 (a)：卸載過衝的修法檢查——提高 SF buffer 偏壓（buf_mult：50→100→200 µA）對 Vout 1.4/1.6 V 過衝、undershoot、最差 PM、Iq 的影響。"""
import json, numpy as np
from ldo_ref import DEFAULT, load_step, loopgain, margins
R = []
for vout in (1.6, 1.4):
    R2 = 8e3 * 0.8 / vout
    for bm in (5, 10, 20):
        p = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=8e3 - R2, R2=R2, buf_mult=bm)
        pms = []
        for IL in (0, 1e-3, 10e-3, 100e-3):
            f, T, v = loopgain(p, IL, "r3sf_lg"); pms.append(round(margins(f, T)["pm"], 1))
            if IL == 0: iq = v["iin"]
        st = {}
        for te in (1e-9, 100e-9, 1e-6):
            t, vo, vpg, m = load_step(p, 0, 0.1, te, "r3sf", thold=8e-6)
            st[f"{te*1e9:g}ns"] = [round(m["undershoot"] * 1e3, 1), round(m["overshoot"] * 1e3, 1)]
        r = dict(Vout=vout, I_SF_uA=bm * 10, Iq_noload_uA=round(iq * 1e6, 1), pm_min=min(pms), pm_0_1_10_100mA=pms, under_over_mV=st)
        R.append(r); print(json.dumps(r), flush=True)
json.dump(R, open("res/r3_8b_sfbias.json", "w"), indent=1)
