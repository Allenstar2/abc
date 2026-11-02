"""代價：NMOS-pass 的閘極 headroom。DC 掃負載，找 Vout 比無載掉 1% 的電流；Vin=1.8 V 與 1.71 V（-5%）。
另跑 Vout=1.2 V 的 PSRR/PM，以及「charge pump」情境（EA 供電 2.5 V 理想、Vout=1.6 V）。"""
import sys, json; sys.path.insert(0, '.')
from c1_lib import *
base = dict(Vref=0.8, CL=100e-12, R2=4e3, Ibias=10e-6)
R1 = {1.0: 1e3, 1.1: 1.5e3, 1.2: 2e3, 1.6: 4e3}
out = dict(dc=[], ac=[])
def dcsweep(p, name):
    net = header(p, name) + supplies(p, 0) + f"""VREF vref 0 {p['Vref']}
X1 vin vdda vout vref fb fb ldo
CL vout 0 {p['CL']}
IL vout 0 DC 0
.control
dc IL 0 60m 0.25m
wrdata {RES}/{name}_dc.txt v(vout) v({'x1.ea' if p['kind']=='nmos' else 'x1.pg'})
quit
.endc
.end
"""
    run(net, name); a = np.loadtxt(f"{RES}/{name}_dc.txt", ndmin=2)
    return a[:, 0], a[:, 1], a[:, 3]
for kind, W in (('nmos', 1000), ('nmos', 2000), ('nmos', 4000), ('pmos', 400)):
    for Vo in (1.0, 1.1, 1.2):
        for Vin in (1.8, 1.71):
            p = dict(base, kind=kind, Vin=Vin, R1=R1[Vo], Cc=3e-12, **({'Wn': W} if kind == 'nmos' else {'Wp': W}))
            I, v, g = dcsweep(p, 'hr')
            v0 = v[0]; bad = np.where(v < v0 * 0.99)[0]
            imax = float(I[bad[0]] * 1e3) if len(bad) else float('inf')
            row = dict(kind=kind, W=W, Vout_target=Vo, Vin=Vin, vout0=round(float(v0), 4), I_1pct_mA=round(imax, 2),
                       vgate_at_10mA=round(float(np.interp(10e-3, I, g)), 3), vout_at_10mA=round(float(np.interp(10e-3, I, v)), 4))
            out['dc'].append(row); print(row, flush=True)
# Vout=1.2 V 的 AC（Vin 1.8 V）
for nm, p in (('N1000_Cc3', dict(base, kind='nmos', Wn=1000, Cc=3e-12)), ('N4000_Cc8', dict(base, kind='nmos', Wn=4000, Cc=8e-12)), ('P400_Cc6', dict(base, kind='pmos', Wp=400, Cc=6e-12))):
    p = dict(p, Vin=1.8, R1=R1[1.2])
    for IL in (0, 1e-3, 5e-3, 10e-3):
        fT, T = loopgain(p, IL, 'hr_lg'); m = margins(fT, T); d, f, vo, vg = op_and_ac(p, IL, 'hr_ps')
        row = dict(design=nm + '@1.2V', IL_mA=IL * 1e3, vout=round(d['vout_op'], 4), vgate=round(d['vg_op'], 3), dc_db=round(m['dc_db'], 1), pm=round(m['pm'], 1), ugf=round(m['ugf_MHz'], 2),
                   psrr_1k_100k_1M_10M_100M=[round(at_db(f, vo, x), 1) for x in (1e3, 1e5, 1e6, 1e7, 1e8)])
        out['ac'].append(row); print(row, flush=True)
# charge-pump 情境：Vout 1.6 V，NMOS 閘極由 2.5 V 乾淨供電的 EA 驅動（理想 pump，未計 pump 漣波；氧化層耐壓未檢查）
for nm, p in (('N1000_cp2.5_Cc3', dict(base, kind='nmos', Wn=1000, Cc=3e-12, ea_supply='clean', Vdda=2.5)),
              ('P4000_Cc8(REF-A寬度)', dict(base, kind='pmos', Wp=4000, Cc=8e-12))):
    p = dict(p, Vin=1.8, R1=R1[1.6])
    for IL in (0, 1e-3, 10e-3, 50e-3):
        fT, T = loopgain(p, IL, 'cp_lg'); m = margins(fT, T); d, f, vo, vg = op_and_ac(p, IL, 'cp_ps')
        row = dict(design=nm + '@1.6V', IL_mA=IL * 1e3, vout=round(d['vout_op'], 4), vgate=round(d['vg_op'], 3), dc_db=round(m['dc_db'], 1), pm=round(m['pm'], 1), ugf=round(m['ugf_MHz'], 2),
                   psrr_1k_100k_1M_10M_100M=[round(at_db(f, vo, x), 1) for x in (1e3, 1e5, 1e6, 1e7, 1e8)])
        out['ac'].append(row); print(row, flush=True)
json.dump(out, open('res/c1_headroom.json', 'w'), indent=1)
