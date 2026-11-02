"""Sensitivity of 'peak TIE' (linear-detrend, (max-min)/2) to the analysis window; compare with sine-fit amplitude.
Also measure slow drift of vdd (per-modulation-cycle mean) after the ripple is switched on."""
import json, numpy as np
from rv import tie, sine_fit, RES
tst = 2e-6
out = {}
for name, fm in (("a_tr_INV7_ldo_fm1000k_A10m", 1e6), ("a_tr_INV7_direct_fm1000k_A10m", 1e6),
                 ("a_tr_CS5_ldo_fm1000k_A10m", 1e6), ("a_tr_CS5_ldo_fm300k_A10m", 300e3),
                 ("a_tr_CS5_direct_fm300k_A10m", 300e3), ("a_tr_CS5_ldo_fm3000k_A10m", 3e6), ("a_tr_INV7_ldo_fm3000k_A10m", 3e6)):
    a = np.loadtxt(f"{RES}/{name}.txt"); t, v, vdd = a[:, 0], a[:, 1], a[:, 3]
    tend = t[-1] - 20e-9
    rows = []
    for t0 in (0.5e-6, 1e-6, 2e-6):
        for t1 in (tend,):
            f0, pk, tc, e = tie(t, v, vdd, tst + t0, t1)
            rows.append(dict(win_us=(round(t0 * 1e6, 2), round((t1 - tst) * 1e6, 2)), pk_ps=round(pk * 1e12, 1),
                             fit_ps=round(sine_fit(tc, e, fm) * 1e12, 1)))
    # vdd mean per modulation cycle from tst
    cyc = []
    tt = tst
    while tt + 1 / fm <= tend:
        s = (t >= tt) & (t < tt + 1 / fm)
        cyc.append(round(float(np.trapezoid(vdd[s], t[s]) * fm) * 1e3, 3)); tt += 1 / fm
    out[name] = dict(windows=rows, vdd_cycle_mean_mV=cyc)
    print(name, rows, "vdd mean per cycle (mV):", cyc)
json.dump(out, open(f"{RES}/a_window.json", "w"), indent=1)
