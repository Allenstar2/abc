"""第 3 輪 (c) 獨立驗證：NMOS-pass vs PMOS-pass LDO（自寫 netlist，不 import repo 或前審查者模組）。
共同條件：Vin=1.8 V、Vref=0.8 V、PTM 180nm、CL=100 pF、相同分壓器（相同 Vout、相同最小負載）。
PMOS 版 = 依 sim/scripts/ldo_ref.py subckt() 的連接重抄（5T OTA → PMOS SF buffer → PMOS pass，Miller Cc Vout→ea）。
NMOS 版 = 5T OTA（輸入對調）直接驅動 NMOS source follower pass 閘極，Cc 由閘極接地。
EA 供電節點 vdda 可接 vin（預設，EA 也吃漣波）或接獨立乾淨電源（對照）。
"""
import os, subprocess, numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = "/home/user/abc/ldo-research/sim/models/180nm_bulk.pm"
NET = os.path.join(HERE, "net"); RES = os.path.join(HERE, "res")
os.makedirs(NET, exist_ok=True); os.makedirs(RES, exist_ok=True)


def run(text, name):
    path = os.path.join(NET, name + ".cir")
    open(path, "w").write(text)
    p = subprocess.run(["ngspice", "-b", path], cwd=NET, capture_output=True, text=True, timeout=600)
    out = p.stdout + p.stderr
    if p.returncode != 0 or "fatal" in out.lower() or "error" in out.lower() and "no error" not in out.lower():
        bad = [l for l in out.splitlines() if "rror" in l or "atal" in l]
        if bad:
            print("[ngspice]", name, bad[:5])
    return out


def pvals(out, keys):
    """解析 ngspice print 輸出 'name = value'。"""
    d = {}
    for line in out.splitlines():
        s = line.strip()
        if "=" not in s:
            continue
        k, v = s.split("=", 1)
        k = k.strip()
        if k in keys:
            try:
                d[k] = float(v.split()[0])
            except ValueError:
                pass
    return d


# ---------------- 電路 ----------------
def sub_pmos(p):
    """REF-A 連接（重抄）：Ibias/偏壓/EA/buffer 都接 vdda，pass source 接 vin。"""
    cc = f"Rz vout ncz {p['Rz']}\nCc ncz ea {p['Cc']}" if p.get('Rz', 0) > 0 else f"Cc vout ea {p['Cc']}"
    tm, bm = p.get('tail_mult', 2), p.get('buf_mult', 5)
    return f"""
.subckt ldo vin vdda vout vref fb fbi
Ibias vdda bn {p['Ibias']}
Mbn bn bn 0 0 NMOS W=4u L=1u
Mt tail bn 0 0 NMOS W={4*tm}u L=1u
M1 d1 fbi tail 0 NMOS W=20u L=1u
M2 ea vref tail 0 NMOS W=20u L=1u
M3 d1 d1 vdda vdda PMOS W=4u L=1u
M4 ea d1 vdda vdda PMOS W=4u L=1u
Mbn2 bp bn 0 0 NMOS W=4u L=1u
Mbp bp bp vdda vdda PMOS W=4u L=1u
Mcs pg bp vdda vdda PMOS W={4*bm}u L=1u
Mb 0 ea pg pg PMOS W=20u L=0.18u
Mp vout pg vin vin PMOS W={p['Wp']}u L={p.get('Lp',0.18)}u
R1 vout fb {p['R1']}
R2 fb 0 {p['R2']}
{cc}
.ends
"""


def sub_nmos(p):
    """NMOS source follower pass；EA = 5T NMOS 輸入 OTA，fb 接 M2（ea 側）→ 反相；Cc 閘極接地。
    body 接地（無 deep N-well）。"""
    tm = p.get('tail_mult', 2)
    ccap = f"Cc ea 0 {p['Cc']}" if p.get('cc_mode', 'gnd') == 'gnd' else f"Cc ea vout {p['Cc']}"
    return f"""
.subckt ldo vin vdda vout vref fb fbi
Ibias vdda bn {p['Ibias']}
Mbn bn bn 0 0 NMOS W=4u L=1u
Mt tail bn 0 0 NMOS W={4*tm}u L=1u
M1 d1 vref tail 0 NMOS W=20u L=1u
M2 ea fbi tail 0 NMOS W=20u L=1u
M3 d1 d1 vdda vdda PMOS W={p.get('Wld',4)}u L=1u
M4 ea d1 vdda vdda PMOS W={p.get('Wld',4)}u L=1u
{ccap}
Mn vin ea vout 0 NMOS W={p['Wn']}u L={p.get('Ln',0.18)}u
R1 vout fb {p['R1']}
R2 fb 0 {p['R2']}
.ends
"""


def header(p, title):
    sub = sub_pmos(p) if p['kind'] == 'pmos' else sub_nmos(p)
    return f"* {title}\n.include {MODEL}\n.options temp=27 reltol=1e-4 abstol=1e-12 vntol=1e-7\n{sub}"


def supplies(p, ac_vin):
    s = f"VIN vin 0 DC {p['Vin']} AC {ac_vin}\n"
    if p.get('ea_supply', 'vin') == 'vin':
        s += "Rtie vdda vin 1e-3\n"          # EA 與 pass 同一個 Vin（漣波也進 EA）
    else:
        s += f"VDDA vdda 0 DC {p.get('Vdda', p['Vin'])} AC 0\n"   # 乾淨的 EA 供電
    return s


PASSDEV = {'pmos': 'm.x1.mp', 'nmos': 'm.x1.mn'}


def op_and_ac(p, IL, name):
    """一次跑：OP（含 pass 小訊號參數）、PSRR（vin AC=1）。"""
    dev = PASSDEV[p['kind']]
    gnode = 'x1.pg' if p['kind'] == 'pmos' else 'x1.ea'
    net = header(p, name) + supplies(p, 1) + f"""VREF vref 0 {p['Vref']}
X1 vin vdda vout vref fb fb ldo
CL vout 0 {p['CL']}
IL vout 0 DC {IL}
.control
op
let vout_op = v(vout)
let vg_op = v({gnode})
let iin = -i(vin)
let gm_p = @{dev}[gm]
let gds_p = @{dev}[gds]
let gmb_p = @{dev}[gmbs]
let id_p = @{dev}[id]
print vout_op vg_op iin gm_p gds_p gmb_p id_p
"""
    if p.get('ea_supply', 'vin') != 'vin':
        net += "let iea = -i(vdda)\nprint iea\n"
    net += f"""ac dec 40 100 1e9
wrdata {RES}/{name}_ps.txt v(vout) v({gnode})
quit
.endc
.end
"""
    out = run(net, name)
    d = pvals(out, ['vout_op', 'vg_op', 'iin', 'gm_p', 'gds_p', 'gmb_p', 'id_p', 'iea'])
    a = np.loadtxt(f"{RES}/{name}_ps.txt", ndmin=2)
    f = a[:, 0]; vo = a[:, 1] + 1j * a[:, 2]; vg = a[:, 4] + 1j * a[:, 5]
    return d, f, vo, vg


def loopgain(p, IL, name):
    net = header(p, name) + supplies(p, 0) + f"""VREF vref 0 {p['Vref']}
X1 vin vdda vout vref fb fbi ldo
Lbrk fb fbi 1e9
Cbrk fbi acs 1
VAC acs 0 DC 0 AC 1
CL vout 0 {p['CL']}
IL vout 0 DC {IL}
.control
ac dec 50 10 3e9
let T = -v(fb)/v(fbi)
wrdata {RES}/{name}_T.txt T
quit
.endc
.end
"""
    run(net, name)
    a = np.loadtxt(f"{RES}/{name}_T.txt", ndmin=2)
    return a[:, 0], a[:, 1] + 1j * a[:, 2]


def margins(f, T):
    mag = 20 * np.log10(np.abs(T)); ph = np.degrees(np.unwrap(np.angle(T)))
    # 相位以 DC 為 0° 起算（T 定義為 -v(fb)/v(fbi)，負回授時 DC 相位 ≈ 0）
    ph = ph - 360 * np.round(ph[0] / 360)
    i = np.where((mag[:-1] > 0) & (mag[1:] <= 0))[0]
    if len(i) == 0:
        return dict(dc_db=float(mag[0]), ugf_MHz=float('nan'), pm=float('nan'), gm_db=float('nan'))
    i = i[0]
    x = mag[i] / (mag[i] - mag[i + 1])
    lf = np.log10(f[i]) + x * (np.log10(f[i + 1]) - np.log10(f[i]))
    phu = ph[i] + x * (ph[i + 1] - ph[i])
    j = np.where((ph[:-1] > -180) & (ph[1:] <= -180))[0]
    gmdb = float(-np.interp(-180, [ph[j[0] + 1], ph[j[0]]], [mag[j[0] + 1], mag[j[0]]])) if len(j) else float('inf')
    return dict(dc_db=float(mag[0]), ugf_MHz=float(10 ** lf / 1e6), pm=float(180 + phu), gm_db=gmdb)


def at_db(f, H, fq):
    return float(np.interp(np.log10(fq), np.log10(f), 20 * np.log10(np.abs(H))))


def openloop_psr(p, IL, name):
    """迴路在 EA 輸入斷開（L-C），Vin 加 AC=1、測試源 AC=0：得到開迴路 Vin→Vout 轉移 G_ol(f)
    與閘極節點的 h(f)=v(gate)/v(vin)。閉迴路 PSR = G_ol/(1+T)（斷點為 MOS 閘極，負載可忽略）。"""
    gnode = 'x1.pg' if p['kind'] == 'pmos' else 'x1.ea'
    net = header(p, name) + supplies(p, 1) + f"""VREF vref 0 {p['Vref']}
X1 vin vdda vout vref fb fbi ldo
Lbrk fb fbi 1e9
Cbrk fbi acs 1
VAC acs 0 DC 0 AC 0
CL vout 0 {p['CL']}
IL vout 0 DC {IL}
.control
ac dec 40 100 1e9
wrdata {RES}/{name}_ol.txt v(vout) v({gnode})
quit
.endc
.end
"""
    run(net, name)
    a = np.loadtxt(f"{RES}/{name}_ol.txt", ndmin=2)
    return a[:, 0], a[:, 1] + 1j * a[:, 2], a[:, 4] + 1j * a[:, 5]
