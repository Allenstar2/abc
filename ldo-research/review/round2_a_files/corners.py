"""Vth/Tox 平移（同 repo s6_corners.py 的作法）＋可選的其他模型參數擾動；模型寫到 scratch。"""
import os, re
from common import MODEL, RES
base = open(MODEL).read()
os.makedirs(f"{RES}/models", exist_ok=True)
CASES = {"TT": (0, 0, 1.0), "SS": (0.05, 0.05, 1.05), "FF": (-0.05, -0.05, 0.95),
         "SF": (0.05, -0.05, 1.0), "FS": (-0.05, 0.05, 1.0)}
def variant(dvthn=0, dvthp=0, tox=1.0, tag="x", nf=1.0, pclm=1.0, u0=1.0, cgdo=1.0, eta0p=1.0):
    s = base
    s = s.replace("Vth0 = 0.3999", f"Vth0 = {0.3999 + dvthn:.4f}")
    s = s.replace("Vth0 = -0.42", f"Vth0 = {-0.42 - dvthp:.4f}")
    s = s.replace("Tox = 4.e-09", f"Tox = {4e-9 * tox:.4e}").replace("Tox = 4.2e-09", f"Tox = {4.2e-9 * tox:.4e}")
    s = s.replace("NFactor= 0.9000000", f"NFactor= {0.9*nf:.4f}").replace("NFactor= 1.4000000", f"NFactor= {1.4*nf:.4f}")
    s = s.replace("Pclm= 5.0000000E-02", f"Pclm= {0.05*pclm:.4e}").replace("Pclm= 2.0000000", f"Pclm= {2.0*pclm:.4e}")
    s = s.replace("U0= 3.5000000E-02", f"U0= {0.035*u0:.4e}").replace("U0= 8.0000000E-03", f"U0= {0.008*u0:.4e}")
    s = s.replace("Cgdo=2.786E-10", f"Cgdo={2.786e-10*cgdo:.4e}").replace("Cgso=2.786E-10", f"Cgso={2.786e-10*cgdo:.4e}")
    s = s.replace("Eta0= 8.5000000", f"Eta0= {8.5*eta0p:.4f}")
    path = f"{RES}/models/m_{re.sub(r'[^A-Za-z0-9_]', '', tag)}.pm"; open(path, "w").write(s); return path
def corner(name, tag=None, **kw):
    dn, dp, tx = CASES[name]
    return variant(dn, dp, tx, tag or name, **kw)
