"""Cc 掃描：在相同 Vout=1.0 V、CL=100 pF、相同分壓（200 µA）下，PMOS（Wp=400/4000 µm）與 NMOS（Wn=1000 µm）的
最差 PM 與 PSRR@1M/10M 隨 Cc 的取捨。用來挑「相同最差 PM」的公平設計點。"""
import sys, json; sys.path.insert(0, '.')
from c1_lib import *
base = dict(Vin=1.8, Vref=0.8, CL=100e-12, R1=1e3, R2=4e3, Ibias=10e-6)
cfgs = {
 'P400':  dict(base, kind='pmos', Wp=400),
 'P4000': dict(base, kind='pmos', Wp=4000),
 'N1000': dict(base, kind='nmos', Wn=1000),
 'N1000_t8': dict(base, kind='nmos', Wn=1000, tail_mult=8),   # EA 尾電流 80 µA → 控制器 Iq ≈ PMOS 版
}
loads = (0, 1e-3, 10e-3, 20e-3)
R = {}
for nm, p0 in cfgs.items():
    R[nm] = []
    ccs = (1.5e-12, 2e-12, 3e-12, 4e-12, 6e-12, 8e-12) if nm.startswith('P') else (1e-12, 2e-12, 3e-12, 5e-12, 8e-12, 12e-12, 20e-12)
    for Cc in ccs:
        p = dict(p0, Cc=Cc); row = dict(Cc_pF=Cc*1e12, per_load=[])
        for IL in loads:
            fT, T = loopgain(p, IL, 'cs_lg'); m = margins(fT, T)
            d, f, vo, vg = op_and_ac(p, IL, 'cs_ps')
            row['per_load'].append(dict(IL_mA=IL*1e3, vout=round(d.get('vout_op', float('nan')), 4), pm=round(m['pm'], 1), ugf=round(m['ugf_MHz'], 2), dc=round(m['dc_db'], 1),
                                        ps=[round(at_db(f, vo, x), 1) for x in (1e3, 1e6, 1e7, 1e8)]))
        row['pm_min'] = min(x['pm'] for x in row['per_load'])
        R[nm].append(row)
        print(nm, row['Cc_pF'], 'PMmin', row['pm_min'], [(x['IL_mA'], x['pm'], x['ugf'], x['ps'][1], x['ps'][2], x['vout']) for x in row['per_load']], flush=True)
json.dump(R, open('res/c1_ccsweep.json', 'w'), indent=1)
