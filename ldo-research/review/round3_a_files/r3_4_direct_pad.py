"""第 3 輪 (a)：最小可行晶片（MVC）是否需要片上監測 buffer？
不加 buffer，Vout 直接經 pad→bond wire→封裝腳/探棒量測時，探棒端看到的 undershoot 與晶片內真值的比例。
假設 [H]：pad 1 pF、bond wire 2 nH＋0.1 Ω、腳位＋探棒 C_probe（主動探棒 ~4 pF、10× 被動探棒 ~13 pF）、1 MΩ。
另外量 probe 的存在對晶片內真值的影響（探棒反向負載）。REF-A，CL=100 pF，0→100 mA，片上理想電流源負載。"""
import json, numpy as np
from ldo_ref import DEFAULT, header
from common import run, RES

p = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
R = []
for te in (1e-9, 10e-9, 100e-9):
    for cp in (0, 4e-12, 13e-12):
        t0 = 1e-6; t1 = t0 + te; tstop = t1 + 3e-6
        tstep = min(te / 40, 1e-9)
        probe = (f"Cpad vout 0 1p\nLbw vout nbw 2n\nRbw nbw npin 0.1\nCpr npin 0 {cp}\nRpr npin 0 1meg\n") if cp > 0 else "Rdummy vout npin 1\nRpr npin 0 1e12\n"
        net = header(p, "r3dp") + f"""
VIN vin 0 DC 1.8
VREF vref 0 0.8
X1 vin vout vref fb fb ldoA
CL vout 0 {p['CL']}
IL vout 0 PWL(0 0 {t0} 0 {t1} 0.1)
{probe}
.control
tran {tstep} {tstop} 0 {tstep*4}
wrdata {RES}/r3dp_tr.txt v(vout) v(npin)
quit
.endc
.end
"""
        run(net, "r3dp")
        a = np.loadtxt(f"{RES}/r3dp_tr.txt", ndmin=2); t = a[:, 0]; vo = a[:, 1]; vp = a[:, 3]
        pre = vo[(t > t0 - 0.2e-6) & (t < t0)].mean(); prep = vp[(t > t0 - 0.2e-6) & (t < t0)].mean()
        w = t > t0
        us_true = pre - vo[w].min(); us_probe = prep - vp[w].min()
        r = dict(edge_ns=te * 1e9, C_probe_pF=cp * 1e12, undershoot_die_mV=round(float(us_true) * 1e3, 1),
                 undershoot_probe_mV=round(float(us_probe) * 1e3, 1), ratio=round(float(us_probe / us_true), 3))
        R.append(r); print(r, flush=True)
json.dump(R, open(f"{RES}/r3_4_direct_pad.json", "w"), indent=1)
