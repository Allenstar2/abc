"""Claim B, part 1: loop gain / PM of REF-A variants across load, temperature and |Vth| shifts.
Designs: D1 = CL 1 nF, Cc 8 pF + Rz 10 kΩ (claim); D0 = CL 100 pF, Cc 5 pF, Rz 0 (REF-A reference).
Loop broken at M1 gate with L-C (gate draws no DC current)."""
import json, sys, itertools, numpy as np
from concurrent.futures import ThreadPoolExecutor
from rv import ngspice, grab, refA_core, margins, model, RES

DESIGNS = {"D1_1n_Cc8_Rz10k": dict(CL=1e-9, Cc=8e-12, Rz=10e3),
           "D0_100p_Cc5": dict(CL=100e-12, Cc=5e-12, Rz=0.0)}
LOADS = [0, 1e-4, 1e-3, 3e-3, 10e-3, 30e-3, 50e-3, 100e-3]


def lg(design, temp, dn, dp, IL):
    d = DESIGNS[design]
    name = f"b1_{design}_T{temp}_n{dn:+d}_p{dp:+d}_I{IL*1e3:g}"
    net = f"""* {name}
.include {model(dn, dp)}
.options temp={temp} reltol=1e-5 abstol=1e-13 vntol=1e-8
{refA_core(Cc=d['Cc'], Rz=d['Rz'], gate_node='fbi')}
VIN vin 0 DC 1.8
VREF vref 0 0.8
Lbrk fb fbi 1e9
Cbrk fbi acs 1
VAC acs 0 DC 0 AC 1
CL vout 0 {d['CL']}
IL vout 0 DC {IL}
.control
op
print v(vout) v(pg) v(ea) v(fb)
ac dec 50 10 1e10
wrdata {RES}/{name}.txt v(fb) v(fbi)
quit
.endc
.end
"""
    out = ngspice(net, name)
    a = np.loadtxt(f"{RES}/{name}.txt")
    f = a[:, 0]
    T = -(a[:, 1] + 1j * a[:, 2]) / (a[:, 4] + 1j * a[:, 5])
    m = margins(f, T)
    return dict(design=design, temp=temp, dn=dn, dp=dp, IL_mA=IL * 1e3,
                vout=grab(out, "v(vout)"), vpg=grab(out, "v(pg)"), vea=grab(out, "v(ea)"),
                dc_db=round(m["dc_db"], 2), ugf_MHz=round(m["ugf"] / 1e6, 4), pm=round(m["pm"], 2),
                gm_db=round(m["gm_db"], 2) if np.isfinite(m["gm_db"]) else None,
                n_cross=len(m["crossings"]), crossings=[(round(x[0] / 1e6, 4), round(x[1], 2), x[2]) for x in m["crossings"]])


if __name__ == "__main__":
    jobs = []
    vth = [(0, 0), (50, 50), (-50, -50), (50, -50), (-50, 50)]   # |Vth| shifts (N,P) in mV
    for design in DESIGNS:
        for temp in (-40, 27, 125):
            for dn, dp in vth:
                for IL in LOADS:
                    jobs.append((design, temp, dn, dp, IL))
    with ThreadPoolExecutor(4) as ex:
        R = list(ex.map(lambda j: lg(*j), jobs))
    json.dump(R, open(f"{RES}/b1_lg_corners.json", "w"), indent=0)
    for r in R:
        print(r["design"], r["temp"], r["dn"], r["dp"], r["IL_mA"], f"Vout={r['vout']:.4f} pg={r['vpg']:.3f}",
              r["dc_db"], r["ugf_MHz"], r["pm"], r["gm_db"], r["n_cross"])
