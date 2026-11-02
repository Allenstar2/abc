"""R2-4：片上負載不是理想電流源。
(1) 以 NMOS 開關（閘極 0→1.8 V，邊沿 t_e）取代理想電流源，W 取 TT 27 °C 在 Vout=1.6 V 時 100 mA；
    比較 0→100 mA undershoot、實際負載電流波形（droop 期間電流掉多少）。
(2) 同一顆 NMOS 負載在各 corner/溫度下的實際電流（Vout=1.6 V）→「100 mA 步階」本身不受控。
(3) cascode 電流鏡式負載（較接近電流源）需要多少 headroom。"""
import json, numpy as np
from common import run, MODEL, RES
from ldo_ref import DEFAULT, header, load_step
from corners import corner

def i_nmos(W, model, temp, vds=1.6, vgs=1.8):
    net = f"* iv\n.include {model}\n.options temp={temp}\nVD d 0 {vds}\nVG g 0 {vgs}\nM1 d g 0 0 NMOS W={W}u L=0.18u\n.control\nop\nprint -i(VD)\nquit\n.endc\n.end\n"
    out = run(net, "r24_iv")
    for l in out.splitlines():
        if "-i(vd)" in l.lower(): return float(l.split("=")[1])
# (0) 找 W
lo, hi = 10, 2000
for _ in range(40):
    mid = (lo + hi) / 2
    if i_nmos(mid, MODEL, 27) > 0.1: hi = mid
    else: lo = mid
Wn = round(hi, 1); R = dict(W_nmos_load_um=Wn)
# (2) corner spread
spread = {}
for cn in ("TT", "SS", "FF", "SF", "FS"):
    for temp in (27, 75):
        spread[f"{cn}_{temp}C"] = round(i_nmos(Wn, corner(cn), temp) * 1e3, 1)
R["I_load_at_Vout1p6_mA"] = spread
R["I_vs_Vout_TT27_mA"] = {str(v): round(i_nmos(Wn, MODEL, 27, vds=v) * 1e3, 1) for v in (1.6, 1.4, 1.2, 1.0, 0.8, 0.6)}
print(R, flush=True)
# (1) 暫態：理想電流源 vs NMOS 開關
p = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
R["step"] = []
for te in (1e-9, 10e-9, 100e-9):
    t, vo, vpg, mi = load_step(p, 0, 100e-3, te, "r24_ideal", thold=4e-6)
    t0 = 2e-6
    extra = f"VGL gl 0 PWL(0 0 {t0} 0 {t0+te} 1.8 {t0+te+4e-6} 1.8 {t0+2*te+4e-6} 0)\nMLD vout gl 0 0 NMOS W={Wn}u L=0.18u"
    name = "r24_nmos"
    net = header(p, name) + f"""
VIN vin 0 DC 1.8
VREF vref 0 0.8
X1 vin vout vref fb fb ldoA
CL vout ncl {p['CL']}
RESR ncl 0 1e-6
{extra}
.control
tran {min(te/20, 2e-9)} {t0+2*te+8e-6} 0 {min(te/20,2e-9)*5}
wrdata {RES}/{name}_tr.txt v(vout) i(VGL) 
let ild = @mld[id]
quit
.endc
.end
"""
    # 用 B-source 量電流較麻煩：改量 vin 電流 = 負載+Iq；這裡直接在 netlist 加 0 V 電源量
    net = net.replace(f"MLD vout gl 0 0 NMOS", f"VMEAS vout vm 0\nMLD vm gl 0 0 NMOS").replace("wrdata " + f"{RES}/{name}_tr.txt v(vout) i(VGL)", f"wrdata {RES}/{name}_tr.txt v(vout) i(VMEAS)")
    run(net, name)
    a = np.loadtxt(f"{RES}/{name}_tr.txt"); tt, vv, ii = a[:, 0], a[:, 1], a[:, 3]
    pre = vv[(tt > t0 - 0.2e-6) & (tt < t0)].mean()
    w = (tt > t0) & (tt < t0 + te + 4e-6)
    k = np.argmin(vv[w]); imin_at_droop = ii[w][k]
    ifinal = ii[(tt > t0 + te + 3.5e-6) & (tt < t0 + te + 4e-6)].mean()
    R["step"].append(dict(edge_ns=te * 1e9, ideal_undershoot_mV=round(mi["undershoot"] * 1e3, 1),
                          nmos_undershoot_mV=round((pre - vv[w].min()) * 1e3, 1),
                          nmos_I_at_vmin_mA=round(imin_at_droop * 1e3, 1), nmos_I_final_mA=round(ifinal * 1e3, 1)))
    print(R["step"][-1], flush=True)
json.dump(R, open(f"{RES}/r2_4_nmos_load.json", "w"), indent=1)
