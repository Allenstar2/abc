"""電晶體級交叉檢查（ngspice，PTM）：行為模型的關鍵機制「類比被切斷＋EA windup 時，同步減掉最後一片造成大下陷」。
公平 B 的類比部分（REF-A 連接、Wp=2400 µm、Cc=5 pF、R1=R2=4 kΩ）＋8 片 PMOS slice（W=130 µm），
slice 閘極用 PWL 依「每 100 ns 減一片」排程（不用 XSPICE，避開事件排序問題）。
情境：95 mA、碼 7 穩態 → 2 µs 時負載降到 IL_end（100 ns 邊沿）→ 2.2 µs 起每 100 ns 關一片（t_off 可調）。"""
import sys, json, subprocess, os; sys.path.insert(0, '.')
import numpy as np
from c1_lib import run, MODEL, RES, NET
def sub(Wp=2400, Cc=5e-12):
    return f"""
.subckt ldoB vin vout fb pg ea
Ibias vin bn 10u
Mbn bn bn 0 0 NMOS W=4u L=1u
Mt tail bn 0 0 NMOS W=8u L=1u
M1 d1 fb tail 0 NMOS W=20u L=1u
M2 ea vref tail 0 NMOS W=20u L=1u
VREF vref 0 0.8
M3 d1 d1 vin vin PMOS W=4u L=1u
M4 ea d1 vin vin PMOS W=4u L=1u
Mbn2 bp bn 0 0 NMOS W=4u L=1u
Mbp bp bp vin vin PMOS W=4u L=1u
Mcs pg bp vin vin PMOS W=20u L=1u
Mb 0 ea pg pg PMOS W=20u L=0.18u
Mp vout pg vin vin PMOS W={Wp}u L=0.18u
R1 vout fb 4k
R2 fb 0 4k
Cc vout ea {Cc}
.ends
"""
def netlist(IL_end, toff, name, ncode=7, t_rel=2e-6, t_rm0=2.2e-6, Trm=100e-9):
    s = f"* {name}\n.include {MODEL}\n.options reltol=1e-4 abstol=1e-12 vntol=1e-7\n{sub()}\nVIN vin 0 1.8\nX1 vin vout fb pg ea ldoB\nCL vout 0 100p\n"
    s += f"IL vout 0 PWL(0 95m {t_rel} 95m {t_rel+100e-9} {IL_end})\n"
    for k in range(1, 9):
        if k <= ncode:
            ti = t_rm0 + (ncode - k) * Trm     # 先關最高的那片
            s += f"Vg{k} g{k} 0 PWL(0 0 {ti} 0 {ti+toff} 1.8)\n"
        else:
            s += f"Vg{k} g{k} 0 1.8\n"
        s += f"Ms{k} vout g{k} vin vin PMOS W=130u L=0.18u\n"
    s += f".control\ntran 0.2n 4.5u 0 0.5n\nwrdata {RES}/{name}.txt v(vout) v(pg) v(ea)\nquit\n.endc\n.end\n"
    return s
if __name__ == '__main__':
    out = []
    for IL_end in (2e-3, 5e-3, 11e-3, 20e-3):
        for toff in (1e-9, 300e-9, 1e-6):
            nm = f"xc_{IL_end*1e3:g}mA_{toff*1e9:g}n"
            run(netlist(IL_end, toff, nm), nm)
            a = np.loadtxt(f"{RES}/{nm}.txt"); t = a[:, 0]; v = a[:, 1]; pg = a[:, 3]; ea = a[:, 5]
            v95 = v[(t > 1.5e-6) & (t < 2e-6)].mean()
            w = t > 2.75e-6
            rec = dict(IL_end_mA=IL_end * 1e3, t_off_ns=toff * 1e9, V_at_95mA=round(float(v95), 4), V_max_after_release=round(float(v[t > 2e-6].max()), 4),
                       ea_max=round(float(ea[(t > 2.3e-6) & (t < 2.75e-6)].max()), 3), pg_max=round(float(pg[(t > 2.3e-6) & (t < 2.75e-6)].max()), 3),
                       V_min_after_last_removal=round(float(v[w].min()), 4), dip_below_95mA_level_mV=round(float((v95 - v[w].min()) * 1e3), 1),
                       V_end=round(float(v[t > 4.3e-6].mean()), 4))
            out.append(rec); print(rec, flush=True)
    json.dump(out, open('res/c2_xcheck_spice.json', 'w'), indent=1)
