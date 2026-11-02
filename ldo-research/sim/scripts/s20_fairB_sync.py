"""第 3 輪審查 (a) 論點 1 的作者重現：照報告規則（2 級同步器＋shift register ÷3）的公平 B，
5→95 mA（100 ns 邊沿）undershoot 與卸載後回到 ±1% 的時間，對 REF-A。"""
import json, numpy as np
from ldo_hybrid import HDEF, run_hybrid
from ldo_ref import DEFAULT, header
from common import run, RES
s12 = json.load(open(f"{RES}/s12_fairB.json"))
te = 100e-9; t0 = 6e-6; hold = 8e-6
def metrics(t, vo, t0, te):
    pre = vo[(t > t0 - 0.3e-6) & (t < t0)].mean()
    us = pre - vo[(t > t0) & (t < t0 + te + hold)].min()
    trel = t0 + te + hold + te
    fin = vo[t > t[-1] - 0.5e-6].mean()
    idx = np.where((t > trel) & (np.abs(vo - fin) > 0.01 * fin))[0]
    rec = (t[idx[-1]] - trel) if len(idx) else 0.0
    os_ = vo[t > trel - te].max() - pre
    dip = fin - vo[t > trel].min()   # 卸載後低於最終值的下陷（slice 逐片移除造成；第 3 輪審查 (c) 指出）
    return dict(undershoot_mV=round(float(us) * 1e3, 1), overshoot_mV=round(float(os_) * 1e3, 1), recovery_1pct_us=round(float(rec) * 1e6, 3),
                post_release_dip_below_final_mV=round(float(dip) * 1e3, 1))
R = {}
load = f"IL vout 0 PWL(0 0 1u 0 1.1u 5m {t0} 5m {t0+te} 95m {t0+te+hold} 95m {t0+2*te+hold} 5m)"
tstop = t0 + 2 * te + hold + 10e-6
for name, extra in (("B_fair_nosync", {}), ("B_fair_sync2_div3", dict(sync=2, reg_div=3))):
    p = dict(HDEF, Wp=s12["Wa_um"], VL=s12["VL_18mA"], VH=s12["VH_3mA"], fclk=10e6, **extra)
    tt, vo, vpg, code = run_hybrid(p, load, tstop, "s20_B", tstep=1e-9)
    R[name] = metrics(tt, vo, t0, te); print(name, R[name], flush=True)
pA = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
net = header(pA, "s20_A") + f"\nVIN vin 0 1.8\nVREF vref 0 0.8\nX1 vin vout vref fb fb ldoA\nCL vout 0 100p\n{load}\n.control\ntran 1n {tstop} 0 5n\nwrdata {RES}/s20_A.txt v(vout)\nquit\n.endc\n.end\n"
run(net, "s20_A"); a = np.loadtxt(f"{RES}/s20_A.txt")
R["A"] = metrics(a[:, 0], a[:, 1], t0, te); print("A", R["A"])
json.dump(R, open(f"{RES}/s20_fairB_sync.json", "w"), indent=1)
