"""第 3 輪審查 (a) 的作者重現：Vout 1.4 V 替代規格的卸載過衝代價（Vout 可衝到 Vin）。"""
import json
from ldo_ref import DEFAULT, load_step
from common import RES
R = {}
for vout, R2 in ((1.6, 4e3), (1.4, 8e3 * 0.8 / 1.4)):
    p = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=8e3 - R2, R2=R2)
    R[str(vout)] = {f"{te*1e9:g}ns": {k: round(v * 1e3, 1) for k, v in load_step(p, 0, 0.1, te, "s21_tr", thold=6e-6)[3].items() if k in ("undershoot", "overshoot")} for te in (1e-9, 10e-9, 100e-9)}
print(R); json.dump(R, open(f"{RES}/s21_vout14_overshoot.json", "w"), indent=1)
