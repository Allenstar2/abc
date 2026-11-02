import sys, json, numpy as np
sys.path.insert(0, ".")
from sim_lg import HDR, core, run
r = json.load(open("lg_results.json"))
vfb = r["IL0"]["op"]["v(fb)"]
for CL in [50e-12, 100e-12, 200e-12, 400e-12]:
    net = HDR + core(g1="g1", CL=CL) + f"""
VIN vin 0 DC 1.8
VREF vref 0 0.8
Vjoin vout r1t 0
Vg1 gdc 0 DC {vfb:.9e}
Rg gdc g1 1
IL vout 0 DC 0
.control
pz g1 0 vout 0 cur pol
print all
.endc
.end
"""
    out = run(net, f"pzCL_{int(CL*1e12)}p")
    poles = []
    for l in out.splitlines():
        if l.strip().startswith("pole("):
            re_, im = l.split("=")[1].split(",")
            poles.append(complex(float(re_), float(im)))
    ps = sorted([abs(p)/(2*np.pi) for p in poles if abs(p) < 1e10])
    print(f"CL={CL*1e12:.0f}p  poles (Hz, |p|<1e10 rad/s):", ", ".join(f"{p/1e6:.4g}M" for p in ps), " p2*CL =", f"{ps[1]*CL*2*np.pi*1e3:.4g} mS")
