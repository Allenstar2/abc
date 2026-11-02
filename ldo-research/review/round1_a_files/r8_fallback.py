"""B（Wa=2400）數位 reset（8 片全關、閘極=Vin）時當純類比 LDO：可用負載範圍與穩定度。對照 A（4 mm）。"""
import json, numpy as np
from ldo_ref import DEFAULT, subckt, loopgain, margins
from common import run, RES, MODEL
R = {}
for arch, Wp, sl in (("A 4mm", 4000, False), ("B2400 reset(code=0)", 2400, True), ("B800 reset(code=0)", 800, True)):
    p = dict(DEFAULT, Wp=Wp, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
    slices = "\n".join(f"Ms{i} vout vin vin vin PMOS W=130u L=0.18u" for i in range(1, 9)) if sl else ""
    net = f"* dc\n.include {MODEL}\n{subckt(p)}\nVIN vin 0 1.8\nVREF vref 0 0.8\nX1 vin vout vref fb fb ldoA\n{slices}\nIL vout 0 0\n.control\ndc IL 0 0.2 0.0005\nwrdata {RES}/r8_dc.txt v(vout) v(x1.pg)\nquit\n.endc\n.end\n"
    run(net, "r8_dc"); a = np.loadtxt(f"{RES}/r8_dc.txt"); il = a[:, 0]; vo = a[:, 1]; pg = a[:, 3]
    v0 = vo[0]
    imax16 = il[np.where(vo < v0-0.016)[0][0]] if (vo < v0-0.016).any() else np.nan
    imax50 = il[np.where(vo < v0-0.050)[0][0]] if (vo < v0-0.050).any() else np.nan
    pms = []
    for IL in (0, 1e-3, 10e-3, 30e-3, 50e-3):
        if IL < imax16:
            q = dict(p); 
            # loopgain 不含 slice；slice 關閉時只貢獻漏電與電容，這裡忽略（保守估計 PM 不變）
            f, T, v = loopgain(q, IL, "r8_lg"); pms.append((IL*1e3, round(margins(f, T)["pm"], 1)))
    R[arch] = dict(vout0=round(v0, 4), Imax_within16mV_mA=round(imax16*1e3, 1), Imax_within50mV_mA=round(imax50*1e3, 1),
                   vout_at_50mA=round(float(np.interp(0.05, il, vo)), 4), vout_at_60mA=round(float(np.interp(0.06, il, vo)), 4), pm=pms)
    print(arch, R[arch], flush=True)
json.dump(R, open("res/r8_fallback.json", "w"), indent=1)
