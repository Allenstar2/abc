"""第 3 輪 (a)：Vref 由外部提供時的 PSRR 量測陷阱。
若量測板用 Vin 的電阻分壓產生 Vref（學生最容易做的接法），Vin 的注入漣波經 Vref×(1/β)=2 直接到 Vout。
比較：(a) 獨立理想 Vref（報告的模擬條件）；(b) 板上分壓 Vin×0.8/1.8（10 kΩ/8 kΩ）；
(c) 分壓＋1 µF；(d) 分壓＋10 µF。REF-A，CL=100 pF，0 mA 與 100 mA。"""
import json, numpy as np
from ldo_ref import DEFAULT, header
from common import run, RES

p = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
modes = {"ideal_Vref": "VREF vref 0 0.8",
         "divider": "Rd1 vin vref 10k\nRd2 vref 0 8k",
         "divider+1uF": "Rd1 vin vref 10k\nRd2 vref 0 8k\nCd vref 0 1u",
         "divider+10uF": "Rd1 vin vref 10k\nRd2 vref 0 8k\nCd vref 0 10u"}
fx = (100, 1e3, 1e4, 1e5, 1e6)
R = []
for IL in (0, 100e-3):
    for mn, ref in modes.items():
        net = header(p, "r3vr") + f"""
VIN vin 0 DC 1.8 AC 1
{ref}
X1 vin vout vref fb fb ldoA
CL vout 0 {p['CL']}
IL vout 0 DC {IL}
.control
ac dec 20 10 1e8
wrdata {RES}/r3vr.txt v(vout)
quit
.endc
.end
"""
        run(net, "r3vr")
        a = np.loadtxt(f"{RES}/r3vr.txt", ndmin=2); f = a[:, 0]; ps = 20 * np.log10(np.hypot(a[:, 1], a[:, 2]))
        r = dict(IL_mA=IL * 1e3, vref=mn, **{f"{x:g}Hz": round(float(np.interp(np.log10(x), np.log10(f), ps)), 1) for x in fx})
        R.append(r); print(r, flush=True)
json.dump(R, open(f"{RES}/r3_5_vref_path.json", "w"), indent=1)
