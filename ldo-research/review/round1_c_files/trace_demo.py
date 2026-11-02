import numpy as np
from hybrid_beh import simulate
L = np.array([4.0 + 1.234e-5])   # window [0.25, 0.25+r]: code 3 (I_a=1.0) and maybe 4 (0.0) ...
for kw, r in ((dict(d=0), 1.5), (dict(d=1), 1.5), (dict(d=1, b=1), 1.5), (dict(d=2), 2.2), (dict(d=2, b=2), 1.05), (dict(order=2, wn=1.0, zeta=0.3), 1.2)):
    lc, pp, trk, trI = simulate(r, loads=L, k0=0, ncyc=60, tail=20, traces=True, **kw)
    print(kw, f"r={r}", "LC" if lc[0] else "stable", "codes:", "".join(str(int(x)) for x in trk[:40, 0]))
