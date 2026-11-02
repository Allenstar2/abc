import json
from hyb2 import HDEF, run_hybrid, step_metrics
R = []
cfgs = [dict(droop_src='vout', Vdr=1.57, tpd_droop=3e-9, tau_chain=2e-9),
        dict(droop_src='vout', Vdr=1.57, tpd_droop=1e-9, tau_chain=1e-9),
        dict(droop_src='vout', Vdr=1.57, tpd_droop=10e-9, tau_chain=5e-9),
        dict(droop_src='vout', Vdr=1.55, tpd_droop=3e-9, tau_chain=2e-9),
        dict(droop_src='pg', VLL=1.12, tpd_droop=3e-9, tau_chain=2e-9)]
for te in (1e-9, 10e-9, 100e-9, 1e-6):
    for c in cfgs:
        p = dict(HDEF, fclk=10e6, droop=True, **c)
        t0 = 6e-6
        load = f"IL vout 0 PWL(0 0 1u 0 1.1u 5m {t0} 5m {t0+te} 95m {t0+te+8e-6} 95m {t0+2*te+8e-6} 5m)"
        tt, vo, vpg, code = run_hybrid(p, load, t0 + 2*te + 16e-6, "r1b_B", tstep=min(1e-9, te/10))
        m = step_metrics(tt, vo, code, t0, te)
        R.append(dict(edge_ns=te*1e9, **c, **m))
        print({k: (round(v*1e9,1) if k in ('tpd_droop','tau_chain') else round(v, 3) if isinstance(v, float) else v) for k, v in R[-1].items()}, flush=True)
json.dump(R, open("res/r1b_fairB_vout.json", "w"), indent=1)
