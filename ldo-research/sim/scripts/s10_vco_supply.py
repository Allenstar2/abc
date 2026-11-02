"""實驗 X5（SerDes 應用連結）：LDO 供電給 ring oscillator 時，Vin 漣波 → VCO 供電漣波 → 週期性 jitter。
1. 7 級 ring（每節點加 30 fF）在 VDD=1.5–1.7 V 的頻率 → Kvdd
2. 解析：峰值 TIE = Kvdd·A/(2π·f_m·f0)，旁波 ≈ 20log(Kvdd·A/(2 f_m)) dBc（窄頻 FM）
3. 共模擬：REF-A（CL=100 pF）供電給 ring，Vin 加 10 mV@1 MHz，量 TIE，對照「理想 1.6 V＋10 mV 漣波（無 LDO）」與解析值
"""
import json, numpy as np
from common import run, MODEL, RES
from ldo_ref import DEFAULT, subckt, psrr

N = 7
def ring(sup):
    s = [f".subckt inv a y vdd\nMn y a 0 0 NMOS W=1u L=0.18u\nMp y a vdd vdd PMOS W=2.5u L=0.18u\nCn y 0 30f\n.ends"]
    for i in range(N):
        s.append(f"Xr{i} n{i} n{(i+1)%N} {sup} inv")
    return "\n".join(s)

def tie_from(t, v, vdd, t0):
    """以 v 穿越 vdd/2 的上升沿算週期，回傳 f0、峰值 TIE（去線性趨勢）。"""
    sel = t > t0; t, v, vdd = t[sel], v[sel], vdd[sel]
    x = v - vdd / 2
    idx = np.where((x[:-1] < 0) & (x[1:] >= 0))[0]
    tc = t[idx] - x[idx] * (t[idx + 1] - t[idx]) / (x[idx + 1] - x[idx])
    k = np.arange(len(tc)); A = np.vstack([k, np.ones_like(k)]).T
    T, b = np.linalg.lstsq(A, tc, rcond=None)[0]
    tie = tc - (k * T + b)
    return 1 / T, float((tie.max() - tie.min()) / 2), len(tc)

R = {}
# 1. f vs VDD
fs = {}
for vdd in (1.5, 1.55, 1.6, 1.65, 1.7):
    net = f"* ring f\n.include {MODEL}\n{ring('vdd')}\nVDD vdd 0 {vdd}\n.ic v(n0)=0\n.control\ntran 2p 40n 0 5p uic\nwrdata {RES}/x5_ring.txt v(n0) v(vdd)\nquit\n.endc\n.end\n"
    run(net, "x5_ring")
    a = np.loadtxt(f"{RES}/x5_ring.txt"); f0, _, n = tie_from(a[:, 0], a[:, 1], a[:, 3], 10e-9)
    fs[vdd] = f0
R["f_vs_vdd_MHz"] = {str(k): round(v / 1e6, 1) for k, v in fs.items()}
Kvdd = (fs[1.65] - fs[1.55]) / 0.1
f0 = fs[1.6]
R["Kvdd_MHz_per_V"] = round(Kvdd / 1e6, 1); R["f0_MHz"] = round(f0 / 1e6, 1)
# ring 平均電流
net = f"* ring I\n.include {MODEL}\n{ring('vdd')}\nVDD vdd 0 1.6\n.ic v(n0)=0\n.control\ntran 2p 40n 0 5p uic\nmeas tran iavg avg i(VDD) from=10n to=40n\nquit\n.endc\n.end\n"
out = run(net, "x5_ring_i")
iavg = [float(l.split("=")[1].split()[0]) for l in out.splitlines() if l.strip().startswith("iavg")][0]
R["ring_Iavg_mA"] = round(-iavg * 1e3, 3)

# 2. 解析：REF-A PSRR（負載≈ring 平均電流）
p = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
f, ps = psrr(p, -iavg, "x5_psr")
A_in = 10e-3
R["analytic"] = []
for fm in (1e5, 1e6, 1e7):
    g = 10 ** (np.interp(np.log10(fm), np.log10(f), ps) / 20)
    for tag, A in (("無LDO(漣波直接上VCO)", A_in), ("經REF-A", A_in * g)):
        R["analytic"].append(dict(fm_MHz=fm / 1e6, path=tag, A_vco_mV=round(A * 1e3, 3),
                                  tie_peak_ps=round(Kvdd * A / (2 * np.pi * fm * f0) * 1e12, 2),
                                  spur_dBc=round(20 * np.log10(Kvdd * A / (2 * fm)), 1), psrr_dB=round(20 * np.log10(g), 1) if tag != "無LDO(漣波直接上VCO)" else 0))

# 3. 共模擬（fm = 1 MHz）
fm = 1e6; tst = 2e-6; tstop = tst + 5e-6
sims = {}
for tag in ("direct", "ldo"):
    if tag == "direct":
        body = f"VDD vdd 0 SIN(1.6 {A_in} {fm} {tst})\n{ring('vdd')}"
    else:
        body = (subckt(p) + f"\nVIN vin 0 SIN(1.8 {A_in} {fm} {tst})\nVREF vref 0 0.8\nX1 vin vdd vref fb fb ldoA\nCL vdd 0 {p['CL']}\n" + ring("vdd"))
    net = f"* x5 {tag}\n.include {MODEL}\n.options reltol=1e-4\n{body}\n.ic v(n0)=0\n.control\ntran 5p {tstop} 0 10p uic\nwrdata {RES}/x5_{tag}.txt v(n0) v(vdd)\nquit\n.endc\n.end\n"
    run(net, f"x5_{tag}", timeout=3000)
    a = np.loadtxt(f"{RES}/x5_{tag}.txt")
    f0s, tie, n = tie_from(a[:, 0], a[:, 1], a[:, 3], tst + 0.5e-6)
    vv = a[:, 3][a[:, 0] > tst + 0.5e-6]
    sims[tag] = dict(f0_MHz=round(f0s / 1e6, 1), tie_peak_ps=round(tie * 1e12, 2), edges=n,
                     vdd_ripple_pp_mV=round(float(np.ptp(vv)) * 1e3, 2))
R["cosim_fm1MHz_Ain10mV"] = sims
json.dump(R, open(f"{RES}/x5_vco_supply.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(R, indent=1, ensure_ascii=False))
