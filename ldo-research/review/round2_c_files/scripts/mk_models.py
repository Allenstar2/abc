"""Create |Vth|-shifted copies of the repo PTM 180nm model (only Vth0 changed). dn/dp = shift of |Vth| in mV."""
import os
src = open('/home/user/abc/ldo-research/sim/models/180nm_bulk.pm').read()
base = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models'); os.makedirs(base, exist_ok=True)
for dn in (-50, 0, 50):
    for dp in (-50, 0, 50):
        s = src.replace('Vth0 = 0.3999', f'Vth0 = {0.3999 + dn/1000:.4f}').replace('Vth0 = -0.42', f'Vth0 = {-0.42 - dp/1000:.4f}')
        assert s.count('Vth0') == 2
        open(os.path.join(base, f'ptm_n{dn:+d}_p{dp:+d}.pm'), 'w').write(s)
