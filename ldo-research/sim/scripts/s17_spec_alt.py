"""第 2 輪審查 (a) 論點 3 的作者重現：規格本身。
(1) 100 mA 時最低可調節 Vin（Vout 掉 1%）：TT 27 °C 與 SS-like 125 °C
(2) Vout 改 1.4 V（β=0.8/1.4，R1+R2 維持 8 kΩ）：滿載 DC 迴路增益、PSRR@1 kHz/1 MHz、最差 PM"""
import json, os, numpy as np
from ldo_ref import DEFAULT, loopgain, margins, psrr, header
from common import run, RES
SS = os.path.join(RES, "tmp", "model_SSlikeVth50mVTox5.pm")
def min_vin(p, IL=0.1):
    net = header(p, "s17_dc") + f"\nVIN vin 0 1.8\nVREF vref 0 0.8\nX1 vin vout vref fb fb ldoA\nIL vout 0 DC {IL}\n.control\ndc VIN 1.3 1.98 0.002\nwrdata {RES}/s17_dc.txt v(vout)\nquit\n.endc\n.end\n"
    run(net, "s17_dc"); a = np.loadtxt(f"{RES}/s17_dc.txt"); vin, vo = a[:, 0], a[:, 1]
    i = np.where(vo >= 0.99 * vo[-1])[0][0]; return round(float(vin[i]), 3), round(float(vo[-1]), 4)
R = {}
base = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
R["minVin_100mA_TT27"] = min_vin(base)
R["minVin_100mA_SS125"] = min_vin(dict(base, model=SS, temp=125))
for vout, R2 in ((1.6, 4e3), (1.4, 8e3 * 0.8 / 1.4)):
    p = dict(base, R1=8e3 - R2, R2=R2)
    pms = []; dcs = []
    for IL in (0, 1e-3, 100e-3):
        f, T, v = loopgain(p, IL, "s17_lg"); m = margins(f, T); pms.append(round(m["pm"], 1)); dcs.append(round(m["dc_db"], 1))
    f, ps = psrr(p, 100e-3, "s17_psr")
    R[f"Vout{vout}"] = dict(R1=round(8e3 - R2), R2=round(R2), pm=pms, dc_db=dcs,
                           psrr_100mA={f"{fx:g}": round(float(np.interp(np.log10(fx), np.log10(f), ps)), 1) for fx in (1e3, 1e6, 1e7)},
                           minVin_100mA_TT27=min_vin(p), minVin_100mA_SS125=min_vin(dict(p, model=SS, temp=125)))
print(json.dumps(R, indent=1))
json.dump(R, open(f"{RES}/s17_spec_alt.json", "w"), indent=1)
