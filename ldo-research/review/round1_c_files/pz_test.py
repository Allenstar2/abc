import sys, json, numpy as np
sys.path.insert(0, ".")
from sim_lg import HDR, core, run
r = json.load(open("lg_results.json"))
for tag, IL in [("IL0", 0.0), ("IL10m", 0.01), ("IL100m", 0.1)]:
    vfb = r[tag]["op"]["v(fb)"]
    net = HDR + core(g1="g1") + f"""
VIN vin 0 DC 1.8
VREF vref 0 0.8
Vjoin vout r1t 0
Vg1 gdc 0 DC {vfb:.9e}
Rg gdc g1 1
IL vout 0 DC {IL}
.control
op
print v(vout)
pz g1 0 vout 0 cur pz
print all
.endc
.end
"""
    out = run(net, f"pz_{tag}")
    print("=====", tag)
    for l in out.splitlines():
        if "pole" in l.lower() or "zero" in l.lower() or "v(vout)" in l:
            print(l)
