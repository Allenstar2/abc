"""R2-11：較大 dropout（Vout 1.4 V）時 A 與公平 B（Wa 2.4 mm、slice 8×130 µm，碼凍結）的 PSRR 差距。
假設：B 的 slice 開啟時閘極 0 V（深 triode），A 的 4 mm pass 在 1.4 V 時接近飽和。70 mA。"""
import json, numpy as np
from common import run, MODEL, RES
from ldo_ref import DEFAULT, subckt, psrr
from ldo_hybrid import HDEF
def at(f, ps, fq): return round(float(np.interp(np.log10(fq), np.log10(f), ps)), 1)
FQ = [1e3, 1e5, 1e6, 1e7]
R = []
for Vout in (1.6, 1.4):
    R1 = (Vout - 0.8) / 200e-6
    pA = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=R1, R2=4e3)
    f, ps = psrr(pA, 70e-3, "r211A"); row = dict(Vout=Vout, A=[at(f, ps, x) for x in FQ])
    pB = dict(HDEF, Wp=2400, R1=R1, R2=4e3)
    for k in (1, 2, 3, 5):
        sl = "\n".join((f"Ms{i} vout vin vin vin PMOS W=130u L=0.18u" if i > k else f"Ms{i} vout 0 vin vin PMOS W=130u L=0.18u") for i in range(1, 9))
        net = f"* psr\n.include {MODEL}\n{subckt(pB)}\nVIN vin 0 DC 1.8 AC 1\nVREF vref 0 0.8\nX1 vin vout vref fb fb ldoA\n{sl}\nCL vout 0 100p\nIL vout 0 DC 70m\n.control\nop\nprint v(vout) v(x1.pg) i(VIN)\nac dec 20 10 1e9\nwrdata {RES}/r211B.txt v(vout)\nquit\n.endc\n.end\n"
        out = run(net, "r211B")
        vo = float([l for l in out.splitlines() if l.strip().startswith("v(vout)")][0].split("=")[1])
        pg = float([l for l in out.splitlines() if l.strip().startswith("v(x1.pg)")][0].split("=")[1])
        a = np.loadtxt(f"{RES}/r211B.txt"); psb = 20 * np.log10(np.hypot(a[:, 1], a[:, 2]))
        row[f"B_code{k}"] = dict(vout=round(vo, 4), vpg=round(pg, 3), psrr=[at(a[:, 0], psb, x) for x in FQ])
    R.append(row); print(row, flush=True)
json.dump(R, open(f"{RES}/r2_11_dropout_AB.json", "w"), indent=1)
