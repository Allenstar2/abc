"""r3_2 的補充：公平 B 時脈 50 MHz 時的卸載回復（確認回復時間 ≈ 碼數／f_clk 的機制）。"""
import json, numpy as np
from ldo_hybrid import HDEF, run_hybrid
from r3_2_release import rel_metrics
pB = dict(HDEF, Wp=2400, VL=1.331, VH=1.455, fclk=50e6)
R = []
for te in (1e-9, 100e-9):
    t0 = 6e-6; t_rel = t0 + te + 8e-6; tstop = t_rel + te + 10e-6
    load = f"IL vout 0 PWL(0 0 1u 0 1.1u 5m {t0} 5m {t0+te} 95m {t_rel} 95m {t_rel+te} 5m)"
    tt, vo, vpg, code = run_hybrid(pB, load, tstop, "r3rel_B50", tstep=min(1e-9, te / 10))
    r = rel_metrics(tt, vo, t_rel, te, (tstop - 1e-6, tstop)); r.update(arch="fair B (50 MHz)", edge_ns=te * 1e9)
    pre = vo[(tt > t0 - 0.3e-6) & (tt < t0)].mean(); r["undershoot_mV"] = round(float(pre - vo[(tt > t0) & (tt < t_rel)].min()) * 1e3, 1)
    toggles = int(np.count_nonzero(np.diff(code[(tt > tstop - 5e-6)]))); r["toggles_last5us"] = toggles
    R.append(r); print(r, flush=True)
json.dump(R, open("res/r3_2b_release_50M.json", "w"), indent=1)
