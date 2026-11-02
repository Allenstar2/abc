"""REF-A 穩定度掃描：最小負載(分壓電流) × Cc × CL × Imax(Wp)。輸出最差 PM。"""
import itertools, json, numpy as np
from ldo_ref import DEFAULT, loopgain, margins
from common import RES

rows = []
for Imax, Wp in ((10e-3, 400), (50e-3, 2000), (100e-3, 4000)):
    for CL in (100e-12, 1e-9):
        for Imin in (50e-6, 200e-6, 500e-6):
            for Cc in (1e-12, 2e-12, 3e-12, 5e-12, 10e-12, 20e-12, 40e-12):
                p = dict(DEFAULT, Wp=Wp, CL=CL, Cc=Cc, R1=0.8/Imin, R2=0.8/Imin)
                res = []
                for frac in (0, 0.01, 0.1, 0.5, 1.0):
                    f, T, v = loopgain(p, frac * Imax, "sw_tmp")
                    m = margins(f, T); m["IL"] = frac * Imax; m["vout"] = v.get("vout_op", np.nan)
                    res.append(m)
                pms = [r["pm"] if np.isfinite(r["pm"]) else -999 for r in res]
                k = int(np.argmin(pms))
                rows.append(dict(Imax_mA=Imax*1e3, Wp_um=Wp, CL_pF=CL*1e12, Imin_uA=Imin*1e6, Cc_pF=Cc*1e12,
                                 pm_min=round(pms[k], 1), pm_min_at_mA=res[k]["IL"]*1e3,
                                 pm_list=[round(x, 1) for x in pms],
                                 ugf_MHz=[round(r["ugf"]/1e6, 2) for r in res],
                                 dc_db=[round(r["dc_db"], 1) for r in res],
                                 vout=[round(r["vout"], 4) for r in res]))
with open(f"{RES}/s1_refA_sweep.json", "w") as f:
    json.dump(rows, f, indent=0)
print("Imax CL  Imin  Cc  -> PMmin(@mA) | PM list (0,1%,10%,50%,100%) | UGF MHz")
for r in rows:
    print(f"{r['Imax_mA']:5.0f} {r['CL_pF']:5.0f} {r['Imin_uA']:4.0f} {r['Cc_pF']:4.0f} -> {r['pm_min']:6.1f} ({r['pm_min_at_mA']:.1f}) | {r['pm_list']} | {r['ugf_MHz']}")
