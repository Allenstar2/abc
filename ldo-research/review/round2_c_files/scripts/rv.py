"""Round-2 (c) reviewer helpers — written from scratch (no import of author modules).
ngspice batch runner, REF-A flat netlist (transcribed from sim/scripts/ldo_ref.py::subckt topology),
loop-gain margin extraction, and TIE extraction."""
import os, subprocess, numpy as np

W = os.path.dirname(os.path.abspath(__file__))
NET = os.path.join(W, "net"); RES = os.path.join(W, "res"); MOD = os.path.join(W, "models")
os.makedirs(NET, exist_ok=True); os.makedirs(RES, exist_ok=True)
MODEL_NOM = "/home/user/abc/ldo-research/sim/models/180nm_bulk.pm"


def model(dn=0, dp=0):
    """dn/dp = shift of |Vth| (mV) for NMOS/PMOS. 0/0 -> repo model file (read-only include)."""
    if dn == 0 and dp == 0:
        return MODEL_NOM
    return os.path.join(MOD, f"ptm_n{dn:+d}_p{dp:+d}.pm")


def ngspice(text, name, timeout=7200):
    path = os.path.join(NET, name + ".cir")
    with open(path, "w") as f:
        f.write(text)
    p = subprocess.run(["ngspice", "-b", path], cwd=NET, capture_output=True, text=True, timeout=timeout)
    out = p.stdout + p.stderr
    with open(os.path.join(RES, name + ".log"), "w") as f:
        f.write("\n".join(l for l in out.splitlines() if "unrecognized parameter" not in l))
    return out


def grab(out, key):
    for l in out.splitlines():
        s = l.strip()
        if s.startswith(key + " ") or s.startswith(key + "="):
            try:
                return float(s.split("=")[1].split()[0])
            except Exception:
                pass
    return float("nan")


def refA_core(Cc=5e-12, Rz=0.0, R1=4e3, R2=4e3, Wp=4000, gate_node="fb", pg_name="pg"):
    """Flat REF-A core. EA non-inverting (feedback) input gate = gate_node.
    5T NMOS OTA -> PMOS source follower (Mb, drain at GND) -> PMOS pass Mp; Miller Cc vout->ea (optional Rz in series)."""
    comp = f"Rz vout ncz {Rz}\nCc ncz ea {Cc}" if Rz > 0 else f"Cc vout ea {Cc}"
    return f"""Ibias vin bn 10u
Mbn bn bn 0 0 NMOS W=4u L=1u
Mt tail bn 0 0 NMOS W=8u L=1u
M1 d1 {gate_node} tail 0 NMOS W=20u L=1u
M2 ea vref tail 0 NMOS W=20u L=1u
M3 d1 d1 vin vin PMOS W=4u L=1u
M4 ea d1 vin vin PMOS W=4u L=1u
Mbn2 bp bn 0 0 NMOS W=4u L=1u
Mbp bp bp vin vin PMOS W=4u L=1u
Mcs {pg_name} bp vin vin PMOS W=20u L=1u
Mb 0 ea {pg_name} {pg_name} PMOS W=20u L=0.18u
Mp vout {pg_name} vin vin PMOS W={Wp}u L=0.18u
R1 vout fb {R1}
R2 fb 0 {R2}
{comp}
"""


def margins(f, T):
    """All 0-dB crossings; PM = 180 + unwrapped phase (phase referenced so that DC ~ 0 deg)."""
    mag = 20 * np.log10(np.abs(T))
    ph = np.unwrap(np.angle(T)) * 180 / np.pi
    ph = ph - 360 * np.round(ph[0] / 360)
    xs = []
    for i in np.where(np.sign(mag[:-1]) != np.sign(mag[1:]))[0]:
        a = mag[i] / (mag[i] - mag[i + 1])
        lf = np.log10(f[i]) + a * (np.log10(f[i + 1]) - np.log10(f[i]))
        fr = 10 ** lf
        phu = ph[i] + a * (ph[i + 1] - ph[i])
        xs.append((float(fr), float(180 + phu), bool(mag[i] > mag[i + 1])))
    down = [x for x in xs if x[2]]
    gm = np.inf
    j = np.where((ph[:-1] > -180) & (ph[1:] <= -180))[0]
    if len(j):
        gm = -float(np.interp(-180, [ph[j[0] + 1], ph[j[0]]], [mag[j[0] + 1], mag[j[0]]]))
    return dict(dc_db=float(mag[0]), crossings=xs,
                ugf=down[0][0] if down else np.nan,
                pm=min(x[1] for x in xs) if xs else np.nan, gm_db=gm)


def tie(t, v, vdd, tmin, tmax=None):
    """Rising crossings of v through vdd/2 (instantaneous), linear-detrended TIE.
    Returns f0, peak TIE ((max-min)/2), fitted fm-component amplitude (if fm given via caller), crossing times."""
    sel = (t > tmin) & ((t < tmax) if tmax else True)
    t, v, vdd = t[sel], v[sel], vdd[sel]
    x = v - vdd / 2
    i = np.where((x[:-1] < 0) & (x[1:] >= 0))[0]
    tc = t[i] - x[i] * (t[i + 1] - t[i]) / (x[i + 1] - x[i])
    k = np.arange(len(tc))
    A = np.vstack([k, np.ones_like(k)]).T
    T, b = np.linalg.lstsq(A, tc, rcond=None)[0]
    e = tc - (k * T + b)
    return 1 / T, float((e.max() - e.min()) / 2), tc, e


def sine_fit(tc, e, fm):
    """Least-squares amplitude of the fm sinusoid in TIE(t) (removes bias/trend + random residue)."""
    M = np.vstack([np.sin(2 * np.pi * fm * tc), np.cos(2 * np.pi * fm * tc), np.ones_like(tc), tc - tc.mean()]).T
    c = np.linalg.lstsq(M, e, rcond=None)[0]
    return float(np.hypot(c[0], c[1]))
