"""R2-5f：CL=100 pF 的設計在同一冷角＋寄生組合（FF −40 °C、Ibias+30%、Cncz=10%Cc、Cea+0.3 pF）下的 PM/GM。"""
import json, numpy as np
import ldo_ref
from ldo_ref import DEFAULT, loopgain, margins
from corners import corner
_orig = ldo_ref.subckt
def sub(p):
    s = _orig(p); extra = f"Ceax ea 0 {p.get('Ceax', 1e-18)}\n"
    if p["Rz"] > 0: extra += f"Cczx ncz 0 {p.get('Cczx', 1e-18)}\n"
    return s.replace(".ends", extra + ".ends")
ldo_ref.subckt = sub
LOADS = [0, 0.3e-3, 1e-3, 3e-3, 10e-3, 30e-3, 50e-3, 100e-3]
R = []
for tag, kw in (("D1 100p/Cc5/Rz0", dict(CL=100e-12, Cc=5e-12, Rz=0)), ("D2 100p/Cc3/Rz5k", dict(CL=100e-12, Cc=3e-12, Rz=5e3)),
                ("100p/Cc3/Rz10k", dict(CL=100e-12, Cc=3e-12, Rz=10e3)), ("100p/Cc5/Rz3k", dict(CL=100e-12, Cc=5e-12, Rz=3e3))):
    for cond, ex in (("nominal", {}), ("FF-40,Ibias+30%,Cncz10%,Cea+0.3p", None)):
        q = dict(DEFAULT, R1=4e3, R2=4e3, **kw)
        if ex is None: q.update(Cczx=0.1 * kw["Cc"], Ceax=0.3e-12, Ibias=13e-6, model=corner("FF"), temp=-40)
        pm, gm = [], []
        for IL in LOADS:
            f, T, v = loopgain(q, IL, "r25f"); m = margins(f, T); pm.append(m["pm"]); gm.append(m["gm_db"])
        R.append(dict(design=tag, cond=cond, pm_min=round(float(np.nanmin(pm)), 1), gm_min=round(float(np.nanmin(gm)), 1))); print(R[-1])
json.dump(R, open("res/r2_5f_100p.json", "w"), indent=1)
