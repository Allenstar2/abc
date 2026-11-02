"""第 2 輪審查 (a) 量測風險的作者重現：量測板在 Vout 腳位加電容對 capless LDO（REF-A）穩定度的影響。
片上 CL=100 pF；pad→bond wire 2 nH＋0.1 Ω→板上 C_ext（ESR 10 mΩ）[H：封裝參數為假設值]。"""
import json, numpy as np
from ldo_ref import DEFAULT, margins, header
from common import run, RES
p = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
R = []
for Cext in (0, 1e-9, 10e-9, 100e-9, 1e-6):
    pms = []
    for IL in (0, 1e-3, 10e-3, 100e-3):
        ext = f"Lbw vout npad 2n\nRbw npad nb 0.1\nCext nb nesr {Cext}\nResr nesr 0 0.01\n" if Cext > 0 else ""
        net = header(p, "s18") + f"\nVIN vin 0 DC 1.8\nVREF vref 0 0.8\nX1 vin vout vref fb fbi ldoA\nLbrk fb fbi 1e9\nCbrk fbi acs 1\nVAC acs 0 DC 0 AC 1\nCL vout 0 {p['CL']}\n{ext}IL vout 0 DC {IL}\n.control\nac dec 40 10 1e10\nlet T = -v(fb)/v(fbi)\nwrdata {RES}/s18_T.txt T\nquit\n.endc\n.end\n"
        run(net, "s18"); a = np.loadtxt(f"{RES}/s18_T.txt"); m = margins(a[:, 0], a[:, 1] + 1j * a[:, 2]); pms.append(round(m["pm"], 1))
    R.append(dict(Cext_nF=Cext * 1e9, pm_0_1_10_100mA=pms, pm_min=min(pms))); print(R[-1], flush=True)
json.dump(R, open(f"{RES}/s18_offchip_cap.json", "w"), indent=1)
