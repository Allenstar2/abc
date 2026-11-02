# Stage 4：各架構電路分析

> 證據標註：[D] 我的推導、[X] 本次 ngspice 模擬（PTM 180nm，非真實製程，只看趨勢）、[H] 假設或推測。
> 文獻一律只讀到摘要（D-009），本文件**不**以文獻電路細節為依據。
> 數字對應的腳本與結果檔寫在每段末尾；`sim/run_all.sh` 可全部重跑。

## 0. 本規格共通的物理限制

| 項目 | 推導 | 數字 |
|---|---|---|
| Pass device 在滿載處於 triode | Vin−Vout = 0.2 V，100 mA 時 PMOS Vsg ≈ 0.67 V（W=4 mm），Vov ≈ 0.3 V > Vsd → triode。三極區 gm/gds ≈ Vsd/(Vov−Vsd) | 模擬 gm_p = 347 mS、gds_p = 260 mS，gm_p/gds_p = 1.33 [X] |
| 滿載迴路增益掉 ~20 dB | T0 = β·A_EA·A_SF·gm_p·R_o；滿載 gm_p·R_o 從 13.2 掉到 1.33 | 輕載 53.0 dB → 滿載 33.7 dB [X] |
| W 與 dropout 的取捨 | W 越大 dropout 越小、triode 越淺，但 C_pg 越大（slew 變慢） | W=4 mm：C_gg = 5.5 pF（零外部負載）～7.9 pF（滿載）[X]；Cox·W·L＋2·Cov·W 估計 8.1 pF [D] |
| Vin 來源 | 若 Vin 是 1.8 V ±10% 的外部電源，Vin=1.62 V 時 100 mA 已在 dropout（REF-A 在 100 mA 的 dropout 為 94 mV，即 Vin≈1.674 V 開始掉）[X] | 要問教授 Vin 從哪來 |
| on-chip 1 nF 的面積 | MOS 電容 C/A ≈ Cox ≈ 8.2 fF/µm² → 0.12 mm²；MIM 若 1–2 fF/µm²（PDK 未知 [H]）→ 0.5–1 mm² | 1 nF 很可能是整顆學生晶片面積的大部分 [H] |
| 100 mA 走 bond wire | 1 nH × 100 mA / 1 ns = 100 mV 的 L·di/dt（bond wire 電感 ~1 nH/mm 為常見經驗值 [H]） | 快邊沿負載**必須做在片上**（見 REPORT g 節） |

---

## A. 純類比 LDO

### A1. 兩級 Miller＋source-follower buffer（本次 REF-A）

**原理**：NMOS 輸入 5T OTA（EA）→ PMOS source follower（body 接 source）→ PMOS pass；Cc 從 Vout 回授到 EA 輸出（pole splitting）；β = 0.5；最小負載由分壓器提供 200 µA（D-008）。

**小訊號模型**（三個節點：EA 輸出 ea、pass 閘極 pg、輸出 vout）[D]：

```
G_ea = gds2 + gds4          (EA 輸出電導)        C1 = ea 節點寄生 (~50 fF)
A_SF = gm_b /(gm_b + gds_b + gds_cs)            G2 = A_SF · gm_p   (ea→vout 的等效轉導)
G_o  = gds_p + 1/(R1+R2)    (電流源負載時)        CL
T(s) ≈ T0 · (1 − s/z) / [(1 + s/p1)(1 + s/p2)(1 + s/p_b)]
T0   = β · gm1/G_ea · G2/G_o
S    = C1·G_o + CL·G_ea + Cc·(G2 + G_ea + G_o)
p1   = G_ea·G_o / S ,   p2 = S / [C1·CL + Cc·(C1 + CL)] ≈ (G2 + G_o)/CL   (Cc ≫ C1)
GBW  = β·gm1·G2 / S ≈ β·gm1/Cc                    (G2 ≫ G_o，輕～中載)
z    = G2/Cc (RHP) ,    p_b = (gm_b + gds_b + gds_cs)/C_pg
```

**手算 vs 模擬**（`sim/scripts/s2_hand_vs_sim.py`，參數取自 ngspice OP，C_pg 以 AC 量測）：

| 設計 | 負載 | T0 手算/模擬 (dB) | UGF 手算/模擬 (MHz) | PM 手算/模擬 (°) | p2 (MHz) | p_b (MHz) | 誤差 |
|---|---|---|---|---|---|---|---|
| CL=100 pF, Cc=5 pF | 0 | 53.2 / 53.0 | 2.50 / 2.45 | 66.4 / 66.4 | 7.8 | 29.0 | T0 +2.2%、UGF +2.3%、PM +0.1% |
| 同上 | 10 mA | 53.9 / 53.8 | 2.66 / 2.62 | 82.3 / 86.3 | 270 | 20.9 | PM −4.7% |
| 同上 | 100 mA | 33.7 / 33.7 | 1.61 / 1.60 | 86.6 / 87.9 | 939 | 20.5 | PM −1.4% |
| CL=1 nF, Cc=20 pF | 0 | 53.2 / 53.0 | 0.54 / 0.53 | 54.2 / 54.7 | 0.80 | 29.0 | ≤2.3% |
| 原始（Imin=50 µA, Cc=3 pF, 100 pF）| 0 | 52.6 / 52.3 | 2.54 / 2.42 | 30.8 / 28.1 | 1.98 | 29.6 | UGF +5.0%、PM +9.5% |

全部 < 30%，不需追查。PM 在中載手算偏低 4–8%：手算把 pass 的 Cgd 前饋路徑忽略了（Cgd 從 pg 直接耦合到 vout，產生 LHP 零點附近的相位補償）[D，未另外驗證]。

**主導限制：最輕載的 p2**。弱反轉時 gm_p ≈ I_min/(n·U_T)，所以 p2 ≈ I_min /(n·U_T·CL) [D]。PM ≥ 60° 需要 p2 ≳ 2.2·GBW：

```
Cc ≳ 2.2 · β · gm1 · n·U_T · CL / I_min        [D]
```

CL 加大 10 倍，Cc 也要大 10 倍（或 I_min 大 10 倍）。掃描結果（`s1_refA_sweep.py`，126 組）[X]：
- CL=100 pF、I_min=50 µA：Cc=3 pF 時 PM 只有 28°；要 Cc≈10 pF 才 52°。
- CL=1 nF、I_min=50 µA：Cc 一路加到 40 pF，PM 仍 ≤ 41°。
- 最後選 I_min=200 µA：100 pF/Cc=5 pF → 最差 66°；1 nF/Cc=20 pF → 最差 55°。代價是 Iq 從 131 µA 變 287 µA [X]。

**大訊號暫態**（`s3_refA_char.py`、`s4_exp_edge.py`）：
- 快邊沿時，Vout 以 ΔI/CL 下滑：100 pF、100 mA → 1 V/ns [D]。任何迴路都來不及，只能靠兩條「天然」快速耦合：Cc 把 Vout 的下降耦合到 ea（耦合比 ≈ Cc/(Cc+C1) ≈ 1），SF 的 PMOS 就強力把 pg 拉低；pass 本身的 Cgd 也直接把 pg 往下帶 [D]。
- 結果：0→100 mA、1 ns 邊沿 undershoot 742 mV（100 pF）、497 mV（1 nF）[X]。
- ~~慢邊沿反而 1 nF 比較差~~ **（第 1 輪審查推翻，見下方附錄與 REVIEW_LOG）**：純 Miller（無 Rz）時 100 ns 邊沿 236 mV（100 pF）vs 345 mV（1 nF）[X]，因為 1 nF 要 Cc=20 pF 才穩定、UGF 掉到 ~0.5 MHz。但加 nulling resistor（Cc=8 pF、Rz=10 kΩ）後，1 nF 最差 PM 62°，undershoot 431/185/80 mV（1 ns/100 ns/1 µs），**全面優於** 100 pF 的 REF-A（742/236/111 mV）[X，作者重現審查者結果]。
- **起點電流很重要**：1 µs 邊沿、CL=100 pF，起點 0/1/10 mA → 111/52/21 mV [X]。輕載時 gm_p 小、pg 接近關斷，迴路既慢又要大幅擺動。
- **Overshoot 被 Vin 夾住**：卸載時 pass 仍送 100 mA，Vout 以 1 V/ns 衝到 Vin（206 mV＝1.8−1.594）[X]。PMOS pass 不能吸電流，Vout 只能靠洩放電流放電：t ≈ CL·ΔV/I_bleed = 1 nF×0.2 V/200 µA = 1 µs [D]，與 1 nF 波形回到 ±1% 需 2.2 µs 一致（100 pF 只需 0.32 µs；`s11_misc_checks.py`）[X]。pg 往上拉只靠 SF 的 50 µA 電流源：50 µA / 7.9 pF ≈ 6.3 V/µs，擺 0.47 V（1.128→1.595 V）需 ~74 ns [D]。

**PSRR**（推導 [D]，對照 [X]）：EA 的 PMOS mirror 與 SF 的電流源都接 Vin，使 pg 大致跟著 Vin 走（a_pg ≈ 1），Vin 的漣波主要經 gds_p 注入：

```
PSRR_LF ≈ gds_p · R_o / (1 + T0)                       （近似：假設 pg 完全跟隨 Vin）
PSRR_LF = R_o · [gds_p + gm_p·(1 − α_pg)] / (1 + T0)   （精確：α_pg = v_pg/v_in）
```
第 1 輪審查 (c) 以小訊號矩陣算出 α_pg = 0.948–0.994（buffer 的 drain 接地使 pg 不完全跟隨 Vin），近似式因此偏樂觀：滿載 0.6 dB、零載 1.0 dB、10 mA 時 2.2 dB [X，審查者]。
- 100 mA：R_o ≈ 1/gds_p → PSRR ≈ −T0 = −33.7 dB；模擬 −33.3 dB [X]。
- 0 mA：gds_p·R_o = 0.253/(0.253+0.125) = 0.67 → −3.5 − 53.2 = −56.7 dB；模擬 −55.3 dB [X]。
- 中頻 |T| 下降，PSRR 在 UGF 附近（1.6–2.5 MHz）升到 −5.3～−8.7 dB @1 MHz（100 mA / 10 mA）[X]。
- 高頻要靠 CL 分流：PSRR ≈ gds_p/(ωCL)，滿載 gds_p=0.26 S、CL=100 pF → 轉折在 414 MHz [D]；模擬 100 MHz 仍 +0.1 dB [X]。
- 結論：**本規格的中高頻 PSR 天生差**（pass 在 triode、gds 大、CL 小）。若教授要求 1–10 MHz PSR，需 A5 類 feedforward 抵消（A01 Park 2014 的方向）[D]。

**失效情境（具體）**：
1. **高溫輕載失去調節**：「SF-like」（Vthn+50 mV、|Vthp|−50 mV）125 °C 時，零外部負載 Vout = 1.6525 V（+46 mV）[X]。此時 pg 已被拉到 1.759 V（離 Vin 只差 41 mV）、EA 輸出 1.643 V 已接近上限，但 4 mm 的 pass 在 Vsg≈41 mV 仍漏出約 0.2 mA，超過 200 µA 洩放電流 [X]（`s6_corners.py` 同條件重跑 OP）。FF-like 125 °C 也有 +20 mV。修法：加大洩放（Iq↑）、改 buffer 讓 pg 能到 Vin、或 pass 用較長 L（犧牲面積）[D]。
2. **為了省 Iq 把洩放降到 50 µA**：CL=100 pF 時 PM 28°，CL=1 nF 時 PM ≤ 41° [X]。
3. **1 ns 邊沿 100 mA 步階**：Vout 掉到 ~0.86 V（742 mV）[X]，對任何數位負載都是失效。

### A2. FVF（flipped voltage follower）型 —— **只推導，未模擬**

**原理**：PMOS common-gate 電晶體 Mc 的 source 接 Vout、gate 接偏壓 V_set、drain（節點 X）接電流源 I_b 並驅動 pass 閘極。Vout 下降 → Mc 的 Vsg 變小 → 電流減少 → X 被 I_b 拉低 → pass 開大。這是局部 shunt feedback，只有一個高阻抗節點 X [D]。

**小訊號** [D]：
```
T_FVF(0) ≈ gm_c · R_X · gm_p · R_o / (1 + gm_c·R_o) ≈ gm_p · R_X   (gm_c·R_o ≫ 1)
Z_out,cl ≈ 1 / (gm_c · gm_p · R_X)
極點：p_X = 1/(R_X·C_pg)（C_pg 5–8 pF，R_X = ro_c‖ro_b 數百 kΩ → ~100 kHz 級）, p_o ≈ gm_c/CL（輸出看進 Mc source 是 1/gm_c）
```
**主導限制**：DC 精度。Vout = V_set + V_SG,c(I_c, T, 製程)，沒有和 Vref 比較，**一定要再加一個慢的 EA 迴路**校正 V_set → 變成 A6 類比雙迴路 [D]。第二個限制是 X 節點掛著整個 C_pg，slew = I_b/C_pg：50 µA/8 pF = 6.3 V/µs [D]，所以實際 FVF LDO 都要再加 SRE 或 buffer。
**Headroom**：Vout=1.6 V 時 V_set ≈ 1.6 − 0.5 ≈ 1.1 V，可行 [D]。
**失效情境**：輕載時 p_o（gm_c/CL）與 p_X 都在低頻 → 兩個低頻極點 → 振盪；若把 V_set 交給一個頻寬接近 FVF 迴路的 EA，兩迴路互搶 [D]。

### A3. 暫態增強路徑（電容耦合 SRE、adaptive/dynamic bias、super source follower）—— **只推導**

**原理** [D]：在小訊號迴路之外，加一條只在大擾動時導通的路徑。例：Vout 經電容 C_f 耦合到一顆平時接近截止的電晶體閘極，Vout 快速下降時它導通、把 pg 灌電流/抽電流（class-AB 行為），靜態不耗電。
**需要的量** [D]：把 pg 在 t_r 內移動 ΔV_g，要 I_drive = C_pg·ΔV_g/t_r。REF-A：C_pg≈8 pF、ΔV_g≈0.47 V（1.595→1.128 V）[X]，要 t_r=5 ns 就需要 ~0.75 mA 的瞬時電流——比 SF 偏壓 50 µA 大約 15 倍。
**小訊號影響** [D]：若 booster 偏在弱反轉，它是一條並聯的 high-pass 前饋路徑，會在迴路增益加入一對零極點；若 booster 在 UGF 附近有增益，可能形成局部正回授。設計原則：耦合路徑的轉折頻率要高於主迴路 UGF 至少數倍，或 booster 完全不導通（dead zone）。
**失效情境**：Vin 漣波經 pass Cgd 耦合到 Vout 再經 C_f 觸發 booster → 在某些頻率 PSRR 變差或誤觸發；dead zone 太大時小步階完全沒改善 [D/H]。
**Adaptive bias**：EA tail ∝ 負載電流，讓 gm1 跟著 gm_p 走，GBW/p2 比值大致固定，可降低輕載 Iq；但 adaptive 迴路本身是正回授（負載↑→偏壓↑→gm↑），要確認不鎖死 [D]。

### A6. 類比雙迴路（快迴路＋慢迴路都是類比）—— 推導

**交互作用** [D]：慢迴路（高增益 EA）校正快迴路（FVF、voltage damper 等）的 DC 誤差。兩迴路頻寬若只差 2–3 倍，閉迴路輸出阻抗會出現**極零點對（doublet）**：快迴路先把 Vout 拉回大部分，剩下的小誤差由慢迴路以自己的時間常數慢慢收斂 → 長尾巴 settling。經驗上兩迴路頻寬要分開 5–10 倍以上 [H]。
（你讀過的 ISCAS 2022「voltage damper＋body feedback loop」從摘要看是這類 [文獻摘要 A02]；但我**沒讀到全文，不推論它的電路細節**。一般而言用 pass device 的 body 當第二個控制端時，要確保 body-source 接面不順偏（body 不能比 source 低超過 ~0.3–0.4 V），否則漏電與 latch-up 風險 [D/H]。）

---

## B. 類比主導雙迴路 hybrid（本次 REF-B）

**原理**：類比迴路（同 REF-A，pass 縮到 800 µm；碼 0 時 Vout 掉 1% 的負載為 33 mA，`s11_misc_checks.py`）永遠負責 Vout；數位迴路只看類比 pass 的閘極 V(pg)：V(pg) < VL（類比快用完）→ 加一片；V(pg) > VH → 減一片。8 片 PMOS slice，每片 W=130 µm，導通（閘極 0 V）時 12.2 mA @Vsd=0.2 V [X/D]。控制器是閘級的雙向 thermometer shift register（XSPICE d_dff＋d_and/d_or/d_nor），時脈 1/10/50 MHz。

**兩迴路交互作用** [D]：從數位迴路看，類比迴路是一個「把 slice 電流變化轉成 pg 電壓變化」的受控體：

```
ΔV_pg ≈ −I_slice / (dI_a/dV_pg)     （類比迴路 settle 之後）
不出現 limit cycle 的必要條件： I_a(VL) − I_a(VH)  >  I_slice  (+ 比較器 offset、溫漂的餘裕)
```
若窗口小於一片電流，就存在某些負載「沒有任何碼能讓類比電流落在窗內」→ 碼在 k 與 k+1 間來回 = limit cycle。

**模擬驗證**（`s5_exp_hybrid.py`，X3a）[X]：
| 窗口（電流） | 時脈 | 20 mA | 45 mA | 70 mA | 95 mA |
|---|---|---|---|---|---|
| 寬 3–18 mA（15 mA > 12.2 mA）| 1/10/50 MHz | 碼 1，穩定 | 碼 3，穩定 | 碼 5，穩定 | 碼 7，穩定 |
| 窄 8–14 mA（6 mA < 12.2 mA）| 1 MHz | **LC：5 次切換/5 µs，Vout p-p 229 mV** | 穩定 | 穩定 | 穩定 |
| 窄 | 10 MHz | **LC：14 次，216 mV** | 穩定 | 穩定 | 穩定 |
| 窄 | 50 MHz | **LC：21 次，191 mV** | 穩定 | 穩定 | 穩定 |

→ 窄窗的 limit cycle **只在某些負載出現**（20 mA 落在兩個碼之間的「洞」），所以量測時只掃幾個負載點可能看不到。時脈越快切換越頻繁。

**切換瞬間（glitch）**（X3e，慢速斜坡 5→95 mA，只有碼變化造成擾動）[X]：
| slice 閘極邊沿 t_drv | 1 ns | 30 ns | 300 ns |
|---|---|---|---|
| 最大正尖峰 | 82.6 mV | 71.4 mV | 34.5 mV |
→ 放慢 slice 開關可以把尖峰減半，但也讓數位迴路對大步階更慢（取捨）。

**大步階**（X3b，5→95 mA，CL=100 pF）[X]：
| 架構 | 1 ns 邊沿 | 100 ns 邊沿 |
|---|---|---|
| REF-A（W=4 mm） | 499 mV | 127 mV |
| REF-B，10 MHz | 756 mV | 313 mV |
| REF-B，50 MHz | 756 mV | 238 mV |
→ **只靠 gate-sensing 的 B 比純類比更差**：類比部分最多供 ~30–35 mA，其餘要等數位一個時脈加一片。要改善就需要非同步 droop detector 或一次開多片——數位部分隨即變複雜。（Leduc 2025 摘要提到 droop detector 讓 undershoot 降 54% [文獻摘要 H01]，方向一致，但細節未讀。）

**PSRR 與迴路增益**（X3c、X3d，碼凍結）[X]：
- slice 導通時是 Vin→Vout 的低阻抗開關（5 片 ≈ 0.3 S 量級 [D]），讓 G_o 變大 → 類比迴路 DC 增益：碼 0 輕載 53.1 dB，碼 3/5/7 只剩 22.8/18.7/16.0 dB；UGF 從 2.4 MHz 掉到 0.4–0.75 MHz。
- 70 mA 時 PSRR @1 kHz：REF-A −38.2 dB，REF-B（碼 5）−18.8 dB，差 19 dB；@100 kHz −25.6 vs −13.3 dB。
- 反過來，數位迴路的積分作用讓類比 pass 永遠回到同一工作點 → 95 mA 時 Vout 1.5975 V（REF-A 1.5936 V），DC load regulation 較好。

**時脈與漣波** [D/H]：本模型的數位是理想的，沒有時脈饋通、沒有電源彈跳。真實電路中：(1) 時脈驅動與 DFF 的電流尖峰會經共用電源/基板耦合到 Vout 與 Vref；(2) 比較器 kickback 會擾動 pg。建議數位與類比分開供電與接地 pad，時脈只在需要時開（gated clock）。

**沒有 Verilog 能不能做？**（[D]，對照閘級 XSPICE）
- 需要：2 個比較器（可用連續比較器＋同步器，不一定要 StrongARM）、8 個 DFF、32 個 2/3 輸入閘＋1 個 NOR、8 個 slice 驅動 inverter、時脈（外部輸入最簡單；片上可用 ring oscillator）、power-on reset。
- 這和你做過的 DFF、除頻器是同一等級，可以手畫或用 PDK 的標準元件庫手拼（需確認平台有無 std cell [H]）。
- XSPICE 模型與閘級實作的差距：d_dff 沒有 setup/hold 違規與 metastability（比較器輸出是非同步訊號，實作時要 2 級 DFF 同步器）。**但同步器會造成決策延遲**：第 1 輪審查 (c) 的行為模型指出延遲 d 個時脈時 limit cycle 分界點從 1 移到 d+1；作者電路級重現（`s13_hybrid_sync.py`，寬窗比值 1.23、31 個負載點）：無同步器 0/31、2 級同步器 **11/31**、2 級同步器＋shift register 用 ÷3 時脈（等效 blanking）0/31 [X]。→ 規則：**有 d 級同步器時，shift register 每 d+1 個時脈才更新一次**（÷(d+1) 計數器，正是你做過的除頻器）；比較器 offset 的影響見下一段「完整條件」；PTM 反相器 FO4 = 54–60 ps [X]，DFF 時脈到輸出約數倍 FO4 [H]，10–50 MHz 時脈沒有時序壓力。

**limit cycle 的完整條件**（第 1 輪審查 (c) 行為模型＋作者電路驗證）：分界點 ≈ 1 ＋ 兩顆比較器 offset 之和（以片電流為單位）＋ 決策延遲 d（若不 blanking）；欠阻尼或比時脈慢的類比響應會再把分界點推高（1.05 到 >3.6，行為模型）[X/D]。

**主導限制**：B 的好處（DC 精度、較小的類比 pass）在 100 mA 規格下不大；壞處（PSRR、glitch、limit cycle 風險、大步階要額外非同步路徑）都會出現在量測上。
**失效情境**：量產或溫度讓比較器 offset 或 I_a(V) 曲線漂移，使窗口縮到小於一片電流 → 特定負載下出現 ~200 mV p-p 的 limit cycle（X3a 窄窗即為示範）[X/D]。

---

## C. 數位主導、類比輔助（預設排除）—— 推導

**原理**：同步比較器＋數位控制器決定導通幾片 slice（主電流），類比迴路只補量化誤差或處理輕載/快速暫態 [文獻摘要 D06、H06]。

**量化漣波估算** [D]：同步 DLDO 在穩態以 limit cycle 在 k、k+1 間跳，一個時脈內 Vout 的變化約
```
ΔV_ripple ≈ (I_u / 2) / (CL · f_clk)
```
- I_u = 12.2 mA（8 片）、CL = 100 pF、f_clk = 10 MHz → 6 V：意即**根本無法調節**，必須靠類比補。
- 要 50 mV 漣波：I_u=1 mA 需 f_clk ≈ 100 MHz；f_clk=10 MHz 需 I_u ≈ 0.1 mA（100 mA 要 1000 片）。
- 0.18 µm（PTM）FO4 ≈ 54–60 ps [X]，比較器＋DFF＋驅動的迴路延遲數百 ps 起跳 [H]，再加上時脈功耗 ∝ f_clk，使「細解析度＋高時脈」都很貴。

**主導限制**：capless（CL ≤ 1 nF）時，量化誤差只能靠類比輔助迴路吸收；但這樣一來類比迴路其實在決定穩態精度，系統就往 B 靠攏。若類比只做暫態，則穩態漣波與 PSR 差（資料集中 8/58 列有 PSRR，Nasir 2015 −5 dB @1 MHz [資料集]）。
**數位實作**：快速暫態演算法（SAR、charge-distribution 逼近，H01/H02 摘要）需要算術或多狀態 FSM，閘級手畫可行性低、驗證困難（沒有 Verilog＋功能模擬）[H]。
**失效情境**：時脈 10 MHz、slice 12 mA、CL 100 pF 時，若類比輔助迴路飽和（例如輕載時類比 pass 關閉），Vout 會以 ±數百 mV 的 limit cycle 振盪 [D]。
**有沒有強力理由選 C？** 在本規格下找不到：Vin=1.8 V 讓類比 EA 有足夠 headroom（DLDO 的原始動機是 0.5 V 以下類比做不起來 [文獻摘要 D01]），Imax 只到 100 mA，教授要偏類比，學生沒有 Verilog。

---

## 總表：主導限制與失效情境

| 架構 | 主導限制 | 具體失效情境 | 證據 |
|---|---|---|---|
| A1 Miller＋buffer | 最輕載 p2 = I_min/(nU_T·CL)；快邊沿下 pg slew | 洩放降到 50 µA → PM 28°（100 pF）；125 °C SF-like 輕載 Vout +46 mV；1 ns 邊沿 742 mV | [X][D] |
| A2 FVF | DC 精度需第二迴路；X 節點掛 C_pg | 輕載兩低頻極點；兩迴路頻寬太近 | [D] |
| A3 SRE/adaptive | 誤觸發、dead zone、局部正回授 | Vin 漣波觸發 booster | [D/H] |
| A6 類比雙迴路 | doublet 長尾 | 頻寬差 < 5× 時 settling 拖長 | [D/H] |
| B（gate-sensing） | 窗口 vs slice 電流；slice 導通時 PSRR、迴路增益掉 | 窗口 < 一片電流 → 特定負載 ~200 mV p-p limit cycle | [X][D] |
| C | 量化漣波 ∝ I_u/(CL·f_clk) | 類比輔助飽和時數百 mV 振盪 | [D] |

## 附：「1 nF 慢邊沿反而較差」是否只是我補償選得不好？——**是。第 1 輪審查推翻**

用更大的洩放（500 µA）讓 1 nF 可以用較小 Cc 再比一次（0→100 mA，undershoot，mV）[X]：

| 設計 | 最差 PM | 1 ns | 100 ns | 1 µs |
|---|---|---|---|---|
| 1 nF，I_min=500 µA，Cc=10 pF | 58.4° | 458 | 261 | 104 |
| 1 nF，I_min=500 µA，Cc=5 pF | 43.3°（不足） | 456 | 213 | 89 |
| 100 pF，I_min=500 µA，Cc=3 pF | 70.4° | 687 | 185 | 72 |
| 100 pF，I_min=200 µA，Cc=5 pF（REF-A） | 66.4° | 742 | 236 | 111 |

我原本只換了洩放電流，結論是「100 ns、1 µs 邊沿仍是 100 pF 較小」。**審查者 (a) 加了 Rz 就推翻了它**；作者重現（`s15_rz_loadreg.py`，存檔 `s15_rz_loadreg.json`）[X]：

| 設計 | 各負載 PM（0/1/10/30/50/100 mA） | 1 ns | 100 ns | 1 µs |
|---|---|---|---|---|
| 1 nF，Cc=8 pF，Rz=10 kΩ | 62.3/107.5/135.5/134.9/130.3/117.8° | 431 | 185 | 80 |
| 100 pF，Cc=3 pF，Rz=5 kΩ | 73.2/101.4/107.2/106.3/104.4/99.7° | 822 | 198 | 83 |
| 100 pF，Cc=5 pF，Rz=0（REF-A） | 66.4/83.0/86.3/86.6/86.8/87.9° | 742 | 236 | 111 |

修正後結論：**各自補償好之後，1 nF 在快邊沿明顯較好、慢邊沿相當**。代價：100 pF 加 Rz 會讓 1 ns 邊沿 undershoot 從 742 變 822 mV（審查者另一組 872 mV）[X]。Rz 的可用範圍窄：審查者掃描（負載 0/0.2/1/10/100 mA）顯示 1 nF、Cc=8 pF 時 Rz=20 kΩ 會讓 **10 mA** 的 PM 掉到 43°、Rz=40 kΩ 掉到 −2°（`review/round1_a_files/res/r4b_rz.json`）——LHP zero 固定，而 p2 隨負載移動，Rz 必須跨負載與 corner 驗證 [X/D]。

## 附：規格敏感度（`s8_sensitivity.py`，0→Imax 步階 undershoot，mV）[X]

| Imax | Wp | CL / Cc | 最差 PM | 滿載 DC 迴路增益 | load reg | Iq | PSRR@1 kHz/1 MHz（滿載） | 1 ns | 100 ns | 1 µs |
|---|---|---|---|---|---|---|---|---|---|---|
| 10 mA | 400 µm | 100 pF / 5 pF | 69.7° | 33.4 dB | 10.2 mV | 289 µA | −33.1 / −5.3 dB | 308 | 152 | 46 |
| 10 mA | 400 µm | 1 nF / 20 pF | 54.4° | 33.4 dB | 10.2 mV | 289 µA | −33.0 / −0.2 dB | 277 | 262 | 98 |
| 50 mA | 2000 µm | 100 pF / 5 pF | 68.8° | 33.7 dB | 12.0 mV | 288 µA | −33.3 / −5.4 dB | 552 | 185 | 81 |
| 50 mA | 2000 µm | 1 nF / 20 pF | 55.2° | 33.7 dB | 12.0 mV | 288 µA | −33.3 / −0.4 dB | 388 | 319 | 132 |
| 100 mA | 4000 µm | 100 pF / 5 pF | 66.4° | 33.7 dB | 12.8 mV | 287 µA | −33.3 / −5.3 dB | 742 | 236 | 111 |
| 100 mA | 4000 µm | 1 nF / 20 pF | 54.7° | 33.7 dB | 12.8 mV | 287 µA | −33.3 / −0.4 dB | 497 | 345 | 151 |

觀察：
1. 穩定度幾乎不受 Imax 影響（最差點都在最輕載，由 I_min 決定）[X]。
2. 滿載 DC 迴路增益都約 33.5 dB：因為 W 跟著 Imax 縮放，滿載時 pass 都在同樣深的 triode [X/D]。
3. Undershoot 大致隨 ΔI 增加，但不成正比（10→100 mA，100 ns 邊沿只從 152 增到 236 mV）[X]。
4. **10 mA 版本仍有 152 mV（100 ns）**：輕載起步的慢迴路是主因，不是 pass 太大 [X/D]。

## 附：第 1 輪審查後的 B 架構修正（公平比較）

審查者 (a) 指出 REF-B 的類比 pass 只有 800 µm 是「稻草人」設計點。作者以 `s12_fairB.py` 獨立重現 [X]：

| 項目（CL=100 pF） | REF-A（4 mm） | REF-B（Wa=800 µm） | 公平 B（Wa=2.4 mm，總寬 3.44 mm，窗口 3–18 mA） |
|---|---|---|---|
| 5→95 mA undershoot（1 ns / 100 ns / 1 µs） | 499 / 127 / 27 mV | 756 / 313 / — mV | 553 / 154 / 33 mV |
| 20/45/70/95 mA 穩態 | 無振盪 | 無振盪（寬窗） | 無振盪，碼 1/3/5/7，Vout 1.6006→1.6001 V（load reg 0.5 mV） |
| PSRR@1 kHz（70 mA，碼凍結） | −38.2 dB | −18.8 dB | −24.2 dB（碼 5）；審查者在碼 3 量到 −30.1 dB → 差 8–14 dB 依窗口位置 |

**修正後的 B 結論**：
1. 「B 比 A 差 2.5 倍／19 dB」只描述 Wa=800 µm 的設計點；Wa 是 B 唯一的主要取捨旋鈕（小 → 暫態/PSRR 差；大 → 面積優勢消失）[X/D]。
2. B 的真實優點：DC load regulation（**同條件 20→95 mA：公平 B 0.5 mV vs A 6.1 mV**；`s12_fairB.json`、`s15_rz_loadreg.json`）[X]；高溫輕載漏電較不敏感，但優勢隨 Wa 縮小而變大——SF-like 125 °C 零載：Wa=800 µm 的 B +9 mV、**公平 B（2.4 mm）+28 mV**、A +46 mV；A 把洩放加到 300 µA 即約 +26 mV（審查者 `r3b_hot.json`、`r7_bleed_bias.json`）[X]。
5. **B 的降級模式**（審查者 (a) 的論點，原本漏記）：數位 reset（碼 0）後，公平 B 就是一顆 Wa=2.4 mm 的類比 LDO，Vout 掉 16 mV 以內可供 88.5 mA、PM 68°（`r8_fallback.json`）[X，審查者]——數位部分失效時仍可用，這是 B 降低下線風險的設計手法。
3. 要讓 B 的暫態贏過 A，需要非同步 droop 路徑。審查者以 1 顆比較器＋DFF 非同步 set 鏈（8 個 AND2，無新時脈）實作，8 組閾值×關閉邊沿設定**全部**在某個負載平台失效（45–360 mV p-p 弛張振盪或 Vout 卡在 +97 mV）；唯一把 100 ns undershoot 壓到 122 mV（< A 的 127 mV）的設定在 20 mA 與 95 mA 振盪 [X，審查者；作者未獨立重現；審查者自承部分現象可能是 XSPICE 事件排序假象]。
4. 1 ns 邊沿時任何數位路徑都來不及（比較器＋set 鏈 ≥2–4 ns），B 一律由類比 pass 寬度決定 [X/D]。
