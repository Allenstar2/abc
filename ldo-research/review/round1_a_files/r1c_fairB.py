import json, sys
import numpy as np
from hyb2 import HDEF, run_hybrid, step_metrics
R = []
cfgs = {
 "B+vdroop(3ns,2ns) toff=300ns": dict(droop=True, droop_src='vout', Vdr=1.57, tpd_droop=3e-9, tau_chain=2e-9, t_off=300e-9),
 "B+vdroop(3ns,1ns) toff=300ns": dict(droop=True, droop_src='vout', Vdr=1.57, tpd_droop=3e-9, tau_chain=1e-9, t_off=300e-9),
 "B+vdroop(5ns,2ns) toff=1us":   dict(droop=True, droop_src='vout', Vdr=1.57, tpd_droop=5e-9, tau_chain=2e-9, t_off=1e-6),
 "B+pgdroop(1.12V,3ns,2ns) toff=300ns": dict(droop=True, droop_src='pg', VLL=1.12, tpd_droop=3e-9, tau_chain=2e-9, t_off=300e-9),
 "B toff=300ns (no droop)": dict(t_off=300e-9),
}
for te in (1e-9, 100e-9, 1e-6):
    for name, c in cfgs.items():
        p = dict(HDEF, fclk=10e6, **c)
        t0 = 6e-6
        load = f"IL vout 0 PWL(0 0 1u 0 1.1u 5m {t0} 5m {t0+te} 95m {t0+te+8e-6} 95m {t0+2*te+8e-6} 5m)"
        tt, vo, vpg, code = run_hybrid(p, load, t0 + 2*te + 16e-6, "r1c_B", tstep=min(1e-9, te/10))
        m = step_metrics(tt, vo, code, t0, te)
        # 步階前 3 µs 的穩態檢查（5 mA）
        pre = (tt > t0-3e-6) & (tt < t0)
        m["pre_pp_mV"] = float((vo[pre].max()-vo[pre].min())*1e3); m["pre_code_changes"] = int(np.count_nonzero(np.diff(code[pre])))
        # 卸載後 8 µs 的穩態
        post = (tt > t0+2*te+12e-6)
        m["post_pp_mV"] = float((vo[post].max()-vo[post].min())*1e3); m["post_code_changes"] = int(np.count_nonzero(np.diff(code[post]))); m["post_mean"]=float(vo[post].mean())
        R.append(dict(cfg=name, edge_ns=te*1e9, **m))
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in R[-1].items()}, flush=True)
json.dump(R, open("res/r1c_fairB.json", "w"), indent=1)
