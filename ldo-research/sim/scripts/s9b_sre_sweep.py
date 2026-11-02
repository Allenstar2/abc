"""X4b：SRE 參數掃描（下拉強度 Wpd、上拉強度 Wpu、耦合電容 Cf）。全部結果都記錄，不只最佳值。"""
import json, itertools, ldo_ref
from ldo_ref import margins
from ldo_sre import SDEF, subckt as ss
from common import RES
orig = ldo_ref.subckt
rows = []
for Wpd, Wpu, Cf in itertools.product((10, 40, 160), (10, 40), (0.5e-12, 2e-12)):
    p = dict(SDEF, Wpd=Wpd, Wpu=Wpu, Cf1=Cf, Cf2=Cf)
    ldo_ref.subckt = ss
    try:
        pm0 = margins(*ldo_ref.loopgain(p, 0, "x4b_lg")[:2])["pm"]
        r = dict(Wpd=Wpd, Wpu=Wpu, Cf_pF=Cf * 1e12, pm0=round(pm0, 1))
        for te in (1e-9, 100e-9, 1e-6):
            t, vo, vpg, m = ldo_ref.load_step(p, 0, 100e-3, te, "x4b_tr", thold=6e-6)
            r[f"u{te*1e9:g}"] = round(m["undershoot"] * 1e3); r[f"o{te*1e9:g}"] = round(m["overshoot"] * 1e3)
    finally:
        ldo_ref.subckt = orig
    rows.append(r); print(r, flush=True)
json.dump(rows, open(f"{RES}/x4b_sre_sweep.json", "w"), indent=1)
