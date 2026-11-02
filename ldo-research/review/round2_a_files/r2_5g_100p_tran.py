"""R2-5g：CL=100 pF 的穩健 Rz 點（Cc 5 p/Rz 3 k）與第 1 輪的 100p/Cc3/Rz10k、REF-A 的 0→100 mA undershoot。"""
import json
from ldo_ref import DEFAULT, load_step
R = []
for tag, kw in (("REF-A 100p/Cc5/Rz0", dict(Cc=5e-12, Rz=0)), ("100p/Cc3/Rz10k(第1輪,冷角不穩)", dict(Cc=3e-12, Rz=10e3)),
                ("100p/Cc3/Rz5k(GM 4 dB@冷角)", dict(Cc=3e-12, Rz=5e3)), ("100p/Cc5/Rz3k(穩健)", dict(Cc=5e-12, Rz=3e3))):
    q = dict(DEFAULT, R1=4e3, R2=4e3, CL=100e-12, **kw); u = {}
    for te in (1e-9, 100e-9, 1e-6):
        t, vo, vpg, ms = load_step(q, 0, 100e-3, te, "r25g", thold=6e-6); u[f"{te*1e9:.0f}ns"] = round(ms["undershoot"] * 1e3, 1)
    R.append(dict(design=tag, undershoot_0to100mA_mV=u)); print(R[-1], flush=True)
json.dump(R, open("res/r2_5g_100p_tran.json", "w"), indent=1, ensure_ascii=False)
