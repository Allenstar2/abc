"""Ideal behavioral predictions on the author's 31 load points: worst-case-IC metric vs ascending staircase,
plus the analytic LC band for d=1 ascending staircase."""
import json, numpy as np
from c1_beh import lc_possible, staircase, run, Is, Ilo, Ihi
levels = list(np.round(np.arange(5, 95.1, 3), 3))
R = {}
for d in (1, 2):
    any_ic = [IL for IL in levels if lc_possible(IL, d=d) > 0]
    up = [b["IL"] for b in staircase(levels, d=d)]
    R[f"d{d}"] = dict(worst_case_IC=dict(n=len(any_ic), loads=any_ic), staircase_up=dict(n=len(up), loads=up))
    print(f"d={d}: worst-case-IC {len(any_ic)}/31 {any_ic}\n      staircase-up {len(up)}/31 {up}")
# analytic d=1 ascending-staircase band: LC starts when Ia(k) > Ihi, escapes when two consecutive codes in window
bands = [(round(Ihi + k * Is, 1), round(Ilo + (k + 2) * Is, 1)) for k in (0, 2, 4, 6)]
R["d1_bands_analytic_mA"] = bands
R["d1_band_fraction_of_2slices"] = (Ilo + 2 * Is - Ihi) / (2 * Is)
print("d=1 analytic LC bands (mA):", bands, " fraction of each 2-slice period:", round(R["d1_band_fraction_of_2slices"], 3))
# code trace example at 20 mA (from steady code 0): d=1 and d=2
for d in (1, 2):
    _, tr = run([17.0, 20.0, 29.0], d=d, ncyc_per=25)
    R[f"trace_d{d}"] = tr
    print(f"d={d} codes @17/20/29 mA:", "".join(map(str, tr[0])), "|", "".join(map(str, tr[1])), "|", "".join(map(str, tr[2])))
json.dump(R, open("res/c2_points.json", "w"), indent=1, default=float)
