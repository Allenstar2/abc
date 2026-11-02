"""第 2 輪審查 (a) 反例的作者獨立重現：Rz 補償在角落＋寄生下是否失穩。
角落：FF-like（|Vth|−50 mV、Tox−5%）−40 °C、Ibias +30%、Cc 底板寄生 Cp=10%·Cc（接在 Rz–Cc 中點 ncz 對地）。
比較：Rz=0（純 Miller）、Rz=3 kΩ、Rz=10 kΩ。"""
import json, os, numpy as np
import ldo_ref
from ldo_ref import DEFAULT, loopgain, margins, load_step
from common import RES
orig = ldo_ref.subckt
FF = os.path.join(RES, "tmp", "model_FFlikeVth50mVTox5.pm")
def sub_cp(p):
    s = orig(p)
    if p.get("Rz", 0) > 0 and p.get("Cp", 0) > 0:
        s = s.replace(".ends", f"Cpb ncz 0 {p['Cp']}\n.ends")
    return s
ldo_ref.subckt = sub_cp
R = []
loads = (0, 0.2e-3, 1e-3, 10e-3, 30e-3, 100e-3)
for CL, Cc, Rz in ((1e-9, 8e-12, 10e3), (1e-9, 8e-12, 3e3), (1e-9, 20e-12, 0), (100e-12, 3e-12, 10e3), (100e-12, 3e-12, 5e3), (100e-12, 5e-12, 0)):
    for cname, extra in (("nominal", {}), ("FF-40C,Ibias+30%,Cp=10%Cc", dict(model=FF, temp=-40, Ibias=13e-6, Cp=0.1 * Cc))):
        p = dict(DEFAULT, CL=CL, Cc=Cc, Rz=Rz, R1=4e3, R2=4e3, **extra)
        pms = [round(margins(*loopgain(p, IL, "s16_lg")[:2])["pm"], 1) for IL in loads]
        row = dict(CL_pF=CL * 1e12, Cc_pF=Cc * 1e12, Rz_k=Rz / 1e3, corner=cname, pm_by_load=dict(zip([f"{x*1e3:g}mA" for x in loads], pms)), pm_min=min(pms))
        if cname == "nominal":
            row["undershoot_1ns_100ns_1us_mV"] = [round(load_step(p, 0, 0.1, te, "s16_tr", thold=6e-6)[3]["undershoot"] * 1e3, 1) for te in (1e-9, 100e-9, 1e-6)]
        R.append(row); print(row, flush=True)
ldo_ref.subckt = orig
json.dump(R, open(f"{RES}/s16_rz_robust.json", "w"), indent=1)
