"""第 1 輪審查 (c) 的追查：limit cycle 分界點在電路級是否受「同步器延遲」影響。
負載 5→95 mA 細掃（3 mA 一階，每階 6 µs，取後 3 µs），REF-B（Wa=800 µm）寬窗（3–18 mA，比值 1.23）：
 (1) 無同步器，10 MHz（回歸對照） (2) 無同步器，50 MHz（審查者要求補掃）
 (3) 2 級 DFF 同步器，10 MHz（預期分界點 → 3，寬窗會 LC）
 (4) 2 級同步器＋shift register 用 ÷3 時脈（等效 blanking，預期回到無 LC）"""
import json, numpy as np
from ldo_hybrid import HDEF, run_hybrid
from common import RES

levels = np.arange(5e-3, 95.1e-3, 3e-3); hold = 6e-6
pwl = ["0 0"]; t = 1e-6
for I in levels:
    pwl += [f"{t:.6g} {pwl[-1].split()[1]}", f"{t+50e-9:.6g} {I:.6g}"]; t += hold
load = "IL vout 0 PWL(" + " ".join(pwl) + ")"
# 註：初版把 shift register 時脈延後 1 ns，使第 2 級同步器透明（等效 d=1），第 2 輪審查 (c) 指出；已改為同一時脈沿。
cases = {"no-sync 10MHz": dict(fclk=10e6), "no-sync 50MHz": dict(fclk=50e6),
         "sync1 10MHz": dict(fclk=10e6, sync=1), "sync2 10MHz": dict(fclk=10e6, sync=2),
         "sync1 10MHz reg÷2": dict(fclk=10e6, sync=1, reg_div=2), "sync2 10MHz reg÷3": dict(fclk=10e6, sync=2, reg_div=3)}
R = {}
for name, c in cases.items():
    p = dict(HDEF, **c)
    tt, vo, vpg, code = run_hybrid(p, load, t, "s13_tmp", tstep=2e-9)
    bad = []; t0 = 1e-6
    for I in levels:
        sel = (tt > t0 + hold - 3e-6) & (tt < t0 + hold - 0.02e-6)
        tog = int(np.count_nonzero(np.diff(code[sel]))); pp = float(np.ptp(vo[sel]) * 1e3)
        if tog > 0 or pp > 5: bad.append(dict(IL_mA=round(I * 1e3, 1), toggles=tog, vpp_mV=round(pp, 1)))
        t0 += hold
    R[name] = dict(n_levels=len(levels), n_limit_cycle=len(bad), frac=round(len(bad) / len(levels), 2), bad=bad)
    print(name, R[name]["n_limit_cycle"], "/", len(levels), [b["IL_mA"] for b in bad], flush=True)
json.dump(R, open(f"{RES}/s13_hybrid_sync.json", "w"), indent=1, ensure_ascii=False)
