"""Claim B, part 3: Rz/Cc tolerance on top of temp & |Vth| corners (worst PM over 8 loads)."""
import json, numpy as np
from concurrent.futures import ThreadPoolExecutor
import b1_lg_corners as b1
from b1_lg_corners import lg, LOADS
from rv import RES
var = {}
for Rz in (6e3, 8e3, 10e3, 12e3, 14e3, 16e3):
    for Cc in (7.2e-12, 8e-12, 8.8e-12):
        var[f"D1v_Rz{Rz/1e3:g}k_Cc{Cc*1e12:g}p"] = dict(CL=1e-9, Cc=Cc, Rz=Rz)
b1.DESIGNS.update(var)
jobs = [(d, T, dn, dp, IL) for d in var for T in (-40, 27, 125) for dn, dp in ((0, 0), (50, 50), (-50, 50), (-50, -50)) for IL in LOADS]
with ThreadPoolExecutor(4) as ex:
    R = list(ex.map(lambda j: lg(*j), jobs))
json.dump(R, open(f"{RES}/b3_rz_tol.json", "w"), indent=0)
from collections import defaultdict
g = defaultdict(list)
for r in R:
    if r['vout'] < 1.62:          # skip corners that are out of regulation (pass leakage > bleed)
        g[(r['design'])].append(r)
for d, v in g.items():
    w = min(v, key=lambda r: r['pm'])
    print(d, 'worst PM %.1f at T=%d n%+d p%+d IL=%g mA' % (w['pm'], w['temp'], w['dn'], w['dp'], w['IL_mA']), 'minGM %.1f' % min((r['gm_db'] or 99) for r in v), 'n=', len(v))
