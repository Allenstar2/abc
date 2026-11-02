"""「1 nF 慢邊沿反而較差」是否只是 EA slew（I_tail/Cc）造成？保持 gm1 約略不變，提高 tail 電流。"""
import json, numpy as np
from ldo_ref import DEFAULT, loopgain, margins, load_step
R = []
designs = [("100p Cc5p tail20u Win20 (REF-A)", dict(CL=100e-12, Cc=5e-12, tail_mult=2, Win=20)),
           ("1n Cc20p tail20u Win20 (REF-A 1nF)", dict(CL=1e-9, Cc=20e-12, tail_mult=2, Win=20)),
           ("1n Cc20p tail100u Win4", dict(CL=1e-9, Cc=20e-12, tail_mult=10, Win=4)),
           ("1n Cc20p tail100u Win2", dict(CL=1e-9, Cc=20e-12, tail_mult=10, Win=2)),
           ("1n Cc20p tail200u Win2", dict(CL=1e-9, Cc=20e-12, tail_mult=20, Win=2)),
           ("100p Cc5p tail100u Win2", dict(CL=100e-12, Cc=5e-12, tail_mult=10, Win=2)),
           ]
for name, kw in designs:
    p = dict(DEFAULT, R1=4e3, R2=4e3, **kw)
    pms, dcs, ugfs = [], [], []
    for IL in (0, 1e-3, 10e-3, 100e-3):
        f, T, v = loopgain(p, IL, "r4_lg"); m = margins(f, T)
        pms.append(round(m["pm"], 1)); dcs.append(round(m["dc_db"], 1)); ugfs.append(round(m["ugf"]/1e6, 2))
    r = dict(design=name, pm=pms, dc_db=dcs, ugf_MHz=ugfs, vout0=round(v["vout_op"], 4))
    for te in (1e-9, 100e-9, 1e-6):
        t, vo, vpg, ms = load_step(p, 0, 100e-3, te, "r4_tr", thold=6e-6)
        r[f"us_{te*1e9:g}ns"] = round(ms["undershoot"]*1e3, 1)
        r["load_reg_mV"] = round(ms["dv_load_reg"]*1e3, 2)
    R.append(r); print(r, flush=True)
json.dump(R, open("res/r4_1nF.json", "w"), indent=1)
