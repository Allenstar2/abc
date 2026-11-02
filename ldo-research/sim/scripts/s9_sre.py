"""實驗 X4：首選架構的暫態增強（SRE）是否有效、是否破壞穩定度與 PSRR。"""
import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import ldo_ref
from ldo_ref import margins
from ldo_sre import SDEF, subckt as subckt_sre
from common import RES, FIG

def with_sre(fn, p, *a, **k):
    orig = ldo_ref.subckt
    ldo_ref.subckt = subckt_sre if p.get("sre") else orig
    try:
        return fn(p, *a, **k)
    finally:
        ldo_ref.subckt = orig

R = []
fig, ax = plt.subplots(1, 3, figsize=(15, 4))
for sre in (False, True):
    p = dict(SDEF, sre=sre)
    pms = []; dcs = []
    for IL in (0, 1e-3, 10e-3, 100e-3):
        f, T, v = with_sre(ldo_ref.loopgain, p, IL, "x4_lg"); m = margins(f, T); pms.append(round(m["pm"], 1)); dcs.append(round(m["dc_db"], 1))
        if IL == 0: iq = v["iin"]
    f, ps = with_sre(ldo_ref.psrr, p, 50e-3, "x4_psr")
    trs = {}
    for j, te in enumerate((1e-9, 100e-9, 1e-6)):
        t, vo, vpg, m = with_sre(ldo_ref.load_step, p, 0, 100e-3, te, "x4_tr", thold=6e-6)
        trs[f"{te*1e9:g}ns"] = dict(under=round(m["undershoot"] * 1e3, 1), over=round(m["overshoot"] * 1e3, 1))
        sel = (t > 1.9e-6) & (t < 2e-6 + 2 * te + 8e-6)
        ax[j].plot((t[sel] - 2e-6) * 1e6, vo[sel], label=("REF-A2 (SRE)" if sre else "REF-A") + f": ΔV-={m['undershoot']*1e3:.0f}, ΔV+={m['overshoot']*1e3:.0f} mV")
        ax[j].set_title(f"0↔100 mA, edge {te*1e9:g} ns, CL=100 pF"); ax[j].grid(alpha=.3); ax[j].legend(fontsize=7); ax[j].set_xlabel("t [µs]")
    R.append(dict(sre=sre, pm=pms, dc_db=dcs, Iq_uA=round(iq * 1e6, 1),
                  psrr_50mA={f"{fx:g}": round(float(np.interp(np.log10(fx), np.log10(f), ps)), 1) for fx in (1e3, 1e5, 1e6, 1e7)},
                  transient=trs))
    print(R[-1], flush=True)
plt.tight_layout(); plt.savefig(f"{FIG}/x4_sre.png", dpi=110)
json.dump(R, open(f"{RES}/x4_sre.json", "w"), indent=1)
