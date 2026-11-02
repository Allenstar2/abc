"""參考 LDO（REF-A）netlist 產生器與量測工具。
拓樸：NMOS 輸入 5T OTA (EA) → PMOS source follower buffer → PMOS pass device，
      Miller Cc 從 Vout 回授到 EA 輸出；回授電阻分壓 β=0.5；Vref=0.8 V 理想源。
所有元件參數集中在 DEFAULT，任何改動都要在 DECISIONS.md / 報告中說明。
"""
import numpy as np
from common import run, load_wrdata, MODEL, RES

DEFAULT = dict(
    Wp=4000,        # pass PMOS W (µm), L=0.18 µm
    Lp=0.18,
    Cc=3e-12,       # Miller 補償電容 Vout→EA 輸出
    Rz=0,           # 與 Cc 串聯的 nulling resistor (0 = 不用)
    R1=16e3, R2=16e3,  # 分壓（同時當最小負載，1.6V/32k = 50 µA）
    Ibias=10e-6,    # 主偏壓電流（理想電流源，來自 vin）
    tail_mult=2,    # EA tail = tail_mult * Ibias
    buf_mult=5,     # buffer 偏壓 = buf_mult * Ibias
    Win=20, Lin=1.0,    # EA 輸入對
    Wld=4, Lld=1.0,     # EA PMOS mirror load
    Wsf=20, Lsf=0.18,   # source follower PMOS
    CL=100e-12,
    ESR=0.0,        # on-chip 電容的串聯電阻（MOS cap 通道電阻等）
    Vin=1.8, Vref=0.8, temp=27,
)


def subckt(p):
    """回傳 REF-A 的 .subckt 文字。節點：vin vout vref fbi(=EA 正端輸入，供斷迴路用) fb"""
    rz = f"Rz vout ncz {p['Rz']}\nCc ncz ea {p['Cc']}" if p['Rz'] > 0 else f"Cc vout ea {p['Cc']}"
    return f"""
.subckt ldoA vin vout vref fb fbi
Ibias vin bn {p['Ibias']}
Mbn bn bn 0 0 NMOS W=4u L=1u
Mt tail bn 0 0 NMOS W={4*p['tail_mult']}u L=1u
M1 d1 fbi tail 0 NMOS W={p['Win']}u L={p['Lin']}u
M2 ea vref tail 0 NMOS W={p['Win']}u L={p['Lin']}u
M3 d1 d1 vin vin PMOS W={p['Wld']}u L={p['Lld']}u
M4 ea d1 vin vin PMOS W={p['Wld']}u L={p['Lld']}u
Mbn2 bp bn 0 0 NMOS W=4u L=1u
Mbp bp bp vin vin PMOS W=4u L=1u
Mcs pg bp vin vin PMOS W={4*p['buf_mult']}u L=1u
Mb 0 ea pg pg PMOS W={p['Wsf']}u L={p['Lsf']}u
Mp vout pg vin vin PMOS W={p['Wp']}u L={p['Lp']}u
R1 vout fb {p['R1']}
R2 fb 0 {p['R2']}
{rz}
.ends
"""


def header(p, title):
    return f"* {title}\n.include {MODEL}\n.options temp={p['temp']} reltol=1e-4 abstol=1e-12 vntol=1e-7\n" + subckt(p)


def loopgain(p, Iload, name, closed_psrr=True):
    """斷迴路於 EA 輸入（高阻抗閘極，L-C 法），回傳 f, T(複數), 以及 PSRR(f)。"""
    net = header(p, name) + f"""
VIN vin 0 DC {p['Vin']} AC 0
VREF vref 0 {p['Vref']}
X1 vin vout vref fb fbi ldoA
Lbrk fb fbi 1e9
Cbrk fbi acs 1
VAC acs 0 DC 0 AC 1
CL vout ncl {p['CL']}
RESR ncl 0 {max(p['ESR'],1e-6)}
IL vout 0 DC {Iload}
.control
op
let vout_op = v(vout)
let vpg_op = v(x1.pg)
let vea_op = v(x1.ea)
let iin = -i(vin)
print vout_op vpg_op vea_op iin
ac dec 40 10 1e10
let T = -v(fb)/v(fbi)
wrdata {RES}/{name}_T.txt T
quit
.endc
.end
"""
    out = run(net, name)
    vals = {}
    for k in ("vout_op", "vpg_op", "vea_op", "iin"):
        for line in out.splitlines():
            if line.strip().startswith(k + " "):
                vals[k] = float(line.split("=")[1])
    a = np.loadtxt(f"{RES}/{name}_T.txt", ndmin=2)
    f = a[:, 0]; T = a[:, 1] + 1j * a[:, 2]
    return f, T, vals


def margins(f, T):
    mag = 20 * np.log10(np.abs(T))
    ph = np.unwrap(np.angle(T)) * 180 / np.pi
    dc = mag[0]
    idx = np.where((mag[:-1] > 0) & (mag[1:] <= 0))[0]
    if len(idx) == 0:
        return dict(dc_db=dc, ugf=np.nan, pm=np.nan, gm_db=np.nan)
    i = idx[0]
    fr = f[i] * (f[i+1]/f[i]) ** (mag[i] / (mag[i] - mag[i+1]))
    phu = np.interp(np.log10(fr), np.log10(f[i:i+2]), ph[i:i+2])
    pm = 180 + phu
    # gain margin：相位到 -180 的頻率
    j = np.where((ph[:-1] > -180) & (ph[1:] <= -180))[0]
    gmdb = -np.interp(-180, [ph[j[0]+1], ph[j[0]]], [mag[j[0]+1], mag[j[0]]]) if len(j) else np.inf
    return dict(dc_db=float(dc), ugf=float(fr), pm=float(pm), gm_db=float(gmdb))


def psrr(p, Iload, name):
    net = header(p, name) + f"""
VIN vin 0 DC {p['Vin']} AC 1
VREF vref 0 {p['Vref']}
X1 vin vout vref fb fb ldoA
CL vout ncl {p['CL']}
RESR ncl 0 {max(p['ESR'],1e-6)}
IL vout 0 DC {Iload}
.control
ac dec 20 10 1e9
let psr = v(vout)
wrdata {RES}/{name}_psr.txt psr
quit
.endc
.end
"""
    run(net, name)
    a = np.loadtxt(f"{RES}/{name}_psr.txt", ndmin=2)
    return a[:, 0], 20 * np.log10(np.hypot(a[:, 1], a[:, 2]))


def load_step(p, I1, I2, tedge, name, thold=5e-6, tstop=None, extra=""):
    """負載電流 I1→I2→I1，邊沿時間 tedge。回傳 t, vout, 量測。"""
    t0 = 2e-6
    t1 = t0 + tedge; t2 = t1 + thold; t3 = t2 + tedge
    tstop = tstop or (t3 + thold)
    tstep = min(tedge / 20, 2e-9)
    net = header(p, name) + f"""
VIN vin 0 DC {p['Vin']}
VREF vref 0 {p['Vref']}
X1 vin vout vref fb fb ldoA
CL vout ncl {p['CL']}
RESR ncl 0 {max(p['ESR'],1e-6)}
IL vout 0 PWL(0 {I1} {t0} {I1} {t1} {I2} {t2} {I2} {t3} {I1})
{extra}
.control
tran {tstep} {tstop} 0 {tstep*5}
wrdata {RES}/{name}_tr.txt v(vout) v(x1.pg) v(x1.ea)
quit
.endc
.end
"""
    run(net, name)
    a = np.loadtxt(f"{RES}/{name}_tr.txt", ndmin=2)
    t = a[:, 0]; vo = a[:, 1]; vpg = a[:, 3]; vea = a[:, 5]
    pre = vo[(t > t0 - 0.2e-6) & (t < t0)].mean()
    w1 = (t > t0) & (t < t2)
    w2 = (t > t2)
    end2 = vo[(t > t2 - 0.3e-6) & (t < t2)].mean()
    return t, vo, vpg, dict(v_pre=float(pre), undershoot=float(pre - vo[w1].min()),
                            overshoot=float(vo[w2].max() - end2), v_heavy=float(end2),
                            dv_load_reg=float(pre - end2))
