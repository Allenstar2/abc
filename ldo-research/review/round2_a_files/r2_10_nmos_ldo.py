"""R2-10：時脈供電用途的對照組——最簡 NMOS source-follower pass LDO（Vin 1.8 V、Vout 1.0 V、≤10 mA）。
EA：NMOS 輸入 5T OTA（同 REF-A 尺寸），fb 接 M2（反相端）；ea 直接驅動 NMOS pass 閘極；Cc 由 ea 接地（主極點）。
目的只是看 1–100 MHz PSRR 的量級差異，**不是**最佳化設計。與 REF-A 類（PMOS pass）在同負載比較。"""
import json, numpy as np
from common import run, MODEL, RES
def at(f, ps, fq): return round(float(np.interp(np.log10(fq), np.log10(f), ps)), 1)
FQ = [1e3, 1e5, 1e6, 1e7, 1e8]
def net(IL, kind, Wn=1000, Cc=5e-12, CL=100e-12, brk=False):
    fbin = "fbi" if brk else "fb"
    s = f"""* nldo
.include {MODEL}
.options reltol=1e-4
Ibias vin bn 10u
Mbn bn bn 0 0 NMOS W=4u L=1u
Mt tail bn 0 0 NMOS W=8u L=1u
M1 d1 vref tail 0 NMOS W=20u L=1u
M2 ea {fbin} tail 0 NMOS W=20u L=1u
M3 d1 d1 vin vin PMOS W=4u L=1u
M4 ea d1 vin vin PMOS W=4u L=1u
Cc ea 0 {Cc}
Mp vin ea vout 0 NMOS W={Wn}u L=0.18u
R1 vout fb 1k
R2 fb 0 4k
CL vout 0 {CL}
IL vout 0 DC {IL}
VREF vref 0 0.8
"""
    if kind == "psrr":
        s += f"VIN vin 0 DC 1.8 AC 1\n.control\nop\nprint v(vout) v(ea)\nac dec 20 10 1e9\nwrdata {RES}/r210.txt v(vout)\nquit\n.endc\n.end\n"
    else:
        s += f"VIN vin 0 DC 1.8\nLbrk fb fbi 1e9\nCbrk fbi acs 1\nVAC acs 0 DC 0 AC 1\n.control\nop\nprint v(vout) v(ea)\nac dec 40 10 1e10\nlet T = -v(fb)/v(fbi)\nwrdata {RES}/r210T.txt T\nquit\n.endc\n.end\n"
    return s
from ldo_ref import margins
R = []
for IL in (0, 1e-3, 10e-3):
    out = run(net(IL, "lg", brk=True), "r210lg")
    a = np.loadtxt(f"{RES}/r210T.txt"); f = a[:, 0]; T = a[:, 1] + 1j * a[:, 2]; m = margins(f, T)
    out2 = run(net(IL, "psrr"), "r210ps")
    vo = [l for l in out2.splitlines() if l.strip().startswith("v(vout)")][0]; ve = [l for l in out2.splitlines() if l.strip().startswith("v(ea)")][0]
    b = np.loadtxt(f"{RES}/r210.txt"); ps = 20 * np.log10(np.hypot(b[:, 1], b[:, 2]))
    R.append(dict(IL_mA=IL * 1e3, op=vo.strip() + "; " + ve.strip(), dc_db=round(m["dc_db"], 1), ugf_MHz=round(m["ugf"] / 1e6, 2), pm=round(m["pm"], 1),
                  psrr_1k_100k_1M_10M_100M=[at(b[:, 0], ps, x) for x in FQ]))
    print(R[-1], flush=True)
json.dump(R, open(f"{RES}/r2_10_nmos_ldo.json", "w"), indent=1)
