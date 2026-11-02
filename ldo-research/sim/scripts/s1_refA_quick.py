import sys, json
from ldo_ref import DEFAULT, loopgain, margins
p = dict(DEFAULT)
for kv in sys.argv[1:]:
    k, v = kv.split("="); p[k] = float(v)
for IL in (0, 1e-3, 10e-3, 50e-3, 100e-3):
    f, T, vals = loopgain(p, IL, f"q_IL{IL}")
    m = margins(f, T)
    print(f"IL={IL*1e3:6.1f}mA vout={vals.get('vout_op',0):.4f} vpg={vals.get('vpg_op',0):.3f} vea={vals.get('vea_op',0):.3f} "
          f"DC={m['dc_db']:.1f}dB UGF={m['ugf']/1e6:.2f}MHz PM={m['pm']:.1f} GM={m['gm_db']:.1f}dB")
