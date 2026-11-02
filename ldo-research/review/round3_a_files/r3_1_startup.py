"""第 3 輪 (a)：REF-A 啟動暫態（Vin 0 → 1.8 V 斜升）。
檢查：Vout 是否過衝、是否卡在錯誤狀態、最終值是否正確。
變數：Vin 斜升時間、偏壓來源（理想外部電流 / Vin→bn 電阻）、Vref 來源（先上電的外部 0.8 V /
板上由 Vin 分壓 / Vin 穩定後才加）、負載（只有分壓洩放 / 16 Ω / 片上 NMOS 負載在上電時被誤開）、CL。
REF-A 參數：CL=100 pF、Cc=5 pF、R1=R2=4 kΩ（與 s3_refA_char.py 相同）。"""
import json, sys, numpy as np
from ldo_ref import DEFAULT, subckt
from common import run, MODEL, RES

def sub_with_bias(p, bias):
    s = subckt(p)
    if bias == "ideal_ext":      # 外部 SMU 灌入 10 µA（從 t=0 起就有）
        s = s.replace(f"Ibias vin bn {p['Ibias']}", f"Ibias 0 bn {p['Ibias']}")
        s = s.replace(".subckt ldoA vin vout vref fb fbi", ".subckt ldoA vin vout vref fb fbi")
    elif bias == "res":          # Vin → bn 電阻（最常見的「外部電阻定偏壓」做法）
        s = s.replace(f"Ibias vin bn {p['Ibias']}", "Rbias vin bn 124k")
    elif bias == "ideal_vin":    # 原模型：理想電流源接在 Vin（Vin=0 時仍送 10 µA，非物理）
        pass
    return s

def startup(p, tr, bias, vref_mode, load, name, tsim=None):
    tsim = tsim or (tr * 3 + 20e-6)
    t_on = 1e-6
    vin = f"VIN vin 0 PWL(0 0 {t_on} 0 {t_on+tr} {p['Vin']})"
    if vref_mode == "fixed":
        vref = f"VREF vref 0 {p['Vref']}"
    elif vref_mode == "divider":
        vref = f"EREF vref 0 vin 0 {p['Vref']/p['Vin']}"
    elif vref_mode == "late":
        tl = t_on + tr + 5e-6
        vref = f"VREF vref 0 PWL(0 0 {tl} 0 {tl+1e-6} {p['Vref']})"
        tsim = max(tsim, tl + 20e-6)
    if load == "bleed":
        ld = ""
    elif load == "R16":
        ld = "RL vout 0 16"
    elif load == "nmos_on":
        ld = "ML vout vin 0 0 NMOS W=139u L=0.18u"
    tmax = min(tr / 400, 5e-9) if tr < 1e-4 else tr / 2000
    net = f"* {name}\n.include {MODEL}\n.options temp={p['temp']} reltol=1e-4 abstol=1e-12 vntol=1e-7\n" + \
          sub_with_bias(p, bias) + f"""
{vin}
{vref}
X1 vin vout vref fb fb ldoA
CL vout 0 {p['CL']}
{ld}
.ic v(vout)=0
.control
tran {tmax} {tsim} 0 {tmax} uic
wrdata {RES}/{name}_tr.txt v(vout) v(vin) v(x1.pg) v(x1.ea) v(vref)
quit
.endc
.end
"""
    run(net, name, timeout=1200)
    a = np.loadtxt(f"{RES}/{name}_tr.txt", ndmin=2)
    t = a[:, 0]; vo = a[:, 1]; vi = a[:, 3]; pg = a[:, 5]
    tail = t > t[-1] - 0.05 * (t[-1] - t[0])
    vfin = float(vo[tail].mean())
    target = 2 * p["Vref"] * (1.0)  # 1.6 V
    vmax = float(vo.max())
    # 過衝：Vout 超過「最終值」多少；以及超過 Vin 斜升期間 Vout−Vin 的最大值
    over = vmax - vfin
    bad = np.where(np.abs(vo - vfin) > 0.016)[0]
    t_ref = t_on + tr if vref_mode != "late" else t_on + tr + 5e-6 + 1e-6
    tset = float(t[bad[-1]] - t_ref) if len(bad) else 0.0   # 相對「Vin（或 Vref）到達最終值」的時刻
    # Vin 到達 1.8 V 後的過衝時間（Vout > 1.6 V+2% 的總時間）
    above = vo > vfin + 0.032
    dt = np.diff(t, prepend=t[0])
    t_above = float((dt * above).sum())
    return dict(name=name, tr_us=tr * 1e6, bias=bias, vref=vref_mode, load=load, CL_pF=p["CL"] * 1e12,
                vout_final=round(vfin, 4), ok=bool(abs(vfin - target) < 0.03) if load == "bleed" else None,
                vout_max=round(vmax, 4), overshoot_mV=round(over * 1e3, 1),
                t_above_2pct_ns=round(t_above * 1e9, 1), t_settle_1pct_after_us=round(tset * 1e6, 3),
                pg_min=round(float(pg.min()), 3))

if __name__ == "__main__":
    P100 = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
    P1n = dict(DEFAULT, CL=1e-9, Cc=20e-12, R1=4e3, R2=4e3)
    R = []
    cases = []
    for tr in (1e-6, 10e-6, 100e-6, 1e-3):
        for bias in ("ideal_ext", "res"):
            cases.append((P100, tr, bias, "fixed", "bleed"))
    for tr in (10e-6, 1e-3):
        cases.append((P100, tr, "res", "divider", "bleed"))
        cases.append((P100, tr, "res", "late", "bleed"))
        cases.append((P100, tr, "res", "fixed", "R16"))
        cases.append((P100, tr, "res", "fixed", "nmos_on"))
        cases.append((P1n, tr, "res", "fixed", "bleed"))
    cases.append((P100, 1e-6, "ideal_vin", "fixed", "bleed"))
    for i, (p, tr, bias, vm, ld) in enumerate(cases):
        r = startup(p, tr, bias, vm, ld, "r3su")
        R.append(r); print(r, flush=True)
    json.dump(R, open(f"{RES}/r3_1_startup.json", "w"), indent=1)
