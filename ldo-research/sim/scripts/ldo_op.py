"""擷取 REF-A 在指定負載下各電晶體的小訊號參數（供手算）。"""
import re, json, sys
from ldo_ref import DEFAULT, header
from common import run

def op_params(p, Iload, name):
    devs = ["m1", "m2", "m3", "m4", "mt", "mb", "mcs", "mp"]
    # BSIM3v1 在 ngspice 不輸出電容參數，閘極電容另以 AC 量測 (cgate_meas)
    prints = " ".join(f"@m.x1.{d}[gm] @m.x1.{d}[gds] @m.x1.{d}[id]" for d in devs)
    net = header(p, name) + f"""
VIN vin 0 {p['Vin']}
VREF vref 0 {p['Vref']}
X1 vin vout vref fb fb ldoA
IL vout 0 DC {Iload}
.control
op
print {prints}
print v(vout) v(x1.pg) v(x1.ea) v(x1.tail) v(x1.d1)
quit
.endc
.end
"""
    out = run(net, name)
    r = {}
    for line in out.splitlines():
        m = re.match(r"\s*(@m\.x1\.(\w+)\[(\w+)\]|v\(([\w.]+)\))\s*=\s*([-\d.eE+]+)", line)
        if m:
            key = (m.group(2) + "_" + m.group(3)) if m.group(2) else ("v_" + m.group(4))
            r[key] = float(m.group(5))
    return r

if __name__ == "__main__":
    p = dict(DEFAULT)
    for IL in (0, 100e-3):
        r = op_params(p, IL, f"op_IL{IL}")
        print(IL, json.dumps({k: f"{v:.4g}" for k, v in r.items()}))

def cgate_meas(Wp, Lp, Vsd, Vg, name="cgate"):
    """以 AC 電流注入量 pass PMOS 閘極總電容 Cgg（drain 為 AC 地，不含 Miller 放大）。回傳 F。"""
    import numpy as np
    net = f"""* cgate
.include {MODEL}
VS s 0 1.8
VD d 0 {1.8-Vsd}
VG g0 0 {Vg}
LG g0 g 1e6
IAC 0 g DC 0 AC 1
M1 d g s s PMOS W={Wp}u L={Lp}u
.control
ac lin 2 1e5 2e5
let c = imag(1/v(g))/(2*3.14159265*frequency)
wrdata {RES}/{name}.txt c
quit
.endc
.end
"""
    run(net, name)
    a = np.loadtxt(f"{RES}/{name}.txt", ndmin=2)
    return float(a[0, 1])
from common import MODEL, RES
