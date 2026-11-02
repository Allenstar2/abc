"""PSRR 拆解：B 的 19 dB 差距來自哪裡、在哪些設計選擇下成立。全部碼凍結、70 mA、CL=100 pF、Cc=5 pF。"""
import json, numpy as np
from ldo_ref import DEFAULT, subckt, psrr
from hyb2 import HDEF
from common import run, RES, MODEL

def at(f, ps, fx): return round(float(np.interp(np.log10(fx), np.log10(f), ps)), 1)

def frozen(k, IL, name, Wa=800, mode="gnd", Ws=130, N=8):
    """mode: gnd  = 開著的 slice 閘極接 0 V（REF-B 原設定）
             vintrack = 開著的 slice 閘極 = Vin−1.8（診斷用：去掉 gm·vin 注入）
             seg  = 開著的 slice 閘極接 pg（分段式 pass：數位只選寬度，電流仍由類比閘極控制）"""
    p = dict(HDEF, Wp=Wa)
    sub = subckt(p).replace(".subckt ldoA vin vout vref fb fbi", ".subckt ldoA vin vout vref fb fbi pg")
    lines = []
    for i in range(1, N+1):
        if i > k:
            lines.append(f"Ms{i} vout vin vin vin PMOS W={Ws}u L=0.18u")
        elif mode == "gnd":
            lines.append(f"Ms{i} vout gl vin vin PMOS W={Ws}u L=0.18u")
        elif mode == "vintrack":
            lines.append(f"Ms{i} vout gt vin vin PMOS W={Ws}u L=0.18u")
        elif mode == "seg":
            lines.append(f"Ms{i} vout pg vin vin PMOS W={Ws}u L=0.18u")
    net = f"""* {name}
.include {MODEL}
{sub}
VIN vin 0 DC 1.8 AC 1
VREF vref 0 0.8
X1 vin vout vref fb fb pg ldoA
Vgl gl 0 0
Egt gt 0 vin 0 1
Vgt0 gt gtx -1.8
Rgt gtx 0 1e6
{chr(10).join(lines)}
CL vout 0 {p['CL']}
IL vout 0 DC {IL}
.control
op
print v(vout) v(pg) @m.x1.mp[id] @m.x1.mp[gm] @m.x1.mp[gds] @ms1[id] @ms1[gm] @ms1[gds]
ac dec 20 10 1e9
wrdata {RES}/{name}.txt v(vout)
quit
.endc
.end
"""
    # 修正 vintrack：gt = vin - 1.8 → 用 E 源直接做
    net = net.replace("Egt gt 0 vin 0 1\nVgt0 gt gtx -1.8\nRgt gtx 0 1e6", "Egt gt 0 vin 0 1\n").replace(
        "Egt gt 0 vin 0 1\n", "Bgt gt 0 V = V(vin) - 1.8\n")
    out = run(net, name)
    a = np.loadtxt(f"{RES}/{name}.txt", ndmin=2)
    f = a[:, 0]; ps = 20*np.log10(np.hypot(a[:, 1], a[:, 2]))
    op = {}
    for l in out.splitlines():
        if "=" in l and ("v(" in l or "@" in l):
            k_, v_ = l.split("=", 1)
            try: op[k_.strip()] = float(v_.split()[0])
            except: pass
    return f, ps, op

R = {}
pA = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
f, ps = psrr(pA, 70e-3, "r2_A70")
R["REF-A 4mm @70mA"] = {fx: at(f, ps, fx) for fx in (1e3, 1e5, 1e6)}
cases = [("REF-B code5 gnd (原設定，類比 ~9 mA)", dict(k=5, mode="gnd")),
         ("B code4 gnd（窗口上移，類比 ~21 mA）", dict(k=4, mode="gnd")),
         ("B code3 gnd（類比 ~33 mA，接近飽和）", dict(k=3, mode="gnd")),
         ("B code5 vintrack（診斷：去掉 gm 注入）", dict(k=5, mode="vintrack")),
         ("B code5 seg（分段 pass：開著的 slice 閘極接 pg）", dict(k=5, mode="seg")),
         ("B Wa=1600 code4 gnd", dict(k=4, mode="gnd", Wa=1600)),
         ("B Wa=2400 code3 gnd", dict(k=3, mode="gnd", Wa=2400)),
         ]
for name, kw in cases:
    f, ps, op = frozen(IL=70e-3, name="r2_B", **kw)
    R[name] = {fx: at(f, ps, fx) for fx in (1e3, 1e5, 1e6)}
    R[name]["op"] = {k: op.get(k) for k in ("v(vout)", "v(pg)", "@m.x1.mp[id]", "@m.x1.mp[gm]", "@m.x1.mp[gds]", "@ms1[id]", "@ms1[gm]", "@ms1[gds]")}
for k, v in R.items(): print(k, v)
json.dump(R, open("res/r2_psrr.json", "w"), indent=1, ensure_ascii=False, default=str)
