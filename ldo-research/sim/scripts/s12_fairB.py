"""第 1 輪審查 (a) 的反例重現（作者獨立重寫，不用審查者的 hyb2.py）：
「公平」的 REF-B：類比 pass 加到 Wa=2400 µm（總寬 2400+8×130=3440 µm < REF-A 4000 µm），
窗口取 Wa 的 I–V 上 3 mA 與 18 mA 對應的閘壓。比較 5→95 mA 步階、20/45/70/95 mA 穩態、PSRR@1 kHz（70 mA，碼凍結）。"""
import json, numpy as np
from common import run, MODEL, RES
from ldo_hybrid import HDEF, run_hybrid
from ldo_ref import DEFAULT, load_step, psrr, subckt

def vg_at(W, targets):
    net = f"* iv\n.include {MODEL}\nVS s 0 1.8\nVD d 0 1.6\nVG g 0 1.0\nM1 d g s s PMOS W={W}u L=0.18u\n.control\ndc VG 0.6 1.79 0.001\nwrdata {RES}/s12_iv.txt i(VS)\nquit\n.endc\n.end\n"
    run(net, "s12_iv"); a = np.loadtxt(f"{RES}/s12_iv.txt"); vg, i = a[:, 0], -a[:, 1] * 1e3
    return {t: float(vg[np.argmin(abs(i - t))]) for t in targets}

R = {}
Wa = 2400
v = vg_at(Wa, (3, 18)); VH, VL = v[3], v[18]
R["Wa_um"] = Wa; R["VH_3mA"] = VH; R["VL_18mA"] = VL
pB = dict(HDEF, Wp=Wa, VL=VL, VH=VH, fclk=10e6)
pA = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
R["step"] = []
for te in (1e-9, 100e-9, 1e-6):
    t, vo, vpg, m = load_step(pA, 5e-3, 95e-3, te, "s12_A", thold=8e-6)
    a_us = m["undershoot"] * 1e3
    t0 = 6e-6
    load = f"IL vout 0 PWL(0 0 1u 0 1.1u 5m {t0} 5m {t0+te} 95m {t0+te+8e-6} 95m {t0+2*te+8e-6} 5m)"
    tt, vo, vpg, code = run_hybrid(pB, load, t0 + 2 * te + 16e-6, "s12_B", tstep=min(1e-9, te / 10))
    pre = vo[(tt > t0 - 0.3e-6) & (tt < t0)].mean()
    b_us = (pre - vo[(tt > t0) & (tt < t0 + te + 8e-6)].min()) * 1e3
    R["step"].append(dict(edge_ns=te * 1e9, A_undershoot_mV=round(a_us, 1), B_fair_undershoot_mV=round(float(b_us), 1)))
    print(R["step"][-1], flush=True)
# 穩態平台
levels = [20e-3, 45e-3, 70e-3, 95e-3]; hold = 10e-6; pwl = ["0 0"]; t = 1e-6
for I in levels:
    pwl += [f"{t:.4g} {pwl[-1].split()[1]}", f"{t+100e-9:.4g} {I}"]; t += hold
tt, vo, vpg, code = run_hybrid(pB, "IL vout 0 PWL(" + " ".join(pwl) + ")", t, "s12_lc", tstep=2e-9)
pl = []; t0 = 1e-6
for I in levels:
    sel = (tt > t0 + hold - 5e-6) & (tt < t0 + hold - 0.05e-6)
    pl.append(dict(IL_mA=I * 1e3, code=int(code[sel][-1]), toggles=int(np.count_nonzero(np.diff(code[sel]))),
                   vpp_mV=round(float(np.ptp(vo[sel])) * 1e3, 2), vout=round(float(vo[sel].mean()), 4)))
    t0 += hold
R["plateaus"] = pl; print(pl)
# PSRR 碼凍結（70 mA → 碼 = round((70-~10)/12.2)≈ 依穩態結果）
k = [q["code"] for q in pl if q["IL_mA"] == 70][0]
sl = "\n".join((f"Ms{i} vout vin vin vin PMOS W=130u L=0.18u" if i > k else f"Ms{i} vout 0 vin vin PMOS W=130u L=0.18u") for i in range(1, 9))
net = f"* psr\n.include {MODEL}\n{subckt(pB)}\nVIN vin 0 DC 1.8 AC 1\nVREF vref 0 0.8\nX1 vin vout vref fb fb ldoA\n{sl}\nCL vout 0 100p\nIL vout 0 DC 70m\n.control\nac dec 20 10 1e9\nwrdata {RES}/s12_psr.txt v(vout)\nquit\n.endc\n.end\n"
run(net, "s12_psr"); a = np.loadtxt(f"{RES}/s12_psr.txt")
psB = 20 * np.log10(np.hypot(a[:, 1], a[:, 2])); fB = a[:, 0]
fA, psA = psrr(pA, 70e-3, "s12_psrA")
R["psrr_1kHz_70mA"] = dict(A=round(float(np.interp(3, np.log10(fA), psA)), 1), B_fair=round(float(np.interp(3, np.log10(fB), psB)), 1), code=k)
print(R["psrr_1kHz_70mA"])
json.dump(R, open(f"{RES}/s12_fairB.json", "w"), indent=1)
