"""Reviewer's own DC small-signal nodal model built from ngspice OP gm/gds/gmbs.
Computes T0 (return ratio at M1 gate), open-loop supply gain A_os, closed-loop PSRR,
and compares with claim-2 formula gds_p*R_o/(1+T0)."""
import json, numpy as np
r = json.load(open("lg_results.json"))
R1 = R2 = 4e3
NODES = ["bn", "tail", "d1", "ea", "bp", "pg", "vout", "fb"]
# (name, d, g, s, b)
TOPO = [("mbn","bn","bn","0","0"), ("mt","tail","bn","0","0"), ("m1","d1","G1","tail","0"),
        ("m2","ea","vref","tail","0"), ("m3","d1","d1","vin","vin"), ("m4","ea","d1","vin","vin"),
        ("mbn2","bp","bn","0","0"), ("mbp","bp","bp","vin","vin"), ("mcs","pg","bp","vin","vin"),
        ("mb","0","ea","pg","pg"), ("mp","vout","pg","vin","vin")]

def solve(op, vin=0.0, vt=None):
    """vt=None -> closed loop (M1 gate = fb); else M1 gate driven by vt (loop broken)."""
    n = len(NODES); idx = {k: i for i, k in enumerate(NODES)}
    G = np.zeros((n, n)); rhs = np.zeros(n)
    known = {"0": 0.0, "vin": vin, "vref": 0.0}
    def add(node, coef, ctrl):
        # adds coef*V(ctrl) to KCL(node) (currents leaving node)
        if node not in idx: return
        if ctrl in idx: G[idx[node], idx[ctrl]] += coef
        else: rhs[idx[node]] -= coef * known[ctrl]
    def cond(a, b, g):
        add(a, g, a); add(a, -g, b); add(b, g, b); add(b, -g, a)
    for name, d, g, s, b in TOPO:
        gm = op[f"@{name}[gm]"]; gds = op[f"@{name}[gds]"]; gmb = op[f"@{name}[gmbs]"]
        if g == "G1":
            if vt is None: g = "fb"
            else: known["G1"] = vt
        # i_ds = gm(vg-vs) + gds(vd-vs) + gmb(vb-vs) leaves drain, enters source
        for node, sgn in ((d, 1), (s, -1)):
            add(node, sgn*gm, g); add(node, -sgn*gm, s)
            add(node, sgn*gds, d); add(node, -sgn*gds, s)
            add(node, sgn*gmb, b); add(node, -sgn*gmb, s)
    cond("vout", "fb", 1/R1); cond("fb", "0", 1/R2)
    v = np.linalg.solve(G, rhs)
    return {k: v[idx[k]] for k in NODES}

out = {}
for tag in ["IL0", "IL10m", "IL100m"]:
    op = r[tag]["op"]
    T0 = -solve(op, vin=0, vt=1.0)["fb"]
    ol = solve(op, vin=1.0, vt=0.0)
    cl = solve(op, vin=1.0, vt=None)
    gm = {d[0]: op[f"@{d[0]}[gm]"] for d in TOPO}; gds = {d[0]: op[f"@{d[0]}[gds]"] for d in TOPO}
    Go = gds["mp"] + 1/(R1+R2); Ro = 1/Go
    Asf = gm["mb"]/(gm["mb"] + gds["mb"] + gds["mcs"])
    G2 = Asf*gm["mp"]; Gea = gds["m2"] + gds["m4"]
    T0_hand = 0.5*gm["m1"]/Gea*G2/Go
    psrr_claim = gds["mp"]*Ro/(1+T0)
    psrr_cl = cl["vout"]
    A_os = ol["vout"]
    # decomposition of A_os: Ro*[gds_p + gm_p*(1-alpha_pg)]
    A_dec = Ro*(gds["mp"] + gm["mp"]*(1 - ol["pg"]))
    sim = r[tag]
    o = dict(gm_p=gm["mp"], gds_p=gds["mp"], gm1=gm["m1"], gds2=gds["m2"], gds4=gds["m4"], gm_b=gm["mb"], gds_b=gds["mb"], gds_cs=gds["mcs"],
             A_SF=Asf, G2=G2, G_o=Go, gm_p_Ro=gm["mp"]*Ro, gds_p_Ro=gds["mp"]*Ro,
             T0_nodal_dB=20*np.log10(T0), T0_hand_dB=20*np.log10(T0_hand), T0_sim_dB=sim["mb"]["dc"],
             alpha_ea=ol["ea"], alpha_pg=ol["pg"], alpha_ea_sim=sim["aos_1Hz"]["ea"], alpha_pg_sim=sim["aos_1Hz"]["pg"],
             A_os=A_os, A_os_dec=A_dec, A_os_sim=sim["aos_1Hz"]["vout"],
             PSRR_nodal_dB=20*np.log10(abs(psrr_cl)), PSRR_Aos_over_1pT_dB=20*np.log10(abs(A_os)/(1+T0)),
             PSRR_claimformula_dB=20*np.log10(psrr_claim), PSRR_sim_dB=sim["psrr_1Hz_dB"],
             p2_formula_MHz=(G2+Go)/(2*np.pi*100e-12)/1e6)
    out[tag] = o
    print("=====", tag)
    for k, v in o.items(): print(f"  {k:22s} {v:.5g}")
json.dump(out, open("ss_results.json", "w"), indent=1)
