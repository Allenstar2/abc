"""第 3 輪 (a)：Vin 短暫掉進 dropout 後回復時的 Vout 過衝（REF-A，CL=100 pF）。
與啟動過衝同一機制：dropout 時 EA 飽和、pg 被拉到底；Vin 回來時 pg 只能以 I_SF/C_pg 往上爬。
ANALYSIS 的線性暫態只做 1.8↔1.98 V（往上），沒有測「掉進 dropout 再回來」。"""
import json, numpy as np
from ldo_ref import DEFAULT, header
from common import run, RES

p = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
R = []
for IL in (10e-3, 100e-3):
    for vlow in (1.70, 1.65, 1.60):
        for te in (100e-9, 1e-6, 10e-6):
            t0 = 2e-6; t1 = t0 + te; t2 = t1 + 3e-6; t3 = t2 + te; tstop = t3 + 6e-6
            tstep = min(te / 20, 2e-9)
            net = header(p, "r3dr") + f"""
VIN vin 0 PWL(0 1.8 {t0} 1.8 {t1} {vlow} {t2} {vlow} {t3} 1.8)
VREF vref 0 0.8
X1 vin vout vref fb fb ldoA
CL vout 0 {p['CL']}
IL vout 0 DC {IL}
.control
tran {tstep} {tstop} 0 {tstep*5}
wrdata {RES}/r3dr_tr.txt v(vout) v(x1.pg)
quit
.endc
.end
"""
            run(net, "r3dr")
            a = np.loadtxt(f"{RES}/r3dr_tr.txt", ndmin=2); t = a[:, 0]; vo = a[:, 1]; pg = a[:, 3]
            pre = vo[(t > t0 - 0.5e-6) & (t < t0)].mean()
            low = vo[(t > t2 - 0.5e-6) & (t < t2)].mean()
            post = vo[t > t3]
            r = dict(IL_mA=IL * 1e3, vin_low=vlow, edge_ns=te * 1e9, vout_pre=round(float(pre), 4),
                     vout_in_dip=round(float(low), 4), pg_in_dip=round(float(pg[(t > t2 - 0.5e-6) & (t < t2)].mean()), 3),
                     overshoot_after_mV=round(float(post.max() - pre) * 1e3, 1))
            R.append(r); print(r, flush=True)
json.dump(R, open(f"{RES}/r3_3_dropout_recovery.json", "w"), indent=1)
