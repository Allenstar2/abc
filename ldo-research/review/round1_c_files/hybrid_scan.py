import numpy as np, json, sys
from hybrid_beh import scan
RGRID = np.round(np.arange(0.5, 4.001, 0.05), 3)
LO = np.linspace(0.0, 8.0, 801) + 1.234e-5

def frac_curve(**kw):
    fr = np.array([float(scan(r, loads=LO, **kw)[0].mean()) for r in RGRID])
    bad = np.where(fr > 0)[0]
    if not len(bad): rc = float(RGRID[0])
    elif bad[-1] + 1 < len(RGRID): rc = float(RGRID[bad[-1] + 1])
    else: rc = float("inf")
    return fr, rc

configs = [("base", dict())]
configs += [(f"os={o}", dict(os=o)) for o in (-0.1, 0.05, 0.1, 0.2)]
configs += [(f"order1 tau={t}", dict(tau=t)) for t in (0.5, 1.0, 3.0, 10.0)]
configs += [(f"order2 wn={w:.2f} zeta={z}", dict(order=2, wn=w, zeta=z)) for w in (3.0, 1.0, 0.3) for z in (0.3, 0.5, 0.7)]
configs += [(f"d={d}", dict(d=d)) for d in (1, 2)]
configs += [(f"d={d},blank={d}", dict(d=d, b=d)) for d in (1, 2)]
configs += [("tau=1,os=0.1", dict(tau=1.0, os=0.1)), ("order2 wn=1 z=0.5,os=0.1", dict(order=2, wn=1.0, zeta=0.5, os=0.1))]
out = {"RGRID": list(map(float, RGRID))}
for name, kw in configs:
    fr, rc = frac_curve(**kw)
    sel = {float(r): float(f) for r, f in zip(RGRID, fr) if r in (0.5, 0.8, 1.0, 1.1, 1.2, 1.5, 2.0, 2.5, 3.0, 3.5)}
    out[name] = dict(kw=kw, r_crit=rc, frac=sel, curve=list(map(float, fr)))
    print(f"{name:28s} r_crit= {rc:5.2f}  | " + " ".join(f"{k}:{v:.2f}" for k, v in sel.items()), flush=True)
json.dump(out, open("hyb_scan.json", "w"), indent=1)
