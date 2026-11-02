import json, sys
from ldo_ref import DEFAULT, load_step
from hyb2 import HDEF, run_hybrid, step_metrics
R = []
for te in (1e-9, 100e-9):
    pA = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
    t, vo, vpg, m = load_step(pA, 5e-3, 95e-3, te, "r0_A", thold=8e-6)
    R.append(dict(arch="REF-A", edge_ns=te*1e9, undershoot_mV=m["undershoot"]*1e3, overshoot_rel_mV=m["overshoot"]*1e3))
    print(R[-1], flush=True)
    p = dict(HDEF, fclk=10e6)
    t0 = 6e-6
    load = f"IL vout 0 PWL(0 0 1u 0 1.1u 5m {t0} 5m {t0+te} 95m {t0+te+8e-6} 95m {t0+2*te+8e-6} 5m)"
    tt, vo, vpg, code = run_hybrid(p, load, t0 + 2*te + 16e-6, "r0_B", tstep=min(1e-9, te/10))
    R.append(dict(arch="REF-B 10MHz (repro)", edge_ns=te*1e9, **step_metrics(tt, vo, code, t0, te)))
    print(R[-1], flush=True)
json.dump(R, open("res/r0_baseline.json", "w"), indent=1)
