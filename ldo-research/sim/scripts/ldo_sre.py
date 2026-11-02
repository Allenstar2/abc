"""REF-A2：REF-A ＋ 電容耦合式 slew-rate enhancement（class-B、靜態幾乎不耗電）。
下拉路徑（Vout 快速下降）：Cf1 把 Vout 耦合到 PMOS Mz 閘極（平時偏在 Vin−Vbp，接近截止）→ Mz 導通把 gdn 拉高 → NMOS My 把 pg 拉低。
上拉路徑（Vout 快速上升）：Cf2 把 Vout 耦合到 NMOS Mx 閘極（平時偏在 Vbn，接近截止）→ Mx 把 gu 拉低 → PMOS Mup 把 pg 拉向 Vin。
偏壓用 replica（二極體接法的同尺寸電晶體＋0.2 µA）經大電阻 Rb 接到偵測管閘極（高通時間常數 Rb·Cf）。
第一版用固定 0.3 V 偏壓失敗（PTM PMOS L=0.18 µm 的 Vth 受 DIBL 影響只剩 ~0.28 V，偵測管靜態導通把 pg 拉到 0），見 LOG.md。
"""
from ldo_ref import DEFAULT, subckt as subckt_a

SDEF = dict(DEFAULT, R1=4e3, R2=4e3, Cc=5e-12, CL=100e-12,
            Cf1=1e-12, Cf2=1e-12, Rb=1e6, Irep=0.2e-6, Ldet=0.5, Wbn=4, Wbp=8, Wpd=40, Wpu=40, Rpu=200e3, Rpd=200e3)


def subckt(p):
    base = subckt_a(p).rstrip()
    assert base.endswith(".ends")
    sre = f"""
* --- SRE 下拉：Vout↓ → gz↓ → Mz on → gdn↑ → My on → pg↓
Cf1 vout gz {p['Cf1']}
* replica 偏壓：Mz 靜態電流 ≈ Irep（與製程/溫度無關的電流密度）
Irz bz 0 {p['Irep']}
Mrz bz bz vin vin PMOS W={p['Wbp']}u L={p['Ldet']}u
Rbz gz bz {p['Rb']}
Mz gdn gz vin vin PMOS W={p['Wbp']}u L={p['Ldet']}u
Rpd gdn 0 {p['Rpd']}
My pg gdn 0 0 NMOS W={p['Wpd']}u L=0.18u
* --- SRE 上拉：Vout↑ → gx↑ → Mx on → gu↓ → Mup on → pg↑
Cf2 vout gx {p['Cf2']}
Irx vin bx {p['Irep']}
Mrx bx bx 0 0 NMOS W={p['Wbn']}u L={p['Ldet']}u
Rbx gx bx {p['Rb']}
Mx gu gx 0 0 NMOS W={p['Wbn']}u L={p['Ldet']}u
Rpu gu vin {p['Rpu']}
Mup pg gu vin vin PMOS W={p['Wpu']}u L=0.18u
.ends
"""
    return base[: -len(".ends")] + sre
