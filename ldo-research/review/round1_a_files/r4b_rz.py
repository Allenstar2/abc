import json
from ldo_ref import DEFAULT, loopgain, margins, load_step
R = []
for Cc, Rz in ((20e-12, 0), (8e-12, 10e3), (8e-12, 20e3), (8e-12, 40e3), (5e-12, 30e3), (5e-12, 60e3), (10e-12, 20e3)):
    p = dict(DEFAULT, R1=4e3, R2=4e3, CL=1e-9, Cc=Cc, Rz=Rz)
    pms, ugfs, gms = [], [], []
    for IL in (0, 0.2e-3, 1e-3, 10e-3, 100e-3):
        f, T, v = loopgain(p, IL, "r4b_lg"); m = margins(f, T)
        pms.append(round(m["pm"], 1)); ugfs.append(round(m["ugf"]/1e6, 2)); gms.append(round(m["gm_db"], 1))
    r = dict(CL="1nF", Cc_pF=Cc*1e12, Rz_k=Rz/1e3, pm=pms, gm_db=gms, ugf_MHz=ugfs)
    if min(pms) > 45:
        for te in (1e-9, 100e-9, 1e-6):
            t, vo, vpg, ms = load_step(p, 0, 100e-3, te, "r4b_tr", thold=6e-6)
            r[f"us_{te*1e9:g}ns"] = round(ms["undershoot"]*1e3, 1)
    R.append(r); print(r, flush=True)
json.dump(R, open("res/r4b_rz.json", "w"), indent=1)
