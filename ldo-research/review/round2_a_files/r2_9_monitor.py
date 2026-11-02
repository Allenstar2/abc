"""R2-9：G1 的「片上 Vout 監測 buffer」要多少偏壓才能看見 1 ns 邊沿的 droop？
輸入：REF-A（100 pF）0→100 mA、1 ns / 100 ns 邊沿的 Vout 波形（ideal 負載）；buffer：NMOS source follower（汲極接獨立 1.8 V），
電流槽 I_b，輸出負載 C_pad（主動探棒 ~4 pF 總和；被動 10× 探棒 ~13 pF 總和 [H]）。量測 buffer 輸出的 droop／小訊號增益 vs 真實 droop。
另加 100 pF 片上 decap 的 REF-A 1 nF+Rz 版本不做（只看 buffer）。"""
import json, numpy as np
from common import run, MODEL, RES
from ldo_ref import DEFAULT, load_step
p = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
R = {}
for te in (1e-9, 100e-9):
    t, vo, vpg, ms = load_step(p, 0, 100e-3, te, "r29src", thold=3e-6)
    sel = (t > 1.9e-6) & (t < 2e-6 + te + 1.5e-6)
    tt, vv = t[sel] - 1.9e-6, vo[sel]
    # 降取樣成 PWL
    idx = np.unique(np.concatenate([np.arange(0, len(tt), max(1, len(tt) // 3000)), [len(tt) - 1]]))
    pwl = " ".join(f"{tt[i]:.4e} {vv[i]:.5f}" for i in idx)
    true_droop = float(vv[tt < 0.09e-6].mean() - vv.min())
    rows = []
    for Cp in (4e-12, 13e-12):
        for Ib in (0.3e-3, 1e-3, 3e-3, 10e-3):
            net = f"""* mon
.include {MODEL}
VIN vg 0 PWL({pwl})
VDDB vdb 0 1.8
M1 vdb vg out 0 NMOS W={max(20, Ib*1e6/20):.0f}u L=0.18u
IB out 0 {Ib}
CP out 0 {Cp}
.control
tran {min(te/40, 2e-10)} {tt[-1]:.4e}
wrdata {RES}/r29.txt v(out) v(vg)
quit
.endc
.end
"""
            run(net, "r29"); a = np.loadtxt(f"{RES}/r29.txt"); to, vout_b = a[:, 0], a[:, 1]
            # 小訊號增益：用 DC 前段與穩態後段的差 / 輸入差
            pre_o, pre_i = vout_b[to < 0.08e-6].mean(), a[:, 3][to < 0.08e-6].mean()
            post_o, post_i = vout_b[to > to[-1] - 0.3e-6].mean(), a[:, 3][to > to[-1] - 0.3e-6].mean()
            g = (pre_o - post_o) / (pre_i - post_i) if abs(pre_i - post_i) > 1e-3 else float("nan")
            seen = float(pre_o - vout_b.min())
            rows.append(dict(Cpad_pF=Cp * 1e12, Ib_mA=Ib * 1e3, seen_droop_mV=round(seen * 1e3, 1),
                             seen_over_true=round(seen / true_droop, 3), dc_gain=round(float(g), 3), vout_dc=round(float(pre_o), 3)))
            print(te, rows[-1], flush=True)
    R[f"edge_{te*1e9:.0f}ns"] = dict(true_droop_mV=round(true_droop * 1e3, 1), buffer=rows)
json.dump(R, open(f"{RES}/r2_9_monitor.json", "w"), indent=1)
