import numpy as np
from common import run, RES, MODEL
for W in (800, 2400):
    net = f"""* idvg
.include {MODEL}
VS s 0 1.8
VD d 0 1.6
VG g 0 1.0
M1 d g s s PMOS W={W}u L=0.18u
.control
dc VG 0.6 1.8 0.005
wrdata {RES}/idvg_{W}.txt -i(VD)
quit
.endc
.end
"""
    run(net, f"idvg_{W}")
    a = np.loadtxt(f"{RES}/idvg_{W}.txt"); vg = a[:, 0]; i = -a[:, 1]
    i = np.abs(a[:,1])
    for I in (3e-3, 8e-3, 14e-3, 18e-3, 25e-3, 35e-3, 60e-3):
        # i 隨 vg 遞減
        k = np.where(i < I)[0]
        print(W, f"I={I*1e3:.0f}mA -> Vg={vg[k[0]] if len(k) else float('nan'):.3f}")
