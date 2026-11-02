import numpy as np, subprocess
from hyb2 import HDEF, hybrid_netlist
te=100e-9; t0=6e-6
p = dict(HDEF, fclk=10e6, droop=True, droop_src='both', Vdr=1.57, Vgate=1.20, tpd_droop=3e-9, tau_chain=2e-9, t_off=300e-9)
load = (f"IL vout 0 PWL(0 0 1u 0 1.1u 5m {t0} 5m {t0+te} 95m {t0+te+10e-6} 95m {t0+2*te+10e-6} 45m "
        f"{t0+2*te+20e-6} 45m {t0+3*te+20e-6} 20m)")
extra = """.model dob dac_bridge(out_low=0 out_high=1 out_undef=0.5)
Aob [up dn droop clk hold q1 q2 q3 q4 d3 d4] [oup odn odr ock oho oq1 oq2 oq3 oq4 od3 od4] dob"""
tstop = t0+3*te+30e-6
net = hybrid_netlist(p, load, tstop, 1e-9, "dbg5", extra)
net = net.replace("wrdata", "wrdata res/dbg5_dig.txt v(oup) v(odn) v(odr) v(ock) v(oho) v(oq1) v(oq2) v(oq3) v(oq4) v(od3) v(od4)\nwrdata")
open("net/dbg5.cir","w").write(net)
subprocess.run(["ngspice","-b","net/dbg5.cir"],capture_output=True,text=True)
a=np.loadtxt("res/dbg5_dig.txt"); b=np.loadtxt("res/dbg5_tr.txt"); t=a[:,0]
ts = t0+3*te+20e-6
for dt in [-0.5, 0, 0.05, 0.1, 0.2, 0.3, 0.5, 1, 2, 5, 9]:
    tn = ts + dt*1e-6
    i=np.argmin(np.abs(t-tn)); j=np.argmin(np.abs(b[:,0]-tn))
    print(f"t=ts{dt:+.2f}us up={a[i,1]:.0f} dn={a[i,3]:.0f} droop={a[i,5]:.0f} hold={a[i,9]:.0f} q1-4={[round(a[i,11+2*k]) for k in range(4)]} d3={a[i,19]:.0f} d4={a[i,21]:.0f} vout={b[j,1]:.3f} pg={b[j,3]:.3f}")
# clock edges near end
w = t > ts+5e-6
print("clk toggles in last window:", np.count_nonzero(np.diff((a[w,7]>0.5).astype(int))))
