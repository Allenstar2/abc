"""第 3 輪 (a)：檢查 REPORT「1 ns、100 mA、100 pF，任何架構都做不到小於 ~200 mV」的下限。
最理想的「無迴路」快速路徑：NMOS source-follower pass，閘極由理想電壓源釘住（等於無限快的閘極驅動），
undershoot ≈ ΔVgs(I_min→100 mA)（含 body effect）＋邊沿期間的電荷缺口。也測 PMOS pass 閘極理想釘住後的響應（等於迴路無限快但需 ΔVg）。"""
import json, numpy as np
from common import run, MODEL, RES
R = []
for W in (4000, 8000, 16000):
    for te in (1e-9, 0.1e-9):
        # 閘極 Vg 先用 DC 找出 Vout=1.0 V@0.2 mA 的值
        net = f"* nfl\n.include {MODEL}\nVIN vin 0 1.8\nVG g 0 1.5\nM1 vin g vout 0 NMOS W={W}u L=0.18u\nIL vout 0 0.2m\n.control\ndc VG 0.8 1.8 0.001\nwrdata {RES}/r3fl_dc.txt v(vout)\nquit\n.endc\n.end\n"
        run(net, "r3fl_dc"); a = np.loadtxt(f"{RES}/r3fl_dc.txt"); vg = float(a[np.argmin(abs(a[:, 1] - 1.0)), 0])
        t0 = 1e-9
        net = f"* nfl\n.include {MODEL}\nVIN vin 0 1.8\nVG g 0 {vg}\nM1 vin g vout 0 NMOS W={W}u L=0.18u\nCL vout 0 100p\nIL vout 0 PWL(0 0.2m {t0} 0.2m {t0+te} 100.2m)\n.ic v(vout)=1.0\n.control\ntran {te/50} 60n 0 {te/50}\nwrdata {RES}/r3fl_tr.txt v(vout)\nquit\n.endc\n.end\n"
        run(net, "r3fl_tr"); a = np.loadtxt(f"{RES}/r3fl_tr.txt"); t, vo = a[:, 0], a[:, 1]
        pre = vo[(t > 0.5e-9) & (t < t0)].mean(); vmin = vo[t > t0].min(); vend = vo[-50:].mean()
        r = dict(pass_type="NMOS SF, ideal gate", W_um=W, edge_ns=te * 1e9, Vg=round(vg, 3), undershoot_mV=round((pre - vmin) * 1e3, 1),
                 static_dV_mV=round((pre - vend) * 1e3, 1))
        R.append(r); print(r, flush=True)
json.dump(R, open(f"{RES}/r3_6_floor.json", "w"), indent=1)
