"""負載平台掃描：每個設定 × 每個負載 L（從 5 mA 往上、或從 95 mA 往下，100 ns 邊沿）跑 25 µs，
看最後 12 µs 是否 p-p>20 mV 或平均值偏離無 droop 基準 >10 mV；另跑 5→95 mA（100 ns）量 undershoot。
用法：python3 h2_sweep.py <實驗名>，結果寫 res/h2_<實驗名>.json。"""
import sys, json, time; sys.path.insert(0, '.')
import numpy as np
from multiprocessing import Pool
from hyb_model import DEF, calibrate, sim, window_metrics

K, Vt = calibrate()
BASE = dict(DEF, K=K, Vt=Vt)
LOADS = np.arange(2, 97, 3) * 1e-3          # 2..95 mA，共 32 點
T_STEP, TE, T_END, W0 = 3e-6, 100e-9, 25e-6, 13e-6


def code_for(I):
    # 穩態碼：讓類比電流落在窗口 3–18 mA 內（從低碼開始）
    c = 0
    while I - c * BASE['Is_nom'] > 18e-3 and c < BASE['N']:
        c += 1
    return c


def run_cfg(args):
    name, over = args
    p = dict(BASE, **over)
    sets, Ib, ic, tags = [], [], [], []
    for d in ('up', 'down'):
        I0 = 5e-3 if d == 'up' else 95e-3
        for L in LOADS:
            sets.append(p); Ib.append([I0, I0, L, L]); ic.append(code_for(I0)); tags.append((d, float(L)))
    sets.append(p); Ib.append([5e-3, 5e-3, 95e-3, 95e-3]); ic.append(0); tags.append(('step', 0.095))
    tb = np.array([0, T_STEP, T_STEP + TE, T_END])
    r = sim(sets, tb, np.array(Ib), T_END, ic_code=ic)
    pp, mean, nchg, ndr = window_metrics(r, W0, T_END, 1.6)
    pre = r['V'][(r['t'] > T_STEP - 0.5e-6) & (r['t'] < T_STEP)].mean(0)
    us = (pre - r['V'][r['t'] > T_STEP].min(0)) * 1e3
    ov = (r['V'][r['t'] > T_STEP].max(0) - pre) * 1e3
    rows = []
    for j, (d, L) in enumerate(tags):
        rows.append(dict(dir=d, IL_mA=round(L * 1e3, 1), pp_mV=round(float(pp[j]), 2), mean_mV=round(float(mean[j]), 2), n_code_chg=int(nchg[j]),
                         n_droop=int(ndr[j]), code_end=int(r['code'][-1, j]), us_mV=round(float(us[j]), 1), ov_mV=round(float(ov[j]), 1)))
    return name, rows


def summarize(name, rows, base_rows=None):
    plat = [x for x in rows if x['dir'] != 'step']
    if base_rows is not None:
        bmap = {(x['dir'], x['IL_mA']): x['mean_mV'] for x in base_rows}
        for x in plat:
            x['dmean_mV'] = round(x['mean_mV'] - bmap[(x['dir'], x['IL_mA'])], 2)
    fail = [x for x in plat if x['pp_mV'] > 20 or abs(x.get('dmean_mV', 0)) > 10]
    step = [x for x in rows if x['dir'] == 'step'][0]
    return dict(name=name, n_fail=len(fail), n_total=len(plat), us_100ns_mV=step['us_mV'],
                fail_loads_up=[x['IL_mA'] for x in fail if x['dir'] == 'up'], fail_loads_down=[x['IL_mA'] for x in fail if x['dir'] == 'down'],
                max_pp_mV=max(x['pp_mV'] for x in plat), max_abs_dmean_mV=max(abs(x.get('dmean_mV', 0)) for x in plat))


EXPS = {
 'A_reviewer_space': [
    ('nodroop_toff1n', {}),
    ('nodroop_toff300n', dict(t_off=300e-9)),
    ('vout_toff1n', dict(droop=1)),
    ('vout_toff300n', dict(droop=1, t_off=300e-9)),
    ('vout_toff1u', dict(droop=1, t_off=1e-6)),
 ] + [(f'gate{vg:.2f}_toff{tn}', dict(droop=1, V_gate=vg, t_off=to)) for vg in (1.20, 1.25, 1.30, 1.35) for tn, to in (('300n', 300e-9), ('1u', 1e-6))],
 'B_mechanism': [
    ('vout_antiwindup', dict(droop=1, e_max=1.78)),
    ('vout_toff3u', dict(droop=1, t_off=3e-6)),
    ('vout_toff1u_antiwindup', dict(droop=1, t_off=1e-6, e_max=1.78)),
    ('vout_toff300n_antiwindup', dict(droop=1, t_off=300e-9, e_max=1.78)),
    ('vout_Vdr1.50', dict(droop=1, V_dr=1.50)),
    ('vout_Vdr1.45', dict(droop=1, V_dr=1.45)),
    ('vout_Vdr1.40', dict(droop=1, V_dr=1.40)),
    ('vout_hys20m', dict(droop=1, V_hys=0.02)),
    ('vout_blank3u', dict(droop=1, T_blank=3e-6)),
    ('vout_blank10u', dict(droop=1, T_blank=10e-6)),
    ('vout_kmax2', dict(droop=1, k_max=2)),
    ('vout_div8', dict(droop=1, div=8)),
 ],
}

if __name__ == '__main__':
    exp = sys.argv[1]
    cfgs = EXPS[exp] if exp in EXPS else json.load(open(exp))
    base_rows = None
    try:
        base_rows = json.load(open('res/h2_A_reviewer_space.json'))['raw']['nodroop_toff1n'] if 'W800' not in exp else None
    except Exception:
        pass
    t0 = time.time()
    with Pool(4) as pool:
        res = pool.map(run_cfg, cfgs)
    raw = dict(res)
    if base_rows is None:
        nk = [k for k in raw if 'nodroop_toff1n' in k]
        if nk:
            base_rows = raw[nk[0]]
    summ = [summarize(n, raw[n], base_rows) for n, _ in cfgs]
    for s in summ:
        print(s, flush=True)
    tag = exp if exp in EXPS else exp.split('/')[-1].replace('.json', '')
    json.dump(dict(cfgs=cfgs, summary=summ, raw=raw), open(f'res/h2_{tag}.json', 'w'), indent=1)
    print('time', time.time() - t0)
