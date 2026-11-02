"""手算 vs 模擬：REF-A 迴路增益 (DC gain, UGF, PM)。
手算模型：兩級 Miller（EA 輸出節點 + Vout 節點）＋ buffer 極點 + RHP zero。
小訊號參數取自 ngspice OP（gm, gds），閘極電容以 AC 量測（BSIM3v1 不輸出電容）。
"""
import json, numpy as np, sys
from ldo_ref import DEFAULT, loopgain, margins
from ldo_op import op_params, cgate_meas
from common import RES

def hand(p, r, Cpg, C1=50e-15):
    beta = p["R2"] / (p["R1"] + p["R2"])
    gm1 = 0.5 * (r["m1_gm"] + r["m2_gm"])
    Gea = r["m2_gds"] + r["m4_gds"]
    gsf = r["mb_gm"] + r["mb_gds"] + r["mcs_gds"]
    Asf = r["mb_gm"] / gsf
    G2 = r["mp_gm"] * Asf
    Go = r["mp_gds"] + 1 / (p["R1"] + p["R2"])
    Cc, CL = p["Cc"], p["CL"]
    T0 = beta * gm1 / Gea * G2 / Go
    S = C1 * Go + CL * Gea + Cc * (G2 + Gea + Go)
    p1 = Gea * Go / S
    p2 = S / (C1 * CL + Cc * (C1 + CL))
    z = G2 / Cc
    pb = gsf / Cpg
    f = np.logspace(1, 10, 20000); s = 2j * np.pi * f
    T = T0 * (1 - s / z) / ((1 + s / p1) * (1 + s / p2) * (1 + s / pb))
    m = margins(f, T)
    return dict(T0_dB=20*np.log10(T0), GBW_MHz=beta*gm1*G2/S/2/np.pi/1e6, p1_kHz=p1/2/np.pi/1e3,
                p2_MHz=p2/2/np.pi/1e6, z_MHz=z/2/np.pi/1e6, pbuf_MHz=pb/2/np.pi/1e6,
                UGF_MHz=m["ugf"]/1e6, PM=m["pm"], Asf=Asf, gmp_mS=r["mp_gm"]*1e3, Ap=r["mp_gm"]/Go)

out = []
cases = [("CL100p_Cc5p", dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)),
         ("CL1n_Cc20p", dict(DEFAULT, CL=1e-9, Cc=20e-12, R1=4e3, R2=4e3)),
         ("orig_Imin50u_Cc3p", dict(DEFAULT))]
for tag, p in cases:
    for IL in (0, 10e-3, 100e-3):
        r = op_params(p, IL, f"hvs_op_{tag}_{IL}")
        Cpg = cgate_meas(p["Wp"], p["Lp"], max(p["Vin"] - r["v_vout"], 0.01), r["v_x1.pg"], "hvs_cg")
        h = hand(p, r, Cpg)
        f, T, v = loopgain(p, IL, f"hvs_lg_{tag}_{IL}")
        m = margins(f, T)
        row = dict(case=tag, IL_mA=IL*1e3, Cpg_pF=Cpg*1e12, hand=h,
                   sim=dict(T0_dB=m["dc_db"], UGF_MHz=m["ugf"]/1e6, PM=m["pm"]))
        row["err_pct"] = dict(T0=100*(10**(h["T0_dB"]/20)/10**(m["dc_db"]/20)-1),
                              UGF=100*(h["UGF_MHz"]/row["sim"]["UGF_MHz"]-1),
                              PM=100*(h["PM"]/m["pm"]-1))
        out.append(row)
        print(f"{tag:18s} IL={IL*1e3:5.1f}mA | T0 {h['T0_dB']:5.1f} vs {m['dc_db']:5.1f} dB | "
              f"UGF {h['UGF_MHz']:5.2f} vs {m['ugf']/1e6:5.2f} MHz | PM {h['PM']:5.1f} vs {m['pm']:5.1f} | "
              f"p2 {h['p2_MHz']:7.2f}MHz pbuf {h['pbuf_MHz']:6.1f}MHz z {h['z_MHz']:8.1f}MHz Ap={h['Ap']:.2f} Cpg={Cpg*1e12:.2f}pF")
json.dump(out, open(f"{RES}/s2_hand_vs_sim.json", "w"), indent=1, default=float)
