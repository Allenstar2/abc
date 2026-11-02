"""第 3 輪 (c)：類比主導 hybrid LDO（B）＋非同步 droop 快速加片路徑的行為級模型（獨立撰寫，不 import 任何 repo/前審查者模組）。

連續部分（向量化，可一次模擬 P 組參數）：
  - Vout 節點：CL、分壓器 R_div、負載 I_L(t)、類比 pass 電流 I_a(pg, Vout)、slice 電流 Σ s_k·I_s(Vout)
  - EA：transconductor gm1·β·(Vout−Vnom)，輸出電流飽和 ±I_tail（slew），輸出阻抗 R_o（DC 增益 A1），
        Miller Cc 由 Vout 接到 EA 輸出 e（e 以「pg 等效電壓」表示），e 被夾在 [e_min, e_max]（e_max>pg_max 代表 windup 深度）
  - buffer：pg 追 min(e, pg_max)，上拉時間常數 tau_b 且 slew 受限（PMOS SF 的電流源 I_buf/C_pg），下拉 tau_dn（SF 主動下拉，快）
  - 類比 pass：EKV 型平滑 PMOS 模型（飽和/三極管/次臨界連續），K、Vt 依「pg 窗口 3–18 mA」校正
  - slice：閘極接地的 PMOS 開關＝三極管電導，I_s(V)=G_s·Vsd·(1−Vsd/(2·Vov_s))；開/關以 t_on/t_off 線性斜坡
離散部分：
  - 同步迴路：時脈 fclk，每個邊沿看 pg 窗口比較器：pg<VL → code+1；pg>VH → code−1；可加 d 級同步延遲與 ÷div 更新
  - 非同步 droop：Vout < V_dr（遲滯 V_hys：Vout > V_dr+V_hys 才解除）、可選 AND pg<V_gate，傳輸延遲 t_dr；
    觸發期間 ripple-set 鏈每 tau_ch 加一片（DFF 非同步 set），droop 期間同步減片被 set 擋住
  - 可選對策：blanking（droop 解除後 T_blank 內停用 droop 路徑）、每次事件最多加 k_max 片、
    anti-windup（e_max 設在 pg_max 附近）、減片間隔（div）
數值：線性隱式 Euler（Vout 節點的電導項隱式處理），dt 預設 0.1 ns。
"""
import numpy as np

UT = 0.0259; NSLOPE = 1.3


def F(x):
    return np.logaddexp(0.0, x / 2.0) ** 2


def ia_pmos(pg, V, Vin, K, Vt):
    """EKV 型 PMOS 汲極電流（source=Vin、gate=pg、drain=V）。強反轉飽和時 → K·(Vsg−Vt)^2。"""
    vov = Vin - pg - Vt
    vsd = np.maximum(Vin - V, 0.0)
    a = 2 * NSLOPE * UT
    return K * a * a * (F(vov / (NSLOPE * UT)) - F((vov - NSLOPE * vsd) / (NSLOPE * UT)))


def calibrate(Vin=1.8, Vnom=1.6, I_lo=3e-3, I_hi=18e-3, pg_lo=1.455, pg_hi=1.335):
    """解 K、Vt 使 Vsd=0.2 V 時 I(pg_lo)=I_lo、I(pg_hi)=I_hi（對應 repo 公平 B 的窗口 3–18 mA、VL/VH）。"""
    from scipy.optimize import fsolve
    def eq(x):
        K, Vt = x
        return [ia_pmos(pg_lo, Vnom, Vin, K, Vt) / I_lo - 1, ia_pmos(pg_hi, Vnom, Vin, K, Vt) / I_hi - 1]
    K, Vt = fsolve(eq, [0.4, 0.27])
    return float(K), float(Vt)


def pg_for_current(I, V, Vin, K, Vt):
    from scipy.optimize import brentq
    return brentq(lambda pg: ia_pmos(pg, V, Vin, K, Vt) - I, 0.0, Vin)


DEF = dict(
    Vin=1.8, Vnom=1.6, CL=100e-12, Rdiv=8e3,
    # EA / 補償
    gm1=0.16e-3, beta=0.5, I_tail=20e-6, A1=100.0, Cc=5e-12, Ce=0.2e-12, e_bal=1.2,
    e_min=0.9, e_max=2.2,            # e 以 pg 等效電壓表示；e_max − pg_max = windup 深度（EA 輸出可越過 pg 的上限）
    pg_max=1.76, tau_b=4e-9, tau_dn=1e-9, sr_up=12.5e6, sr_dn=1e9,   # buffer：上拉受 50 µA/4 pF ≈ 12.5 V/µs 限制；SF 下拉快
    # 類比 pass（K、Vt 由 calibrate() 填）
    K=None, Vt=None,
    # slices
    N=8, Is_nom=12.2e-3, Vov_s=1.38, t_on=1e-9, t_off=1e-9,
    # 同步迴路
    fclk=10e6, VL=1.335, VH=1.455, d_sync=0, div=1,
    # droop 路徑
    droop=0, V_dr=1.57, V_hys=0.0, t_dr=3e-9, tau_ch=2e-9, V_gate=9.9, T_blank=0.0, k_max=99, T_brm=0.0, t_sync0=0.0,
)


def sim(par_list, tb, Ib, T, dt=0.1e-9, rec_every=10, ic_code=None):
    """par_list: P 個參數 dict；tb (K,) 負載轉折時間；Ib (P,K) 負載值。回傳 dict（t、V、pg、code 的抽樣軌跡）。"""
    P = len(par_list)
    g = lambda k: np.array([p[k] for p in par_list], dtype=float)
    Vin, Vnom, CL, Rdiv = g('Vin'), g('Vnom'), g('CL'), g('Rdiv')
    gm1, beta, Itail, A1, Cc, Ce, ebal = g('gm1'), g('beta'), g('I_tail'), g('A1'), g('Cc'), g('Ce'), g('e_bal')
    Ro = A1 / gm1
    emin, emax, pgmax, taub, taudn, srup, srdn = g('e_min'), g('e_max'), g('pg_max'), g('tau_b'), g('tau_dn'), g('sr_up'), g('sr_dn')
    K, Vt = g('K'), g('Vt')
    N = int(par_list[0]['N'])
    Isn, Vovs, ton, toff = g('Is_nom'), g('Vov_s'), g('t_on'), g('t_off')
    Gs = Isn / ((Vin - Vnom) * (1 - (Vin - Vnom) / (2 * Vovs)))
    fclk, VL, VH = g('fclk'), g('VL'), g('VH')
    dsync = np.array([int(p['d_sync']) for p in par_list]); div = np.array([int(p['div']) for p in par_list])
    droop_en = g('droop') > 0
    Vdr, Vhys, tdr, tauch, Vgate, Tblank, kmax = g('V_dr'), g('V_hys'), g('t_dr'), g('tau_ch'), g('V_gate'), g('T_blank'), g('k_max')
    Tbrm = g('T_brm'); tsync0 = g('t_sync0')
    nd = np.maximum(1, np.round(tdr / dt).astype(int)); Lbuf = int(nd.max()) + 1
    hist = np.zeros((P, Lbuf), dtype=bool)
    # 初始狀態
    V = Vnom.copy(); IL0 = Ib[:, 0]
    code = np.zeros(P, dtype=int) if ic_code is None else np.array(ic_code, dtype=int)
    s = (np.arange(N)[None, :] < code[:, None]).astype(float)
    Ineed = IL0 + Vnom / Rdiv - (s.sum(1) * Isn)
    pg = np.array([pg_for_current(max(i, 1e-6), Vnom[j], Vin[j], K[j], Vt[j]) for j, i in enumerate(Ineed)])
    e = pg.copy()
    droop_raw = np.zeros(P, bool); droop = np.zeros(P, bool)
    chain_t = np.zeros(P); nadd = np.zeros(P); blank_until = np.full(P, -1.0)
    Tclk = 1 / fclk; next_edge = Tclk.copy(); edge_cnt = np.zeros(P, dtype=int)
    qhist = np.zeros((P, 8), dtype=int)   # 同步器：過去的決策（+1/−1/0）
    nsteps = int(round(T / dt)); nrec = nsteps // rec_every + 1
    tr_t = np.zeros(nrec); tr_V = np.zeros((nrec, P), np.float32); tr_pg = np.zeros((nrec, P), np.float32)
    tr_code = np.zeros((nrec, P), np.int8); tr_dr = np.zeros((nrec, P), bool)
    ridx = 0; hp = 0
    M11 = Ce + Cc; M12 = -Cc; M21 = -Cc; M22 = CL + Cc
    tb = np.asarray(tb); kseg = 0
    for n in range(nsteps):
        t = n * dt
        # 負載（分段線性）
        while kseg < len(tb) - 2 and t >= tb[kseg + 1]:
            kseg += 1
        fr = min(max((t - tb[kseg]) / (tb[kseg + 1] - tb[kseg]), 0.0), 1.0)
        IL = Ib[:, kseg] + fr * (Ib[:, kseg + 1] - Ib[:, kseg])
        # ---- 連續部分 ----
        vsd = Vin - V
        Isl_unit = Gs * vsd * (1 - vsd / (2 * Vovs)); dIsl_dV = -Gs * (1 - vsd / Vovs)
        ssum = s.sum(1)
        Ia = ia_pmos(pg, V, Vin, K, Vt)
        dIa_dV = (ia_pmos(pg, V + 1e-4, Vin, K, Vt) - Ia) / 1e-4
        A = Itail * np.tanh(gm1 * beta * (V - Vnom) / Itail) - (e - ebal) / Ro
        dA_dV = gm1 * beta / np.cosh(gm1 * beta * (V - Vnom) / Itail) ** 2
        B = Ia + ssum * Isl_unit - IL - V / Rdiv
        dB_dV = dIa_dV + ssum * dIsl_dV - 1 / Rdiv
        # e 在夾限且仍往外推時，視為固定（EA 飽和）
        a11 = M11.copy(); a12 = M12 - dt * dA_dV; a21 = M21.copy(); a22 = M22 - dt * dB_dV
        r1 = dt * A; r2 = dt * B
        det = a11 * a22 - a12 * a21
        de = (r1 * a22 - a12 * r2) / det; dV = (a11 * r2 - a21 * r1) / det
        clamp = ((e + de > emax) & (de > 0)) | ((e + de < emin) & (de < 0))
        if clamp.any():
            de = np.where(clamp, np.clip(e + de, emin, emax) - e, de)
            dV = np.where(clamp, (r2 - a21 * de) / a22, dV)
        e = e + de; V = V + dV
        # buffer
        tgt = np.minimum(e, pgmax)
        dpg = (tgt - pg) / np.where(tgt > pg, taub, taudn) * dt
        dpg = np.clip(dpg, -srdn * dt, srup * dt)
        pg = pg + dpg
        # ---- droop 比較器（遲滯＋傳輸延遲）----
        assert_c = (V < Vdr) & (pg < Vgate)
        release_c = (V > Vdr + Vhys) | (pg >= Vgate)
        droop_raw = np.where(assert_c, True, np.where(release_c, False, droop_raw))
        hist[:, hp] = droop_raw & droop_en & (t >= blank_until)
        prev = droop
        droop = hist[np.arange(P), (hp - nd) % Lbuf]
        hp = (hp + 1) % Lbuf
        fell = prev & ~droop
        if Tblank.max() > 0:
            blank_until = np.where(fell & (Tblank > 0), t + Tblank, blank_until)
            droop = droop & (t >= blank_until) | (droop & prev)   # 進行中的事件不被自己的 blanking 切斷
        rose = droop & ~prev
        nadd = np.where(rose, 0, nadd)
        chain_t = np.where(droop, chain_t + dt, 0.0)
        add = droop & (chain_t >= tauch) & (code < N) & (nadd < kmax)
        code = code + add; nadd = nadd + add; chain_t = np.where(add, 0.0, chain_t)
        # ---- 同步時脈邊沿 ----
        edge = t >= next_edge
        if edge.any():
            dec = np.where(pg < VL, 1, np.where(pg > VH, -1, 0))
            qhist = np.where(edge[:, None], np.roll(qhist, 1, axis=1), qhist)
            qhist[:, 0] = np.where(edge, dec, qhist[:, 0])
            use = qhist[np.arange(P), dsync]
            edge_cnt = edge_cnt + edge
            upd = edge & (edge_cnt % div == 0) & (t >= tsync0)
            inc = upd & (use > 0) & (code < N)
            decm = upd & (use < 0) & (code > 0) & ~droop      # droop 期間 set 擋住清除
            code = code + inc - decm
            # 選項：同步減片後 T_brm 內停用 droop 路徑（只遮蔽「自己造成的」下陷）
            blank_until = np.where(decm & (Tbrm > 0), np.maximum(blank_until, t + Tbrm), blank_until)
            next_edge = np.where(edge, next_edge + Tclk, next_edge)
        # ---- slice 閘極斜坡 ----
        target = (np.arange(N)[None, :] < code[:, None])
        s = np.where(target, np.minimum(s + dt / ton[:, None], 1.0), np.maximum(s - dt / toff[:, None], 0.0))
        if n % rec_every == 0:
            tr_t[ridx] = t; tr_V[ridx] = V; tr_pg[ridx] = pg; tr_code[ridx] = code; tr_dr[ridx] = droop; ridx += 1
    return dict(t=tr_t[:ridx], V=tr_V[:ridx], pg=tr_pg[:ridx], code=tr_code[:ridx], droop=tr_dr[:ridx])


def window_metrics(res, t0, t1, Vref):
    m = (res['t'] >= t0) & (res['t'] < t1)
    V = res['V'][m]; c = res['code'][m]; dr = res['droop'][m]
    pp = (V.max(0) - V.min(0)) * 1e3
    mean = (V.mean(0) - Vref) * 1e3
    nchg = (np.abs(np.diff(c.astype(int), axis=0)) > 0).sum(0)
    ndr = (np.diff(dr.astype(int), axis=0) > 0).sum(0)
    return pp, mean, nchg, ndr


def loopgain_lin(p, Ia, Gsl, f):
    """小訊號迴路增益（EA 輸入處斷開）：狀態 e、V、pg（buffer 一階）。回傳 T(jω)。"""
    K, Vt, Vin, Vnom = p['K'], p['Vt'], p['Vin'], p['Vnom']
    pg = pg_for_current(Ia, Vnom, Vin, K, Vt)
    gma = -(ia_pmos(pg + 1e-5, Vnom, Vin, K, Vt) - ia_pmos(pg - 1e-5, Vnom, Vin, K, Vt)) / 2e-5
    gdsa = (ia_pmos(pg, Vnom - 1e-5, Vin, K, Vt) - ia_pmos(pg, Vnom + 1e-5, Vin, K, Vt)) / 2e-5
    Go = gdsa + Gsl + 1 / p['Rdiv']
    Ro = p['A1'] / p['gm1']
    T = []
    for fr in f:
        s = 2j * np.pi * fr
        Hb = 1 / (1 + s * p['tau_b'])
        # [s(Ce+Cc)+1/Ro, -sCc; -sCc + gma*Hb, s(CL+Cc)+Go] [e;V] = [gm1*beta*u; 0]
        M = np.array([[s * (p['Ce'] + p['Cc']) + 1 / Ro, -s * p['Cc']], [-s * p['Cc'] + gma * Hb, s * (p['CL'] + p['Cc']) + Go]])
        e_, V_ = np.linalg.solve(M, np.array([p['gm1'] * p['beta'], 0.0]))
        T.append(-V_)   # u 增加 → e 增加 → I_a 減少 → V 減少；負回授時 T = -V/u 的 DC 值為正
    T = np.array(T)
    return T, gma
