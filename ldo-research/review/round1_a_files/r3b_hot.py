"""125 °C、SF-like（Vthn+50 mV、|Vthp|−50 mV）零外部負載：A（4 mm pass）vs B（800 µm 類比＋8×130 µm slice 閘極接 Vin）。
與 s6_corners.py 相同的模型改法，但模型檔寫到 scratch。"""
import json, re, numpy as np
from ldo_ref import DEFAULT, subckt
from common import run, RES, MODEL
base = open(MODEL).read()
def variant(dn, dp, tag):
    s = base.replace("Vth0 = 0.3999", f"Vth0 = {0.3999+dn:.4f}").replace("Vth0 = -0.42", f"Vth0 = {-0.42-dp:.4f}")
    path = f"{RES}/model_{tag}.pm"; open(path, "w").write(s); return path
R = []
for corner, (dn, dp) in {"TT": (0, 0), "SF-like": (0.05, -0.05), }.items():
    mp = variant(dn, dp, re.sub(r"\W", "", corner))
    for temp in (125,):
        for arch, Wp, slices in (("A 4mm", 4000, False), ("B 800", 800, True), ("B 1600", 1600, True), ("B 2400", 2400, True)):
            for R12 in (4e3,):
                p = dict(DEFAULT, Wp=Wp, CL=100e-12, Cc=5e-12, R1=R12, R2=R12, temp=temp)
                sl = "\n".join(f"Ms{i} vout vin vin vin PMOS W=130u L=0.18u" for i in range(1, 9)) if slices else ""
                net = f"""* hot
.include {mp}
.options temp={temp}
{subckt(p)}
VIN vin 0 DC 1.8
VREF vref 0 0.8
X1 vin vout vref fb fb ldoA
{sl}
IL vout 0 DC 0
.control
op
print v(vout) v(x1.pg) v(x1.ea) @m.x1.mp[id] {'@ms1[id]' if slices else ''}
quit
.endc
.end
"""
                out = run(net, "r3_hot")
                vals = {}
                for l in out.splitlines():
                    if "=" in l:
                        k, v = l.split("=", 1)
                        try: vals[k.strip()] = float(v.split()[0])
                        except: pass
                r = dict(corner=corner, temp=temp, arch=arch, bleed_uA=round(1.6/(2*R12)*1e6), vout=vals.get("v(vout)"),
                         vpg=vals.get("v(x1.pg)"), I_pass_uA=-1e6*vals.get("@m.x1.mp[id]", np.nan),
                         I_slice_each_nA=(-1e9*vals.get("@ms1[id]", np.nan)) if slices else None)
                R.append(r); print(r, flush=True)
json.dump(R, open("res/r3b_hot.json", "w"), indent=1, ensure_ascii=False)
