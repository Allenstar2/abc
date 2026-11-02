"""規格敏感度：Imax ∈ {10, 50, 100} mA（pass W 依 D-006 縮放）× CL ∈ {100 pF, 1 nF}。
補償沿用 D-008（100 pF: Cc=5 pF；1 nF: Cc=20 pF；洩放 200 µA）。"""
import json, numpy as np
from ldo_ref import DEFAULT, loopgain, margins, psrr, load_step
from common import RES

rows = []
for Imax, Wp in ((10e-3, 400), (50e-3, 2000), (100e-3, 4000)):
    for CL, Cc in ((100e-12, 5e-12), (1e-9, 20e-12)):
        p = dict(DEFAULT, Wp=Wp, CL=CL, Cc=Cc, R1=4e3, R2=4e3)
        pms = []
        for fr in (0, 0.01, 0.5, 1):
            f, T, v = loopgain(p, fr * Imax, "s8_lg"); pms.append(margins(f, T)["pm"])
            if fr == 1: dcfull = margins(f, T)["dc_db"]; vfull = v["vout_op"]
            if fr == 0: v0 = v["vout_op"]; iq = v["iin"]
        f, ps = psrr(p, Imax, "s8_psr")
        us = {}
        for te in (1e-9, 100e-9, 1e-6):
            t, vo, vpg, m = load_step(p, 0, Imax, te, "s8_tr", thold=6e-6)
            us[f"{te*1e9:g}ns"] = round(m["undershoot"] * 1e3, 1)
        rows.append(dict(Imax_mA=Imax * 1e3, Wp_um=Wp, CL_pF=CL * 1e12, Cc_pF=Cc * 1e12,
                         pm_min=round(min(pms), 1), dc_db_full=round(dcfull, 1),
                         load_reg_mV=round((v0 - vfull) * 1e3, 1), Iq_uA=round(iq * 1e6, 1),
                         psrr_1k_full=round(float(np.interp(3, np.log10(f), ps)), 1),
                         psrr_1M_full=round(float(np.interp(6, np.log10(f), ps)), 1),
                         undershoot_0_to_Imax_mV=us))
        print(rows[-1], flush=True)
json.dump(rows, open(f"{RES}/s8_sensitivity.json", "w"), indent=1)
