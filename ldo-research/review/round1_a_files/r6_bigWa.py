import json, numpy as np
from hyb2 import HDEF, run_hybrid, step_metrics
R = []
cfgs = {"B Wa=2400 win3-18mA": dict(Wp=2400, VL=1.335, VH=1.455),
        "B Wa=2400 win5-25mA": dict(Wp=2400, VL=1.295, VH=1.43),
        "B Wa=2400 win5-25mA toff300n": dict(Wp=2400, VL=1.295, VH=1.43, t_off=300e-9)}
for name, c in cfgs.items():
    for te in (1e-9, 100e-9, 1e-6):
        p = dict(HDEF, fclk=10e6, **c); t0 = 6e-6
        load = f"IL vout 0 PWL(0 0 1u 0 1.1u 5m {t0} 5m {t0+te} 95m {t0+te+8e-6} 95m {t0+2*te+8e-6} 5m)"
        tt, vo, vpg, code = run_hybrid(p, load, t0+2*te+16e-6, "r6_B", tstep=min(1e-9, te/10))
        m = step_metrics(tt, vo, code, t0, te)
        R.append(dict(cfg=name, edge_ns=te*1e9, **{k: m[k] for k in ("undershoot_mV", "overshoot_during_mV", "overshoot_release_mV", "t_settle10mV_us", "code_end", "v_end")}))
        print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in R[-1].items()}, flush=True)
    # 穩態 limit-cycle 檢查（20/45/70/95 mA 平台）
    p = dict(HDEF, fclk=10e6, **c)
    levels = [20e-3, 45e-3, 70e-3, 95e-3]; hold = 10e-6; pwl = ["0 0"]; t = 1e-6
    for I in levels:
        pwl += [f"{t:.4g} {pwl[-1].split()[1]}", f"{t+100e-9:.4g} {I}"]; t += hold
    tt, vo, vpg, code = run_hybrid(p, "IL vout 0 PWL(" + " ".join(pwl) + ")", t, "r6_lc", tstep=2e-9)
    t0 = 1e-6; pl = []
    for I in levels:
        sel = (tt > t0+hold-5e-6) & (tt < t0+hold-0.05e-6)
        pl.append((I*1e3, int(code[sel][-1]), int(np.count_nonzero(np.diff(code[sel]))), round(float((vo[sel].max()-vo[sel].min())*1e3), 2), round(float(vo[sel].mean()), 4)))
        t0 += hold
    R.append(dict(cfg=name, plateaus=pl)); print(name, pl, flush=True)
json.dump(R, open("res/r6_bigWa.json", "w"), indent=1)
