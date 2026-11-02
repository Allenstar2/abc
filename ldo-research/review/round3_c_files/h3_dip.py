"""「自己造成的下陷」包絡：關掉 droop 路徑，讓系統從「burst 之後」的狀態開始（碼 = 穩態碼 + k，類比被切斷、EA windup），
t_sync0=2 µs 後同步迴路開始減片。量測減片過程中的 min Vout，以及 Vout<V_dr 期間的 min pg。
預測規則：若 min Vout < V_dr（且 gated 時 min pg|V<V_dr < V_gate）→ droop 會被自己的減片重新觸發 → 弛張振盪。
與 h2 掃描（實際開 droop 路徑）的失效負載比對。"""
import sys, json; sys.path.insert(0, '.')
import numpy as np
from multiprocessing import Pool
from hyb_model import DEF, calibrate, sim

K, Vt = calibrate(); K8, Vt8 = calibrate(pg_lo=1.39, pg_hi=1.155)
VAR = {'W2400': dict(K=K, Vt=Vt), 'W800': dict(K=K8, Vt=Vt8, VL=1.155, VH=1.39, e_min=0.6)}
LOADS = np.arange(2, 97, 3) * 1e-3
VDR = 1.57


def code_for(I):
    c = 0
    while I - c * DEF['Is_nom'] > 18e-3 and c < DEF['N']:
        c += 1
    return c


def job(args):
    var, toff, emax = args
    sets, Ib, ic, tags = [], [], [], []
    for k in (1, 2):
        for L in LOADS:
            c = min(code_for(L) + k, DEF['N'])
            sets.append(dict(DEF, **VAR[var], t_off=toff, e_max=emax, t_sync0=2e-6)); Ib.append([L, L]); ic.append(c); tags.append((k, float(L)))
    r = sim(sets, np.array([0, 10e-6]), np.array(Ib), 6.5e-6, ic_code=ic)
    m = r['t'] >= 2e-6
    V = r['V'][m]; pg = r['pg'][m]
    minV = V.min(0)
    low = V < VDR
    minpg_low = np.where(low.any(0), np.where(low, pg, 9.0).min(0), 9.0)
    t_low = low.sum(0) * (r['t'][1] - r['t'][0])
    out = []
    for j, (k, L) in enumerate(tags):
        out.append(dict(k=k, IL_mA=round(L * 1e3, 1), minV=round(float(minV[j]), 4), dip_below_nom_mV=round(float((1.6 - minV[j]) * 1e3), 1),
                        minpg_when_low=round(float(minpg_low[j]), 3), t_below_Vdr_ns=round(float(t_low[j] * 1e9), 1),
                        V_start=round(float(r['V'][r['t'] < 2e-6][-1, j]), 4)))
    return f"{var}|toff={toff*1e9:g}n|emax={emax}", out


if __name__ == '__main__':
    jobs = [(v, to, em) for v in VAR for to in (1e-9, 300e-9, 1e-6) for em in (2.2, 1.78)]
    with Pool(4) as pool:
        res = dict(pool.map(job, jobs))
    json.dump(res, open('res/h3_dip.json', 'w'), indent=1)
    for k, rows in res.items():
        r1 = [x for x in rows if x['k'] == 1]
        print(k, 'max dip(k=1) mV', max(x['dip_below_nom_mV'] for x in r1), ' loads with minV<1.57 (k=1):', [x['IL_mA'] for x in r1 if x['minV'] < VDR])
