"""Claim C, circuit level (own netlist): analog-dominant hybrid, REF-A core with 800 um pass + 8 x 130 um PMOS slices,
gate-sensing window comparators on V(pg) (VL=1.155 V, VH=1.39 V -> ~3-18 mA analog window, r~1.23), XSPICE thermometer
shift register at 10 MHz. Variants differ only in the synchronizer clocking:
  nosync      : register samples comparators directly                        (d = 0)
  sync2_skew  : 2 DFF sync on clk, register on clk + 1 ns (author's clocking) (d_eff = 1, see c0_sync_timing)
  sync2       : 2 DFF sync and register on the same clk (textbook)            (d = 2)
  sync2_div3  : as sync2, register clock = clk / 3 (zero-skew divided clock)  (d = 2, update every 3 clocks)
  sync2_div2  : as sync2, register clock = clk / 2                           (d = 2, update every 2 clocks)
Load: 5 -> 95 mA ascending staircase, 3 mA steps, 6 us per step, 50 ns ramps (author's protocol)."""
import json, sys, numpy as np
from concurrent.futures import ThreadPoolExecutor
from rv import ngspice, refA_core, model, RES

N, Ws, VL, VH, fclk = 8, 130, 1.155, 1.39, 10e6
T = 1 / fclk
levels = np.arange(5e-3, 95.1e-3, 3e-3); hold = 6e-6


def load_src():
    pwl = ["0 0"]; t = 1e-6
    for I in levels:
        pwl += [f"{t:.7g} {pwl[-1].split()[1]}", f"{t + 50e-9:.7g} {I:.6g}"]; t += hold
    return "IL vout 0 PWL(" + " ".join(pwl) + ")", t


def digital(variant):
    sync = variant.startswith("sync2")
    div = 3 if variant.endswith("div3") else (2 if variant.endswith("div2") else 1)
    skew = 1e-9 if variant == "sync2_skew" else 0.0
    s = [f"""* comparators: smooth B-source (gain ~1800 V/V around threshold) + adc_bridge (tpd 1 ns)
Bup upa 0 V = 0.9*(1+tanh(2000*({VL}-V(pg))))
Bdn dna 0 V = 0.9*(1+tanh(2000*(V(pg)-{VH})))
Vck cka 0 PULSE(0 1.8 {T/2} 0.1n 0.1n {T/2 - 0.1e-9} {T})
Vckr ckra 0 PULSE(0 1.8 {T/2 + skew} 0.1n 0.1n {T*div/2 - 0.1e-9} {T*div})
.model brg adc_bridge(in_low=0.9 in_high=0.9 rise_delay=1e-9 fall_delay=1e-9)
Abr [cka ckra upa dna] [clk ckr up0 dn0] brg
.model ff d_dff(clk_delay=2e-10 set_delay=2e-10 reset_delay=2e-10 ic=0 rise_delay=1e-10 fall_delay=1e-10)
.model g_and d_and(rise_delay=5e-11 fall_delay=5e-11)
.model g_or d_or(rise_delay=5e-11 fall_delay=5e-11)
.model g_nor d_nor(rise_delay=5e-11 fall_delay=5e-11)
.model pu d_pullup
.model pd d_pulldown
Apu q0 pu
Apd q{N+1} pd
.model drv dac_bridge(out_low=0 out_high=1.8 out_undef=0.9 input_load=1e-12 t_rise=1e-9 t_fall=1e-9)"""]
    if sync:
        s.append("Asu1 up0 clk NULL NULL up1 NULL ff\nAsu2 up1 clk NULL NULL up NULL ff\n"
                 "Asd1 dn0 clk NULL NULL dn1 NULL ff\nAsd2 dn1 clk NULL NULL dn NULL ff")
        rclk = "ckr"
    else:
        s.append("Aup_buf [up0 up0] up g_and\nAdn_buf [dn0 dn0] dn g_and")
        rclk = "clk"
    s.append("Ahold [up dn] hold g_nor")
    for i in range(1, N + 1):
        s.append(f"Aa{i} [up q{i-1}] za{i} g_and\nAb{i} [dn q{i+1}] zb{i} g_and\nAc{i} [hold q{i}] zc{i} g_and\n"
                 f"Ao{i} [za{i} zb{i} zc{i}] zd{i} g_or\nAq{i} zd{i} {rclk} NULL NULL q{i} qn{i} ff\n"
                 f"Adr{i} [qn{i}] [g{i}] drv\nMs{i} vout g{i} vin vin PMOS W={Ws}u L=0.18u")
    return "\n".join(s)


def run(variant):
    src, tend = load_src()
    name = f"c3_{variant}"
    net = f"""* {name}
.include {model()}
.options reltol=1e-4 abstol=1e-12 vntol=1e-7
{refA_core(Cc=5e-12, Rz=0, Wp=800, gate_node='fb')}
VIN vin 0 DC 1.8
VREF vref 0 0.8
CL vout 0 100p
{src}
{digital(variant)}
.control
tran 2n {tend:.7g} 0 10n
wrdata {RES}/{name}.txt v(vout) v(pg) {' '.join(f'v(g{i})' for i in range(1, N + 1))}
quit
.endc
.end
"""
    ngspice(net, name, timeout=20000)
    a = np.loadtxt(f"{RES}/{name}.txt")
    t, vo, vpg = a[:, 0], a[:, 1], a[:, 3]
    code = (a[:, 5::2] < 0.9).sum(axis=1)
    rows = []; t0 = 1e-6
    for I in levels:
        sel = (t > t0 + hold - 3e-6) & (t < t0 + hold - 0.02e-6)
        tog = int(np.count_nonzero(np.diff(code[sel])))
        rows.append(dict(IL_mA=round(I * 1e3, 1), toggles=tog, kmin=int(code[sel].min()), kmax=int(code[sel].max()),
                         vpp_mV=round(float(np.ptp(vo[sel])) * 1e3, 1), vpg_mean=round(float(vpg[sel].mean()), 4)))
        t0 += hold
    bad = [r for r in rows if r["toggles"] > 0 or r["vpp_mV"] > 5]
    return variant, dict(n_lc=len(bad), of=len(levels), lc_loads=[r["IL_mA"] for r in bad], rows=rows)


if __name__ == "__main__":
    variants = sys.argv[1:] or ["nosync", "sync2_skew", "sync2", "sync2_div3"]
    with ThreadPoolExecutor(len(variants)) as ex:
        R = dict(ex.map(run, variants))
    for v, r in R.items():
        print(v, r["n_lc"], "/", r["of"], r["lc_loads"], flush=True)
    try:
        old = json.load(open(f"{RES}/c3_hybrid.json"))
    except Exception:
        old = {}
    old.update(R)
    json.dump(old, open(f"{RES}/c3_hybrid.json", "w"), indent=1)
