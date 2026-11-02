"""產生代表性 netlist（存到 net/rep_*.cir）：P400_Cc6 與 N1000_Cc3，10 mA，PSRR 與迴路增益。"""
import sys; sys.path.insert(0, '.')
from c1_lib import *
base = dict(Vin=1.8, Vref=0.8, CL=100e-12, R1=1e3, R2=4e3, Ibias=10e-6)
for nm, p in (('P400_Cc6', dict(base, kind='pmos', Wp=400, Cc=6e-12)), ('N1000_Cc3', dict(base, kind='nmos', Wn=1000, Cc=3e-12))):
    op_and_ac(p, 10e-3, f'rep_{nm}_10mA_psrr'); loopgain(p, 10e-3, f'rep_{nm}_10mA_loopgain')
