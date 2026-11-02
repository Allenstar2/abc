"""R2-1：結論 v2 理由 3 說「HBM/SerDes 在意 MHz–百 MHz 的 PSRR，B/C 在這個指標上結構性吃虧」。
檢查：REF-A 與公平 B（Wa=2.4 mm，碼凍結）在 1 kHz–100 MHz 的 PSRR 差距；另加 A 的 1 nF＋Rz 版本。"""
import json, numpy as np
from common import run, MODEL, RES
from ldo_ref import DEFAULT, subckt, psrr
from ldo_hybrid import HDEF

FREQS = [1e3, 1e5, 1e6, 1e7, 1e8]
def at(f, ps, fq): return round(float(np.interp(np.log10(fq), np.log10(f), ps)), 1)

def psrr_B(Wa, k, IL, name, CL=100e-12):
    p = dict(HDEF, Wp=Wa)
    sl = "\n".join((f"Ms{i} vout vin vin vin PMOS W=130u L=0.18u" if i > k else f"Ms{i} vout 0 vin vin PMOS W=130u L=0.18u") for i in range(1, 9))
    net = f"* psr\n.include {MODEL}\n{subckt(p)}\nVIN vin 0 DC 1.8 AC 1\nVREF vref 0 0.8\nX1 vin vout vref fb fb ldoA\n{sl}\nCL vout 0 {CL}\nIL vout 0 DC {IL}\n.control\nop\nprint v(vout) v(x1.pg)\nac dec 20 10 1e9\nwrdata {RES}/{name}.txt v(vout)\nquit\n.endc\n.end\n"
    out = run(net, name)
    vo = [l for l in out.splitlines() if l.strip().startswith("v(vout)")]
    a = np.loadtxt(f"{RES}/{name}.txt")
    return a[:, 0], 20*np.log10(np.hypot(a[:, 1], a[:, 2])), vo[0] if vo else ""

R = {}
for IL in (20e-3, 70e-3):
    rows = {}
    pA = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
    f, ps = psrr(pA, IL, "r21_A"); rows["A_100p_Cc5"] = [at(f, ps, x) for x in FREQS]
    pA2 = dict(DEFAULT, CL=1e-9, Cc=8e-12, Rz=10e3, R1=4e3, R2=4e3)
    f, ps = psrr(pA2, IL, "r21_A1n"); rows["A_1n_Cc8_Rz10k"] = [at(f, ps, x) for x in FREQS]
    for k in ((0, 1) if IL < 50e-3 else (3, 5)):
        f, ps, vo = psrr_B(2400, k, IL, f"r21_B{k}")
        rows[f"B_Wa2400_code{k}"] = [at(f, ps, x) for x in FREQS]
        rows[f"B_Wa2400_code{k}_op"] = vo
    R[f"IL_{IL*1e3:.0f}mA"] = rows
    print(IL, json.dumps(rows, ensure_ascii=False), flush=True)
R["freqs_Hz"] = FREQS
json.dump(R, open(f"{RES}/r2_1_psrr_hf.json", "w"), indent=1, ensure_ascii=False)
