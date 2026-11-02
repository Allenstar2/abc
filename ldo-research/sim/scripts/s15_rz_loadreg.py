"""第 2 輪審查 (b) 要求存檔的數字：
1. Rz 補償表（1 nF Cc=8p Rz=10k；100 pF Cc=3p Rz=5k；REF-A），PM @0/1/10/30/50/100 mA 與 undershoot
2. 同條件 load regulation：REF-A 在 20→95 mA 與 0→95 mA；公平 B 的值取自 s12（20→95）
"""
import json
from ldo_ref import DEFAULT, loopgain, margins, load_step
from common import RES
R = {"rz": []}
for name, p in (("1n_Cc8_Rz10k", dict(DEFAULT, CL=1e-9, Cc=8e-12, Rz=10e3, R1=4e3, R2=4e3)),
                ("100p_Cc3_Rz5k", dict(DEFAULT, CL=100e-12, Cc=3e-12, Rz=5e3, R1=4e3, R2=4e3)),
                ("100p_Cc5_Rz0_REF-A", dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3))):
    pms = [round(margins(*loopgain(p, IL, "s15_lg")[:2])["pm"], 1) for IL in (0, 1e-3, 10e-3, 30e-3, 50e-3, 100e-3)]
    us = [round(load_step(p, 0, 0.1, te, "s15_tr", thold=6e-6)[3]["undershoot"] * 1e3, 1) for te in (1e-9, 100e-9, 1e-6)]
    R["rz"].append(dict(design=name, pm_0_1_10_30_50_100mA=pms, undershoot_1ns_100ns_1us_mV=us)); print(R["rz"][-1], flush=True)
p = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
v = {IL: loopgain(p, IL, "s15_op")[2]["vout_op"] for IL in (0, 20e-3, 95e-3)}
R["REF-A_vout"] = {f"{k*1e3:g}mA": v[k] for k in v}
R["REF-A_loadreg_20to95_mV"] = round((v[20e-3] - v[95e-3]) * 1e3, 2)
R["REF-A_loadreg_0to95_mV"] = round((v[0] - v[95e-3]) * 1e3, 2)
print(R)
json.dump(R, open(f"{RES}/s15_rz_loadreg.json", "w"), indent=1)
