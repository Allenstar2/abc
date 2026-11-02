"""Claim B cross-check: Middlebrook double injection at the vout -> R1 break (different method from gate L-C)."""
import json, numpy as np
from rv import ngspice, refA_core, margins, model, RES
from b1_lg_corners import lg

def mb(temp, dn, dp, IL, CL=1e-9, Cc=8e-12, Rz=10e3):
    core = refA_core(Cc=Cc, Rz=Rz, gate_node='fb').replace("R1 vout fb", "R1 r1t fb")
    common = f".include {model(dn, dp)}\n.options temp={temp} reltol=1e-5 abstol=1e-13 vntol=1e-8\n{core}\nVIN vin 0 DC 1.8\nVREF vref 0 0.8\nCL vout 0 {CL}\nIL vout 0 DC {IL}\n"
    nv = f"mbv_T{temp}_{dn}_{dp}_{IL}"; ni = f"mbi_T{temp}_{dn}_{dp}_{IL}"
    ngspice(f"* {nv}\n{common}Vinj r1t vout DC 0 AC 1\n.control\nac dec 50 10 1e10\nwrdata {RES}/{nv}.txt v(vout) v(r1t)\nquit\n.endc\n.end\n", nv)
    ngspice(f"* {ni}\n{common}Vsa vout j 0\nVsb j r1t 0\nIinj 0 j DC 0 AC 1\n.control\nac dec 50 10 1e10\nwrdata {RES}/{ni}.txt i(Vsa) i(Vsb)\nquit\n.endc\n.end\n", ni)
    a = np.loadtxt(f"{RES}/{nv}.txt"); b = np.loadtxt(f"{RES}/{ni}.txt")
    f = a[:, 0]
    Tv = -(a[:, 1] + 1j * a[:, 2]) / (a[:, 4] + 1j * a[:, 5])
    Ti = -(b[:, 1] + 1j * b[:, 2]) / (b[:, 4] + 1j * b[:, 5])
    T = (Tv * Ti - 1) / (Tv + Ti + 2)
    return margins(f, T)

R = []
for (temp, dn, dp) in ((27, 0, 0), (125, -50, 50), (125, 50, 50), (-40, -50, 50)):
    for IL in (0, 1e-3, 30e-3, 100e-3):
        m = mb(temp, dn, dp, IL); g = lg("D1_1n_Cc8_Rz10k", temp, dn, dp, IL)
        R.append(dict(temp=temp, dn=dn, dp=dp, IL_mA=IL * 1e3, pm_middlebrook=round(m["pm"], 2), pm_gateLC=g["pm"],
                      ugf_mb_MHz=round(m["ugf"] / 1e6, 4), ugf_lc_MHz=g["ugf_MHz"], dc_mb=round(m["dc_db"], 2), dc_lc=g["dc_db"]))
        print(R[-1])
json.dump(R, open(f"{RES}/b4_middlebrook.json", "w"), indent=0)
