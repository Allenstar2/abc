"""第 3 輪 (a)：卸載（load release）過衝 A vs 公平 B。
s12_fairB.py 只比較了加載 undershoot；本腳本用同一組設定（5→95→5 mA、CL=100 pF、
公平 B：Wa=2.4 mm＋8×130 µm slice、窗口 3–18 mA、10 MHz）量卸載後的過衝峰值與「回到 ±1%/±2% 所需時間」。
機制預期：PMOS pass 不能吸電流；A 只要把 pg 拉回去，B 還要等數位一個時脈關一片 slice。"""
import json, numpy as np
from ldo_ref import DEFAULT, load_step
from ldo_hybrid import HDEF, run_hybrid
from common import RES

def rel_metrics(t, vo, t_rel, te, vfin_window):
    pre = vo[(t > vfin_window[0]) & (t < vfin_window[1])].mean()
    w = t > t_rel
    peak = vo[w].max()
    out = {}
    for tol in (0.016, 0.032):
        bad = np.where((t > t_rel) & (np.abs(vo - pre) > tol))[0]
        out[f"t_rec_{int(tol*1e3)}mV_ns"] = round(float(t[bad[-1]] - (t_rel + te)) * 1e9, 1) if len(bad) else 0.0
    return dict(overshoot_mV=round(float(peak - pre) * 1e3, 1), v_peak=round(float(peak), 4), v_final=round(float(pre), 4), **out)

if __name__ == "__main__":
    pA = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
    pB = dict(HDEF, Wp=2400, VL=1.331, VH=1.455, fclk=10e6)
    R = []
    for te in (1e-9, 100e-9, 1e-6):
        # A
        thold = 8e-6
        t, vo, vpg, m = load_step(pA, 5e-3, 95e-3, te, "r3rel_A", thold=thold, tstop=2e-6 + 2 * te + 2 * thold)
        t_rel = 2e-6 + te + thold
        rA = rel_metrics(t, vo, t_rel, te, (t[-1] - 1e-6, t[-1]))
        rA.update(arch="A (4 mm)", edge_ns=te * 1e9, undershoot_mV=round(m["undershoot"] * 1e3, 1))
        R.append(rA); print(rA, flush=True)
        # 公平 B
        t0 = 6e-6
        t_rel = t0 + te + 8e-6
        tstop = t_rel + te + 10e-6
        load = f"IL vout 0 PWL(0 0 1u 0 1.1u 5m {t0} 5m {t0+te} 95m {t_rel} 95m {t_rel+te} 5m)"
        tt, vo, vpg, code = run_hybrid(pB, load, tstop, "r3rel_B", tstep=min(1e-9, te / 10))
        rB = rel_metrics(tt, vo, t_rel, te, (tstop - 1e-6, tstop))
        pre = vo[(tt > t0 - 0.3e-6) & (tt < t0)].mean()
        rB.update(arch="fair B (10 MHz)", edge_ns=te * 1e9,
                  undershoot_mV=round(float(pre - vo[(tt > t0) & (tt < t_rel)].min()) * 1e3, 1),
                  code_before_release=int(code[(tt < t_rel) & (tt > t_rel - 0.5e-6)][-1]),
                  code_end=int(code[-1]))
        # 碼回到穩態所需時間
        cfin = code[-1]
        ch = np.where((tt > t_rel) & (code != cfin))[0]
        rB["t_code_settle_ns"] = round(float(tt[ch[-1]] - t_rel) * 1e9, 1) if len(ch) else 0.0
        R.append(rB); print(rB, flush=True)
    json.dump(R, open(f"{RES}/r3_2_release.json", "w"), indent=1)
