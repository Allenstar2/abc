"""R2-12：量測板上在 Vout 腳位加電容（常見習慣）對 capless LDO 穩定度的影響。
Vout 片上 CL=100 pF；pad→bond wire/封裝 2 nH＋0.1 Ω→板上電容 C_ext（ESR 10 mΩ）。"""
import json, numpy as np
import ldo_ref
from ldo_ref import DEFAULT, margins, header
from common import run, RES
LOADS = [0, 1e-3, 10e-3, 100e-3]
R = []
for Cext in (0, 10e-12, 1e-9, 10e-9, 100e-9, 1e-6):
    for des, kw in (("REF-A 100p/Cc5", dict(CL=100e-12, Cc=5e-12, Rz=0)),):
        p = dict(DEFAULT, R1=4e3, R2=4e3, **kw); pms, gms = [], []
        for IL in LOADS:
            ext = f"Lbw vout npad 2n\nRbw npad nb 0.1\nCext nb nesr {max(Cext,1e-18)}\nResr nesr 0 0.01\n" if Cext > 0 else ""
            net = header(p, "r212") + f"""
VIN vin 0 DC 1.8 AC 0
VREF vref 0 0.8
X1 vin vout vref fb fbi ldoA
Lbrk fb fbi 1e9
Cbrk fbi acs 1
VAC acs 0 DC 0 AC 1
CL vout 0 {p['CL']}
{ext}IL vout 0 DC {IL}
.control
ac dec 40 10 1e10
let T = -v(fb)/v(fbi)
wrdata {RES}/r212_T.txt T
quit
.endc
.end
"""
            run(net, "r212"); a = np.loadtxt(f"{RES}/r212_T.txt"); f = a[:, 0]; T = a[:, 1] + 1j * a[:, 2]
            # 多次穿越：取所有 0 dB 穿越點的最小 PM
            mag = 20 * np.log10(abs(T)); ph = np.unwrap(np.angle(T)) * 180 / np.pi
            idx = np.where(np.sign(mag[:-1]) != np.sign(mag[1:]))[0]
            pmc = [180 + ph[i] for i in idx]
            pms.append(round(float(min(pmc)) if pmc else float("nan"), 1)); gms.append(len(idx))
        R.append(dict(Cext=Cext, design=des, pm_min_over_crossings=pms, n_crossings=gms)); print(R[-1], flush=True)
json.dump(R, open("res/r2_12_offchip.json", "w"), indent=1)
