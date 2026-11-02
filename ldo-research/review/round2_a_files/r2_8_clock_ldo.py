"""R2-8：若專題轉向「為 ring oscillator / clock 供電」（負載 ≤10 mA，主要指標 1–100 MHz PSRR），
REF-A 拓樸的哪些旋鈕有用？比較 10 mA 負載下的 PSRR：
 pass 依 100 mA 設計（4 mm）vs 依 10 mA 設計（400 µm）；CL 100 pF vs 1 nF（Cc 8 p、Rz 5 k）；Vout 1.6 vs 1.2 V。
另：NMOS source-follower pass 在 Vin=1.8 V 的閘極需求（含 body effect）。"""
import json, numpy as np
from common import run, MODEL, RES
from ldo_ref import DEFAULT, loopgain, margins, psrr, load_step
def at(f, ps, fq): return round(float(np.interp(np.log10(fq), np.log10(f), ps)), 1)
FQ = [1e3, 1e5, 1e6, 1e7, 1e8]
CASES = [("Wp4000_100p_1.6V", dict(Wp=4000, CL=100e-12, Cc=5e-12, Rz=0, Vout=1.6)),
         ("Wp400_100p_1.6V", dict(Wp=400, CL=100e-12, Cc=5e-12, Rz=0, Vout=1.6)),
         ("Wp400_1n_Rz5k_1.6V", dict(Wp=400, CL=1e-9, Cc=8e-12, Rz=5e3, Vout=1.6)),
         ("Wp4000_1n_Rz5k_1.6V", dict(Wp=4000, CL=1e-9, Cc=8e-12, Rz=5e3, Vout=1.6)),
         ("Wp200_100p_1.2V", dict(Wp=200, CL=100e-12, Cc=5e-12, Rz=0, Vout=1.2)),
         ("Wp200_1n_Rz5k_1.2V", dict(Wp=200, CL=1e-9, Cc=8e-12, Rz=5e3, Vout=1.2))]
R = {"freqs_Hz": FQ, "cases": []}
for tag, c in CASES:
    Vout = c.pop("Vout"); R1 = (Vout - 0.8) / 200e-6
    p = dict(DEFAULT, R1=R1, R2=4e3, **c)
    pms = []
    for IL in (0, 1e-3, 10e-3):
        f, T, v = loopgain(p, IL, "r28lg"); pms.append(round(margins(f, T)["pm"], 1))
        if IL == 10e-3: vo10 = v["vout_op"]
    f, ps = psrr(p, 10e-3, "r28ps")
    t, vo, vpg, ms = load_step(p, 1e-3, 10e-3, 10e-9, "r28tr", thold=3e-6)
    row = dict(case=tag, pm_0_1_10mA=pms, vout_10mA=round(vo10, 4), psrr_10mA=[at(f, ps, x) for x in FQ],
               undershoot_1to10mA_10ns_mV=round(ms["undershoot"] * 1e3, 1))
    R["cases"].append(row); print(row, flush=True)
# NMOS pass 閘極需求：Vout=1.6/1.2/1.0 V、10 mA、W=400 µm，body 接地（無 deep n-well）
nm = {}
for vout in (1.6, 1.2, 1.0, 0.8):
    net = f"* n\n.include {MODEL}\nVD d 0 1.8\nVS s 0 {vout}\nVG g 0 2\nM1 d g s 0 NMOS W=400u L=0.18u\n.control\ndc VG {vout} 3.3 0.002\nwrdata {RES}/r28n.txt i(VD)\nquit\n.endc\n.end\n"
    run(net, "r28n"); a = np.loadtxt(f"{RES}/r28n.txt"); vg, i = a[:, 0], -a[:, 1]
    nm[f"Vout{vout}"] = dict(Vgate_for_10mA=round(float(np.interp(10e-3, i, vg)), 3), Vgate_for_100mA_W4000_equiv=round(float(np.interp(10e-3, i, vg)), 3))
R["nmos_pass_gate_needed_10mA_W400"] = nm
print(nm)
json.dump(R, open(f"{RES}/r2_8_clock_ldo.json", "w"), indent=1)
