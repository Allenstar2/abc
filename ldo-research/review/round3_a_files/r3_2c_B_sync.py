"""r3_2 的補充：報告自己的 B 設計規則要求「同步器＋每 d+1 個時脈更新」（sync=2、reg_div=3）。
s12 的公平 B 數字（553/154/33 mV）是無同步器的理想 B。這裡量「照報告規則實作」的公平 B：
5→95→5 mA，邊沿 1 ns/100 ns/1 µs，undershoot、卸載過衝與回復時間；時脈 10 / 50 MHz。
注意：作者 ldo_hybrid.py 在 sync>0 時 register 時脈比同步器晚 1 ns（第 2 輪 (c) 指出等效延遲只有 1 拍）；
本腳本沿用作者模組，只把它當「報告規則下」的代表，不是時序精確模型。"""
import json, numpy as np
from ldo_hybrid import HDEF, run_hybrid
from r3_2_release import rel_metrics
R = []
for fclk in (10e6, 50e6):
    pB = dict(HDEF, Wp=2400, VL=1.331, VH=1.455, fclk=fclk, sync=2, reg_div=3)
    for te in (1e-9, 100e-9, 1e-6):
        t0 = 6e-6; t_rel = t0 + te + 8e-6; tstop = t_rel + te + 10e-6
        load = f"IL vout 0 PWL(0 0 1u 0 1.1u 5m {t0} 5m {t0+te} 95m {t_rel} 95m {t_rel+te} 5m)"
        tt, vo, vpg, code = run_hybrid(pB, load, tstop, "r3rel_Bs", tstep=min(1e-9, te / 10))
        r = rel_metrics(tt, vo, t_rel, te, (tstop - 1e-6, tstop))
        pre = vo[(tt > t0 - 0.3e-6) & (tt < t0)].mean()
        r.update(arch=f"fair B sync2+div3 ({fclk/1e6:g} MHz)", edge_ns=te * 1e9,
                 undershoot_mV=round(float(pre - vo[(tt > t0) & (tt < t_rel)].min()) * 1e3, 1),
                 code_at_95mA=int(code[(tt < t_rel) & (tt > t_rel - 0.5e-6)][-1]),
                 toggles_95mA_last3us=int(np.count_nonzero(np.diff(code[(tt > t_rel - 3e-6) & (tt < t_rel)]))),
                 toggles_5mA_last3us=int(np.count_nonzero(np.diff(code[tt > tstop - 3e-6]))))
        R.append(r); print(r, flush=True)
json.dump(R, open("res/r3_2c_B_sync.json", "w"), indent=1)
