import json, re, numpy as np
from ldo_ref import DEFAULT, subckt
from common import run, RES, MODEL
base = open(MODEL).read()
mp = f"{RES}/model_SF.pm"; open(mp, "w").write(base.replace("Vth0 = 0.3999", "Vth0 = 0.4499").replace("Vth0 = -0.42", "Vth0 = -0.3700"))
out = {"bleed": [], "bias": {}}
# (1) A 在 SF-like 125 °C 零負載，需要多大洩放
for Ib in (200e-6, 300e-6, 400e-6, 600e-6, 800e-6):
    R12 = 1.6/Ib/2
    p = dict(DEFAULT, Wp=4000, R1=R12, R2=R12, temp=125)
    net = f"* b\n.include {mp}\n.options temp=125\n{subckt(p)}\nVIN vin 0 1.8\nVREF vref 0 0.8\nX1 vin vout vref fb fb ldoA\nIL vout 0 0\n.control\nop\nprint v(vout) v(x1.pg)\nquit\n.endc\n.end\n"
    o = run(net, "r7_b"); v = {l.split("=")[0].strip(): float(l.split("=")[1]) for l in o.splitlines() if l.strip().startswith("v(")}
    out["bleed"].append(dict(bleed_uA=Ib*1e6, vout=v["v(vout)"], vpg=v["v(x1.pg)"])); print(out["bleed"][-1], flush=True)
# (2) 非理想偏壓：Ibias 改成 Vin 到 bn 的電阻（最粗糙的偏壓），看 A 與 B 的 PSRR
def psr(net_body, name):
    run(net_body, name); a = np.loadtxt(f"{RES}/{name}.txt", ndmin=2)
    f = a[:, 0]; ps = 20*np.log10(np.hypot(a[:, 1], a[:, 2]))
    return {fx: round(float(np.interp(np.log10(fx), np.log10(f), ps)), 1) for fx in (1e3, 1e5, 1e6)}
for bias in ("ideal", "resistor"):
    for arch, Wp, k in (("A 4mm", 4000, 0), ("B 800 code5", 800, 5), ("B 2400 code3", 2400, 3)):
        p = dict(DEFAULT, Wp=Wp, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
        sub = subckt(p)
        if bias == "resistor":
            sub = sub.replace(f"Ibias vin bn {p['Ibias']}", "Rbias vin bn 124k")
        sl = "\n".join((f"Ms{i} vout vin vin vin PMOS W=130u L=0.18u" if i > k else f"Ms{i} vout gl vin vin PMOS W=130u L=0.18u") for i in range(1, 9)) if arch.startswith("B") else ""
        net = f"* p\n.include {MODEL}\n{sub}\nVIN vin 0 DC 1.8 AC 1\nVREF vref 0 0.8\nVgl gl 0 0\nX1 vin vout vref fb fb ldoA\n{sl}\nCL vout 0 100p\nIL vout 0 DC 70m\n.control\nac dec 20 10 1e9\nwrdata {RES}/r7_p.txt v(vout)\nquit\n.endc\n.end\n"
        out["bias"][f"{arch} / {bias}"] = psr(net, "r7_p"); print(arch, bias, out["bias"][f"{arch} / {bias}"], flush=True)
json.dump(out, open("res/r7_bleed_bias.json", "w"), indent=1)
