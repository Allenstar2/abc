"""Reviewer 版 hybrid：在 REF-B 上加「公平化」選項（全部在 scratch，不改 repo）。
新增：
- droop: 非同步 droop 偵測（比較 V(pg) < VLL，表示類比 pass 已飽和），經 ripple-set 鏈
  非同步依序打開 slice：set_k = droop AND q_{k-1}（AND 延遲 tau_chain）。純閘級，不需 Verilog。
- t_on / t_off：slice 閘極下降（開）與上升（關）邊沿可分開設定。
- Wa：類比 pass 寬度。
"""
import numpy as np
from ldo_ref import DEFAULT, subckt
from common import run, MODEL, RES

HDEF = dict(DEFAULT, Wp=800, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3,
            N=8, Ws=130, VL=1.155, VH=1.39, fclk=10e6, tpd_cmp=1e-9, t_on=1e-9, t_off=1e-9,
            droop=False, droop_src='pg', Vdr=1.57, Vgate=1.35, VLL=1.0, tpd_droop=3e-9, tau_chain=2e-9, ic_code=0)


def droop_expr(p):
    if p['droop_src'] == 'pg':
        return 'Bdr dra 0 V = 0.9*(1+tanh((V(vll)-V(pg))*2000))'
    if p['droop_src'] == 'vout':
        return f"Bdr dra 0 V = 0.9*(1+tanh(({p['Vdr']}-V(vout))*2000))"
    # both: Vout droop AND pg < Vgate（類比確實在用力）
    return (f"Bdr dra 0 V = 1.8*0.25*(1+tanh(({p['Vdr']}-V(vout))*2000))*(1+tanh(({p['Vgate']}-V(pg))*2000))")


def digital_block(p):
    N = p["N"]; T = 1 / p["fclk"]
    s = [f"""
Vclk clka 0 PULSE(0 1.8 {T/2} 0.1n 0.1n {T/2-0.1e-9} {T})
Vvl vl 0 {p['VL']}
Vvh vh 0 {p['VH']}
Vvll vll 0 {p['VLL']}
Bup upa 0 V = 0.9*(1+tanh((V(vl)-V(pg))*2000))
Bdn dna 0 V = 0.9*(1+tanh((V(pg)-V(vh))*2000))
{droop_expr(p)}
.model adcb adc_bridge(in_low=0.9 in_high=0.9 rise_delay={p['tpd_cmp']} fall_delay={p['tpd_cmp']})
.model adcd adc_bridge(in_low=0.9 in_high=0.9 rise_delay={p['tpd_droop']} fall_delay={p['tpd_droop']})
Aadc [clka upa dna] [clk up dn] adcb
Aadd [dra] [droopr] adcd
.model dff1 d_dff(clk_delay=2e-10 set_delay=2e-10 reset_delay=2e-10 ic=0 rise_delay=1e-10 fall_delay=1e-10)
.model and2 d_and(rise_delay=5e-11 fall_delay=5e-11)
.model and2c d_and(rise_delay={p['tau_chain']} fall_delay=5e-11)
.model or3 d_or(rise_delay=5e-11 fall_delay=5e-11)
.model nor2 d_nor(rise_delay=5e-11 fall_delay=5e-11)
.model one d_pullup
.model zero d_pulldown
Ahi q0 one
Alo q{N+1} zero
Ahold [up dn] hold nor2
.model dacb dac_bridge(out_low=0 out_high={p['Vin']} out_undef=0.9 input_load=1e-12 t_rise={p['t_off']} t_fall={p['t_on']})
"""]
    if p["droop"]:
        s.append("Adrb droopr droop and2  ; buffer\n".replace("Adrb droopr droop and2  ; buffer", "Adrb [droopr droopr] droop and2"))
    for i in range(1, N + 1):
        if p["droop"]:
            setn = f"s{i}"
            s.append(f"As{i} [droop q{i-1}] s{i} and2c")
        else:
            setn = "NULL"
        s.append(f"Aa{i} [up q{i-1}] a{i} and2\nAb{i} [dn q{i+1}] b{i} and2\nAc{i} [hold q{i}] c{i} and2\n"
                 f"Ao{i} [a{i} b{i} c{i}] d{i} or3\nAf{i} d{i} clk {setn} NULL q{i} qb{i} dff1\n"
                 f"Adac{i} [qb{i}] [g{i}] dacb\nMs{i} vout g{i} vin vin PMOS W={p['Ws']}u L=0.18u\n")
    return "\n".join(s)


def hybrid_netlist(p, load_src, tstop, tstep, name, extra=""):
    sub = subckt(p).replace(".subckt ldoA vin vout vref fb fbi", ".subckt ldoA vin vout vref fb fbi pg")
    code_vecs = " ".join(f"v(g{i})" for i in range(1, p["N"] + 1))
    return f"""* {name}
.include {p.get('model', MODEL)}
.options temp={p['temp']} reltol=1e-4 abstol=1e-12 vntol=1e-7
{sub}
VIN vin 0 DC {p['Vin']}
VREF vref 0 {p['Vref']}
X1 vin vout vref fb fb pg ldoA
CL vout 0 {p['CL']}
{load_src}
{extra}
{digital_block(p)}
.control
tran {tstep} {tstop} 0 {tstep*5}
wrdata {RES}/{name}_tr.txt v(vout) v(pg) {code_vecs}
quit
.endc
.end
"""


def run_hybrid(p, load_src, tstop, name, tstep=1e-9, extra=""):
    run(hybrid_netlist(p, load_src, tstop, tstep, name, extra), name, timeout=3000)
    a = np.loadtxt(f"{RES}/{name}_tr.txt", ndmin=2)
    t = a[:, 0]; vo = a[:, 1]; vpg = a[:, 3]
    gates = a[:, 5::2]
    code = (gates < p["Vin"] / 2).sum(axis=1)
    return t, vo, vpg, code


def step_metrics(tt, vo, code, t0, te, thold=8e-6):
    pre = vo[(tt > t0 - 0.3e-6) & (tt < t0)].mean()
    w = (tt > t0) & (tt < t0 + te + thold)
    us = pre - vo[w].min()
    end = vo[(tt > t0 + te + thold - 0.5e-6) & (tt < t0 + te + thold)].mean()
    os_up = vo[w].max() - pre  # 加載期間的正向過衝（droop 後打開過多 slice）
    wr = tt > t0 + te + thold
    os_rel = vo[wr].max() - end if wr.any() else np.nan
    # 回復時間：最後一次離開 end±10 mV 的時刻
    dev = np.abs(vo[w] - end) > 10e-3
    trec = (tt[w][np.where(dev)[0][-1]] - t0) if dev.any() else 0.0
    return dict(pre=float(pre), undershoot_mV=float(us * 1e3), overshoot_during_mV=float(os_up * 1e3),
                overshoot_release_mV=float(os_rel * 1e3), v_end=float(end), t_settle10mV_us=float(trec * 1e6),
                code_end=int(code[(tt > t0 + te + thold - 0.2e-6)][0]), code_max=int(code[w].max()))
