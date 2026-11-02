"""Claim A: supply ripple -> ring-oscillator TIE, with an oscillator different from the author's.
Oscillator 'CS5': 5-stage current-starved ring, bias I_ref = (VDD - Vgs)/Rb (resistor-referenced, so VDD-sensitive).
Also 'INV7': re-measurement of the author's 7-stage inverter ring (own netlist) for f0/Kvdd only."""
import json, sys, numpy as np
from concurrent.futures import ThreadPoolExecutor
from rv import ngspice, grab, refA_core, model, RES, tie, sine_fit

N_CS = 5


def ring_cs(sup="vdd"):
    s = [f"""* 5-stage current-starved ring; bias from resistor to {sup}
Rb {sup} nb 20k
Mnb nb nb 0 0 NMOS W=2u L=0.5u
Mn2 pb nb 0 0 NMOS W=2u L=0.5u
Mpb pb pb {sup} {sup} PMOS W=5u L=0.5u"""]
    for i in range(N_CS):
        a, y = f"n{i}", f"n{(i + 1) % N_CS}"
        s.append(f"Mpc{i} xp{i} pb {sup} {sup} PMOS W=5u L=0.5u\nMps{i} {y} {a} xp{i} {sup} PMOS W=2u L=0.18u\n"
                 f"Mns{i} {y} {a} xn{i} 0 NMOS W=1u L=0.18u\nMnc{i} xn{i} nb 0 0 NMOS W=2u L=0.5u\nCl{i} {y} 0 20f")
    return "\n".join(s)


def ring_inv7(sup="vdd"):
    s = [".subckt inv a y vdd\nMn y a 0 0 NMOS W=1u L=0.18u\nMp y a vdd vdd PMOS W=2.5u L=0.18u\nCn y 0 30f\n.ends"]
    for i in range(7):
        s.append(f"Xr{i} n{i} n{(i + 1) % 7} {sup} inv")
    return "\n".join(s)


RINGS = {"CS5": (ring_cs, 60e-9, 10e-12), "INV7": (ring_inv7, 40e-9, 5e-12)}


def f_vs_vdd(ring, vdd):
    fn, tst, ms = RINGS[ring]
    name = f"a_f_{ring}_{vdd}"
    net = f"""* {name}
.include {model()}
.options reltol=1e-4
{fn('vdd')}
VDD vdd 0 {vdd}
.ic v(n0)=0
.control
tran {ms} {tst + 150e-9} 0 {ms}
meas tran iavg avg i(VDD) from={tst}n to={tst + 150e-9}
wrdata {RES}/{name}.txt v(n0) v(vdd)
quit
.endc
.end
""".replace(f"from={tst}n", f"from={tst}")
    out = ngspice(net, name)
    a = np.loadtxt(f"{RES}/{name}.txt")
    f0, _, tc, _ = tie(a[:, 0], a[:, 1], a[:, 3], tst)
    return vdd, f0, -grab(out, "iavg"), len(tc)


def psrr_refA(Iload, fms):
    name = "a_psrr"
    net = f"""* {name}
.include {model()}
{refA_core(Cc=5e-12, Rz=0, gate_node='fb')}
VIN vin 0 DC 1.8 AC 1
VREF vref 0 0.8
CL vout 0 100p
IL vout 0 DC {Iload}
.control
ac dec 100 1e3 1e8
wrdata {RES}/{name}.txt v(vout)
quit
.endc
.end
"""
    ngspice(net, name)
    a = np.loadtxt(f"{RES}/{name}.txt")
    f = a[:, 0]; g = np.hypot(a[:, 1], a[:, 2])
    return {fm: float(10 ** np.interp(np.log10(fm), np.log10(f), np.log10(g))) for fm in fms}


def cosim(ring, path, fm, A, ncyc, tst=2e-6, settle=1e-6):
    fn, _, ms = RINGS[ring]
    tm0 = tst + settle; tm1 = tm0 + ncyc / fm
    name = f"a_tr_{ring}_{path}_fm{fm/1e3:g}k_A{A*1e3:g}m"
    if path == "direct":
        body = f"VDD vdd 0 DC 1.6 SIN(1.6 {A} {fm} {tst})\n{fn('vdd')}"
    else:
        body = (refA_core(Cc=5e-12, Rz=0, gate_node='fb').replace("vout", "vdd") +
                f"VIN vin 0 DC 1.8 SIN(1.8 {A} {fm} {tst})\nVREF vref 0 0.8\nCL vdd 0 100p\n{fn('vdd')}")
    net = f"""* {name}
.include {model()}
.options reltol=1e-4
{body}
.ic v(n0)=0
.control
tran {ms} {tm1 + 20e-9} 0 {ms}
wrdata {RES}/{name}.txt v(n0) v(vdd)
quit
.endc
.end
"""
    ngspice(net, name, timeout=20000)
    a = np.loadtxt(f"{RES}/{name}.txt")
    t, v, vdd = a[:, 0], a[:, 1], a[:, 3]
    f0, tie_pk, tc, e = tie(t, v, vdd, tm0, tm1)
    tie_fit = sine_fit(tc, e, fm)
    # supply ripple seen by the ring: fit fm component of v(vdd) on a uniform grid
    tg = np.linspace(tm0, tm1, 200001); vg = np.interp(tg, t, vdd)
    M = np.vstack([np.sin(2 * np.pi * fm * tg), np.cos(2 * np.pi * fm * tg), np.ones_like(tg)]).T
    c = np.linalg.lstsq(M, vg, rcond=None)[0]
    return dict(ring=ring, path=path, fm_kHz=fm / 1e3, A_in_mV=A * 1e3, f0_MHz=f0 / 1e6,
                tie_pk_ps=tie_pk * 1e12, tie_fit_ps=tie_fit * 1e12, A_vdd_fit_mV=float(np.hypot(c[0], c[1]) * 1e3),
                vdd_mean=float(c[2]), edges=len(tc))


if __name__ == "__main__":
    stage = sys.argv[1]
    if stage == "kvdd":
        R = {}
        for ring in RINGS:
            with ThreadPoolExecutor(4) as ex:
                res = list(ex.map(lambda v: f_vs_vdd(ring, v), (1.5, 1.55, 1.6, 1.65, 1.7)))
            fs = {v: f for v, f, i, n in res}
            p = np.polyfit(np.array(list(fs)) - 1.6, np.array(list(fs.values())), 2)
            R[ring] = dict(f_MHz={str(v): round(f / 1e6, 3) for v, f in fs.items()},
                           f0_MHz=fs[1.6] / 1e6, Kvdd_cd_MHz_per_V=(fs[1.65] - fs[1.55]) / 0.1 / 1e6,
                           Kvdd_poly_MHz_per_V=p[1] / 1e6, curv_MHz_per_V2=p[0] / 1e6,
                           Iavg_mA={str(v): round(i * 1e3, 4) for v, f, i, n in res}, edges=[n for *_, n in res])
            print(ring, R[ring], flush=True)
        json.dump(R, open(f"{RES}/a_kvdd.json", "w"), indent=1)
    if stage == "cosim":
        K = json.load(open(f"{RES}/a_kvdd.json"))
        jobs = []
        for path in ("direct", "ldo"):
            for fm, nc in ((300e3, 2), (1e6, 4), (3e6, 12)):
                jobs.append(("CS5", path, fm, 10e-3, nc))
            jobs.append(("CS5", path, 1e6, 0.0, 4))          # zero-ripple control: numerical/self-ripple floor
        for path in ("direct", "ldo"):
            jobs.append(("INV7", path, 1e6, 10e-3, 4))       # author's ring, own netlist
        jobs.append(("INV7", "ldo", 3e6, 10e-3, 12))
        with ThreadPoolExecutor(4) as ex:
            R = list(ex.map(lambda j: cosim(*j), jobs))
        # predictions
        ps = {}
        for ring in ("CS5", "INV7"):
            Iring = K[ring]["Iavg_mA"]["1.6"] * 1e-3
            ps[ring] = psrr_refA(Iring, (300e3, 1e6, 3e6))
        for r in R:
            k = K[r["ring"]]; Kv = k["Kvdd_cd_MHz_per_V"] * 1e6; f0 = k["f0_MHz"] * 1e6; fm = r["fm_kHz"] * 1e3
            g = 1.0 if r["path"] == "direct" else ps[r["ring"]][fm]
            r["psrr_ac_dB"] = 20 * np.log10(g)
            r["A_vco_pred_mV"] = r["A_in_mV"] * g
            r["tie_pred_ps"] = Kv * r["A_in_mV"] * 1e-3 * g / (2 * np.pi * fm * f0) * 1e12
            # prediction using the ripple actually seen on vdd in the transient (isolates the Kvdd/TIE formula)
            r["tie_pred_from_Avdd_ps"] = Kv * r["A_vdd_fit_mV"] * 1e-3 / (2 * np.pi * fm * f0) * 1e12
            print({k2: (round(v, 3) if isinstance(v, float) else v) for k2, v in r.items()}, flush=True)
        json.dump(R, open(f"{RES}/a_cosim.json", "w"), indent=1)
