import json, itertools
from hyb2 import HDEF, run_hybrid, step_metrics
R = []
cfgs = [dict(tpd_droop=3e-9, tau_chain=2e-9, VLL=1.0),
        dict(tpd_droop=3e-9, tau_chain=1e-9, VLL=1.0),
        dict(tpd_droop=10e-9, tau_chain=5e-9, VLL=1.0),
        dict(tpd_droop=3e-9, tau_chain=2e-9, VLL=0.9),
        dict(tpd_droop=20e-9, tau_chain=10e-9, VLL=1.0)]
for te in (1e-9, 100e-9):
    for c in cfgs:
        p = dict(HDEF, fclk=10e6, droop=True, **c)
        t0 = 6e-6
        load = f"IL vout 0 PWL(0 0 1u 0 1.1u 5m {t0} 5m {t0+te} 95m {t0+te+8e-6} 95m {t0+2*te+8e-6} 5m)"
        tt, vo, vpg, code = run_hybrid(p, load, t0 + 2*te + 16e-6, "r1_B", tstep=min(1e-9, te/10))
        m = step_metrics(tt, vo, code, t0, te)
        R.append(dict(arch="B+droop", edge_ns=te*1e9, **{k: (v*1e9 if k != 'VLL' else v) for k, v in c.items()}, **m))
        print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in R[-1].items()}, flush=True)
json.dump(R, open("res/r1_fairB_step.json", "w"), indent=1)
