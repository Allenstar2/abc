"""第 3 輪 (a)：第三選項檢查——A4 NMOS-pass 放大到 100 mA（Vin 1.8 V、Vout 1.0 V）。
第 2 輪 (a) 的 r2_10 只到 10 mA、只看 PSRR。這裡問：同一個「最簡」NMOS-pass 在 0→100 mA 的
穩定度、undershoot（1/100/1000 ns）與 PSRR 是否全面優於 REF-A（A1，1.6 V）。
EA 與 r2_10 相同（NMOS 輸入 5T OTA、ea 直接驅動 NMOS pass、Cc 由 ea 接地），pass W 放大；
分壓 R1=1k、R2=4k（β=0.8，洩放 200 µA，與 REF-A 相同）。未最佳化。"""
import json, numpy as np
from common import run, MODEL, RES
from ldo_ref import margins

def core(Wn, Cc, CL, fbin="fb"):
    return f"""Ibias vin bn 10u
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
VREF vref 0 0.8
"""

def lg(Wn, Cc, CL, IL):
    s = f"* n100lg\n.include {MODEL}\n.options reltol=1e-4\n" + core(Wn, Cc, CL, "fbi") + \
        f"IL vout 0 DC {IL}\nVIN vin 0 DC 1.8\nLbrk fb fbi 1e9\nCbrk fbi acs 1\nVAC acs 0 DC 0 AC 1\n.control\nop\nprint v(vout) v(ea)\nac dec 40 10 1e10\nlet T = -v(fb)/v(fbi)\nwrdata {RES}/r3n_T.txt T\nquit\n.endc\n.end\n"
    out = run(s, "r3n_lg")
    a = np.loadtxt(f"{RES}/r3n_T.txt"); m = margins(a[:, 0], a[:, 1] + 1j * a[:, 2])
    vo = float([l for l in out.splitlines() if l.strip().startswith("v(vout)")][0].split("=")[1])
    ve = float([l for l in out.splitlines() if l.strip().startswith("v(ea)")][0].split("=")[1])
    return m, vo, ve

def psrr(Wn, Cc, CL, IL):
    s = f"* n100ps\n.include {MODEL}\n.options reltol=1e-4\n" + core(Wn, Cc, CL) + \
        f"IL vout 0 DC {IL}\nVIN vin 0 DC 1.8 AC 1\n.control\nac dec 20 10 1e9\nwrdata {RES}/r3n_ps.txt v(vout)\nquit\n.endc\n.end\n"
    run(s, "r3n_ps"); b = np.loadtxt(f"{RES}/r3n_ps.txt"); ps = 20 * np.log10(np.hypot(b[:, 1], b[:, 2]))
    return {f"{x:g}": round(float(np.interp(np.log10(x), np.log10(b[:, 0]), ps)), 1) for x in (1e3, 1e5, 1e6, 1e7, 1e8)}

def step(Wn, Cc, CL, te, I1=0.0, I2=0.1):
    t0 = 2e-6; t1 = t0 + te; t2 = t1 + 8e-6; t3 = t2 + te; tstop = t3 + 8e-6; ts = min(te / 20, 2e-9)
    s = f"* n100tr\n.include {MODEL}\n.options reltol=1e-4\n" + core(Wn, Cc, CL) + \
        f"VIN vin 0 DC 1.8\nIL vout 0 PWL(0 {I1} {t0} {I1} {t1} {I2} {t2} {I2} {t3} {I1})\n.control\ntran {ts} {tstop} 0 {ts*5}\nwrdata {RES}/r3n_tr.txt v(vout) v(ea)\nquit\n.endc\n.end\n"
    run(s, "r3n_tr"); a = np.loadtxt(f"{RES}/r3n_tr.txt"); t, vo = a[:, 0], a[:, 1]
    pre = vo[(t > t0 - 0.2e-6) & (t < t0)].mean(); w1 = (t > t0) & (t < t2); end2 = vo[(t > t2 - 0.3e-6) & (t < t2)].mean()
    return dict(undershoot_mV=round(float(pre - vo[w1].min()) * 1e3, 1), overshoot_mV=round(float(vo[t > t2].max() - end2) * 1e3, 1),
                load_reg_mV=round(float(pre - end2) * 1e3, 1))

def main():
  R = []
  for Wn, Cc in ((8000, 20e-12), (8000, 50e-12), (16000, 50e-12)):
      pms = []; ops = []
      for IL in (0, 1e-3, 10e-3, 50e-3, 100e-3):
          m, vo, ve = lg(Wn, Cc, 100e-12, IL); pms.append(round(m["pm"], 1)); ops.append((IL * 1e3, round(vo, 4), round(ve, 3), round(m["dc_db"], 1), round(m["ugf"] / 1e6, 2)))
      r = dict(Wn_um=Wn, Cc_pF=Cc * 1e12, pm_0_1_10_50_100mA=pms, op_IL_vout_vea_dcdb_ugfMHz=ops,
               psrr_100mA=psrr(Wn, Cc, 100e-12, 0.1), psrr_10mA=psrr(Wn, Cc, 100e-12, 0.01),
               step_0to100mA={f"{te*1e9:g}ns": step(Wn, Cc, 100e-12, te) for te in (1e-9, 100e-9, 1e-6)})
      R.append(r); print(json.dumps(r), flush=True)
  json.dump(R, open(f"{RES}/r3_7_nmos100.json", "w"), indent=1)

if __name__ == "__main__":
    main()
