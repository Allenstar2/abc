"""行為模型 vs 電晶體級（c2_xcheck_spice）：同一情境（95 mA、碼 7 → 負載降到 2/5/11 mA → 同步每 100 ns 減一片），比較最後一次減片後的下陷。"""
import sys, json; sys.path.insert(0, '.')
import numpy as np
from hyb_model import DEF, calibrate, sim
K, Vt = calibrate()
P, tags = [], []
for IL in (2e-3, 5e-3, 11e-3):
    for toff in (1e-9, 300e-9, 1e-6):
        P.append(dict(DEF, K=K, Vt=Vt, t_off=toff, VL=-1.0, t_sync0=2.15e-6)); tags.append((IL, toff))
Ib = np.array([[95e-3, 95e-3, IL, IL] for IL, _ in tags])
r = sim(P, np.array([0, 2e-6, 2.1e-6, 10e-6]), Ib, 4.5e-6, ic_code=[7] * len(P))
sp = {(x['IL_end_mA'], x['t_off_ns']): x for x in json.load(open('res/c2_xcheck_spice.json'))}
out = []
for j, (IL, toff) in enumerate(tags):
    v95 = r['V'][(r['t'] > 1.5e-6) & (r['t'] < 2e-6), j].mean()
    w = r['t'] > 2.75e-6
    dip = (v95 - r['V'][w, j].min()) * 1e3
    s = sp[(IL * 1e3, toff * 1e9)]
    out.append(dict(IL_end_mA=IL * 1e3, t_off_ns=toff * 1e9, model_dip_mV=round(float(dip), 1), spice_dip_mV=s['dip_below_95mA_level_mV'],
                    model_Vmax=round(float(r['V'][(r['t'] > 2e-6) & (r['t'] < 2.75e-6), j].max()), 4), spice_Vmax=s['V_max_after_release']))
    print(out[-1])
json.dump(out, open('res/h6_model_vs_spice.json', 'w'), indent=1)
