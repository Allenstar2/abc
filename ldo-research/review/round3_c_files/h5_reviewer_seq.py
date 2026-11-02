"""用前審查者 r1f_map2 的同一測試序列（5 mA → 95 mA(100 ns) → 45 → 20 mA，每段 10 µs，取各段最後 5 µs）
在 W800（REF-B，前審查者實際用的電路）與 W2400 上跑同一組 8 個 gated 設定＋對照，逐項比對。"""
import sys, json; sys.path.insert(0, '.')
import numpy as np
from hyb_model import DEF, calibrate, sim, window_metrics
K, Vt = calibrate(); K8, Vt8 = calibrate(pg_lo=1.39, pg_hi=1.155)
VAR = {'W800': dict(K=K8, Vt=Vt8, VL=1.155, VH=1.39, e_min=0.6), 'W2400': dict(K=K, Vt=Vt)}
names, P = [], []
for var, vp in VAR.items():
    cf = [('nodroop_toff1n', {}), ('nodroop_toff300n', dict(t_off=300e-9))]
    cf += [(f'gate{vg:.2f}_toff{tn}', dict(droop=1, V_gate=vg, t_off=to)) for vg in (1.20, 1.25, 1.30, 1.35) for tn, to in (('300n', 300e-9), ('1u', 1e-6))]
    cf += [('vout_toff300n', dict(droop=1, t_off=300e-9)), ('vout_brm1u_toff300n', dict(droop=1, T_brm=1e-6, t_off=300e-9))]
    for n, o in cf:
        names.append(f'{var}|{n}'); P.append(dict(DEF, **vp, **o))
te = 100e-9; t0 = 6e-6
tb = np.array([0, 1e-6, 1.1e-6, t0, t0 + te, t0 + te + 10e-6, t0 + 2 * te + 10e-6, t0 + 2 * te + 20e-6, t0 + 3 * te + 20e-6, t0 + 3 * te + 30e-6])
Ib = np.array([[0, 0, 5, 5, 95, 95, 45, 45, 20, 20]] * len(P)) * 1e-3
r = sim(P, tb, Ib, tb[-1])
pre = r['V'][(r['t'] > t0 - 0.5e-6) & (r['t'] < t0)].mean(0)
us = (pre - r['V'][(r['t'] > t0) & (r['t'] < t0 + 10e-6)].min(0)) * 1e3
win = {'p5': (t0 - 3e-6, t0), 'p95': (t0 + te + 5e-6, t0 + te + 10e-6), 'p45': (t0 + 2 * te + 15e-6, t0 + 2 * te + 20e-6), 'p20': (t0 + 3 * te + 25e-6, tb[-1])}
M = {k: window_metrics(r, a, b, 1.6) for k, (a, b) in win.items()}
out = []
for j, n in enumerate(names):
    row = dict(cfg=n, undershoot_100ns_mV=round(float(us[j]), 1))
    for k in win:
        pp, mean, nchg, ndr = M[k]
        row[k] = dict(pp_mV=round(float(pp[j]), 1), mean_mV=round(float(mean[j]), 1), n_code_chg=int(nchg[j]))
    base = 'W800|nodroop_toff1n' if n.startswith('W800') else 'W2400|nodroop_toff1n'
    out.append(row)
bm = {o['cfg']: o for o in out}
for o in out:
    b = bm['W800|nodroop_toff1n'] if o['cfg'].startswith('W800') else bm['W2400|nodroop_toff1n']
    o['all_ok'] = all(o[k]['pp_mV'] < 20 and abs(o[k]['mean_mV'] - b[k]['mean_mV']) < 10 for k in win)
    print(o['cfg'], o['undershoot_100ns_mV'], 'OK' if o['all_ok'] else 'FAIL', {k: (o[k]['pp_mV'], o[k]['mean_mV']) for k in win})
json.dump(out, open('res/h5_reviewer_seq.json', 'w'), indent=1)
