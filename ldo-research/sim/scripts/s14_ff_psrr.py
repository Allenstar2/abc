"""實驗 X6：feedforward ripple 抵消在 200 mV dropout 下的負載敏感度（理想行為級）。
推導 [D]：PSRR_LF = R_o·[gds_p + gm_p(1−α_pg)]/(1+T0)。完全抵消需 α_pg = 1 + gds_p/gm_p。
gds_p/gm_p 在零載 ~0.05、滿載（triode）~0.75 → 需要的過追蹤量隨負載變 15 倍。
做法：在 pg 注入理想 VCCS I = gff·(Vin−1.8)（DC 為 0，只有 AC），掃 gff 與負載，看 PSRR@1 kHz、1 MHz。
這不是電路設計，只是驗證「固定增益的 feedforward 無法跨負載抵消」。"""
import json, numpy as np
import ldo_ref
from ldo_ref import DEFAULT
from common import run, RES, MODEL

p = dict(DEFAULT, CL=100e-12, Cc=5e-12, R1=4e3, R2=4e3)
def psrr_ff(gff, IL, name="x6"):
    sub = ldo_ref.subckt(p).replace(".subckt ldoA vin vout vref fb fbi", ".subckt ldoA vin vout vref fb fbi").rstrip()
    sub = sub[:-len(".ends")] + f"Bff 0 pg I = {gff}*(V(vin)-{p['Vin']})\n.ends\n"
    net = f"* {name}\n.include {MODEL}\n{sub}\nVIN vin 0 DC {p['Vin']} AC 1\nVREF vref 0 0.8\nX1 vin vout vref fb fb ldoA\nCL vout 0 {p['CL']}\nIL vout 0 DC {IL}\n.control\nac dec 20 10 1e9\nwrdata {RES}/{name}.txt v(vout)\nquit\n.endc\n.end\n"
    run(net, name); a = np.loadtxt(f"{RES}/{name}.txt"); f = a[:, 0]; ps = 20 * np.log10(np.hypot(a[:, 1], a[:, 2]))
    return {f"{fx:g}": round(float(np.interp(np.log10(fx), np.log10(f), ps)), 1) for fx in (1e3, 1e5, 1e6, 1e7)}
R = []
for gff in (0, 0.03e-3, 0.06e-3, 0.1e-3, 0.3e-3, 0.6e-3, 1.0e-3):
    row = dict(gff_mS=gff * 1e3)
    for IL in (0, 10e-3, 100e-3):
        row[f"{IL*1e3:g}mA"] = psrr_ff(gff, IL)
    R.append(row); print(row, flush=True)
json.dump(R, open(f"{RES}/x6_ff_psrr.json", "w"), indent=1)
