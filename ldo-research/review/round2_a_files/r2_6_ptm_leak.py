"""R2-6：PTM PMOS（L=0.18 µm）的 Vth、DIBL、Ioff、次臨界斜率。用來判斷 v2 列的「B 高溫輕載漏電優勢」與 A 的 +46 mV 失效有多少是模型造成。
定電流法 Vth：|Id| = 0.1 µA·W/L。W=10 µm。"""
import json, numpy as np
from common import run, MODEL, RES
from corners import corner
R = {}
W, L = 10, 0.18
for cn in ("TT", "SF"):
    for temp in (27, 125):
        row = {}
        for vsd in (0.05, 0.2, 1.8):
            net = f"* p\n.include {corner(cn)}\n.options temp={temp}\nVS s 0 1.8\nVD d 0 {1.8-vsd}\nVG g 0 1.8\nM1 d g s s PMOS W={W}u L={L}u\n.control\ndc VG 1.8 0.6 -0.002\nwrdata {RES}/r26.txt i(VS)\nquit\n.endc\n.end\n"
            run(net, "r26"); a = np.loadtxt(f"{RES}/r26.txt"); vsg = 1.8 - a[:, 0]; i = np.abs(a[:, 1])
            ith = 0.1e-6 * W / L
            vth = float(np.interp(ith, i, vsg))
            ioff = float(i[0]) / W
            # 次臨界斜率（mV/dec）在 Ioff~Ith 之間
            sel = (i > ioff * W * 3) & (i < ith / 3)
            S = float(1e3 / np.polyfit(vsg[sel], np.log10(i[sel]), 1)[0]) if sel.sum() > 3 else float("nan")
            row[f"vsd{vsd}"] = dict(vth_cc_V=round(vth, 3), ioff_pA_per_um=round(ioff * 1e12, 1), S_mV_dec=round(S, 1),
                                    i_at_vsg41mV_nA_per_um=round(float(np.interp(0.041, vsg, i)) / W * 1e9, 2))
        row["DIBL_mV_per_V"] = round((row["vsd0.05"]["vth_cc_V"] - row["vsd1.8"]["vth_cc_V"]) / 1.75 * 1e3, 1)
        row["pass4mm_ioff_vsd0.15_uA_est"] = round(row["vsd0.2"]["ioff_pA_per_um"] * 4000 * 1e-6, 2)
        R[f"{cn}_{temp}C"] = row; print(cn, temp, row, flush=True)
json.dump(R, open(f"{RES}/r2_6_ptm_leak.json", "w"), indent=1)
