"""REF-B 固定碼迴路增益：開著的 slice 讓 R_out 變小 → 類比迴路 DC 增益下降。"""
import json, numpy as np
from ldo_hybrid import HDEF
from ldo_ref import subckt, margins
from common import run, RES, MODEL

def lg_frozen(k, IL, name):
    p = dict(HDEF)
    sl = "\n".join((f"Ms{i} vout vin vin vin PMOS W={p['Ws']}u L=0.18u" if i > k else
                    f"Ms{i} vout 0 vin vin PMOS W={p['Ws']}u L=0.18u") for i in range(1, p['N'] + 1))
    net = f"""* {name}
.include {MODEL}
{subckt(p)}
VIN vin 0 DC 1.8
VREF vref 0 0.8
X1 vin vout vref fb fbi ldoA
Lbrk fb fbi 1e9
Cbrk fbi acs 1
VAC acs 0 DC 0 AC 1
{sl}
CL vout 0 {p['CL']}
IL vout 0 DC {IL}
.control
op
print v(vout) v(x1.pg)
ac dec 40 10 1e10
let T = -v(fb)/v(fbi)
wrdata {RES}/{name}_T.txt T
quit
.endc
.end
"""
    out = run(net, name)
    a = np.loadtxt(f"{RES}/{name}_T.txt", ndmin=2)
    m = margins(a[:, 0], a[:, 1] + 1j * a[:, 2])
    vpg = [l for l in out.splitlines() if "v(x1.pg)" in l]
    return m, vpg

rows = []
for k, IL in ((0, 0), (0, 15e-3), (3, 45e-3), (5, 70e-3), (7, 95e-3)):
    m, vpg = lg_frozen(k, IL, "x3d")
    rows.append(dict(code=k, IL_mA=IL * 1e3, dc_db=round(m["dc_db"], 1), ugf_MHz=round(m["ugf"] / 1e6, 2), pm=round(m["pm"], 1)))
    print(rows[-1], vpg)
json.dump(rows, open(f"{RES}/x3d_hybrid_loop_frozen.json", "w"), indent=1)
