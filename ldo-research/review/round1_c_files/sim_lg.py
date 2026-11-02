"""Reviewer's independent loop-gain / PSRR driver (does NOT import repo modules).
Circuit = REF-A transcribed flat; R1=R2=4k, Cc=5p, CL=100p, ESR~0.
Loop-break methods:
  mb   : Middlebrook double injection (V and I) at vout -> R1-top (r1t)
  lcn  : L-C break at vout -> r1t, no replica load (expected loading error)
  lcr  : L-C break at vout -> r1t, with AC-only 8k replica load on vout
  gate : L-C break at fb -> M1 gate (the original author's location), for cross-ref
"""
import subprocess, os, sys, numpy as np
D = os.path.dirname(os.path.abspath(__file__))
MODEL = "/home/user/abc/ldo-research/sim/models/180nm_bulk.pm"
DEV = ["mbn","mt","m1","m2","m3","m4","mbn2","mbp","mcs","mb","mp"]

def core(g1="fb", Cc=5e-12, CL=100e-12, R1=4e3, R2=4e3):
    return f"""
Ibias vin bn 10u
Mbn  bn bn 0 0 NMOS W=4u L=1u
Mt   tail bn 0 0 NMOS W=8u L=1u
M1   d1 {g1} tail 0 NMOS W=20u L=1u
M2   ea vref tail 0 NMOS W=20u L=1u
M3   d1 d1 vin vin PMOS W=4u L=1u
M4   ea d1 vin vin PMOS W=4u L=1u
Mbn2 bp bn 0 0 NMOS W=4u L=1u
Mbp  bp bp vin vin PMOS W=4u L=1u
Mcs  pg bp vin vin PMOS W=20u L=1u
Mb   0 ea pg pg PMOS W=20u L=0.18u
Mp   vout pg vin vin PMOS W=4000u L=0.18u
R1   r1t fb {R1}
R2   fb 0 {R2}
Cc   vout ea {Cc}
CL   vout ncl {CL}
RESR ncl 0 1e-6
"""

HDR = f"* reviewer r1c\n.include {MODEL}\n.options temp=27 reltol=1e-4 abstol=1e-12 vntol=1e-7\n"

def run(net, name):
    p = os.path.join(D, name + ".cir")
    open(p, "w").write(net)
    r = subprocess.run(["ngspice", "-b", p], cwd=D, capture_output=True, text=True, timeout=600)
    out = r.stdout + r.stderr
    open(os.path.join(D, name + ".log"), "w").write(out)
    return out

def acload(name):
    a = np.loadtxt(os.path.join(D, name), ndmin=2)
    f = a[:, 0]
    cols = [a[:, 2*i+1] + 1j*a[:, 2*i+2] for i in range((a.shape[1]-1)//3 + 0)] if False else None
    # wrdata writes (x, re, im) per vector for complex
    n = a.shape[1] // 3
    vecs = [a[:, 3*i+1] + 1j*a[:, 3*i+2] for i in range(n)]
    return f, vecs

AC = "ac dec 40 1 1e10"

def op(IL, tag):
    prints = "\n".join(f"print @{d}[gm] @{d}[gds] @{d}[gmbs] @{d}[id] @{d}[vgs] @{d}[vds] @{d}[vth] @{d}[vdsat]" for d in DEV)
    net = HDR + core() + f"""
VIN vin 0 DC 1.8
VREF vref 0 0.8
Vjoin vout r1t 0
IL vout 0 DC {IL}
.control
op
print v(vout) v(pg) v(ea) v(fb) v(tail) v(d1) v(bp) v(bn) i(VIN)
{prints}
.endc
.end
"""
    out = run(net, f"op_{tag}")
    vals = {}
    for line in out.splitlines():
        s = line.strip()
        if " = " in s and (s.startswith("v(") or s.startswith("@") or s.startswith("i(")):
            k, v = s.split(" = ")
            try: vals[k.strip()] = float(v.split()[0])
            except: pass
    return vals

def mb(IL, tag, **kw):
    # voltage injection: v(r1t) - v(vout) = 1   (a = vout side, b = r1t side)
    netv = HDR + core(**kw) + f"""
VIN vin 0 DC 1.8
VREF vref 0 0.8
Vinj r1t vout DC 0 AC 1
IL vout 0 DC {IL}
.control
{AC}
wrdata mbv_{tag}.txt v(vout) v(r1t)
.endc
.end
"""
    run(netv, f"mbv_{tag}")
    neti = HDR + core(**kw) + f"""
VIN vin 0 DC 1.8
VREF vref 0 0.8
Vsa vout j DC 0
Vsb j r1t DC 0
Iinj 0 j DC 0 AC 1
IL vout 0 DC {IL}
.control
{AC}
wrdata mbi_{tag}.txt i(Vsa) i(Vsb)
.endc
.end
"""
    run(neti, f"mbi_{tag}")
    f, (va, vb) = acload(f"mbv_{tag}.txt")
    f2, (iy, ix) = acload(f"mbi_{tag}.txt")
    Tv = -va / vb
    Ti = -iy / ix
    T = (Tv * Ti - 1) / (Tv + Ti + 2)
    return f, T, Tv, Ti

def lc(IL, tag, replica, **kw):
    rep = "Rrep vout nrep 8k\nCrep nrep 0 1\n" if replica else ""
    net = HDR + core(**kw) + f"""
VIN vin 0 DC 1.8
VREF vref 0 0.8
Lbrk vout r1t 1e9
Cbrk r1t acs 1
Vac acs 0 DC 0 AC 1
{rep}IL vout 0 DC {IL}
.control
{AC}
wrdata lc{'r' if replica else 'n'}_{tag}.txt v(vout) v(r1t)
.endc
.end
"""
    run(net, f"lc{'r' if replica else 'n'}_{tag}")
    f, (va, vb) = acload(f"lc{'r' if replica else 'n'}_{tag}.txt")
    return f, -va / vb

def gate(IL, tag, **kw):
    net = HDR + core(g1="g1", **kw) + f"""
VIN vin 0 DC 1.8
VREF vref 0 0.8
Vjoin vout r1t 0
Lbrk fb g1 1e9
Cbrk g1 acs 1
Vac acs 0 DC 0 AC 1
IL vout 0 DC {IL}
.control
{AC}
wrdata gate_{tag}.txt v(fb) v(g1)
.endc
.end
"""
    run(net, f"gate_{tag}")
    f, (vf, vg) = acload(f"gate_{tag}.txt")
    return f, -vf / vg

def psrr_cl(IL, tag):
    net = HDR + core() + f"""
VIN vin 0 DC 1.8 AC 1
VREF vref 0 0.8
Vjoin vout r1t 0
IL vout 0 DC {IL}
.control
{AC}
wrdata psr_{tag}.txt v(vout) v(pg) v(ea)
.endc
.end
"""
    run(net, f"psr_{tag}")
    return acload(f"psr_{tag}.txt")

def supply_open(IL, tag):
    # open loop at M1 gate: DC via L, AC-grounded gate (C to ground) -> vin->vout open-loop gain
    net = HDR + core(g1="g1") + f"""
VIN vin 0 DC 1.8 AC 1
VREF vref 0 0.8
Vjoin vout r1t 0
Lbrk fb g1 1e9
Cbrk g1 0 1
IL vout 0 DC {IL}
.control
{AC}
wrdata aos_{tag}.txt v(vout) v(pg) v(ea) v(d1)
.endc
.end
"""
    run(net, f"aos_{tag}")
    return acload(f"aos_{tag}.txt")

def margins(f, T):
    mag = 20*np.log10(np.abs(T))
    ph = np.unwrap(np.angle(T))*180/np.pi
    # normalise phase so that DC phase is ~0 (T positive real at DC for negative feedback)
    ph = ph - 360*np.round(ph[0]/360)
    idx = np.where((mag[:-1] > 0) & (mag[1:] <= 0))[0]
    if len(idx) == 0:
        return dict(dc=mag[0], ugf=np.nan, pm=np.nan)
    i = idx[0]
    x = mag[i]/(mag[i]-mag[i+1])
    lf = np.log10(f[i]) + x*(np.log10(f[i+1])-np.log10(f[i]))
    ugf = 10**lf
    phu = ph[i] + x*(ph[i+1]-ph[i])
    return dict(dc=float(mag[0]), ugf=float(ugf), pm=float(180+phu))

if __name__ == "__main__":
    import json
    res = {}
    for IL, tag in [(0.0, "IL0"), (0.1, "IL100m"), (0.01, "IL10m")]:
        o = op(IL, tag)
        r = {"op": o}
        f, T, Tv, Ti = mb(IL, tag)
        r["mb"] = margins(f, T); r["mb_Tv"] = margins(f, Tv); r["mb_Ti"] = margins(f, Ti)
        f, T = lc(IL, tag, False); r["lcn"] = margins(f, T)
        f, T = lc(IL, tag, True); r["lcr"] = margins(f, T)
        f, T = gate(IL, tag); r["gate"] = margins(f, T)
        f, (vo, vpg, vea) = psrr_cl(IL, tag)
        r["psrr_10Hz_dB"] = float(20*np.log10(abs(vo[np.argmin(abs(f-10))])))
        r["psrr_1Hz_dB"] = float(20*np.log10(abs(vo[0])))
        f, (vo, vpg, vea, vd1) = supply_open(IL, tag)
        r["aos_1Hz"] = dict(vout=float(abs(vo[0])), vout_dB=float(20*np.log10(abs(vo[0]))), pg=float(vpg[0].real), ea=float(vea[0].real), d1=float(vd1[0].real))
        res[tag] = r
        print(tag, json.dumps({k: v for k, v in r.items() if k != "op"}, indent=1))
    json.dump(res, open(os.path.join(D, "lg_results.json"), "w"), indent=1)
