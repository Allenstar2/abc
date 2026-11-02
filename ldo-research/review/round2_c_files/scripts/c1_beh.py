"""Claim C: own behavioral model of the analog-dominant hybrid (gate-sensing, thermometer slices).
Written from scratch (not the round-1 hybrid_beh.py). Units: mA, clock cycles.

Per clock edge n:
  c[n] = comparator decision sampled at edge n from analog current Ia(t_n):  +1 if Ia > I_hi (V(pg) < VL), -1 if Ia < I_lo, else 0
  register update at edge n (only on edges where n % div == 0):  k <- clip(k + c[n-d], 0, N)
  analog: Ia relaxes toward clip(IL - k*Is, 0, Iamax) with first-order time constant tau (tau=0: instantaneous)
Synchronizer of d stages == pure delay of d comparator samples (textbook, same clock).
"""
import json, sys, numpy as np

Is, Ilo, Ihi, N, Iamax = 12.2, 3.0, 18.0, 8, 33.0    # REF-B numbers: slice 12.2 mA, window 3-18 mA (r = 1.23)


def run(IL_seq, d=0, div=1, tau=0.0, k0=0, hist=None, Is=Is, Ilo=Ilo, Ihi=Ihi, ncyc_per=60, tail=30, phase=0, Iamax=None):
    """IL_seq: list of loads, each held ncyc_per clocks. Returns per-load (toggles in last `tail` clocks, codes seen)."""
    Iamax = Iamax if Iamax is not None else max(globals()['Iamax'], Ihi + 5.0)
    k = k0
    a = np.exp(-1 / tau) if tau > 0 else 0.0
    tgt = lambda IL, k: min(max(IL - k * Is, 0.0), Iamax)
    Ia = tgt(IL_seq[0], k)
    pipe = list(hist) if hist is not None else [0] * d       # pending decisions (oldest first)
    out = []; n = phase
    trace = []
    for IL in IL_seq:
        codes = []
        for j in range(ncyc_per):
            # analog evolves during one clock period with the current code
            Ia = tgt(IL, k) + (Ia - tgt(IL, k)) * a
            c = 1 if Ia > Ihi else (-1 if Ia < Ilo else 0)
            pipe.append(c)
            u = pipe.pop(0)          # decision sampled d edges ago (d=0 -> this edge)
            if n % div == 0:
                k = int(min(max(k + u, 0), N))
            n += 1
            codes.append(k)
        cs = codes[-tail:]
        out.append(dict(IL=IL, toggles=int(np.count_nonzero(np.diff(cs))), kmin=min(cs), kmax=max(cs), k_end=k))
        trace.append(codes)
    return out, trace


def staircase(levels, **kw):
    out, _ = run(levels, **kw)
    return [o for o in out if o["toggles"] > 0]


def lc_possible(IL, d, div=1, tau=0.0, ncyc=300, early=False, **kw):
    """Explore many initial conditions (start code 0..N, steady analog, empty/arbitrary pipeline) -> fraction LC."""
    res = []
    rng = np.random.default_rng(1)
    starts = [(k0, None) for k0 in range(N + 1)]
    for _ in range(12):
        starts.append((int(rng.integers(0, N + 1)), list(rng.integers(-1, 2, size=d))))
    for k0, h in starts:
        o, _ = run([IL], d=d, div=div, tau=tau, k0=k0, hist=h, ncyc_per=ncyc, tail=100, **kw)
        res.append(o[0]["toggles"] > 0)
        if early and res[-1]:
            return 1.0
    return float(np.mean(res))


if __name__ == "__main__":
    R = {}
    levels = list(np.round(np.arange(5, 95.1, 3), 3))
    # 1) author's protocol (ascending 3-mA staircase, 31 points), different delays / dividers
    cases = {"d0": dict(d=0), "d1": dict(d=1), "d2": dict(d=2), "d3": dict(d=3),
             "d1_div2": dict(d=1, div=2), "d2_div3": dict(d=2, div=3), "d3_div4": dict(d=3, div=4),
             "d2_div2": dict(d=2, div=2)}
    R["staircase_up"] = {}
    for nm, kw in cases.items():
        bad = staircase(levels, **kw)
        R["staircase_up"][nm] = dict(n_lc=len(bad), of=len(levels), loads=[b["IL"] for b in bad])
        print("up  ", nm, len(bad), "/", len(levels), [b["IL"] for b in bad], flush=True)
    # phase sensitivity of the ascending staircase (where the load step falls in the LC cycle)
    R["staircase_up_phase"] = {}
    for nm in ("d1", "d2"):
        cnt = []
        for hold in range(57, 64):
            bad = staircase(levels, ncyc_per=hold, tail=30, **cases[nm])
            cnt.append(len(bad))
        R["staircase_up_phase"][nm] = cnt
        print("hold 57..63 clocks", nm, cnt, flush=True)
    R["staircase_down"] = {}
    for nm in ("d0", "d1", "d2", "d2_div3"):
        bad = staircase(levels[::-1], k0=N, **cases[nm])
        R["staircase_down"][nm] = dict(n_lc=len(bad), of=len(levels), loads=[b["IL"] for b in bad])
        print("down", nm, len(bad), "/", len(levels), [b["IL"] for b in bad], flush=True)
    # 2) worst-case over initial conditions, fine load grid 0-100 mA
    grid = np.round(np.arange(0, 100.01, 0.25), 3)
    R["ic_scan"] = {}
    for nm in ("d0", "d1", "d2", "d2_div3"):
        fr = np.array([lc_possible(IL, **cases[nm]) for IL in grid])
        R["ic_scan"][nm] = dict(frac_loads_any_LC=float(np.mean(fr > 0)), frac_loads_all_LC=float(np.mean(fr == 1)),
                                mean_frac_ICs_LC=float(fr.mean()))
        print("IC  ", nm, R["ic_scan"][nm], flush=True)
    # 3) r_crit scan: smallest window ratio with no LC for any load / IC (window centred: Ilo fixed 3 mA)
    R["rcrit"] = {}
    gridc = np.round(np.arange(0, 100.01, 0.5), 3)
    for nm, kw in (("d0", dict(d=0)), ("d1", dict(d=1)), ("d2", dict(d=2)), ("d3", dict(d=3)),
                   ("d1_div2", dict(d=1, div=2)), ("d2_div3", dict(d=2, div=3)), ("d2_div2", dict(d=2, div=2)),
                   ("d0_tau1", dict(d=0, tau=1.0)), ("d2_div3_tau1", dict(d=2, div=3, tau=1.0)),
                   ("d2_div3_tau3", dict(d=2, div=3, tau=3.0))):
        rc = None
        for r in np.round(np.arange(0.9, 4.01, 0.05), 3):
            hi = Ilo + r * Is
            ok = all(lc_possible(IL, Ihi=hi, early=True, **kw) == 0 for IL in gridc)
            if ok:
                rc = float(r); break
        R["rcrit"][nm] = rc
        print("rcrit", nm, rc, flush=True)
    json.dump(R, open("res/c1_beh.json", "w"), indent=1)
