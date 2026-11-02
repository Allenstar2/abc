"""REF-B：類比主導雙迴路 hybrid LDO（XSPICE 行為級數位）。
- 類比迴路：與 REF-A 相同核心，但 pass device 縮小為 Wa（負責 DC 精度與快速細調）。
- 數位迴路：N 個 PMOS slice（開=閘極 0 V、關=Vin），由雙向 thermometer shift register 控制。
  決策依據是「類比 pass 閘極電壓 V(pg)」：V(pg) < VL（類比快用完）→ UP 加一片；V(pg) > VH → DN 減一片。
  這代表數位迴路只做粗調「重新置中」，Vout 永遠由類比迴路決定 → 屬於 B 類。
- 比較器：理想連續比較器（B-source + adc_bridge，含 tpd），由 d_dff 在時脈上升沿取樣。
  與閘級/電晶體實作的差距：沒有 offset、沒有 metastability、沒有 kickback、沒有時脈饋通、DFF 無 setup/hold 違規模型。
"""
import numpy as np
from ldo_ref import DEFAULT, subckt
from common import run, MODEL, RES

HDEF = dict(DEFAULT, Wp=800, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3,
            N=8, Ws=130, VL=1.155, VH=1.39, fclk=10e6, tpd_cmp=1e-9, t_drv=1e-9,
            fast=False, Vdroop=0.05, sync=0, reg_div=1)


def digital_block(p):
    N = p["N"]; T = 1 / p["fclk"]
    if p.get("sync", 0) > 0:
        lines = []
        prev_u, prev_d = "up0", "dn0"
        for k in range(1, p["sync"] + 1):
            lu = "up" if k == p["sync"] else f"upq{k}"; ld = "dn" if k == p["sync"] else f"dnq{k}"
            lines.append(f"Asu{k} {prev_u} clk NULL NULL {lu} NULL dff1\nAsd{k} {prev_d} clk NULL NULL {ld} NULL dff1")
            prev_u, prev_d = lu, ld
        sync_block = "* 比較器輸出同步器（{} 級 DFF）\n".format(p["sync"]) + "\n".join(lines)
    else:
        sync_block = "* 無同步器"
    legacy = p.get("sync", 0) == 0 and p.get("reg_div", 1) == 1   # 與最初版本（X3a–X3e）完全相同的 netlist
    s = [f"""
Vclk clka 0 PULSE(0 1.8 {T/2} 0.1n 0.1n {T/2-0.1e-9} {T})
Vclkr clkra 0 PULSE(0 1.8 {T/2} 0.1n 0.1n {T*p['reg_div']/2-0.1e-9} {T*p['reg_div']})
Vvl vl 0 {p['VL']}
Vvh vh 0 {p['VH']}
Bup upa 0 V = 0.9*(1+tanh((V(vl)-V(pg))*2000))
Bdn dna 0 V = 0.9*(1+tanh((V(pg)-V(vh))*2000))
.model adcb adc_bridge(in_low=0.9 in_high=0.9 rise_delay={p['tpd_cmp']} fall_delay={p['tpd_cmp']})
Aadc [clka upa dna clkra] [clk up0 dn0 clkr] adcb
.model dff1 d_dff(clk_delay=2e-10 set_delay=2e-10 reset_delay=2e-10 ic=0 rise_delay=1e-10 fall_delay=1e-10)
.model and2 d_and(rise_delay=5e-11 fall_delay=5e-11)
.model or3 d_or(rise_delay=5e-11 fall_delay=5e-11)
.model nor2 d_nor(rise_delay=5e-11 fall_delay=5e-11)
.model one d_pullup
.model zero d_pulldown
Ahi q0 one
Alo q{N+1} zero
{sync_block}
Ahold [up dn] hold nor2
.model dacb dac_bridge(out_low=0 out_high={p['Vin']} out_undef=0.9 input_load=1e-12 t_rise={p['t_drv']} t_fall={p['t_drv']})
"""]
    for i in range(1, N + 1):
        s.append(f"Aa{i} [up q{i-1}] a{i} and2\nAb{i} [dn q{i+1}] b{i} and2\nAc{i} [hold q{i}] c{i} and2\n"
                 f"Ao{i} [a{i} b{i} c{i}] d{i} or3\nAf{i} d{i} clkr NULL NULL q{i} qb{i} dff1\n"
                 f"Adac{i} [qb{i}] [g{i}] dacb\nMs{i} vout g{i} vin vin PMOS W={p['Ws']}u L=0.18u\n")
    txt = "\n".join(s)
    if legacy:
        txt = (txt.replace("Aadc [clka upa dna clkra] [clk up0 dn0 clkr] adcb", "Aadc [clka upa dna] [clk up dn] adcb")
                  .replace(" clkr NULL NULL q", " clk NULL NULL q"))
        txt = "\n".join(l for l in txt.splitlines() if not l.startswith("Vclkr "))
    return txt


def hybrid_netlist(p, load_src, tstop, tstep, name, save_codes=True):
    sub = subckt(p).replace(".subckt ldoA vin vout vref fb fbi", ".subckt ldoA vin vout vref fb fbi pg")
    code_vecs = " ".join(f"v(g{i})" for i in range(1, p["N"] + 1)) if save_codes else ""
    return f"""* {name}
.include {MODEL}
.options temp={p['temp']} reltol=1e-4 abstol=1e-12 vntol=1e-7
{sub}
VIN vin 0 DC {p['Vin']}
VREF vref 0 {p['Vref']}
X1 vin vout vref fb fb pg ldoA
CL vout 0 {p['CL']}
{load_src}
{digital_block(p)}
.control
tran {tstep} {tstop} 0 {tstep*5}
wrdata {RES}/{name}_tr.txt v(vout) v(pg) {code_vecs}
quit
.endc
.end
"""


def run_hybrid(p, load_src, tstop, name, tstep=1e-9):
    run(hybrid_netlist(p, load_src, tstop, tstep, name), name, timeout=1800)
    a = np.loadtxt(f"{RES}/{name}_tr.txt", ndmin=2)
    t = a[:, 0]; vo = a[:, 1]; vpg = a[:, 3]
    gates = a[:, 5::2]
    code = (gates < p["Vin"] / 2).sum(axis=1)
    return t, vo, vpg, code
