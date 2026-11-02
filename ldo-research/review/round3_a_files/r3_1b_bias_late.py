"""r3_1 補充：外部偏壓（IBIAS pad）比 Vin 晚到或斷線時，Vout 是否失控。
Vin 10 µs 斜升到 1.8 V；偏壓經 124 kΩ 接到另一個外部電源 VB，VB 在 t_b 時才 1 µs 斜升到 1.8 V（或永遠不來＝bond 斷線）。"""
import json, numpy as np
from ldo_ref import DEFAULT, subckt
from common import run, MODEL, RES
p = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
R = []
for tb in (None, 30e-6):
    s = subckt(p).replace(".subckt ldoA vin vout vref fb fbi", ".subckt ldoA vin vout vref fb fbi vb").replace(f"Ibias vin bn {p['Ibias']}", "Rbias vb bn 124k")
    vb = "VB vb 0 0" if tb is None else f"VB vb 0 PWL(0 0 {tb} 0 {tb+1e-6} 1.8)"
    tsim = 60e-6
    net = f"* bl\n.include {MODEL}\n.options reltol=1e-4\n{s}\nVIN vin 0 PWL(0 0 1u 0 11u 1.8)\nVREF vref 0 0.8\n{vb}\nX1 vin vout vref fb fb vb ldoA\nCL vout 0 100p\n.control\ntran 5n {tsim} 0 5n uic\nwrdata {RES}/r3bl_tr.txt v(vout) v(x1.pg)\nquit\n.endc\n.end\n"
    run(net, "r3bl")
    a = np.loadtxt(f"{RES}/r3bl_tr.txt"); t, vo, pg = a[:, 0], a[:, 1], a[:, 3]
    pre = vo[(t > 20e-6) & (t < 29e-6)].mean()
    r = dict(bias_arrives_us=None if tb is None else tb * 1e6, vout_before_bias=round(float(pre), 4), pg_before_bias=round(float(pg[(t > 20e-6) & (t < 29e-6)].mean()), 3),
             vout_final=round(float(vo[t > 55e-6].mean()), 4), vout_max_after_bias=round(float(vo[t > 29e-6].max()), 4))
    R.append(r); print(r)
json.dump(R, open("res/r3_1b_bias_late.json", "w"), indent=1)
