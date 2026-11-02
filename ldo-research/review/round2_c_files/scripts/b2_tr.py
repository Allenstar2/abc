"""Claim B, part 2: 0->100 mA load-step undershoot (1 ns / 100 ns / 1 us edges), nominal + corners."""
import json, numpy as np
from concurrent.futures import ThreadPoolExecutor
from rv import ngspice, refA_core, model, RES
from b1_lg_corners import DESIGNS


def step(design, temp, dn, dp, edge, I1=0.0, I2=0.1, hold=6e-6):
    d = DESIGNS[design]
    t0 = 2e-6; t1 = t0 + edge; t2 = t1 + hold; t3 = t2 + edge; tstop = t3 + 4e-6
    ts = min(edge / 20, 2e-9)
    name = f"b2_{design}_T{temp}_n{dn:+d}_p{dp:+d}_e{edge*1e9:g}"
    net = f"""* {name}
.include {model(dn, dp)}
.options temp={temp} reltol=1e-4 abstol=1e-12 vntol=1e-7
{refA_core(Cc=d['Cc'], Rz=d['Rz'], gate_node='fb')}
VIN vin 0 DC 1.8
VREF vref 0 0.8
CL vout 0 {d['CL']}
IL vout 0 PWL(0 {I1} {t0} {I1} {t1} {I2} {t2} {I2} {t3} {I1})
.control
tran {ts} {tstop} 0 {ts*4}
wrdata {RES}/{name}.txt v(vout)
quit
.endc
.end
"""
    ngspice(net, name)
    a = np.loadtxt(f"{RES}/{name}.txt")
    t, v = a[:, 0], a[:, 1]
    pre = v[(t > t0 - 0.3e-6) & (t < t0)].mean()
    w = (t >= t0) & (t <= t2)
    heavy = v[(t > t2 - 0.3e-6) & (t < t2)].mean()
    post = v[t > t2]
    # settling after the up-step: last time |v - heavy| > 5 mV
    tw, vw = t[w], v[w]
    out = np.where(np.abs(vw - heavy) > 5e-3)[0]
    tset = float(tw[out[-1]] - t0) if len(out) else 0.0
    # count local minima/maxima excursions > 2 mV after the main dip (ringing indicator)
    return dict(design=design, temp=temp, dn=dn, dp=dp, edge_ns=edge * 1e9,
                v_pre=round(float(pre), 5), undershoot_mV=round(float(pre - vw.min()) * 1e3, 1),
                overshoot_mV=round(float(post.max() - heavy) * 1e3, 1) if len(post) else None,
                v_heavy=round(float(heavy), 5), t_settle5mV_us=round(tset * 1e6, 3))


if __name__ == "__main__":
    corners = [(27, 0, 0), (125, 0, 0), (125, 50, 50), (125, -50, 50), (-40, 0, 0), (-40, -50, -50)]
    jobs = [(dz, *c, e) for dz in DESIGNS for c in corners for e in (1e-9, 100e-9, 1e-6)]
    with ThreadPoolExecutor(4) as ex:
        R = list(ex.map(lambda j: step(*j), jobs))
    json.dump(R, open(f"{RES}/b2_tr.json", "w"), indent=0)
    for r in R:
        print(r)
