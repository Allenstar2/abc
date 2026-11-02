"""第 3 輪審查 (b) 指出沒有腳本可重現的兩個數字：
1. 片上 NMOS 負載電流密度（W=100 µm、L=0.18 µm、Vgs=1.8 V、Vds=1.6 V）
2. SF-like 125 °C 零載時 REF-A 的 pg、ea、Vout（高溫漏電失效情境）"""
import json, os
from common import run, MODEL, RES
from ldo_ref import DEFAULT, loopgain
R = {}
out = run(f"* nmos load density\n.include {MODEL}\nVD d 0 1.6\nVG g 0 1.8\nM1 d g 0 0 NMOS W=100u L=0.18u\n.control\nop\nprint -i(VD)\nquit\n.endc\n.end\n", "s19_nload")
i = float([l for l in out.splitlines() if "i(vd)" in l.lower()][0].split("=")[1])
R["nmos_load_mA_per_um"] = round(i * 1e3 / 100, 3)
sf = os.path.join(RES, "tmp", "model_SFlikeVthn50Vthp50.pm")
if not os.path.exists(sf):
    import subprocess; subprocess.run(["python3", "s6_corners.py"], check=True)
f, T, v = loopgain(dict(DEFAULT, R1=4e3, R2=4e3, Cc=5e-12, model=sf, temp=125), 0, "s19_sf")
R["SFlike_125C_noload"] = {k: round(val, 4) for k, val in v.items()}
print(R); json.dump(R, open(f"{RES}/s19_repro_misc.json", "w"), indent=1)
