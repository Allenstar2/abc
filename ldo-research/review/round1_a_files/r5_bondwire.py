"""Vin 經 bond wire（R=0.1 Ω, L=1 nH）+ 片上 Vin decap 時的 5→95 mA 步階。A 與 B（REF-B 原設計）都跑。"""
import json, numpy as np
from ldo_ref import DEFAULT, header
from hyb2 import HDEF, run_hybrid, step_metrics
from common import run, RES
def stepA(p, I1, I2, te, name, vinnet, thold=8e-6):
    t0 = 2e-6; t1 = t0+te; t2 = t1+thold; t3 = t2+te; tstop = t3+thold; tstep = min(te/20, 2e-9)
    net = header(p, name) + f"""
{vinnet}
VREF vref 0 {p['Vref']}
X1 vin vout vref fb fb ldoA
CL vout 0 {p['CL']}
IL vout 0 PWL(0 {I1} {t0} {I1} {t1} {I2} {t2} {I2} {t3} {I1})
.control
tran {tstep} {tstop} 0 {tstep*5}
wrdata {RES}/{name}_tr.txt v(vout) v(vin)
quit
.endc
.end
"""
    run(net, name)
    a = np.loadtxt(f"{RES}/{name}_tr.txt", ndmin=2); t = a[:, 0]; vo = a[:, 1]; vi = a[:, 3]
    pre = vo[(t > t0-0.2e-6) & (t < t0)].mean(); w = (t > t0) & (t < t2)
    return dict(undershoot_mV=round(float((pre-vo[w].min())*1e3), 1), vin_min=round(float(vi[w].min()), 3),
                ring_pp_late_mV=round(float((vo[(t > t1+1e-6) & (t < t2)].max()-vo[(t > t1+1e-6) & (t < t2)].min())*1e3), 2))
R = []
nets = {"ideal Vin": "VIN vin 0 DC 1.8",
        "1nH+0.1Ω, Cin=200p": "VIN vbrd 0 DC 1.8\nRbw vbrd vbw 0.1\nLbw vbw vin 1n\nCin vin 0 200p",
        "1nH+0.1Ω, Cin=1n": "VIN vbrd 0 DC 1.8\nRbw vbrd vbw 0.1\nLbw vbw vin 1n\nCin vin 0 1n",
        "2nH+0.2Ω, Cin=1n": "VIN vbrd 0 DC 1.8\nRbw vbrd vbw 0.2\nLbw vbw vin 2n\nCin vin 0 1n"}
for nn, vn in nets.items():
    for te in (1e-9, 100e-9):
        pA = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
        r = dict(arch="REF-A", vin=nn, edge_ns=te*1e9, **stepA(pA, 5e-3, 95e-3, te, "r5_A", vn)); R.append(r); print(r, flush=True)
        p = dict(HDEF, fclk=10e6); t0 = 6e-6
        load = f"IL vout 0 PWL(0 0 1u 0 1.1u 5m {t0} 5m {t0+te} 95m {t0+te+8e-6} 95m)"
        # hybrid netlist 內 VIN 行替換
        import hyb2
        net = hyb2.hybrid_netlist(p, load, t0+te+8e-6, min(1e-9, te/10), "r5_B").replace("VIN vin 0 DC 1.8", vn)
        run(net, "r5_B", timeout=3000)
        a = np.loadtxt(f"{RES}/r5_B_tr.txt", ndmin=2); tt = a[:, 0]; vo = a[:, 1]
        pre = vo[(tt > t0-0.3e-6) & (tt < t0)].mean(); us = pre - vo[tt > t0].min()
        r = dict(arch="REF-B 10MHz", vin=nn, edge_ns=te*1e9, undershoot_mV=round(float(us*1e3), 1)); R.append(r); print(r, flush=True)
json.dump(R, open("res/r5_bondwire.json", "w"), indent=1, ensure_ascii=False)
