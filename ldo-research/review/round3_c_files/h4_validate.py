"""驗證判據：從「burst 之後」狀態（碼 = 穩態碼 + 1，同步迴路 2 µs 後啟動）開 droop 路徑跑 14 µs，
看最後 6 µs 是否振盪（p-p>20 mV）；與 h3 的下陷包絡判據（min V < V_dr 且 min pg|V<V_dr < V_gate）比對。"""
import sys, json; sys.path.insert(0, '.')
import numpy as np
from multiprocessing import Pool
from hyb_model import DEF, calibrate, sim, window_metrics

K, Vt = calibrate(); K8, Vt8 = calibrate(pg_lo=1.39, pg_hi=1.155)
VAR = {'W2400': dict(K=K, Vt=Vt), 'W800': dict(K=K8, Vt=Vt8, VL=1.155, VH=1.39, e_min=0.6)}
LOADS = np.arange(2, 97, 3) * 1e-3
dip = json.load(open('res/h3_dip.json'))


def code_for(I):
    c = 0
    while I - c * DEF['Is_nom'] > 18e-3 and c < DEF['N']:
        c += 1
    return c


CFG = []
for var in ('W2400', 'W800'):
    for toff in (1e-9, 300e-9, 1e-6):
        CFG.append((var, f'vout_toff{toff*1e9:g}n', dict(droop=1, t_off=toff), 9.9, toff, 2.2))
    CFG.append((var, 'vout_aw_toff1000n', dict(droop=1, t_off=1e-6, e_max=1.78), 9.9, 1e-6, 1.78))
gates = {'W2400': (1.30, 1.34, 1.36, 1.38), 'W800': (1.10, 1.15, 1.20, 1.30)}
for var in ('W2400', 'W800'):
    for vg in gates[var]:
        for toff in (300e-9, 1e-6):
            CFG.append((var, f'gate{vg:.2f}_toff{toff*1e9:g}n', dict(droop=1, V_gate=vg, t_off=toff), vg, toff, 2.2))


def job(c):
    var, name, over, vg, toff, emax = c
    sets, Ib, ic = [], [], []
    for L in LOADS:
        sets.append(dict(DEF, **VAR[var], **over, t_sync0=2e-6)); Ib.append([L, L]); ic.append(min(code_for(L) + 1, DEF['N']))
    r = sim(sets, np.array([0, 20e-6]), np.array(Ib), 14e-6, ic_code=ic)
    pp, mean, nchg, ndr = window_metrics(r, 8e-6, 14e-6, 1.6)
    d = {x['IL_mA']: x for x in dip[f"{var}|toff={toff*1e9:g}n|emax={emax}"] if x['k'] == 1}
    rows = []
    for j, L in enumerate(LOADS):
        x = d[round(L * 1e3, 1)]
        pred = (x['minV'] < 1.57) and (x['minpg_when_low'] < vg)
        rows.append(dict(IL_mA=round(L * 1e3, 1), osc=bool(pp[j] > 20), pp_mV=round(float(pp[j]), 1), pred=bool(pred)))
    agree = sum(r_['osc'] == r_['pred'] for r_ in rows)
    fn = [r_['IL_mA'] for r_ in rows if r_['osc'] and not r_['pred']]
    fp = [r_['IL_mA'] for r_ in rows if r_['pred'] and not r_['osc']]
    return dict(var=var, cfg=name, n_osc=sum(r_['osc'] for r_ in rows), n_pred=sum(r_['pred'] for r_ in rows), agree=agree, n=len(rows),
                missed=fn, false_alarm=fp, rows=rows)


if __name__ == '__main__':
    with Pool(4) as pool:
        res = pool.map(job, CFG)
    json.dump(res, open('res/h4_validate.json', 'w'), indent=1)
    for r in res:
        print(f"{r['var']:6s} {r['cfg']:22s} osc {r['n_osc']:2d}/32  pred {r['n_pred']:2d}/32  agree {r['agree']}/32  missed {r['missed']}  false_alarm {r['false_alarm']}")
