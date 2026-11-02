import json, itertools
import numpy as np
from hyb2 import HDEF, run_hybrid, step_metrics
R = []
te = 100e-9; t0 = 6e-6
for Vg, toff, tpd in itertools.product((1.20, 1.25, 1.30, 1.35), (300e-9, 1e-6), (3e-9,)):
    p = dict(HDEF, fclk=10e6, droop=True, droop_src='both', Vdr=1.57, Vgate=Vg, tpd_droop=tpd, tau_chain=2e-9, t_off=toff)
    # 5 mA 穩態 → 5→95 (100 ns) → 95 mA 平台 10 µs → 95→45 → 45 平台 → 45→20 → 20 平台
    load = (f"IL vout 0 PWL(0 0 1u 0 1.1u 5m {t0} 5m {t0+te} 95m {t0+te+10e-6} 95m {t0+2*te+10e-6} 45m "
            f"{t0+2*te+20e-6} 45m {t0+3*te+20e-6} 20m)")
    tstop = t0 + 3*te + 30e-6
    tt, vo, vpg, code = run_hybrid(p, load, tstop, "r1e_B", tstep=1e-9)
    m = step_metrics(tt, vo, code, t0, te, thold=10e-6)
    def plat(a, b):
        w = (tt > a) & (tt < b)
        return round(float((vo[w].max()-vo[w].min())*1e3), 1), int(np.count_nonzero(np.diff(code[w])))
    r = dict(Vgate=Vg, t_off_ns=toff*1e9, tpd_ns=tpd*1e9, undershoot_100ns_mV=round(m["undershoot_mV"], 1),
             overshoot_during_mV=round(m["overshoot_during_mV"], 1),
             pp_5mA=plat(t0-3e-6, t0), pp_95mA=plat(t0+te+5e-6, t0+te+10e-6),
             pp_45mA=plat(t0+2*te+15e-6, t0+2*te+20e-6), pp_20mA=plat(t0+3*te+25e-6, tstop))
    R.append(r); print(r, flush=True)
json.dump(R, open("res/r1e_map.json", "w"), indent=1)
