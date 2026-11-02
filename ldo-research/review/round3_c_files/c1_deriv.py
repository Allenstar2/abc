"""推導驗證：用 OP 小訊號參數 + 開迴路閘極轉移 h(f) 帶入解析式，預測開迴路 G_ol(f)，與模擬比較。
NMOS(source follower，閘極經 Cc 接地)：G_ol = (gds + gm·h)/(gm + gmb + gds + G_L + jωCL)
PMOS(common source，Miller Cc)：      G_ol = (gm·(1-h) + gds)/(gds + G_L + jωCL)，h = v(pg)/v(vin)
另外用 AC 測試量 NMOS pass 的 Cgd、Cgs，估 h_cgd ≈ Cgd/(Cc+Cgd+Cgs(1-A))。"""
import sys, json; sys.path.insert(0, '.')
from c1_lib import *
base = dict(Vin=1.8, Vref=0.8, CL=100e-12, R1=1e3, R2=4e3, Ibias=10e-6)
D = {'P400_Cc6': dict(base, kind='pmos', Wp=400, Cc=6e-12), 'N1000_Cc3': dict(base, kind='nmos', Wn=1000, Cc=3e-12),
     'N1000iq_Cc8': dict(base, kind='nmos', Wn=1000, Cc=8e-12, tail_mult=8, Wld=16)}
FQ = (1e5, 1e6, 1e7, 1e8)
out = {}
for nm, p0 in D.items():
    for sup in ('vin', 'clean'):
        p = dict(p0, ea_supply=sup)
        for IL in (1e-3, 10e-3):
            d, f, vo, vg = op_and_ac(p, IL, 'dv_ps')
            fo, G, h = openloop_psr(p, IL, 'dv_ol')
            gm, gds, gmb = d['gm_p'], d['gds_p'], d['gmb_p']; GL = 1 / (p['R1'] + p['R2']); w = 2 * np.pi * fo
            if p['kind'] == 'nmos':
                Gp = (gds + gm * h) / (gm + gmb + gds + GL + 1j * w * p['CL'])
                Gfloor = gds / (gm + gmb + gds + GL + 1j * w * p['CL'])      # h=0：只剩 pass 本身的 gds
            else:
                Gp = (gm * (1 - h) + gds) / (gds + GL + 1j * w * p['CL'])
                Gfloor = (gm + gds) / (gm + gds + GL + 1j * w * p['CL'])     # h=v(pg)=v(vout)（Miller 使閘極追 Vout）
            r = dict(gm_mS=round(gm * 1e3, 2), gds_mS=round(gds * 1e3, 3), gmb_mS=round(gmb * 1e3, 2),
                     gm_over_gds=round(gm / gds, 1),
                     G_sim=[round(at_db(fo, G, x), 1) for x in FQ], G_formula_with_simh=[round(at_db(fo, Gp, x), 1) for x in FQ],
                     G_simple=[round(at_db(fo, Gfloor, x), 1) for x in FQ], h_dB=[round(at_db(fo, h, x), 1) for x in FQ],
                     h_over_vout_dB=[round(at_db(fo, h / G, x), 1) for x in FQ])
            key = f"{nm}|ea={sup}|IL={IL*1e3:g}mA"; out[key] = r; print(key, r, flush=True)
# NMOS pass 電容（AC 法）：在 N1000 10 mA 的工作點
for IL, vg, vs in ((1e-3, 1.454, 0.993), (10e-3, 1.565, 0.9894)):
    net = f"""* cap
.include {MODEL}
VD d 0 DC 1.8 AC 1
VG g 0 DC {vg}
VS s 0 DC {vs}
M1 d g s 0 NMOS W=1000u L=0.18u
.control
ac lin 1 1e7 1e7
let cgd = imag(-i(vg))/(2*pi*1e7)
print cgd
alter vd ac=0
alter vg ac=1
ac lin 1 1e7 1e7
let cgg = imag(i(vg))/(2*pi*1e7)
let cgs = imag(i(vs))/(2*pi*1e7)
print cgg cgs
quit
.endc
.end
"""
    o = run(net, 'dv_cap'); vals = pvals(o, ['cgd', 'cgg', 'cgs'])
    out[f"N1000_caps_IL={IL*1e3:g}mA"] = {k: round(v * 1e12, 3) for k, v in vals.items()}
    print(IL, {k: v * 1e12 for k, v in vals.items()})
json.dump(out, open('res/c1_deriv.json', 'w'), indent=1)
