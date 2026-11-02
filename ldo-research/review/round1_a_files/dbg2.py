import numpy as np
from hyb2 import HDEF, run_hybrid
te=100e-9; t0=6e-6
p = dict(HDEF, fclk=10e6, droop=True, droop_src='vout', Vdr=1.57, tpd_droop=3e-9, tau_chain=2e-9)
load = f"IL vout 0 PWL(0 0 1u 0 1.1u 5m {t0} 5m {t0+te} 95m {t0+te+8e-6} 95m {t0+2*te+8e-6} 5m)"
tt, vo, vpg, code = run_hybrid(p, load, 8e-6, "dbg2", tstep=1e-9)
for tn in [0, 0.05, 0.1,0.2,0.5,1,1.05,1.1,1.2,1.5,2,3,4,5,5.9]:
    i = np.argmin(np.abs(tt - tn*1e-6))
    print(f"t={tn}us vout={vo[i]:.4f} pg={vpg[i]:.4f} code={code[i]}")
