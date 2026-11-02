"""Measure how fast the analog pass current I(Mp) picks up a current step of one slice (12.2 mA)
in REF-A (reviewer netlist). Slice turning ON == load step DOWN by 12.2 mA as seen by the analog loop."""
import numpy as np, sys
sys.path.insert(0, ".")
from sim_lg import HDR, core, run
res = []
for I1, I2, tag in [(0.0122, 0.0002, "dn12_0"), (0.0002, 0.0124, "up0_12"), (0.0222, 0.010, "dn22_10"), (0.010, 0.0222, "up10_22")]:
    c = core().replace("Mp   vout pg vin vin", "Mp   vpd pg vin vin") + "Vmp vpd vout 0\n"
    net = HDR + c + f"""
VIN vin 0 DC 1.8
VREF vref 0 0.8
Vjoin vout r1t 0
IL vout 0 PWL(0 {I1} 1u {I1} 1.001u {I2})
.control
tran 0.2n 4u 0 0.2n
wrdata tau_{tag}.txt i(Vmp) v(vout) v(pg)
.endc
.end
"""
    run(net, f"tau_{tag}")
    a = np.loadtxt(f"tau_{tag}.txt"); t = a[:, 0]; i = a[:, 1]; vo = a[:, 3]; pg = a[:, 5]
    i0 = i[(t > 0.9e-6) & (t < 1e-6)].mean(); i_end = i[t > 3.8e-6].mean()
    tt = t - 1.0005e-6
    frac = (i - i0) / (i_end - i0)
    def tcross(x):
        k = np.where((tt > 0) & (frac >= x))[0]
        return tt[k[0]] if len(k) else np.nan
    t63, t90 = tcross(0.632), tcross(0.9)
    vdev = (vo[t > 1e-6] - vo[(t > 0.9e-6) & (t < 1e-6)].mean())
    res.append((tag, i0*1e3, i_end*1e3, t63*1e9, t90*1e9, vdev.max()*1e3, vdev.min()*1e3))
    print(f"{tag:8s} I_pass {i0*1e3:6.2f}->{i_end*1e3:6.2f} mA  t63={t63*1e9:6.1f} ns  t90={t90*1e9:6.1f} ns  Vout dev max/min = {vdev.max()*1e3:.1f}/{vdev.min()*1e3:.1f} mV")

print("--- V(pg) and Vout settling (fraction of final step reached) ---")
for tag in ["dn12_0", "up0_12", "dn22_10", "up10_22"]:
    a = np.loadtxt(f"tau_{tag}.txt"); t = a[:, 0]; vo = a[:, 3]; pg = a[:, 5]
    tt = t - 1.0005e-6
    for nm, x in (("pg", pg), ("vout", vo)):
        x0 = x[(t > 0.9e-6) & (t < 1e-6)].mean(); xe = x[t > 3.8e-6].mean()
        fr = (x - x0) / (xe - x0) if abs(xe - x0) > 1e-6 else None
        if fr is None:
            # settle relative to peak deviation
            dev = np.abs(x - x0); pk = dev.max(); k = np.where((tt > 0) & (dev < 0.1*pk) & (np.arange(len(t)) > np.argmax(dev)))[0]
            print(f"{tag:8s} {nm:4s} step~0, peak {pk*1e3:.1f} mV, back within 10% of peak at {tt[k[0]]*1e9 if len(k) else np.nan:.0f} ns")
            continue
        def tc(v):
            k = np.where((tt > 0) & (np.abs(fr - 1) <= v) )[0]
            # first time after which it stays within band
            inside = (np.abs(fr - 1) <= v) & (tt > 0)
            last_out = np.where(~inside & (tt > 0))[0]
            return tt[last_out[-1] + 1] if len(last_out) and last_out[-1] + 1 < len(tt) else np.nan
        print(f"{tag:8s} {nm:4s} dX={1e3*(xe-x0):7.2f} mV  settle to 10%: {tc(0.1)*1e9:7.1f} ns   to 2%: {tc(0.02)*1e9:7.1f} ns")
