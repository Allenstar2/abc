"""R2-7b：SF-like 125 °C 零載 Vout（A 的 +46 mV 失效）對 PMOS Vth 假設的敏感度。"""
import json
from ldo_ref import DEFAULT, loopgain
from corners import variant
R = []
for dvp in (0.0, 0.05, 0.10, 0.15):
    for W in (4000, 8000):
        m = variant(0.05, -0.05 + dvp, 1.0, tag=f"sf{dvp}")
        p = dict(DEFAULT, Wp=W, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3, model=m, temp=125)
        f, T, v = loopgain(p, 0, "r27b")
        R.append(dict(dVthp_extra_V=dvp, Wp_um=W, vout_0_SF125=round(v["vout_op"], 4), vpg=round(v["vpg_op"], 3))); print(R[-1])
json.dump(R, open("res/r2_7b_hot.json", "w"), indent=1)
