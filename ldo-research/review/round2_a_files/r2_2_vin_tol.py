"""R2-2：規格 1.8→1.6 V（200 mV dropout）對 Vin 容差的敏感度。
REF-A（Wp=4 mm）DC 掃 Vin，找 |Vout−1.6|<1%（16 mV）在 100 mA 時的最低 Vin；跨 corner/溫度。"""
import json, numpy as np
from common import run, RES
from ldo_ref import DEFAULT, header
from corners import corner
R = []
for cn, temp in (("TT", 27), ("TT", 125), ("SS", 125), ("SS", 27), ("FF", -40), ("SS", -40)):
    for Wp in (4000, 6000):
        p = dict(DEFAULT, Wp=Wp, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3, model=corner(cn), temp=temp)
        row = dict(corner=cn, temp=temp, Wp_um=Wp)
        for IL in (0, 50e-3, 100e-3):
            name = "r22"
            net = header(p, name) + f"""
VIN vin 0 DC 1.8
VREF vref 0 0.8
X1 vin vout vref fb fb ldoA
IL vout 0 DC {IL}
.control
dc VIN 1.5 2.0 0.002
wrdata {RES}/{name}.txt v(vout)
quit
.endc
.end
"""
            run(net, name)
            a = np.loadtxt(f"{RES}/{name}.txt"); vin, vo = a[:, 0], a[:, 1]
            v18 = float(np.interp(1.8, vin, vo))
            ok = np.abs(vo - 1.6) < 0.016
            # 最低 Vin：從 2.0 往下，連續 ok 的最低點
            idx = len(vin) - 1
            while idx > 0 and ok[idx - 1]: idx -= 1
            row[f"IL{IL*1e3:.0f}"] = dict(vout_at_1p8=round(v18, 4), vin_min_1pct=round(float(vin[idx]), 3) if ok[-1] else None,
                                          vout_at_1p71=round(float(np.interp(1.71, vin, vo)), 4), vout_at_1p62=round(float(np.interp(1.62, vin, vo)), 4))
        R.append(row); print(row, flush=True)
json.dump(R, open(f"{RES}/r2_2_vin_tol.json", "w"), indent=1)
