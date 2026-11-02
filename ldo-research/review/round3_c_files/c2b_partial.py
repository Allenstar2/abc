"""電晶體級：95→45 mA（碼 7→3）與 95→20 mA（碼 7→1）的「部分減片」情境（同步迴路實際會停在的碼），量下陷。"""
import sys, json; sys.path.insert(0, '.')
import numpy as np
from c1_lib import run, RES
import c2_xcheck_spice as X
out = []
for IL_end, code_end in ((45e-3, 3), (20e-3, 1)):
    for toff in (1e-9, 300e-9, 1e-6):
        nm = f"xcp_{IL_end*1e3:g}mA_{toff*1e9:g}n"
        s = X.netlist(IL_end, toff, nm)
        # 只關掉 slice code_end+1..7：把 1..code_end 的 PWL 改成常 0
        for k in range(1, code_end + 1):
            import re
            s = re.sub(rf"Vg{k} g{k} 0 PWL\([^)]*\)", f"Vg{k} g{k} 0 0", s)
        run(s, nm)
        a = np.loadtxt(f"{RES}/{nm}.txt"); t = a[:, 0]; v = a[:, 1]
        v95 = v[(t > 1.5e-6) & (t < 2e-6)].mean(); w = t > 2.2e-6
        rec = dict(IL_end_mA=IL_end * 1e3, code_end=code_end, t_off_ns=toff * 1e9, V_min=round(float(v[w].min()), 4),
                   dip_below_nom_mV=round(float((v95 - v[w].min()) * 1e3), 1), V_end=round(float(v[t > 4.3e-6].mean()), 4))
        out.append(rec); print(rec, flush=True)
json.dump(out, open('res/c2b_partial.json', 'w'), indent=1)
