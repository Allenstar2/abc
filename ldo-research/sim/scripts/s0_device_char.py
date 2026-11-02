"""Stage 0b：PTM 180nm 在 L = 0.18 / 0.5 / 1 µm 的行為。
量測：(1) Vth(L)  (2) gm/Id 對 Id/(W/L)  (3) 在固定 gm/Id 下 gm/gds 對 Vds
     (4) PMOS pass device 在 Vsg=1.8V、Vsd=0.2V 的 Id/W（給 pass device 尺寸用）
"""
import numpy as np, os, json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import run, load_wrdata, MODEL, RES, FIG

Ls = [0.18, 0.5, 1.0]
summary = {}

def char(dev, L):
    W = 10 * L  # W/L = 10
    tag = f"{dev}_L{L}"
    if dev == "n":
        net = f"""* {tag}
.include {MODEL}
VD d 0 0.6
VG g 0 0.6
M1 d g 0 0 NMOS W={W}u L={L}u
.save @m1[id] @m1[gm] @m1[gds] @m1[vth]
.control
dc VG 0.2 1.2 0.005
wrdata {RES}/dc_{tag}_vgs.txt @m1[id] @m1[gm] @m1[gds] @m1[vth]
alter VG 0.6
dc VD 0.05 1.8 0.01 VG 0.5 0.8 0.1
wrdata {RES}/dc_{tag}_vds.txt @m1[id] @m1[gm] @m1[gds]
quit
.endc
.end
"""
    else:
        # PMOS：source 接 1.8V，掃 |Vgs| 與 |Vds|
        net = f"""* {tag}
.include {MODEL}
VS s 0 1.8
VD d 0 1.2
VG g 0 1.2
M1 d g s s PMOS W={W}u L={L}u
.save @m1[id] @m1[gm] @m1[gds] @m1[vth]
.control
dc VG 1.6 0.6 -0.005
wrdata {RES}/dc_{tag}_vgs.txt @m1[id] @m1[gm] @m1[gds] @m1[vth]
alter VG 1.2
dc VD 1.75 0.0 -0.01 VG 1.3 1.0 -0.1
wrdata {RES}/dc_{tag}_vds.txt @m1[id] @m1[gm] @m1[gds]
quit
.endc
.end
"""
    run(net, "s0_char_" + tag)
    return tag

fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
for dev in ("n", "p"):
    for L in Ls:
        tag = char(dev, L)
        x, (idd, gm, gds, vth) = load_wrdata(f"{RES}/dc_{tag}_vgs.txt")
        idd = np.abs(idd)
        vov_axis = (1.8 - x) if dev == "p" else x
        gmid = gm / np.maximum(idd, 1e-15)
        # gm/Id = 10 的點
        i10 = np.argmin(np.abs(gmid - 10))
        gain10 = gm[i10] / gds[i10]
        jd10 = idd[i10] / 10  # Id per (W/L)
        vth_mid = float(np.abs(vth[len(vth)//2]))
        # 輸出曲線：固定 Vgs 中間那條（|Vgs|=0.6+）在 |Vds|=0.3, 0.9 的 gm/gds
        xd, (idd2, gm2, gds2) = load_wrdata(f"{RES}/dc_{tag}_vds.txt")
        summary[tag] = dict(L_um=L, W_um=10*L, vth_V=round(vth_mid, 4),
                            gmid_at_point=round(float(gmid[i10]), 2),
                            Id_over_WL_at_gmid10_uA=round(jd10*1e6, 3),
                            gm_over_gds_at_gmid10_Vds0p6=round(float(gain10), 1))
        lab = f"{dev.upper()}MOS L={L}µm"
        ax[0].semilogx(idd / 10 * 1e6, gmid, label=lab)
        ax[1].plot(vov_axis, gm / gds, label=lab)
for a, t, xl in zip(ax[:2], ["gm/Id vs Id/(W/L)", "gm/gds vs |Vgs| (|Vds|=0.6V)"],
                    ["Id/(W/L) [µA]", "|Vgs| [V]"]):
    a.set_title(t); a.set_xlabel(xl); a.grid(True, which="both", alpha=.3); a.legend(fontsize=7)
ax[0].set_ylabel("gm/Id [1/V]"); ax[1].set_ylabel("gm/gds [V/V]"); ax[1].set_yscale("log")

# 輸出阻抗：PMOS/NMOS 在固定 gm/Id≈10 附近的 gds vs |Vds|
for dev in ("n", "p"):
    for L in Ls:
        tag = f"{dev}_L{L}"
        a = np.loadtxt(f"{RES}/dc_{tag}_vds.txt", ndmin=2)
        # 第二層 sweep 被串接：用 x 的重複切成段
        x = a[:, 0]; gds = a[:, 5]; gm = a[:, 3]
        brk = np.where(np.diff(x) * (1 if dev == "n" else -1) < 0)[0] + 1
        segs = np.split(np.arange(len(x)), brk)
        s = segs[1] if len(segs) > 1 else segs[0]  # |Vgs| = 0.6 (n) / 1.8-1.2=0.6 (p)
        xv = x[s] if dev == "n" else 1.8 - x[s]
        ax[2].semilogy(xv, gm[s] / gds[s], label=f"{dev.upper()} L={L}")
        for vds in (0.2, 0.3, 0.9):
            k = np.argmin(np.abs(xv - vds))
            summary[tag][f"gm_over_gds_Vgs0p6_Vds{vds}"] = round(float(gm[s][k] / gds[s][k]), 1)
ax[2].set_title("gm/gds vs |Vds| (|Vgs|=0.6 V)"); ax[2].set_xlabel("|Vds| [V]"); ax[2].grid(True, alpha=.3); ax[2].legend(fontsize=7)
plt.tight_layout(); plt.savefig(f"{FIG}/s0_device_char.png", dpi=120)

# PMOS pass device：Vsg=1.8（閘極拉到 0），Vsd = 0.2 V，L=0.18 → 每 µm W 的電流
net = f"""* pass device sizing
.include {MODEL}
VS s 0 1.8
VD d 0 1.6
VG g 0 0
M1 d g s s PMOS W=1000u L=0.18u
.control
dc VG 0 1.0 0.01
wrdata {RES}/dc_pass_idvg.txt i(VS)
quit
.endc
.end
"""
run(net, "s0_pass_sizing")
x, (ivs,) = load_wrdata(f"{RES}/dc_pass_idvg.txt")
summary["pass_pmos_W1000u_L0.18_Vsd0.2"] = {f"Vg={v:.1f}V_Id_mA": round(float(-ivs[np.argmin(np.abs(x-v))])*1e3, 2)
                                             for v in (0.0, 0.2, 0.4, 0.6, 0.8)}
with open(f"{RES}/s0_device_char.json", "w") as f:
    json.dump(summary, f, indent=1, ensure_ascii=False)
print(json.dumps(summary, indent=1, ensure_ascii=False))
