"""R2-5c：驗證 D3（1 nF/Cc 8 pF/Rz 10 kΩ）在 Rz–Cc 中點有 0.8 pF 寄生時的近不穩定：
(a) |T| 在 1–100 MHz 的形狀；(b) 10→12 mA、1 ns 小步階的時域振鈴（頻率、衰減）。"""
import json, numpy as np
import ldo_ref
from ldo_ref import DEFAULT, loopgain, margins, load_step
_orig = ldo_ref.subckt
def sub(p):
    s = _orig(p); extra = f"Ceax ea 0 {p.get('Ceax', 1e-18)}\n"
    if p["Rz"] > 0: extra += f"Cczx ncz 0 {p.get('Cczx', 1e-18)}\n"
    return s.replace(".ends", extra + ".ends")
ldo_ref.subckt = sub
R = {}
for tag, kw in (("nominal", {}), ("Cncz=0.8p", dict(Cczx=0.8e-12)), ("Cncz=0.4p", dict(Cczx=0.4e-12)), ("Cncz=1.2p", dict(Cczx=1.2e-12)), ("Cncz=0.8p,Rz=5k", dict(Cczx=0.8e-12, Rz=5e3))):
    p = dict(DEFAULT, R1=4e3, R2=4e3, CL=1e-9, Cc=8e-12, Rz=10e3); p.update(kw)
    row = {}
    for IL in (10e-3, 30e-3):
        f, T, v = loopgain(p, IL, "r25c"); mag = 20*np.log10(abs(T)); ph = np.unwrap(np.angle(T))*180/np.pi
        sel = (f > 1e6) & (f < 1e8)
        k = np.argmax(mag[sel]); m = margins(f, T)
        row[f"{IL*1e3:.0f}mA"] = dict(T_at_1M_dB=round(float(np.interp(6, np.log10(f), mag)), 1), T_at_10M_dB=round(float(np.interp(7, np.log10(f), mag)), 1),
                                      T_at_20M_dB=round(float(np.interp(np.log10(2e7), np.log10(f), mag)), 1), peak_1_100MHz_dB=round(float(mag[sel][k]), 1),
                                      peak_f_MHz=round(float(f[sel][k]) / 1e6, 1), pm=round(m["pm"], 1), gm=round(m["gm_db"], 1), ugf_MHz=round(m["ugf"] / 1e6, 2))
    t, vo, vpg, ms = load_step(p, 10e-3, 12e-3, 1e-9, "r25c_tr", thold=2e-6)
    t0 = 2e-6 + 1e-9; sel = (t > t0) & (t < t0 + 1e-6); tt = t[sel]; vv = vo[sel] - vo[sel][-200:].mean()
    # 振鈴：找 zero crossings 估頻率，前 1 µs 內的峰值序列
    zc = np.where(np.diff(np.sign(vv)) != 0)[0]
    fr = (len(zc) - 1) / 2 / (tt[zc[-1]] - tt[zc[0]]) if len(zc) > 3 else 0
    row["step_10to12mA_1ns"] = dict(undershoot_mV=round(ms["undershoot"]*1e3, 2), n_zero_cross_1us=int(len(zc)), ring_f_MHz=round(fr/1e6, 2),
                                    pp_100_300ns_mV=round(float(np.ptp(vo[(t > t0+100e-9) & (t < t0+300e-9)]))*1e3, 2),
                                    pp_300_1000ns_mV=round(float(np.ptp(vo[(t > t0+300e-9) & (t < t0+1000e-9)]))*1e3, 2))
    R[tag] = row; print(tag, row, flush=True)
json.dump(R, open("res/r2_5c_verify.json", "w"), indent=1)
