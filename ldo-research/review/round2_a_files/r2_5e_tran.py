"""R2-5e：(a) D3（1 nF/Cc 8 p/Rz 10 k）在 FF −40 °C、Ibias+30%、Cncz=0.8 pF、Cea+0.3 pF 的時域：是否持續振盪；
(b) 穩健設計點（Cc 16 p/Rz 3 k、Cc 12 p/Rz 5 k）與 D3、REF-A 的 0→100 mA undershoot（1/100/1000 ns），看「1 nF＋Rz 全面優於 REF-A」在穩健設計下是否還成立。"""
import json, numpy as np
import ldo_ref
from ldo_ref import DEFAULT, load_step
from corners import corner
_orig = ldo_ref.subckt
def sub(p):
    s = _orig(p); extra = f"Ceax ea 0 {p.get('Ceax', 1e-18)}\n"
    if p["Rz"] > 0: extra += f"Cczx ncz 0 {p.get('Cczx', 1e-18)}\n"
    return s.replace(".ends", extra + ".ends")
ldo_ref.subckt = sub
R = {}
p = dict(DEFAULT, R1=4e3, R2=4e3, CL=1e-9, Cc=8e-12, Rz=10e3, Cczx=0.8e-12, Ceax=0.3e-12, Ibias=13e-6, model=corner("FF"), temp=-40)
out = {}
for I1 in (3e-3, 10e-3, 30e-3):
    t, vo, vpg, ms = load_step(p, I1, I1 + 2e-3, 1e-9, "r25e_osc", thold=6e-6)
    t0 = 2e-6
    w = lambda a, b: vo[(t > t0 + a) & (t < t0 + b)]
    out[f"{I1*1e3:.0f}mA"] = dict(pp_before_step_mV=round(float(np.ptp(vo[(t > 1e-6) & (t < t0)])) * 1e3, 2),
                                  pp_4_6us_after_mV=round(float(np.ptp(w(4e-6, 6e-6))) * 1e3, 2))
R["D3_FFm40_Ibias+30_parasitic"] = out; print(out, flush=True)
R["undershoot"] = []
for tag, kw in (("REF-A 100p/Cc5/Rz0", dict(CL=100e-12, Cc=5e-12, Rz=0)), ("D3 1n/Cc8/Rz10k(第1輪)", dict(CL=1e-9, Cc=8e-12, Rz=10e3)),
                ("1n/Cc12/Rz5k", dict(CL=1e-9, Cc=12e-12, Rz=5e3)), ("1n/Cc16/Rz3k", dict(CL=1e-9, Cc=16e-12, Rz=3e3)),
                ("1n/Cc20/Rz0(REF-A 1nF)", dict(CL=1e-9, Cc=20e-12, Rz=0))):
    q = dict(DEFAULT, R1=4e3, R2=4e3, **kw); u = {}
    for te in (1e-9, 100e-9, 1e-6):
        t, vo, vpg, ms = load_step(q, 0, 100e-3, te, "r25e_u", thold=6e-6); u[f"{te*1e9:.0f}ns"] = round(ms["undershoot"] * 1e3, 1)
    R["undershoot"].append(dict(design=tag, undershoot_0to100mA_mV=u)); print(R["undershoot"][-1], flush=True)
json.dump(R, open("res/r2_5e_tran.json", "w"), indent=1, ensure_ascii=False)
