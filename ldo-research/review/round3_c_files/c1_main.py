"""主張 1 主表：相同 Vout(1.0 V)、相同 CL(100 pF)、相同分壓(200 µA 最小負載)，最差 PM 對齊(~64–66°)。
每個設計跑 EA 供電 = Vin（預設）與 EA 供電 = 乾淨 1.8 V 兩種。輸出 res/c1_main.json。"""
import sys, json; sys.path.insert(0, '.')
from c1_lib import *
base = dict(Vin=1.8, Vref=0.8, CL=100e-12, R1=1e3, R2=4e3, Ibias=10e-6)
D = {
 'P400_Cc6':    dict(base, kind='pmos', Wp=400, Cc=6e-12),
 'P4000_Cc8':   dict(base, kind='pmos', Wp=4000, Cc=8e-12),
 'N1000_Cc3':   dict(base, kind='nmos', Wn=1000, Cc=3e-12),
 'N1000iq_Cc8': dict(base, kind='nmos', Wn=1000, Cc=8e-12, tail_mult=8, Wld=16),
 'N2000_Cc5':   dict(base, kind='nmos', Wn=2000, Cc=5e-12),
}
FQ = (1e3, 1e5, 1e6, 1e7, 1e8)
loads = (0, 1e-3, 10e-3, 20e-3)
R = {}
for nm, p0 in D.items():
    for sup in ('vin', 'clean'):
        p = dict(p0, ea_supply=sup); key = f"{nm}|ea={sup}"; R[key] = []
        for IL in loads:
            fT, T = loopgain(p, IL, 'm_lg'); m = margins(fT, T)
            d, f, vo, vg = op_and_ac(p, IL, 'm_ps')
            fo, Gol, hol = openloop_psr(p, IL, 'm_ol')
            Ti = np.interp(np.log10(fo), np.log10(fT), T.real) + 1j * np.interp(np.log10(fo), np.log10(fT), T.imag)
            iq = d['iin'] - IL - d['vout_op'] / (p['R1'] + p['R2']) + d.get('iea', 0.0)
            row = dict(IL_mA=IL * 1e3, vout=round(d['vout_op'], 4), vgate=round(d['vg_op'], 3), iq_ctrl_uA=round(iq * 1e6, 1),
                       iq_total_uA=round((iq + d['vout_op'] / (p['R1'] + p['R2'])) * 1e6, 1),
                       gm_mS=round(d['gm_p'] * 1e3, 2), gds_mS=round(d['gds_p'] * 1e3, 3), gmb_mS=round(d['gmb_p'] * 1e3, 2),
                       dc_db=round(m['dc_db'], 1), ugf_MHz=round(m['ugf_MHz'], 2), pm=round(m['pm'], 1), gm_db=round(m['gm_db'], 1),
                       psrr=[round(at_db(f, vo, x), 1) for x in FQ],
                       Gol=[round(at_db(fo, Gol, x), 1) for x in FQ],
                       one_plus_T=[round(at_db(fo, 1 + Ti, x), 1) for x in FQ],
                       pred_Gol_over_1pT=[round(at_db(fo, Gol / (1 + Ti), x), 1) for x in FQ],
                       h_gate_cl=[round(at_db(f, vg, x), 1) for x in FQ])
            R[key].append(row)
            print(key, row, flush=True)
json.dump(dict(freqs=FQ, designs={k: {kk: (vv if not isinstance(vv, float) else vv) for kk, vv in v.items()} for k, v in D.items()}, rows=R),
          open('res/c1_main.json', 'w'), indent=1)
