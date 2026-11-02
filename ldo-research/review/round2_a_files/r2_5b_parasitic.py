"""R2-5b：nulling resistor 設計對 ea 節點／Rz–Cc 中點寄生電容的敏感度（佈局後才看得到；學生只有 LTspice、無 PEX）。
Cc 若用 MIM，底板寄生約 5–15% Cc [H]，接在 Rz–Cc 中點（ncz）或 ea。"""
import json, numpy as np
import ldo_ref
from ldo_ref import DEFAULT, loopgain, margins, load_step
_orig = ldo_ref.subckt
def sub(p):
    s = _orig(p)
    extra = f"Ceax ea 0 {p.get('Ceax', 1e-18)}\n"
    if p["Rz"] > 0: extra += f"Cczx ncz 0 {p.get('Cczx', 1e-18)}\n"
    return s.replace(".ends", extra + ".ends")
ldo_ref.subckt = sub
LOADS = [0, 0.3e-3, 1e-3, 3e-3, 10e-3, 30e-3, 50e-3, 100e-3]
DES = {"D1_100p_Cc5_Rz0": dict(CL=100e-12, Cc=5e-12, Rz=0),
       "D2_100p_Cc3_Rz5k": dict(CL=100e-12, Cc=3e-12, Rz=5e3),
       "D3_1n_Cc8_Rz10k": dict(CL=1e-9, Cc=8e-12, Rz=10e3)}
R = {}
for dn, d in DES.items():
    rows = []
    for tag, kw in (("nominal", {}), ("Cea+0.3p", dict(Ceax=0.3e-12)), ("Cea+0.6p", dict(Ceax=0.6e-12)),
                    ("Cncz=10%Cc", dict(Cczx=0.1 * d["Cc"])), ("Cea+0.3p&Cncz=10%Cc", dict(Ceax=0.3e-12, Cczx=0.1 * d["Cc"]))):
        if d["Rz"] == 0 and "Cncz" in tag: continue
        p = dict(DEFAULT, R1=4e3, R2=4e3, **d); p.update(kw)
        pms, gms, ugfs = [], [], []
        for IL in LOADS:
            f, T, v = loopgain(p, IL, "r25b"); m = margins(f, T); pms.append(round(m["pm"], 1)); gms.append(round(m["gm_db"], 1)); ugfs.append(round(m["ugf"] / 1e6, 2))
        row = dict(case=tag, pm=pms, gm_dB=gms, ugf_MHz=ugfs)
        # 時域：10→30 mA（GM 最小附近）100 ns 步階的振鈴
        jm = int(np.argmin(gms)); ILw = LOADS[jm]
        t, vo, vpg, ms = load_step(p, ILw, ILw + 5e-3, 10e-9, "r25b_tr", thold=3e-6)
        sel = (t > 2e-6 + 10e-9 + 1.5e-6) & (t < 2e-6 + 10e-9 + 3e-6)
        row.update(gm_min_at_mA=ILw * 1e3, ripple_after_step_pp_mV=round(float(np.ptp(vo[sel])) * 1e3, 2))
        rows.append(row); print(dn, row, flush=True)
    R[dn] = rows
json.dump(R, open("res/r2_5b_parasitic.json", "w"), indent=1)
