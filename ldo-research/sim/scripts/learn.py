"""LEARNING.md 的「先預測再看答案」實驗。用法：python3 learn.py Q1 （或 all）
每題都以 REF-A（CL=100 pF、Cc=5 pF、洩放 200 µA、Wp=4 mm）為基準，只改一個變數。"""
import sys, json, numpy as np
from ldo_ref import DEFAULT, loopgain, margins, psrr, load_step, header
from common import run, RES

BASE = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)

def pm_list(p, loads=(0, 1e-3, 100e-3)):
    out = []
    for IL in loads:
        f, T, v = loopgain(p, IL, "learn_lg"); m = margins(f, T)
        out.append(dict(IL_mA=IL * 1e3, PM=round(m["pm"], 1), UGF_MHz=round(m["ugf"] / 1e6, 2), DC_dB=round(m["dc_db"], 1)))
    return out

def us(p, I1=0, I2=100e-3, te=100e-9):
    t, vo, vpg, m = load_step(p, I1, I2, te, "learn_tr", thold=6e-6)
    return dict(undershoot_mV=round(m["undershoot"] * 1e3, 1), overshoot_mV=round(m["overshoot"] * 1e3, 1))

def dropout(p, IL=100e-3):
    net = header(p, "learn_dc") + f"""
VIN vin 0 1.8
VREF vref 0 0.8
X1 vin vout vref fb fb ldoA
IL vout 0 DC {IL}
.control
dc VIN 1.4 1.98 0.002
wrdata {RES}/learn_dc.txt v(vout)
quit
.endc
.end
"""
    run(net, "learn_dc")
    a = np.loadtxt(f"{RES}/learn_dc.txt"); vin, vo = a[:, 0], a[:, 1]
    vreg = vo[-1]; i = np.where(vo >= 0.99 * vreg)[0][0]
    return round(float(vin[i] - vo[i]) * 1e3, 1)

Q = {}
Q["Q1"] = lambda: {"Cc=5pF": dict(pm=pm_list(BASE), tr=us(BASE)), "Cc=2pF": dict(pm=pm_list(dict(BASE, Cc=2e-12)), tr=us(dict(BASE, Cc=2e-12))),
                   "Cc=10pF": dict(pm=pm_list(dict(BASE, Cc=10e-12)), tr=us(dict(BASE, Cc=10e-12)))}
Q["Q2"] = lambda: {f"Wp={w}um": dict(pm=pm_list(dict(BASE, Wp=w)), tr=us(dict(BASE, Wp=w)), dropout_mV=dropout(dict(BASE, Wp=w)))
                   for w in (2000, 4000, 8000)}
Q["Q3"] = lambda: {"CL=100p,Cc=5p": pm_list(BASE), "CL=1n,Cc=5p(不改Cc)": pm_list(dict(BASE, CL=1e-9))}
Q["Q4"] = lambda: {f"bleed={i*1e6:g}uA": dict(pm=pm_list(dict(BASE, R1=0.8 / i, R2=0.8 / i)), Iq_uA=round(loopgain(dict(BASE, R1=0.8 / i, R2=0.8 / i), 0, 'learn_iq')[2]['iin'] * 1e6, 1))
                   for i in (50e-6, 200e-6, 500e-6)}
Q["Q5"] = lambda: {f"tail={m*10}uA": dict(pm=pm_list(dict(BASE, tail_mult=m)), tr=us(dict(BASE, tail_mult=m))) for m in (1, 2, 4)}
Q["Q6"] = lambda: {f"I1={i*1e3:g}mA": us(BASE, I1=i, te=1e-9) for i in (0, 1e-3, 10e-3)}
Q["Q7"] = lambda: {f"edge={te*1e9:g}ns": us(BASE, te=te) for te in (1e-9, 100e-9, 1e-6)}
def q8():
    out = {}
    for T in (27, 125):
        f, Tl, v = loopgain(dict(BASE, temp=T), 0, "learn_t"); out[f"{T}C"] = dict(vout_noload=round(v["vout_op"], 4), vpg=round(v["vpg_op"], 3))
    return out
Q["Q8"] = q8
def q9():
    from ldo_hybrid import HDEF, run_hybrid
    out = {}
    for name, (VL, VH) in {"寬窗 3–18 mA": (1.155, 1.39), "窄窗 8–14 mA": (1.21, 1.30)}.items():
        t, vo, vpg, code = run_hybrid(dict(HDEF, VL=VL, VH=VH), "IL vout 0 PWL(0 0 1u 0 1.1u 20m)", 12e-6, "learn_hb")
        sel = t > 7e-6
        out[name] = dict(code_toggles_last5us=int(np.count_nonzero(np.diff(code[sel]))), vout_pp_mV=round(float(np.ptp(vo[sel]) * 1e3), 1))
    return out
Q["Q9"] = q9
def q10():
    f, ps = psrr(BASE, 70e-3, "learn_psr")
    a = round(float(np.interp(3, np.log10(f), ps)), 1)
    return {"REF-A 70mA PSRR@1kHz": a, "REF-B 碼5凍結 70mA PSRR@1kHz（見 sim/results/x3_hybrid.json X3c）": json.load(open(f"{RES}/x3_hybrid.json"))["X3c"]["REF-B_70mA_code5"]["1000"]}
Q["Q10"] = q10

if __name__ == "__main__":
    keys = list(Q) if (len(sys.argv) < 2 or sys.argv[1] == "all") else sys.argv[1:]
    res = {}
    for k in keys:
        res[k] = Q[k](); print(k, json.dumps(res[k], ensure_ascii=False), flush=True)
    if len(keys) == len(Q):
        json.dump(res, open(f"{RES}/learn_answers.json", "w"), indent=1, ensure_ascii=False)
