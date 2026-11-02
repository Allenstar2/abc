import numpy as np
from hyb2 import HDEF, run_hybrid
te=100e-9; t0=6e-6
p = dict(HDEF, fclk=10e6, droop=True, tpd_droop=3e-9, tau_chain=2e-9, VLL=1.0)
load = f"IL vout 0 PWL(0 0 1u 0 1.1u 5m {t0} 5m {t0+te} 95m {t0+te+8e-6} 95m {t0+2*te+8e-6} 5m)"
tt, vo, vpg, code = run_hybrid(p, load, t0 + 2*te + 16e-6, "dbg1", tstep=1e-9)
for tn in list(range(-20, 200, 10)) + [250, 300, 400, 500, 700, 1000]:
    i = np.argmin(np.abs(tt - (t0 + tn*1e-9)))
    IL = 5 + 90*min(max(tn,0),100)/100
    print(f"t={tn:5d}ns IL={IL:5.1f}mA vout={vo[i]:.4f} pg={vpg[i]:.4f} code={code[i]}")
w=(tt>t0)&(tt<t0+2e-6); i=np.argmin(vo[w]); print("min at", (tt[w][i]-t0)*1e9, "ns", vo[w][i])
