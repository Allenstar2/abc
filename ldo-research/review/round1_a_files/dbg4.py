import numpy as np
from hyb2 import HDEF, run_hybrid
te=100e-9; t0=6e-6
p = dict(HDEF, fclk=10e6, droop=True, droop_src='both', Vdr=1.57, Vgate=1.30, tpd_droop=3e-9, tau_chain=2e-9, t_off=300e-9)
load = f"IL vout 0 PWL(0 0 1u 0 1.1u 5m {t0} 5m {t0+te} 95m {t0+te+8e-6} 95m {t0+2*te+8e-6} 5m)"
tt, vo, vpg, code = run_hybrid(p, load, t0 + 2*te + 16e-6, "dbg4", tstep=1e-9)
for tn in [0,5,10,15,20,30,40,60,80,100,150,200,300,500,800,1000,1500,2000,3000,4000,5000,6000,7000,8000]:
    i = np.argmin(np.abs(tt - (t0 + tn*1e-9)))
    print(f"t={tn:5d}ns vout={vo[i]:.4f} pg={vpg[i]:.4f} code={code[i]}")
w=(tt>t0+3e-6)&(tt<t0+8e-6)
print("plateau 3-8us: pp=%.1f mV, code changes=%d, mean=%.4f"%((vo[w].max()-vo[w].min())*1e3, np.count_nonzero(np.diff(code[w])), vo[w].mean()))
