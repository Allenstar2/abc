"""Check: with pure latency d (instant analog), LC iff fewer than d+1 consecutive codes lie in the window."""
import numpy as np
from hybrid_beh import scan, I_LO, N
LO = np.linspace(0.0, 8.0, 801) + 1.234e-5
for d in (1, 2):
    for r in (1.2, 1.5, 1.9, 2.0, 2.5, 2.9, 3.0):
        lc, _ = scan(r, loads=LO, d=d, ncyc=2000, tail=400)
        IH = I_LO + r; IMAX = IH + 0.35
        pred = np.zeros(len(LO), bool)
        for i, L in enumerate(LO):
            Ia = np.clip(L - np.arange(N + 1), 0, IMAX)
            n_in = int(((Ia >= I_LO) & (Ia <= IH)).sum())
            # regulating interior: a code exists with Ia above window and another below
            interior = (Ia > IH).any() and (Ia < I_LO).any()
            pred[i] = interior and n_in < d + 1
        print(f"d={d} r={r:3.1f}  sim LC frac={lc.mean():.3f}   predicted(n_in<d+1, interior)={pred.mean():.3f}   agree={100*(lc==pred).mean():.1f}%")
