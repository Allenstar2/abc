"""R2-5d：CL=1 nF 的 Cc×Rz 設計窗口，要求同時滿足：標稱最差 PM、含寄生（Cncz=10%Cc、Cea+0.3 pF）最差 GM、
以及 SS 125 °C＋被動 −15/+20% 組合的最差 PM。β·gm1·Rz（平台迴路增益）一併列出。"""
import json, itertools, numpy as np
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
def worst(p):
    pm, gm = [], []
    for IL in LOADS:
        f, T, v = loopgain(p, IL, "r25d"); m = margins(f, T); pm.append(m["pm"]); gm.append(m["gm_db"])
    return round(float(np.nanmin(pm)), 1), round(float(np.nanmin(gm)), 1)
R = []
gm1 = 184e-6; beta = 0.5
for Cc, Rz in itertools.product((8e-12, 12e-12, 16e-12), (3e3, 5e3, 7e3, 10e3)):
    base = dict(DEFAULT, R1=4e3, R2=4e3, CL=1e-9, Cc=Cc, Rz=Rz)
    nom = worst(base)
    par = worst(dict(base, Cczx=0.1 * Cc, Ceax=0.3e-12))
    cmb = worst(dict(base, Rz=Rz * 0.8, CL=1.2e-9, Cc=Cc * 0.85, Ibias=7e-6, model=corner("SS"), temp=125))
    cold = worst(dict(base, Cczx=0.1 * Cc, Ceax=0.3e-12, Ibias=13e-6, model=corner("FF"), temp=-40))
    row = \
          {"Cc_pF": Cc * 1e12, "Rz_k": Rz / 1e3, "beta_gm1_Rz": round(beta * gm1 * Rz, 2), "nominal_pm_gm": nom, "parasitic_pm_gm": par,
           "SS125_passive_combo_pm_gm": cmb, "FFm40_Ibias+30%_parasitic_pm_gm": cold}
    R.append(row); print(row, flush=True)
json.dump(R, open("res/r2_5d_window.json", "w"), indent=1)
