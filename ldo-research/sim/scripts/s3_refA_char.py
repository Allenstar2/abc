"""REF-A 完整特性：Bode、PSRR、負載暫態(邊沿時間掃描)、線性暫態、Iq、dropout。"""
import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ldo_ref import DEFAULT, loopgain, margins, psrr, load_step, header
from common import run, RES, FIG, load_wrdata

D100 = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
D1n = dict(DEFAULT, CL=1e-9, Cc=20e-12, R1=4e3, R2=4e3)
designs = {"CL=100pF,Cc=5pF": D100, "CL=1nF,Cc=20pF": D1n}
R = {}

# 1) Bode
fig, ax = plt.subplots(2, 2, figsize=(12, 7), sharex=True)
for j, (dn, p) in enumerate(designs.items()):
    R[dn] = {"loop": [], "psrr": {}, "load_tr": [], "line_tr": {}}
    for IL in (0, 1e-3, 50e-3, 100e-3):
        f, T, v = loopgain(p, IL, "c_lg")
        m = margins(f, T); m["IL_mA"] = IL * 1e3; m["vout"] = v["vout_op"]; m["iin_mA"] = v["iin"] * 1e3
        R[dn]["loop"].append(m)
        ax[0, j].semilogx(f, 20*np.log10(abs(T)), label=f"IL={IL*1e3:g} mA (PM={m['pm']:.0f}°)")
        ax[1, j].semilogx(f, np.unwrap(np.angle(T))*180/np.pi)
    ax[0, j].set_title(f"REF-A loop gain, {dn}"); ax[0, j].axhline(0, c="k", lw=.5); ax[0, j].legend(fontsize=8)
    ax[0, j].set_ylim(-60, 70); ax[1, j].set_ylim(-270, 10); ax[1, j].axhline(-180, c="k", lw=.5)
    ax[1, j].set_xlabel("f [Hz]"); ax[0, j].set_ylabel("|T| [dB]"); ax[1, j].set_ylabel("∠T [deg]")
    for a in ax[:, j]: a.grid(True, which="both", alpha=.3)
plt.tight_layout(); plt.savefig(f"{FIG}/s3_refA_bode.png", dpi=110); plt.close()

# 2) PSRR
fig, ax = plt.subplots(figsize=(7, 4))
for dn, p in designs.items():
    for IL in (0, 10e-3, 100e-3):
        f, ps = psrr(p, IL, "c_psr")
        R[dn]["psrr"][f"{IL*1e3:g}mA"] = {f"{fx:g}Hz": round(float(np.interp(np.log10(fx), np.log10(f), ps)), 1)
                                        for fx in (1e3, 1e5, 1e6, 1e7, 1e8)}
        ax.semilogx(f, ps, label=f"{dn}, {IL*1e3:g} mA")
ax.set_xlabel("f [Hz]"); ax.set_ylabel("Vout/Vin [dB] (PSRR)"); ax.grid(True, which="both", alpha=.3); ax.legend(fontsize=7)
ax.set_title("REF-A PSRR (理想 Vref 與偏壓源；未含 bandgap 的 PSR)".encode("ascii", "ignore").decode() or "REF-A PSRR")
plt.tight_layout(); plt.savefig(f"{FIG}/s3_refA_psrr.png", dpi=110); plt.close()

# 3) 負載暫態：Imin(分壓器 200 µA 已在內部) 0 → 100 mA，邊沿 1 ns / 100 ns / 1 µs
fig, ax = plt.subplots(2, 3, figsize=(15, 7))
for j, tedge in enumerate((1e-9, 100e-9, 1e-6)):
    for dn, p in designs.items():
        t, vo, vpg, m = load_step(p, 0, 100e-3, tedge, "c_ltr", thold=10e-6)
        m.update(tedge_ns=tedge*1e9, design=dn, dI_mA=100)
        R[dn]["load_tr"].append(m)
        sel = (t > 1.8e-6) & (t < 2e-6 + tedge + 6e-6)
        ax[0, j].plot((t[sel]-2e-6)*1e6, vo[sel], label=f"{dn}: ΔV-={m['undershoot']*1e3:.0f} mV")
        sel2 = (t > 12e-6 + tedge - 0.2e-6) & (t < 12e-6 + 2*tedge + 6e-6)
        ax[1, j].plot((t[sel2]-(12e-6+tedge))*1e6, vo[sel2], label=f"{dn}: ΔV+={m['overshoot']*1e3:.0f} mV")
    ax[0, j].set_title(f"0→100 mA, edge {tedge*1e9:g} ns"); ax[1, j].set_title(f"100→0 mA, edge {tedge*1e9:g} ns")
    for a in ax[:, j]: a.grid(True, alpha=.3); a.legend(fontsize=7); a.set_xlabel("t [µs]"); a.set_ylabel("Vout [V]")
plt.tight_layout(); plt.savefig(f"{FIG}/s3_refA_load_tr.png", dpi=110); plt.close()

# 4) 線性暫態：Vin 1.8 → 1.98 → 1.8 V（1 µs 邊沿），IL = 50 mA
for dn, p in designs.items():
    net = header(p, "line") + f"""
VIN vin 0 PWL(0 1.8 5u 1.8 6u 1.98 26u 1.98 27u 1.8)
VREF vref 0 0.8
X1 vin vout vref fb fb ldoA
CL vout 0 {p['CL']}
IL vout 0 DC 50m
.control
tran 2n 50u 0 10n
wrdata {RES}/c_line_tr.txt v(vout)
quit
.endc
.end
"""
    run(net, "c_line")
    t, (vo,) = load_wrdata(f"{RES}/c_line_tr.txt")
    base = vo[(t > 4e-6) & (t < 5e-6)].mean(); hi = vo[(t > 24e-6) & (t < 26e-6)].mean()
    R[dn]["line_tr"] = dict(up_peak_mV=float((vo[(t > 5e-6) & (t < 26e-6)].max() - base) * 1e3),
                            down_peak_mV=float((hi - vo[(t > 26e-6)].min()) * 1e3),
                            line_reg_mV_per_V=float((hi - base) / 0.18 * 1e3))

# 5) Iq 與 6) dropout（DC 掃 Vin，IL = 100 mA 與 0）
for dn, p in list(designs.items())[:1]:
    net = header(p, "dc") + f"""
VIN vin 0 1.8
VREF vref 0 0.8
X1 vin vout vref fb fb ldoA
IL vout 0 DC 0
.control
op
let iq_total = -i(vin)
print iq_total
dc VIN 1.4 1.98 0.002
wrdata {RES}/c_dc_noload.txt v(vout)
alter IL dc = 0.1
dc VIN 1.4 1.98 0.002
wrdata {RES}/c_dc_fullload.txt v(vout) v(x1.pg) v(x1.ea)
alter IL dc = 0.05
dc VIN 1.4 1.98 0.002
wrdata {RES}/c_dc_halfload.txt v(vout)
quit
.endc
.end
"""
    out = run(net, "c_dc")
    iq = float([l for l in out.splitlines() if l.strip().startswith("iq_total")][0].split("=")[1])
    vin, (vo0,) = load_wrdata(f"{RES}/c_dc_noload.txt")
    vin, (vo1, vpg, vea) = load_wrdata(f"{RES}/c_dc_fullload.txt")
    vin, (vo5,) = load_wrdata(f"{RES}/c_dc_halfload.txt")
    vnom = np.interp(1.8, vin, vo1)
    def dropout(vo):
        vreg = np.interp(1.98, vin, vo)
        i = np.where(vo >= 0.99 * vreg)[0][0]
        return float(vin[i] - vo[i]), float(vin[i])
    R["dc"] = dict(Iq_total_uA=iq*1e6, Iq_breakdown="分壓 200 µA + EA tail 20 µA + buffer ~40–50 µA + 偏壓 2×10 µA",
                   vout_noload_1p8=float(np.interp(1.8, vin, vo0)), vout_fullload_1p8=float(vnom),
                   load_reg_mV=float((np.interp(1.8, vin, vo0) - vnom) * 1e3),
                   dropout_full_V=dropout(vo1), dropout_half_V=dropout(vo5),
                   vpg_full_at_vin1p8=float(np.interp(1.8, vin, vpg)))
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(vin, vo0, label="IL=0"); ax.plot(vin, vo5, label="IL=50 mA"); ax.plot(vin, vo1, label="IL=100 mA")
    ax.plot(vin, vpg, "--", label="pass gate @100 mA")
    ax.axvline(1.8, c="k", lw=.5); ax.set_xlabel("Vin [V]"); ax.set_ylabel("V"); ax.grid(True, alpha=.3); ax.legend()
    ax.set_title("REF-A DC: Vout vs Vin (dropout)"); plt.tight_layout(); plt.savefig(f"{FIG}/s3_refA_dc.png", dpi=110); plt.close()

json.dump(R, open(f"{RES}/s3_refA_char.json", "w"), indent=1, default=float, ensure_ascii=False)
print(json.dumps(R, indent=1, default=lambda x: round(float(x), 4), ensure_ascii=False))
