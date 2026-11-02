"""R2-5：A 的補償（含 v2 推薦的 nulling resistor）跨 corner、模型參數、被動元件、佈局寄生的穩健性。
設計：D1 REF-A 100p/Cc5/Rz0；D2 100p/Cc3/Rz5k；D3 1n/Cc8/Rz10k；洩放 200 µA；負載 0–100 mA 8 點。
擾動：Vth/Tox corner×溫度；NFactor、Pclm、U0、Cgdo；Rz±20%、Cc±15%、CL±20%；pg 加 2 pF、ea 加 0.3 pF；Ibias±30%。"""
import json, itertools, numpy as np
import ldo_ref
from ldo_ref import DEFAULT, loopgain, margins
from corners import corner, variant
_orig = ldo_ref.subckt
ldo_ref.subckt = lambda p: _orig(p).replace(".ends", f"Cpgx pg 0 {p.get('Cpgx', 1e-18)}\nCeax ea 0 {p.get('Ceax', 1e-18)}\n.ends")
LOADS = [0, 0.3e-3, 1e-3, 3e-3, 10e-3, 30e-3, 50e-3, 100e-3]
DES = {"D1_100p_Cc5_Rz0": dict(CL=100e-12, Cc=5e-12, Rz=0),
       "D2_100p_Cc3_Rz5k": dict(CL=100e-12, Cc=3e-12, Rz=5e3),
       "D3_1n_Cc8_Rz10k": dict(CL=1e-9, Cc=8e-12, Rz=10e3)}
def pert(d):
    L = [("nominal", {})]
    for cn, temp in itertools.product(("TT", "SS", "FF", "SF", "FS"), (-40, 27, 125)):
        if (cn, temp) != ("TT", 27): L.append((f"{cn}_{temp}C", dict(model=corner(cn), temp=temp)))
    for k, vals in (("nf", (0.7, 1.4)), ("pclm", (0.5, 2.0)), ("u0", (0.8, 1.2)), ("cgdo", (0.5, 1.5)), ("eta0p", (0.5,))):
        for v in vals: L.append((f"{k}x{v}", dict(model=variant(tag=f"{k}{v}", **{k: v}))))
    if d["Rz"] > 0:
        L += [("Rz-20%", dict(Rz=d["Rz"] * 0.8)), ("Rz+20%", dict(Rz=d["Rz"] * 1.2))]
    L += [("Cc-15%", dict(Cc=d["Cc"] * 0.85)), ("Cc+15%", dict(Cc=d["Cc"] * 1.15)),
          ("CL-20%", dict(CL=d["CL"] * 0.8)), ("CL+20%", dict(CL=d["CL"] * 1.2)),
          ("Cpg+2pF", dict(Cpgx=2e-12)), ("Cea+0.3pF", dict(Ceax=0.3e-12)),
          ("Ibias-30%", dict(Ibias=7e-6)), ("Ibias+30%", dict(Ibias=13e-6)),
          ("worst_combo:Rz+20%,CL-20%,Cc-15%,Cpg+2p,Ibias-30%,FF125", dict(Rz=d["Rz"] * 1.2, CL=d["CL"] * 0.8, Cc=d["Cc"] * 0.85, Cpgx=2e-12, Ibias=7e-6, model=corner("FF"), temp=125)),
          ("worst_combo2:Rz-20%,CL+20%,Cc-15%,Cpg+2p,Ibias-30%,SS125", dict(Rz=d["Rz"] * 0.8, CL=d["CL"] * 1.2, Cc=d["Cc"] * 0.85, Cpgx=2e-12, Ibias=7e-6, model=corner("SS"), temp=125))]
    return L
R = {}
for dn, d in DES.items():
    rows = []
    for tag, kw in pert(d):
        p = dict(DEFAULT, R1=4e3, R2=4e3, **d); p.update(kw)
        pms, gms = [], []
        for IL in LOADS:
            f, T, v = loopgain(p, IL, "r25"); m = margins(f, T); pms.append(m["pm"]); gms.append(m["gm_db"])
        i = int(np.nanargmin(pms))
        rows.append(dict(case=tag, pm_min=round(float(np.nanmin(pms)), 1), at_mA=LOADS[i] * 1e3,
                         gm_min_dB=round(float(np.nanmin(gms)), 1), pm_list=[round(x, 1) for x in pms]))
        print(dn, rows[-1], flush=True)
    R[dn] = rows
json.dump(R, open("res/r2_5_robust.json", "w"), indent=1)
for dn, rows in R.items():
    w = sorted(rows, key=lambda r: r["pm_min"])[:5]
    print("\n", dn, "nominal", rows[0]["pm_min"], "| worst5:", [(r["case"], r["pm_min"], r["at_mA"]) for r in w])
