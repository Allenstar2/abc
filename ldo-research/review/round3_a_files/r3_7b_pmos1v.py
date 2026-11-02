"""第 3 輪 (a)：r3_7 的公平對照——同樣 Vout≈1.0 V（β=0.8、洩放 200 µA）時，PMOS-pass（A1 拓樸）表現如何？
用來分辨 1 ns undershoot 的改善是來自 NMOS source follower（架構），還是來自較低 Vout／較大 headroom（規格）。
另量兩者 100 mA 時的最低 Vin（Vout 掉 1%）。"""
import json, numpy as np
from ldo_ref import DEFAULT, loopgain, margins, psrr, load_step, header
from common import run, RES, MODEL
R = []
for Wp in (1000, 2000, 4000):
    p = dict(DEFAULT, Wp=Wp, CL=100e-12, Cc=5e-12, R1=1e3, R2=4e3)
    pms = []
    for IL in (0, 1e-3, 10e-3, 100e-3):
        f, T, v = loopgain(p, IL, "r3p1_lg"); pms.append(round(margins(f, T)["pm"], 1))
    f, ps = psrr(p, 0.1, "r3p1_ps")
    st = {}
    for te in (1e-9, 100e-9, 1e-6):
        t, vo, vpg, m = load_step(p, 0, 0.1, te, "r3p1_tr", thold=8e-6)
        st[f"{te*1e9:g}ns"] = dict(undershoot_mV=round(m["undershoot"] * 1e3, 1), overshoot_mV=round(m["overshoot"] * 1e3, 1))
    net = header(p, "r3p1_dc") + f"\nVIN vin 0 1.8\nVREF vref 0 0.8\nX1 vin vout vref fb fb ldoA\nIL vout 0 DC 0.1\n.control\ndc VIN 1.0 1.98 0.002\nwrdata {RES}/r3p1_dc.txt v(vout)\nquit\n.endc\n.end\n"
    run(net, "r3p1_dc"); a = np.loadtxt(f"{RES}/r3p1_dc.txt"); i = np.where(a[:, 1] >= 0.99 * a[-1, 1])[0][0]
    r = dict(arch="A1 PMOS, Vout 1.0 V", Wp_um=Wp, pm_0_1_10_100mA=pms,
             psrr_100mA={f"{x:g}": round(float(np.interp(np.log10(x), np.log10(f), ps)), 1) for x in (1e3, 1e5, 1e6, 1e7, 1e8)},
             step_0to100mA=st, minVin_100mA=round(float(a[i, 0]), 3))
    R.append(r); print(json.dumps(r), flush=True)
# NMOS（r3_7 的 W=8 mm/16 mm、Cc 50 pF）最低 Vin
from r3_7_nmos100 import core
for Wn in (8000, 16000):
    s = f"* ndc\n.include {MODEL}\n" + core(Wn, 50e-12, 100e-12) + f"VIN vin 0 1.8\nIL vout 0 DC 0.1\n.control\ndc VIN 1.0 1.98 0.002\nwrdata {RES}/r3n_dc.txt v(vout)\nquit\n.endc\n.end\n"
    run(s, "r3n_dc"); a = np.loadtxt(f"{RES}/r3n_dc.txt"); i = np.where(a[:, 1] >= 0.99 * a[-1, 1])[0][0]
    r = dict(arch="A4 NMOS SF, Vout 1.0 V", Wn_um=Wn, minVin_100mA=round(float(a[i, 0]), 3)); R.append(r); print(r)
json.dump(R, open(f"{RES}/r3_7b_pmos1v.json", "w"), indent=1)
