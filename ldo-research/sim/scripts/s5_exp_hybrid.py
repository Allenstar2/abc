"""實驗 X3：類比主導 hybrid（REF-B）的雙迴路交互作用。
X3a 穩態 limit cycle：dead band（VH−VL 對應的電流窗）vs 每片電流；時脈 1/10/50 MHz。
X3b 大負載步階：REF-A vs REF-B（不同時脈）。
X3c 固定碼 PSRR：開著的 slice 是 Vin→Vout 的低阻抗路徑。
"""
import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ldo_hybrid import HDEF, run_hybrid, subckt
from ldo_ref import DEFAULT, load_step, psrr
from common import run, RES, FIG, MODEL

R = {"X3a": [], "X3b": [], "X3c": {}}
windows = {"wide(3–18mA)": (1.155, 1.39), "narrow(8–14mA)": (1.21, 1.30)}
levels = [20e-3, 45e-3, 70e-3, 95e-3]; hold = 10e-6
pwl = ["0 0"]; t = 1e-6
for I in levels:
    pwl += [f"{t:.4g} {pwl[-1].split()[1]}", f"{t+100e-9:.4g} {I}"]; t += hold
load = "IL vout 0 PWL(" + " ".join(pwl) + ")"
tstop = t
fig, axs = plt.subplots(len(windows), 3, figsize=(16, 7), sharex=True)
for wi, (wn, (VL, VH)) in enumerate(windows.items()):
    for fi, fclk in enumerate((1e6, 10e6, 50e6)):
        p = dict(HDEF, VL=VL, VH=VH, fclk=fclk)
        tt, vo, vpg, code = run_hybrid(p, load, tstop, "x3a_tmp", tstep=min(2e-9, 0.1 / fclk))
        res = dict(window=wn, fclk_MHz=fclk / 1e6, plateaus=[])
        t0 = 1e-6
        for I in levels:
            sel = (tt > t0 + hold - 5e-6) & (tt < t0 + hold - 0.05e-6)
            toggles = int(np.count_nonzero(np.diff(code[sel])))
            res["plateaus"].append(dict(IL_mA=I * 1e3, code_final=int(code[sel][-1]),
                                        code_toggles_last5us=toggles,
                                        vout_pp_mV=float((vo[sel].max() - vo[sel].min()) * 1e3),
                                        vout_mean=float(vo[sel].mean())))
            t0 += hold
        R["X3a"].append(res)
        ax = axs[wi, fi]; ax.plot(tt * 1e6, vo, lw=.6, label="Vout")
        ax2 = ax.twinx(); ax2.step(tt * 1e6, code, "r", lw=.6, where="post"); ax2.set_ylim(-0.5, 9)
        ax.set_title(f"{wn}, fclk={fclk/1e6:g} MHz", fontsize=9); ax.set_ylim(1.45, 1.7); ax.grid(alpha=.3)
        if fi == 0: ax.set_ylabel("Vout [V]")
        if fi == 2: ax2.set_ylabel("code (slices ON)", color="r")
        if wi == len(windows) - 1: ax.set_xlabel("t [µs]")
        print(wn, fclk / 1e6, [(q["IL_mA"], q["code_final"], q["code_toggles_last5us"], round(q["vout_pp_mV"], 1)) for q in res["plateaus"]], flush=True)
plt.suptitle("X3a: hybrid steady state, load steps 20/45/70/95 mA (red = digital code)")
plt.tight_layout(); plt.savefig(f"{FIG}/x3a_limit_cycle.png", dpi=110); plt.close()

# X3b：5 → 95 mA 大步階
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
for j, te in enumerate((1e-9, 100e-9)):
    pA = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
    t, vo, vpg, m = load_step(pA, 5e-3, 95e-3, te, "x3b_A", thold=8e-6)
    R["X3b"].append(dict(arch="REF-A (Wp=4mm)", edge_ns=te * 1e9, undershoot_mV=m["undershoot"] * 1e3,
                         overshoot_mV=m["overshoot"] * 1e3))
    sel = (t > 1.9e-6) & (t < 7e-6); ax[j].plot((t[sel] - 2e-6) * 1e6, vo[sel], label=f"REF-A: ΔV-={m['undershoot']*1e3:.0f} mV")
    for fclk in (10e6, 50e6):
        p = dict(HDEF, fclk=fclk)
        t0 = 6e-6  # 先讓碼在 5 mA 穩定
        load = f"IL vout 0 PWL(0 0 1u 0 1.1u 5m {t0} 5m {t0+te} 95m {t0+te+8e-6} 95m {t0+2*te+8e-6} 5m)"
        tt, vo, vpg, code = run_hybrid(p, load, t0 + 2 * te + 16e-6, "x3b_B", tstep=min(1e-9, te / 10))
        pre = vo[(tt > t0 - 0.3e-6) & (tt < t0)].mean()
        us = pre - vo[(tt > t0) & (tt < t0 + te + 8e-6)].min()
        end = vo[(tt > t0 + te + 7.5e-6) & (tt < t0 + te + 8e-6)].mean()
        os_ = vo[tt > t0 + te + 8e-6].max() - pre
        # 回復時間：Vout 回到 end 的 ±1% 內
        R["X3b"].append(dict(arch=f"REF-B fclk={fclk/1e6:g}MHz", edge_ns=te * 1e9, undershoot_mV=us * 1e3,
                             overshoot_mV=os_ * 1e3, code_after=int(code[(tt > t0 + te + 7e-6)][0])))
        sel = (tt > t0 - 0.1e-6) & (tt < t0 + 5e-6)
        ax[j].plot((tt[sel] - t0) * 1e6, vo[sel], label=f"REF-B {fclk/1e6:g} MHz: ΔV-={us*1e3:.0f} mV")
    ax[j].set_title(f"5→95 mA, edge {te*1e9:g} ns, CL=100 pF"); ax[j].set_xlabel("t [µs]"); ax[j].grid(alpha=.3); ax[j].legend(fontsize=8)
plt.tight_layout(); plt.savefig(f"{FIG}/x3b_hybrid_step.png", dpi=110); plt.close()
for r in R["X3b"]: print(r)

# X3c：固定碼 PSRR（數位碼凍結；k 片導通 + 類比 pass 補足）
def psrr_frozen(k, IL, name):
    p = dict(HDEF)
    sub = subckt(p)
    sl = "\n".join(f"Ms{i} vout g{i} vin vin PMOS W={p['Ws']}u L=0.18u\nVg{i} g{i} 0 {'0' if i <= k else 'DC 0'}" for i in range(1, p['N'] + 1))
    # 關閉的 slice：閘極接 vin（與 vin 同漣波，避免人為注入）
    sl = "\n".join((f"Ms{i} vout vin vin vin PMOS W={p['Ws']}u L=0.18u" if i > k else
                    f"Ms{i} vout g{i} vin vin PMOS W={p['Ws']}u L=0.18u\nVg{i} g{i} 0 0") for i in range(1, p['N'] + 1))
    net = f"""* {name}
.include {MODEL}
{sub}
VIN vin 0 DC 1.8 AC 1
VREF vref 0 0.8
X1 vin vout vref fb fb ldoA
{sl}
CL vout 0 {p['CL']}
IL vout 0 DC {IL}
.control
op
print v(vout) v(x1.pg)
ac dec 20 10 1e9
wrdata {RES}/{name}.txt v(vout)
quit
.endc
.end
"""
    out = run(net, name)
    a = np.loadtxt(f"{RES}/{name}.txt", ndmin=2)
    return a[:, 0], 20 * np.log10(np.hypot(a[:, 1], a[:, 2])), out

fig, ax = plt.subplots(figsize=(7, 4))
pA = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
f, ps = psrr(pA, 70e-3, "x3c_A")
ax.semilogx(f, ps, label="REF-A @70 mA")
R["X3c"]["REF-A_70mA"] = {f"{fx:g}": round(float(np.interp(np.log10(fx), np.log10(f), ps)), 1) for fx in (1e3, 1e5, 1e6, 1e7)}
f, ps, out = psrr_frozen(5, 70e-3, "x3c_B")
ax.semilogx(f, ps, label="REF-B @70 mA, code=5 frozen")
R["X3c"]["REF-B_70mA_code5"] = {f"{fx:g}": round(float(np.interp(np.log10(fx), np.log10(f), ps)), 1) for fx in (1e3, 1e5, 1e6, 1e7)}
ax.set_xlabel("f [Hz]"); ax.set_ylabel("PSRR [dB]"); ax.grid(True, which="both", alpha=.3); ax.legend()
plt.tight_layout(); plt.savefig(f"{FIG}/x3c_psrr_frozen.png", dpi=110); plt.close()
print(R["X3c"])
json.dump(R, open(f"{RES}/x3_hybrid.json", "w"), indent=1, ensure_ascii=False)
