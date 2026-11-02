import json, itertools
import numpy as np
from hyb2 import HDEF, run_hybrid, step_metrics
R = []
te = 100e-9; t0 = 6e-6
cfgs = [("REF-B (no droop, toff=1ns)", dict()), ("B no droop, toff=300ns", dict(t_off=300e-9))]
for Vg, toff in itertools.product((1.20, 1.25, 1.30, 1.35), (300e-9, 1e-6)):
    cfgs.append((f"gated droop pg<{Vg}, toff={toff*1e9:g}ns", dict(droop=True, droop_src='both', Vdr=1.57, Vgate=Vg, tpd_droop=3e-9, tau_chain=2e-9, t_off=toff)))
for name, c in cfgs:
    p = dict(HDEF, fclk=10e6, **c)
    load = (f"IL vout 0 PWL(0 0 1u 0 1.1u 5m {t0} 5m {t0+te} 95m {t0+te+10e-6} 95m {t0+2*te+10e-6} 45m "
            f"{t0+2*te+20e-6} 45m {t0+3*te+20e-6} 20m)")
    tstop = t0 + 3*te + 30e-6
    tt, vo, vpg, code = run_hybrid(p, load, tstop, "r1f_B", tstep=1e-9)
    m = step_metrics(tt, vo, code, t0, te, thold=10e-6)
    def plat(a, b):
        w = (tt > a) & (tt < b)
        return dict(mean=round(float(vo[w].mean()), 4), pp=round(float((vo[w].max()-vo[w].min())*1e3), 1),
                    dcode=int(np.count_nonzero(np.diff(code[w]))), code=int(code[w][-1]))
    r = dict(cfg=name, undershoot_100ns_mV=round(m["undershoot_mV"], 1),
             p5=plat(t0-3e-6, t0), p95=plat(t0+te+5e-6, t0+te+10e-6), p45=plat(t0+2*te+15e-6, t0+2*te+20e-6), p20=plat(t0+3*te+25e-6, tstop))
    ok = all(abs(r[k]["mean"]-1.598) < 0.01 and r[k]["pp"] < 20 for k in ("p5", "p95", "p45", "p20"))
    r["all_plateaus_ok(|ΔV|<10mV, pp<20mV)"] = ok
    R.append(r); print(r, flush=True)
json.dump(R, open("res/r1f_map2.json", "w"), indent=1)
