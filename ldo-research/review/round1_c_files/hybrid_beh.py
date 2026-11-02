"""Reviewer's behavioural model of the analog-dominant hybrid (claim 3).
Units: slice current I_s = 1, clock period T = 1.
  - digital: N=8 slices, thermometer code k, +-1 per clock edge (bidirectional shift register).
  - comparators sample the analog-pass current I_a (proxy of V_pg) at each clock edge:
        up   if I_a > I_H - os      (V_pg < VL : analog nearly used up)
        down if I_a < I_lo + os     (V_pg > VH)
    window W = I_H - I_lo = r * I_s.  os > 0 shrinks the window on both sides (worst-case
    input-referred offset, current units); if both fire, 'up' wins.
  - code decided at edge n reaches the slices d clocks later (pure latency, e.g. synchroniser).
  - optional blanking b: after a code change the comparators are ignored for b clocks.
  - analog loop: I_a -> target = clip(I_L - k*I_s, 0, I_amax)
        order 1: time constant tau (exact exponential update per clock; tau=0 -> instant)
        order 2: natural freq wn [rad/clock], damping zeta (exact ZOH discretisation)
  - I_amax = I_H + 0.35 so that the 'up' threshold is always reachable.
  - limit cycle (LC) = applied code still changing during the last `tail` clocks.
Each load starts from k=0 and k=8 (analog settled); flagged LC if either ends oscillating.
"""
import numpy as np
from scipy.linalg import expm

N = 8; I_LO = 0.25
LOADS = np.linspace(0.0, 8.0, 4001) + 1.234e-5   # small offset avoids exact threshold hits

def simulate(r, tau=0.0, d=0, os=0.0, b=0, order=1, wn=None, zeta=0.7, loads=LOADS,
             ncyc=3000, tail=500, k0=0, traces=False):
    IH = I_LO + r; IMAX = IH + 0.35
    nL = len(loads)
    if order == 1:
        a = np.exp(-1.0/tau) if tau > 0 else 0.0
    else:
        A = np.array([[0, 1], [-wn**2, -2*zeta*wn]]); Bm = np.array([[0], [wn**2]])
        M = expm(np.block([[A, Bm], [np.zeros((1, 3))]]))
        Ad, Bd = M[:2, :2], M[:2, 2]
    k_cmd = np.full(nL, k0, dtype=int)
    hist = [k_cmd.copy() for _ in range(d + 1)]
    Ia = np.clip(loads - k0, 0, IMAX); dIa = np.zeros(nL)
    blank = np.zeros(nL, dtype=int)
    kmin = np.full(nL, 99); kmax = np.full(nL, -1)
    trk, trI = [], []
    for n in range(ncyc):
        act = blank == 0
        up = (Ia > IH - os) & act
        dn = (Ia < I_LO + os) & ~up & act
        new = np.clip(k_cmd + up.astype(int) - dn.astype(int), 0, N)
        changed = new != k_cmd
        blank = np.where(changed, b, np.maximum(blank - 1, 0))
        k_cmd = new
        hist.append(k_cmd.copy()); hist.pop(0)
        k_app = hist[0]
        tgt = np.clip(loads - k_app, 0, IMAX)
        if order == 1:
            Ia = tgt + (Ia - tgt) * a
        else:
            x0, x1 = Ia.copy(), dIa.copy()
            Ia = Ad[0, 0]*x0 + Ad[0, 1]*x1 + Bd[0]*tgt
            dIa = Ad[1, 0]*x0 + Ad[1, 1]*x1 + Bd[1]*tgt
        if n >= ncyc - tail:
            kmin = np.minimum(kmin, k_app); kmax = np.maximum(kmax, k_app)
        if traces: trk.append(k_app.copy()); trI.append(Ia.copy())
    lc = kmax > kmin
    if traces: return lc, kmax - kmin, np.array(trk), np.array(trI)
    return lc, kmax - kmin

def scan(r, loads=LOADS, **kw):
    lc0, pp0 = simulate(r, k0=0, loads=loads, **kw)
    lc8, pp8 = simulate(r, k0=N, loads=loads, **kw)
    return lc0 | lc8, np.maximum(pp0, pp8)

def theory_quasistatic(r, os=0.0, loads=LOADS):
    """LC iff no code puts I_a inside the effective window while adjacent codes straddle it."""
    lo, hi = I_LO + os, I_LO + r - os; IMAX = I_LO + r + 0.35
    lc = np.zeros(len(loads), bool)
    for i, L in enumerate(loads):
        Ia = np.clip(L - np.arange(N + 1), 0, IMAX)
        inside = (Ia >= lo) & (Ia <= hi) if hi >= lo else np.zeros(N + 1, bool)
        if inside.any(): continue
        lc[i] = np.any((Ia[:-1] > hi) & (Ia[1:] < lo))
    return lc

def intervals(mask, loads=LOADS):
    out = []; i = 0
    while i < len(mask):
        if mask[i]:
            j = i
            while j + 1 < len(mask) and mask[j + 1]: j += 1
            out.append((round(float(loads[i]), 3), round(float(loads[j]), 3))); i = j + 1
        else: i += 1
    return out

if __name__ == "__main__":
    import json
    res = {}
    print("=== A. baseline (tau=0, d=0, os=0), loads 0..8 I_s, 4001 points ===")
    for r in [0.3, 0.5, 0.8, 0.95, 1.0, 1.05, 1.2, 1.5, 2.0]:
        lc, pp = scan(r)
        th = theory_quasistatic(r)
        iv = intervals(lc)
        res[f"r{r}"] = dict(frac=float(lc.mean()), theory=float(th.mean()), agree=float((lc == th).mean()),
                            pp_max=int(pp.max()), n_intervals=len(iv), intervals=iv)
        print(f"r={r:4.2f}  LC frac={lc.mean():.3f} (theory {th.mean():.3f}; agree {100*(lc==th).mean():.2f}%)  "
              f"code p-p max={pp.max()}  #LC intervals={len(iv)}  e.g. {iv[:3]}")
    json.dump(res, open("hyb_A.json", "w"), indent=1)
