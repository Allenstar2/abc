"""R2-3：若規格改成較大 dropout（Vout=1.4/1.2 V，Vin=1.8 V），REF-A 拓樸的迴路增益、PSRR、暫態、Vin 容差怎麼變？
維持 200 µA 分壓洩放、Vref=0.8 V（改 β），Cc=5 pF、CL=100 pF。"""
import json, numpy as np
from common import run, RES
from ldo_ref import DEFAULT, header, loopgain, margins, psrr, load_step
def at(f, ps, fq): return round(float(np.interp(np.log10(fq), np.log10(f), ps)), 1)
R = []
for Vout, Wp in ((1.6, 4000), (1.4, 4000), (1.4, 1500), (1.2, 1500), (1.2, 800)):
    R2 = 4e3; R1 = (Vout - 0.8) / 200e-6
    p = dict(DEFAULT, Wp=Wp, CL=100e-12, Cc=5e-12, R1=R1, R2=R2)
    row = dict(Vout=Vout, Wp_um=Wp)
    pms = []
    for IL in (0, 1e-3, 10e-3, 100e-3):
        f, T, v = loopgain(p, IL, "r23_lg"); m = margins(f, T); pms.append(m["pm"])
        if IL == 100e-3: row["dc_db_100mA"] = round(m["dc_db"], 1); row["vout_100mA"] = round(v["vout_op"], 4); row["vpg_100mA"] = round(v["vpg_op"], 3)
        if IL == 0: row["dc_db_0"] = round(m["dc_db"], 1)
    row["pm_list_0_1_10_100mA"] = [round(x, 1) for x in pms]
    for IL in (10e-3, 100e-3):
        f, ps = psrr(p, IL, "r23_ps"); row[f"psrr_{IL*1e3:.0f}mA_1k_1M_10M"] = [at(f, ps, x) for x in (1e3, 1e6, 1e7)]
    t, vo, vpg, ms = load_step(p, 0, 100e-3, 100e-9, "r23_tr", thold=4e-6)
    row["undershoot_0to100mA_100ns_mV"] = round(ms["undershoot"] * 1e3, 1)
    row["load_reg_0to100mA_mV"] = round(ms["dv_load_reg"] * 1e3, 1)
    # Vin_min @100 mA
    net = header(p, "r23_dc") + f"\nVIN vin 0 DC 1.8\nVREF vref 0 0.8\nX1 vin vout vref fb fb ldoA\nIL vout 0 DC 0.1\n.control\ndc VIN 1.2 2.0 0.002\nwrdata {RES}/r23_dc.txt v(vout)\nquit\n.endc\n.end\n"
    run(net, "r23_dc"); a = np.loadtxt(f"{RES}/r23_dc.txt"); vin, vo = a[:, 0], a[:, 1]
    vo18 = np.interp(1.8, vin, vo); ok = vo > vo18 - 0.01 * Vout
    idx = len(vin) - 1
    while idx > 0 and ok[idx - 1]: idx -= 1
    row["vin_min_100mA_1pct"] = round(float(vin[idx]), 3)
    R.append(row); print(row, flush=True)
json.dump(R, open(f"{RES}/r2_3_vout_alt.json", "w"), indent=1)
