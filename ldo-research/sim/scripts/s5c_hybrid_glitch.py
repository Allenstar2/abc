"""X3e：slice 切換瞬間的尖峰 vs slice 閘極驅動邊沿時間（慢速負載斜坡，只讓碼改變造成擾動）。
另量 0.18 µm (PTM) 反相器 FO4 延遲，作為數位時脈上限的粗估。"""
import json, numpy as np
from ldo_hybrid import HDEF, run_hybrid
from common import run, RES, MODEL

R = {"glitch": [], "fo4": None}
load = "IL vout 0 PWL(0 5m 2u 5m 42u 95m 45u 95m)"
for tdrv in (1e-9, 30e-9, 300e-9):
    p = dict(HDEF, t_drv=tdrv, fclk=10e6)
    t, vo, vpg, code = run_hybrid(p, load, 45e-6, "x3e_tmp", tstep=1e-9)
    sel = (t > 3e-6) & (t < 42e-6)
    dev = vo[sel] - np.median(vo[sel])
    nchg = int(np.count_nonzero(np.diff(code[sel])))
    R["glitch"].append(dict(t_drv_ns=tdrv * 1e9, code_changes=nchg, max_pos_mV=float(dev.max() * 1e3),
                            max_neg_mV=float(-dev.min() * 1e3), final_code=int(code[-1])))
    print(R["glitch"][-1], flush=True)

net = f"""* FO4 inverter delay, PTM 180nm, VDD 1.8
.include {MODEL}
VDD vdd 0 1.8
VIN in 0 PULSE(0 1.8 1n 50p 50p 2n 4n)
.subckt inv a y vdd
Mn y a 0 0 NMOS W=1u L=0.18u
Mp y a vdd vdd PMOS W=2.5u L=0.18u
.ends
X1 in a vdd inv
X2 a b vdd inv
X3 b c vdd inv
X4 b c2 vdd inv
X5 b c3 vdd inv
X6 b c4 vdd inv
X7 c d vdd inv
X8 c d2 vdd inv
X9 c d3 vdd inv
X10 c d4 vdd inv
.control
tran 1p 6n
meas tran tphl trig v(a) val=0.9 rise=1 targ v(b) val=0.9 fall=1
meas tran tplh trig v(a) val=0.9 fall=1 targ v(b) val=0.9 rise=1
quit
.endc
.end
"""
out = run(net, "fo4")
vals = {k: float(l.split("=")[1].split()[0]) for l in out.splitlines() for k in ("tphl", "tplh") if l.strip().startswith(k)}
R["fo4"] = dict(tphl_ps=vals.get("tphl", np.nan) * 1e12, tplh_ps=vals.get("tplh", np.nan) * 1e12)
print(R["fo4"])
json.dump(R, open(f"{RES}/x3e_glitch_fo4.json", "w"), indent=1)
