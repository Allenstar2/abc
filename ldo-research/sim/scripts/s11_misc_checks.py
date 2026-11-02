"""補充查核（第 1 輪審查 (b) 指出無法查證的數字）：
1. BSIM3 version=3.1 vs 3.3.0 單點比較（存檔）
2. 1 nF 設計卸載 overshoot 的回復時間
3. REF-B 類比部分（碼 0）可供應的最大電流、Iq
4. 1 nF 補償公平性表（500 µA 洩放）存檔
"""
import json, numpy as np, os
from common import run, MODEL, RES
from ldo_ref import DEFAULT, header, load_step, loopgain, margins
from ldo_hybrid import HDEF
R = {}
# 1
src = open(MODEL).read()
m33 = os.path.join(RES, "tmp", "model_v330.pm"); os.makedirs(os.path.dirname(m33), exist_ok=True)
open(m33, "w").write(src.replace("version =3.1", "version =3.3.0"))
for tag, mp in (("v3.1", MODEL), ("v3.3.0", m33)):
    out = run(f"""* bsim ver
.include {mp}
VD d 0 0.9
VG g 0 0.7
M1 d g 0 0 NMOS W=10u L=1u
.control
op
print @m1[gm] @m1[gds] @m1[id]
quit
.endc
.end
""", "s11_ver")
    R[f"bsim_{tag}"] = {l.split("=")[0].strip(): float(l.split("=")[1]) for l in out.splitlines() if l.strip().startswith("@m1")}
# 2
p = dict(DEFAULT, CL=1e-9, Cc=20e-12, R1=4e3, R2=4e3)
t, vo, vpg, m = load_step(p, 0, 100e-3, 1e-9, "s11_rec", thold=10e-6, tstop=30e-6)
t2 = 2e-6 + 1e-9 + 10e-6
final = vo[-200:].mean()
after = (t > t2)
idx = np.where(after & (np.abs(vo - final) > 0.01 * final))[0]
R["recovery_1nF_overshoot_to_1pct_us"] = float((t[idx[-1]] - t2) * 1e6) if len(idx) else 0.0
p = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
t, vo, vpg, m = load_step(p, 0, 100e-3, 1e-9, "s11_rec", thold=10e-6, tstop=30e-6)
final = vo[-200:].mean(); idx = np.where((t > t2) & (np.abs(vo - final) > 0.01 * final))[0]
R["recovery_100pF_overshoot_to_1pct_us"] = float((t[idx[-1]] - t2) * 1e6) if len(idx) else 0.0
# 3 REF-B 類比部分（碼 0）：負載掃描，Vout 掉 1% 的電流
pb = dict(HDEF)
net = header(pb, "s11_hb") + f"""
VIN vin 0 1.8
VREF vref 0 0.8
X1 vin vout vref fb fb ldoA
IL vout 0 DC 0
.control
op
print -i(VIN)
dc IL 0 0.06 0.0005
wrdata {RES}/s11_hb_dc.txt v(vout) v(x1.pg)
quit
.endc
.end
"""
out = run(net, "s11_hb")
R["REFB_code0_Iq_uA"] = float([l for l in out.splitlines() if "i(vin)" in l.lower()][0].split("=")[1]) * 1e6
a = np.loadtxt(f"{RES}/s11_hb_dc.txt"); il, vv = a[:, 0], a[:, 1]
i = np.where(vv < 0.99 * vv[0])[0]
R["REFB_analog_max_mA_at_1pct_drop"] = float(il[i[0]] * 1e3) if len(i) else None
# 4 1 nF 公平性
rows = []
for name, q in (("1n_Imin500_Cc10", dict(DEFAULT, CL=1e-9, Cc=10e-12, R1=1.6e3, R2=1.6e3)),
                ("1n_Imin500_Cc5", dict(DEFAULT, CL=1e-9, Cc=5e-12, R1=1.6e3, R2=1.6e3)),
                ("100p_Imin500_Cc3", dict(DEFAULT, CL=100e-12, Cc=3e-12, R1=1.6e3, R2=1.6e3))):
    pms = [round(margins(*loopgain(q, IL, "s11_lg")[:2])["pm"], 1) for IL in (0, 1e-3, 0.1)]
    us = [round(load_step(q, 0, 0.1, te, "s11_tr", thold=6e-6)[3]["undershoot"] * 1e3) for te in (1e-9, 100e-9, 1e-6)]
    rows.append(dict(design=name, pm=pms, undershoot_1ns_100ns_1us_mV=us))
R["fairness_1nF"] = rows
json.dump(R, open(f"{RES}/s11_misc_checks.json", "w"), indent=1)
print(json.dumps(R, indent=1))
