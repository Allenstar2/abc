"""數值收斂檢查：dt=0.1 ns vs 0.05 ns，幾個代表性負載/設定的 p-p 與 undershoot。"""
import sys, json; sys.path.insert(0, '.')
import numpy as np
from hyb_model import DEF, calibrate, sim, window_metrics
K, Vt = calibrate(); B = dict(DEF, K=K, Vt=Vt)
cfgs = {'vout_toff1n': dict(droop=1), 'vout_toff300n': dict(droop=1, t_off=300e-9), 'gate1.36_toff300n': dict(droop=1, V_gate=1.36, t_off=300e-9), 'R2_brm1u': dict(droop=1, T_brm=1e-6, t_off=300e-9)}
cases = [('down', 5e-3), ('down', 20e-3), ('up', 20e-3), ('down', 47e-3), ('step', 95e-3)]
P, Ib, ic, tags = [], [], [], []
for cn, o in cfgs.items():
    for d, L in cases:
        I0 = 95e-3 if d == 'down' else 5e-3
        P.append(dict(B, **o)); Ib.append([I0, I0, L, L]); ic.append(7 if d == 'down' else 0); tags.append((cn, d, L))
out = {}
for dt in (0.1e-9, 0.05e-9):
    r = sim(P, np.array([0, 3e-6, 3.1e-6, 25e-6]), np.array(Ib), 25e-6, dt=dt, rec_every=int(round(1e-9 / dt)), ic_code=ic)
    pp, mean, nchg, ndr = window_metrics(r, 13e-6, 25e-6, 1.6)
    pre = r['V'][(r['t'] > 2.5e-6) & (r['t'] < 3e-6)].mean(0); us = (pre - r['V'][r['t'] > 3e-6].min(0)) * 1e3
    for j, tg in enumerate(tags):
        out.setdefault('|'.join(map(str, tg)), {})[f'dt={dt*1e9:g}ns'] = dict(pp_mV=round(float(pp[j]), 1), us_mV=round(float(us[j]), 1), osc=bool(pp[j] > 20))
for k, v in out.items():
    print(k, v)
json.dump(out, open('res/h7_dtcheck.json', 'w'), indent=1)
