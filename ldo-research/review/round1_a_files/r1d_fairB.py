import json
import numpy as np
from hyb2 import HDEF, run_hybrid, step_metrics
from ldo_ref import DEFAULT, load_step
R = []
# REF-A 對照（同一步階 5→95 mA）
for te in (1e-9, 10e-9, 100e-9, 1e-6):
    pA = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
    t, vo, vpg, m = load_step(pA, 5e-3, 95e-3, te, "r1d_A", thold=8e-6)
    R.append(dict(cfg="REF-A 4mm", edge_ns=te*1e9, undershoot_mV=m["undershoot"]*1e3, overshoot_release_mV=m["overshoot"]*1e3))
    print(R[-1], flush=True)
cfgs = {
 "B+gated droop(Vout<1.57 & pg<1.35; 3ns; 2ns)": dict(droop=True, droop_src='both', Vdr=1.57, Vgate=1.35, tpd_droop=3e-9, tau_chain=2e-9, t_off=300e-9),
 "B+gated droop(Vout<1.57 & pg<1.30; 3ns; 2ns)": dict(droop=True, droop_src='both', Vdr=1.57, Vgate=1.30, tpd_droop=3e-9, tau_chain=2e-9, t_off=300e-9),
 "B+gated droop(Vout<1.57 & pg<1.35; 5ns; 3ns)": dict(droop=True, droop_src='both', Vdr=1.57, Vgate=1.35, tpd_droop=5e-9, tau_chain=3e-9, t_off=300e-9),
 "B+gated droop(Vout<1.57 & pg<1.35; 10ns; 5ns)": dict(droop=True, droop_src='both', Vdr=1.57, Vgate=1.35, tpd_droop=10e-9, tau_chain=5e-9, t_off=300e-9),
}
for te in (1e-9, 10e-9, 100e-9, 1e-6):
    for name, c in cfgs.items():
        p = dict(HDEF, fclk=10e6, **c)
        t0 = 6e-6
        load = f"IL vout 0 PWL(0 0 1u 0 1.1u 5m {t0} 5m {t0+te} 95m {t0+te+8e-6} 95m {t0+2*te+8e-6} 5m)"
        tt, vo, vpg, code = run_hybrid(p, load, t0 + 2*te + 16e-6, "r1d_B", tstep=min(1e-9, te/10))
        m = step_metrics(tt, vo, code, t0, te)
        pre = (tt > t0-3e-6) & (tt < t0)
        m["pre_pp_mV"] = float((vo[pre].max()-vo[pre].min())*1e3); m["pre_code_changes"] = int(np.count_nonzero(np.diff(code[pre])))
        post = (tt > t0+2*te+12e-6)
        m["post_pp_mV"] = float((vo[post].max()-vo[post].min())*1e3); m["post_code_changes"] = int(np.count_nonzero(np.diff(code[post])))
        R.append(dict(cfg=name, edge_ns=te*1e9, **m))
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in R[-1].items()}, flush=True)
json.dump(R, open("res/r1d_fairB.json", "w"), indent=1)
