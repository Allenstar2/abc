import numpy as np, subprocess
from hyb2 import HDEF, hybrid_netlist
te=100e-9; t0=6e-6
p = dict(HDEF, fclk=10e6, droop=True, droop_src='vout', Vdr=1.57, tpd_droop=3e-9, tau_chain=2e-9)
load = f"IL vout 0 PWL(0 0 1u 0 1.1u 5m {t0} 5m)"
extra = """.model dob dac_bridge(out_low=0 out_high=1 out_undef=0.5)
Aob [up dn droop clk s1 s2 s3 s4 s5] [oup odn odr ock os1 os2 os3 os4 os5] dob"""
net = hybrid_netlist(p, load, 3e-6, 1e-9, "dbg3", extra)
net = net.replace("wrdata", "wrdata res/dbg3_dig.txt v(oup) v(odn) v(odr) v(ock) v(os1) v(os2) v(os3) v(os4) v(os5)\nwrdata")
open("net/dbg3.cir","w").write(net)
out = subprocess.run(["ngspice","-b","net/dbg3.cir"],capture_output=True,text=True).stdout
a=np.loadtxt("res/dbg3_dig.txt"); b=np.loadtxt("res/dbg3_tr.txt")
t=a[:,0]
for tn in np.arange(0.99,1.6,0.02):
    i=np.argmin(np.abs(t-tn*1e-6)); j=np.argmin(np.abs(b[:,0]-tn*1e-6))
    codes=''.join('1' if b[j,5+2*k]<0.9 else '0' for k in range(8))
    print(f"{tn:.2f}us up={a[i,1]:.0f} dn={a[i,3]:.0f} droop={a[i,5]:.0f} s1-5={[round(a[i,9+2*k]) for k in range(5)]} vout={b[j,1]:.3f} pg={b[j,3]:.3f} q={codes}")
