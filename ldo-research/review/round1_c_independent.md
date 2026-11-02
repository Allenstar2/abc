# Round 1-C：獨立驗證（REF-A 迴路增益、PSRR、hybrid limit cycle）

> 驗證者：獨立 reviewer（未 import 原作者任何 python 模組；netlist 由 `sim/scripts/ldo_ref.py::subckt()` 的電晶體連接重抄成 flat netlist）。
> 工具：ngspice-42（batch）、PTM 180 nm（`sim/models/180nm_bulk.pm`，BSIM3 level 49）、Python 3 + numpy/scipy。
> 工作目錄：`/tmp/claude-0/-home-user/24b1423c-959f-5794-9f98-bbcbade8908e/scratchpad/review_r1c/`；腳本、關鍵 netlist、結果 json 複製在 `review/round1_c_files/`。repo 內既有檔案**未修改**。
> 標註：[X] 本次模擬、[D] 本次推導、[H] 假設。

## 0. 結論摘要

| 主張 | 判定 | 差距 |
|---|---|---|
| 1. REF-A 迴路增益（0 / 100 mA）與 p2 ≈ (G2+G_o)/CL | **成立** | DC、UGF、PM 與原主張差 ≤ 0.3%（三種不同斷迴路法互相一致）；p2 公式比 `.pz` 真實極點低 12%（< 30%，原因已找到：與 buffer 極點 p_b 交互作用） |
| 2. 低頻 PSRR ≈ gds_p·R_o/(1+T0)，滿載 ≈ −33 dB、零載 ≈ −55 dB | **大致成立**（數字成立，公式是近似） | 模擬 −33.3 / −55.5 dB，與主張差 ≤ 0.5 dB；但公式本身忽略 pg 對 Vin 追蹤不完全的項，系統性偏樂觀 0.6 dB（滿載）、1.0 dB（零載）、**2.2 dB（10 mA）** |
| 3. 窗口 < 一片電流 → 某些負載 limit cycle；窗口 > 一片電流 → 不會 | **部分成立** | 前半句完全成立（LC 負載比例 = 1 − r，與理論 100% 吻合）；後半句只在「類比在一個時脈內 settle、比較器無 offset、無 pipeline 延遲」時成立。offset 使分界點移到 1 + 2·os/I_s；每多 1 個時脈的純延遲（如 2 級 DFF 同步器）分界點約 +1（d=1 → 2.0）；欠阻尼類比響應也會把分界點往上推 |

（完整數字見各節；第 3 節的掃描表在第 3.3 節。）

---

## 1. 主張 1：REF-A 迴路增益

### 1.1 方法

**電路**：`subckt()` 的 11 顆電晶體照抄（NMOS 5T OTA → PMOS source follower → 4 mm PMOS pass），DEFAULT 參數但 R1=R2=4 kΩ、Cc=5 pF（Vout→ea）、CL=100 pF（ESR 1 µΩ）、Vin=1.8 V、Vref=0.8 V 理想源、Ibias=10 µA 理想源、負載為理想電流源 IL（0 / 10 mA / 100 mA）。netlist 摘要：

```
Ibias vin bn 10u
Mbn  bn bn 0 0 NMOS W=4u L=1u        Mt   tail bn 0 0 NMOS W=8u L=1u
M1   d1 fb tail 0 NMOS W=20u L=1u    M2   ea vref tail 0 NMOS W=20u L=1u
M3   d1 d1 vin vin PMOS W=4u L=1u    M4   ea d1 vin vin PMOS W=4u L=1u
Mbn2 bp bn 0 0 NMOS W=4u L=1u        Mbp  bp bp vin vin PMOS W=4u L=1u
Mcs  pg bp vin vin PMOS W=20u L=1u   Mb   0 ea pg pg PMOS W=20u L=0.18u
Mp   vout pg vin vin PMOS W=4000u L=0.18u
R1 r1t fb 4k   R2 fb 0 4k   Cc vout ea 5p   CL vout ncl 100p   RESR ncl 0 1e-6
```

原作者在 **fb → M1 閘極**（高阻抗點）用 L-C 斷迴路。我改在 **Vout → 分壓器頂端（r1t）** 斷開——這裡兩側都是有限阻抗（vout 側 R_o ≈ 2.6 kΩ、分壓器側 8 kΩ），單純斷開會有負載效應，因此用：

1. **Middlebrook 雙注入法**（主要方法）。兩次 AC 模擬：
   - 電壓注入：`Vinj r1t vout DC 0 AC 1`，T_v = −v(vout)/v(r1t)
   - 電流注入：`Vsa vout j 0`、`Vsb j r1t 0`、`Iinj 0 j AC 1`，T_i = −i(Vsa)/i(Vsb)
   - T = (T_v·T_i − 1)/(T_v + T_i + 2)
   - 推導 [D]：把 vout 側當 Thevenin（開路電壓 −A·v_b、阻抗 Z_a），分壓器側當 Z_b。可得 T_v = A + Z_a/Z_b、T_i = (A+1)·Z_b/Z_a，代入上式化簡為 A·Z_b/(Z_a+Z_b)，也就是正確的迴路增益（推導過程見附錄 A.1）。
2. **Vout→分壓器 L-C 斷開、不加 replica**（故意示範負載誤差）。
3. **Vout→分壓器 L-C 斷開，在 vout 加 AC-only 8 kΩ replica**（`Rrep vout nrep 8k` + `Crep nrep 0 1F`）。
4. **fb→M1 閘極 L-C**（原作者的位置，我自己重寫，只當交叉參考）。
5. **自己寫的 DC 小訊號節點矩陣**：從 ngspice OP 抽出 11 顆電晶體的 gm/gds/gmbs，自己組 KCL 矩陣，在 M1 閘極算 return ratio（`ss_model.py`）。
6. **非主極點**：ngspice `.pz`（M1 閘極以 DC 源加 1 Ω 固定在閉迴路 OP 值，`pz g1 0 vout 0 cur pz`；已用 RC 測試確認 ngspice pz 輸出單位為 rad/s）。

### 1.2 OP（零外部負載）[X]

Vout = 1.6061 V、V(pg) = 1.5949 V（pass Vsg = 0.205 V，弱反轉）、V(ea) = 1.2721 V、V(fb) = 0.80303 V（EA 系統性 offset 3 mV）、I(Vin) = 286.7 µA。
100 mA：Vout = 1.5932 V、V(pg) = 1.1278 V。

抽出的小訊號參數 [X]：

| 參數 | 0 mA | 10 mA | 100 mA |
|---|---|---|---|
| gm_p / gds_p (mS) | 4.980 / 0.2534 | 165.3 / 12.20 | 347.0 / 260.0 |
| gm1 (µS) | 183.6 | 181.7 | 179.0 |
| G_ea = gds2+gds4 (µS) | 2.38 | 2.35 | 2.39 |
| A_SF = gm_b/(gm_b+gds_b+gds_cs) | 0.910 | 0.963 | 0.961 |
| G2 = A_SF·gm_p (mS) | 4.530 | 159.1 | 333.5 |
| G_o = gds_p + 1/8k (mS) | 0.378 | 12.33 | 260.1 |

### 1.3 數字對照 [X]

| 負載 | 量 | 原主張 | Middlebrook（vout→R1） | L-C+replica | 閘極 L-C（交叉參考） | 自寫節點矩陣 | 誤差（Middlebrook vs 主張） |
|---|---|---|---|---|---|---|---|
| 0 | DC | 53 dB | **52.99 dB** | 52.99 | 52.99 | 52.99（手算公式 53.27） | −0.01 dB（線性 −0.1%） |
| 0 | UGF | 2.45 MHz | **2.448 MHz** | 2.448 | 2.448 | — | −0.1% |
| 0 | PM | 66° | **66.2°** | 66.2 | 66.4 | — | +0.3% |
| 100 mA | DC | 33.7 dB | **33.74 dB** | 33.74 | 33.74 | 33.74（手算 33.62） | +0.04 dB（+0.4%） |
| 100 mA | UGF | 1.6 MHz | **1.598 MHz** | 1.598 | 1.598 | — | −0.1% |
| 100 mA | PM | （未主張） | 87.7° | 87.7 | 87.9 | — | — |
| 10 mA | DC / UGF / PM | （未主張） | 53.84 dB / 2.616 MHz / 86.1° | 同 | 同 | 53.84 | — |

三種方法的 DC 值到小數點後 3 位都相同，代表原作者的閘極斷迴路沒有負載誤差；PM 差 0.1–0.2°，來自閘極斷點的高頻反向傳輸（Cgs/Cgd），可以忽略。

**超過 30% 的唯一差異（已找到原因）**：Vout→分壓器 L-C 斷開但**沒加 replica** 時，零載 DC = 56.47 dB（+3.48 dB，線性 +49%），UGF 2.50 MHz、PM 65.3°。原因 [D]：大電感讓 vout 在 AC 時看不到分壓器的 125 µS，G_o 從 378 µS 變成 253 µS，比值 1.493 = +3.48 dB，剛好解釋全部差距。加上 replica 或改用 Middlebrook 之後就完全吻合。100 mA 時 G_o 由 gds_p = 0.26 S 主導，同一種錯誤只有 +0.004 dB。

### 1.4 p2 ≈ (G2+G_o)/CL 的檢查

| 項目 | 數值 |
|---|---|
| 主張公式（我抽的 G2+G_o = 4.908 mS，CL=100 pF） | 7.81 MHz（原作者表列 7.8 MHz） |
| ngspice `.pz` 真實非主極點（開迴路，CL=100 pF）[X] | **8.89 MHz**；其餘極點：p1 = 5.72 kHz、下一個 21.5 MHz（buffer p_b）、RHP 零點 47 MHz |
| 公式誤差 | −12%（< 30%） |

找原因：我掃了 CL，看 p2·CL 是否收斂到 G2+G_o [X]：

| CL | `.pz` p2 | p2·2π·CL | (G2+G_o)/(2π·CL) | 公式誤差 |
|---|---|---|---|---|
| 50 pF | 18.5 MHz **共軛複數對**（p2 與 p_b 合併） | — | 15.6 MHz | 公式不再適用 |
| 100 pF | 8.89 MHz | 5.59 mS | 7.81 MHz | −12% |
| 200 pF | 4.09 MHz | 5.15 mS | 3.91 MHz | −4.6% |
| 400 pF | 2.04 MHz | 5.12 mS | 1.95 MHz | −4.2% |

p2 與 1/CL 成正比，大 CL 時 p2·CL 收斂到 5.12 mS，比 G2+G_o 高 4%，這是公式的 first-order 精度。CL=100 pF 時 p2 只比 p_b 低約 2.4 倍，兩個極點互相推開，所以誤差到 12%；CL ≤ 50 pF 時兩者合併成複數極點，公式失效。在 UGF 2.45 MHz 處的相位貢獻：公式組（7.8 / 29 MHz）17.4°+4.8° = 22.2°，`.pz` 組（8.9 / 21.5 MHz）15.4°+6.5° = 21.9°，所以 PM 預測幾乎不受影響。

**判定：主張 1 成立。**

---

## 2. 主張 2：低頻 PSRR

### 2.1 推導 [D]

在 M1 閘極斷迴路（閘極沒有 DC 電流，所以斷點是單向的）。由疊加原理：

```
v_out = A_os·v_in + A_f·v_g1 ,   v_g1 = β·v_out ,   T0 = −β·A_f
⇒  PSRR(DC) = v_out/v_in = A_os / (1 + T0)                       (精確)
```

A_os 是開迴路（M1 閘極 AC 接地）時 Vin→Vout 的增益。在 vout 節點寫 KCL（負載是理想電流源，不提供電導）：

```
G_o·v_out = gds_p·v_in + gm_p·(v_in − v_pg)
A_os = R_o·[ gds_p + gm_p·(1 − α_pg) ] ,   α_pg ≡ ∂v_pg/∂v_in (開迴路) ,  R_o = 1/(gds_p + 1/(R1+R2))
```

α_pg 來自 buffer 節點 pg 的 KCL：pg = A_SF·v_ea + [gds_cs·v_in + gm_cs·(v_in − v_bp)]/(gm_b+gds_b+gds_cs)。其中 5T OTA 的 PMOS mirror 讓 α_ea ≈ 1，Mcs 的閘極 bp 由二極體 Mbp 參考 Vin。

**主張的公式 gds_p·R_o/(1+T0) 等於假設 α_pg = 1**（pass 閘極完全跟著 Vin，pass 只靠 gds_p 漏電）。實際上 Mb 的 drain 接 GND，gds_b 把 pg 往地拉，所以 α_pg < 1。修正因子是 1 + (gm_p/gds_p)·(1−α_pg)。

### 2.2 數字 [X]/[D]

| 負載 | α_ea | α_pg | gm_p/gds_p·(1−α_pg) | A_os（節點矩陣 / AC 模擬） | 主張公式 gds_p·R_o/(1+T0) | 精確 A_os/(1+T0)（節點矩陣） | 閉迴路 AC 模擬 @1 Hz | 原主張 | 主張 vs 模擬 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 1.0167 | 0.9941 | 0.117 | 0.7477 / 0.7477 | −56.49 dB | −55.54 dB | **−55.54 dB** | ≈ −55 dB | 0.54 dB（線性 6%） |
| 10 mA | 1.0030 | 0.9790 | 0.284 | 1.271 / 1.271 | −53.95 dB | −51.77 dB | **−51.77 dB** | （未主張） | 公式偏樂觀 2.17 dB（線性 −22%） |
| 100 mA | 0.9748 | 0.9482 | 0.069 | 1.069 / 1.069 | −33.92 dB | −33.34 dB | **−33.34 dB** | ≈ −33 dB | 0.34 dB（線性 4%） |

- 自寫節點矩陣的 A_os、α_ea、α_pg、T0 與 ngspice AC（1 Hz）**到 5 位有效數字都相同**，所以 OP 抽參數與我的 KCL 矩陣都是對的。
- 公式與模擬的差（0.96 / 2.17 / 0.58 dB）完全等於 20·log10[1 + (gm_p/gds_p)(1−α_pg)]，原因確定。
- 10 mA 最差：gm_p/gds_p ≈ 13.5 仍然大，但 1−α_pg 已有 2.1%。滿載時 pass 在 triode，gm_p/gds_p 只有 1.33，所以影響小。

**判定：主張 2 大致成立。** 兩個主張數字（−33、−55 dB）與模擬差 ≤ 0.5 dB。公式只是近似，若拿來外推到中載會偏樂觀約 2 dB；建議在 ANALYSIS.md 註明公式假設 α_pg = 1，或改寫為 R_o·[gds_p + gm_p(1−α_pg)]/(1+T0)。

---

## 3. 主張 3：hybrid 窗口 vs slice 電流

### 3.1 行為模型（`hybrid_beh.py`，Python 離散時間）

正規化：slice 電流 I_s = 1、時脈週期 T = 1、N = 8 片。

- **比較器**在每個時脈邊沿取樣類比 pass 電流 I_a（V_pg 單調對應 I_a，所以 V 門檻可以換成電流門檻）：I_a > I_H − os → 加一片；I_a < I_lo + os → 減一片；兩者都成立時加一片優先。窗口 W = I_H − I_lo = r·I_s，I_lo = 0.25。os > 0 表示兩顆比較器的 offset 都往縮小窗口的方向（worst case，以電流表示：os = V_os·dI_a/dV_pg）。
- **數位**：雙向 thermometer，每個時脈 ±1 碼。可加純延遲 d 個時脈（例如同步器），也可加 blanking b：碼改變後 b 個時脈內不看比較器。
- **類比迴路**：I_a 追向 target = clip(I_L − k·I_s, 0, I_amax)。
  - 一階：時間常數 τ，每個時脈用精確指數更新；τ = 0 表示一個時脈內 settle。
  - 二階：ω_n（rad/時脈）、ζ，用 ZOH 精確離散化。
  - I_amax = I_H + 0.35，確保上門檻一定碰得到。
- **判定**：負載 0–8·I_s 細掃（基準 4001 點、r 掃描 801 點）。每個負載從 k=0 和 k=8 兩種初值各跑 3000 個時脈；只要任一個初值在最後 500 個時脈內碼還在變，就算 limit cycle（LC）。

**建模陷阱（已修正）**：第一版把 I_amax 固定在 2.6，結果 r ≥ 2.35 時 I_H ≥ I_amax，上比較器永遠不會觸發，碼卡在 0，被誤判成「沒有 LC」（實際上是調節失效）。修正為 I_amax = I_H + 0.35 後重跑，下文都是修正後的結果。原作者若用電路模擬掃窗口，也要注意 VL 不能低於類比 pass 實際能拉到的 V_pg。

### 3.2 基準（τ = 0、d = 0、os = 0）：準靜態理論 [D] vs 模擬 [X]

推導 [D]：碼 k 時 I_a = I_L − k·I_s，候選點彼此相距 I_s。寬 W 的閉區間對任何負載都至少含一個候選點 ⇔ W ≥ I_s。W < I_s 時，洞位於 I_L ∈ (I_H + k·I_s, I_lo + (k+1)·I_s)，每個 slice 週期寬 I_s − W，負載落在洞裡碼就在 k ↔ k+1 之間來回（p-p 1 碼）。所以 LC 負載比例 ≈ 1 − r。W = I_s 時洞寬為 0（只剩邊界點，用 ≥/≤ 比較時不會 LC）。

| r = W/I_s | LC 負載比例（模擬） | 理論 | 逐點一致率 | 碼 p-p | LC 區間（前 3 個，單位 I_s） |
|---|---|---|---|---|---|
| 0.30 | 0.669 | 0.669 | 100% | 1 | (0.55,1.25) (1.55,2.25) (2.55,3.25) … 共 8 段 |
| 0.50 | 0.469 | 0.469 | 100% | 1 | (0.75,1.25) (1.75,2.25) … 8 段 |
| 0.80 | 0.175 | 0.175 | 100% | 1 | (1.05,1.25) (2.05,2.25) … 7 段 |
| 0.95 | 0.044 | 0.044 | 100% | 1 | (1.20,1.25) … 7 段 |
| **1.00** | **0** | 0 | 100% | 0 | — |
| 1.05 / 1.2 / 1.5 / 2.0 | 0 | 0 | 100% | 0 | — |

（比例以整個 0–8·I_s 計算，含兩端不會 LC 的飽和區，所以 r = 0.3 是 0.669，不是 0.7。）

**與原作者 X3a 對照** [D]：代入 REF-B 的數字（slice 12.2 mA；窄窗 8–14 mA，r = 0.49；寬窗 3–18 mA，r = 1.23）：
- 窄窗的洞在 (14.0, 20.2)、(26.2, 32.4)、(38.4, 44.6)、(50.6, 56.8)、(62.8, 69.0)、(75.0, 81.2)、(87.2, 93.4) mA，約占 0–100 mA 的 44%。
- 20 mA 落在洞內（LC），45 / 70 / 95 mA 分別在碼 3 / 5 / 7 的窗內（穩定）。
- 寬窗沒有洞。

四個負載點與原作者的電路模擬**完全一致**。補充：窄窗的 LC 不是只出現在「某些少數負載」，而是 0–100 mA 約 44% 的負載都會 LC，原作者剛好只有 1/4 的測點落在洞裡。

**基準結論：在準靜態條件下，1.0 正是分界點（模擬與理論逐點 100% 一致）。**

### 3.3 offset、類比延遲、純延遲對分界點的影響 [X]

r_crit 定義為：r ≥ r_crit 時，0–8·I_s 所有負載都不會 LC（r 以 0.05 步進掃 0.5–4.0）。

| 情境 | r_crit | LC 比例 @ r=1.0 | @1.2 | @1.5 | @2.0 | 推導 / 解讀 |
|---|---|---|---|---|---|---|
| 基準 | **1.00** | 0 | 0 | 0 | 0 | W ≥ I_s |
| offset os = −0.1（窗口變寬） | 0.80 | 0 | 0 | 0 | 0 | r_crit = 1 + 2·os |
| os = +0.05 | 1.10 | 0.09 | 0 | 0 | 0 | 同上，與模擬完全吻合 |
| os = +0.10 | 1.20 | 0.17 | 0 | 0 | 0 | 〃 |
| os = +0.20 | 1.40 | 0.35 | 0.17 | 0 | 0 | 〃 |
| 一階類比 τ = 0.5 / 1 / 3 / 10 T | **1.00** | 0 | 0 | 0 | 0 | 單調、無慣性的延遲只會讓鎖定變慢，不會產生持續 LC |
| 二階 ω_n = 3 rad/T，ζ = 0.3 / 0.5 / 0.7 | 1.45 / 1.15 / 1.05 | 0.60 / 0.20 / 0.03 | 0.31 / 0 / 0 | 0 | 0 | ≈ 1 + 過衝量 M_p（0.37 / 0.16 / 0.05） |
| 二階 ω_n = 1 rad/T，ζ = 0.3 / 0.5 / 0.7 | 2.05 / 1.60 / 1.50 | 0.86 / 0.86 / 0.52 | 0.66 / 0.58 / 0.29 | 0.44 / 0.07 / 0 | 0.01 / 0 / 0 | 響應跨好幾個時脈，二階起始段等效為延遲，加上過衝 |
| 二階 ω_n = 0.3 rad/T，ζ = 0.3 / 0.5 / 0.7 | > 4 / 3.60 / 2.90 | 0.89 / 0.86 / 0.85 | 0.87 / 0.84 / 0.82 | 0.84 / 0.81 / 0.78 | 0.79 / 0.75 / 0.72 | 類比遠慢於時脈 |
| 純延遲 d = 1 時脈 | **2.00** | 0.84 | 0.67 | 0.41 | 0 | r_crit = d + 1 |
| 純延遲 d = 2（2 級 DFF 同步器） | **3.00** | 0.84 | 0.82 | 0.78 | 0.72 | r_crit = d + 1 |
| d = 1 + blanking 1 / d = 2 + blanking 2 | **1.00** | 0 | 0 | 0 | 0 | 每步之後等 d 個時脈，恢復準靜態 |
| τ = 1 T + os = 0.1 | 1.20 | 0.17 | 0 | 0 | 0 | 一階延遲不影響，只剩 offset 項 |
| 二階 ω_n = 1, ζ = 0.5 + os = 0.1 | 1.85 | 0.88 | 0.85 | 0.47 | 0 | 效應大致相加 |

**純延遲的推導 [D] 與驗證 [X]**：類比瞬間 settle、比較器結果晚 d 個時脈才生效時，碼依 k[n+1] = k[n] + u(k[n−d]) 更新。碼第一次進入窗內時，pipeline 裡已經有 d 個同方向的命令，所以碼一定會衝到 k_first ± d。要停住，就必須 k_first … k_first ± d 這 d+1 個碼都在窗內。長度 W 的區間對所有負載都保證含 d+1 個候選點 ⇔ W ≥ (d+1)·I_s。用「窗內碼數 < d+1 且位於可調節區內」去預測 LC 負載，對 d = 1、2 和 r = 1.2–3.0 的 14 組模擬**逐點 100% 一致**（`delay_theory.out`）。

碼序列範例（負載 4.0·I_s，`trace_demo.out`）：
```
d=0, r=1.5          stable : 1233333333…
d=1, r=1.5          LC     : 0123443223443223443…   (週期 6，p-p 2 碼)
d=1, r=1.5, blank=1 stable : 0112233333…
d=2, r=2.2          LC     : 0012344432111234443211…  (p-p 3 碼)
二階 ω_n=1, ζ=0.3, r=1.2 LC : 1234432234432234…
```

### 3.4 實際電路的時間尺度（用 REF-A 做參考，不是 REF-B）[X]

我在自己的 REF-A netlist 上施加一片 slice 大小（12.2 mA、1 ns 邊沿）的負載步階。從類比迴路的角度看，slice 導通等同負載減少（`tau_tr.out`）：

| 步階 | pass 電流 t63 / t90 | V(pg) 回到 10% / 2% | Vout 偏移峰值 | Vout 回到 2% |
|---|---|---|---|---|
| 12.4 → 0.4 mA（輕載端） | 1.8 / 4.0 ns | 85 / 121 ns | +188 mV | 301 ns |
| 0.4 → 12.6 mA | 2.8 / 3.4 ns | 3.6 / 71 ns | −258 mV | 430 ns |
| 22.4 → 10.2 mA | 1.0 / 2.2 ns | 5.8 / 61 ns | +106 mV | 418 ns |
| 10.2 → 22.4 mA | 1.2 / 2.0 ns | 2.8 / 88 ns | −106 mV | 433 ns |

- pass 電流經 Cc 快速路徑在幾 ns 內就接手，但比較器看的是 V(pg)。V(pg) 有 60–120 ns 的慢尾巴：Vout 以迴路頻寬（約 µs 等級）回到穩態時，pass 的 Vsd 跟著改變，V(pg) 也隨之漂移。
- 對照時脈：1 MHz（T = 1 µs）幾乎完全準靜態；10 MHz（T = 100 ns）大致準靜態；**50 MHz（T = 20 ns）時慢尾巴橫跨 3–6 個時脈**。若尾巴帶有欠阻尼成分，依 3.3 節分界點會明顯上移。
- 限制 [H]：REF-B 的 pass 是 800 µm，再加上 slice 讓 G_o 變大、迴路增益掉到 16–23 dB，時間尺度和 REF-A 不同；上表只能說明量級。原作者 X3a 的寬窗（r = 1.23）在 50 MHz 只測了 4 個負載點，我**無法**用自己的模擬確認或否定它在所有負載都穩定。

### 3.5 主張 3 判定：**部分成立**

- 「窗口 < 一片電流 → 某些負載 LC」：**成立**。LC 負載比例 = 1 − r（逐點 100% 與理論一致），也和原作者 4 個負載點的電路結果一致。
- 「窗口 > 一片電流 → 不會 LC」：**只在準靜態下成立**，也就是類比在一個時脈內 settle 且不過衝、比較器沒有 offset、比較器到 slice 沒有額外的 pipeline 延遲。ANALYSIS.md 原文把它寫成「**必要**條件」（並提到 offset 餘裕），這個措辭是對的；但如果當成充分條件來用就不成立。分界點的移動：
  1. **offset**：r_crit = 1 + (os_H + os_L)/I_s，與模擬完全吻合。兩顆比較器的 offset 直接相加，而不是只需要大於 3σ。
  2. **純延遲 d 個時脈**：r_crit = d + 1。ANALYSIS.md 第 161 行建議實作時加 2 級 DFF 同步器，如果直接加上去（d = 2）而不改控制器，**r = 1.23 的寬窗在約 80% 的負載會 LC**（r = 1.2、d = 2 時比例 0.82）。對策：每次改碼後 blanking d 個時脈（模擬證實可恢復 r_crit = 1），或把窗口拉到 > 3 片電流。
  3. **類比動態**：單調的一階延遲（τ ≤ 10 T）不移動分界點；欠阻尼或比時脈慢的二階響應會把 r_crit 推到 1.05–3.6 以上（見表）。50 MHz 時脈 + 輕載這個組合最需要再驗證。

---

## 4. 總結與建議

1. **主張 1 成立**：換成 Middlebrook 雙注入（斷在 vout→分壓器），DC / UGF / PM 與原主張差 ≤ 0.3%。p2 公式比 `.pz` 低 12%，原因是與 buffer 極點交互；CL ≤ 50 pF 時兩者合併成複數極點，公式失效，建議在 ANALYSIS.md 註明適用範圍。
2. **主張 2 大致成立**：數字差 ≤ 0.5 dB；公式忽略 α_pg < 1（Mb 的 drain 接地，SF 增益 < 1），中載偏樂觀 2.2 dB。建議改寫成 A_os/(1+T0)，其中 A_os = R_o[gds_p + gm_p(1−α_pg)]。
3. **主張 3 部分成立**：1.0 是**準靜態**分界點。報告中「窗口 > 一片電流就安全」應改成 `W > I_s·(1 + d) + os_H + os_L`，並加上「類比對 slice 步階的 V(pg) 響應在 1 個時脈內 settle 且無明顯過衝」的條件。建議原作者在 50 MHz、r = 1.23 下對負載做細掃（例如 0–100 mA 每 0.5 mA 一點），確認寬窗沒有動態 LC。

**本次驗證的限制**：(a) 主張 1、2 用的是同一個 PTM 模型和同一份電路（重抄），所以驗證的是「方法與推導」，不是模型準確度。(b) 主張 3 是行為模型，沒有重跑 REF-B 電路；slice 電流視為常數（實際會隨 Vout 變化）；比較器沒有 metastability 和雜訊。

---

## 附錄 A.1 Middlebrook 雙注入推導 [D]

在斷點，vout 側是 Thevenin（開路電壓 = −A·v_b，A 是由 b 側電壓經分壓器→EA→pass 回到 vout 的增益；輸出阻抗 Z_a），分壓器側是 Z_b，真正的迴路增益是 T = A·Z_b/(Z_a+Z_b)。

- 電壓注入（v_b = v_a + v_inj）：i = v_b/Z_b，v_a = −A·v_b − Z_a·v_b/Z_b，所以 T_v = −v_a/v_b = A + Z_a/Z_b。
- 電流注入（注入節點電壓 v）：i_y = (−A·v − v)/Z_a（由 a 側流出），i_x = v/Z_b（流進 b 側），所以 T_i = −i_y/i_x = (A+1)·Z_b/Z_a。
- 令 ρ = Z_a/Z_b：(T_v·T_i − 1)/(T_v+T_i+2) = [A(A+1+ρ)/ρ] / [(ρ+1)(A+ρ+1)/ρ] = A/(1+ρ) = T。✔

這個公式假設斷點沒有反向傳輸（分壓器側只經 M1 閘極往前送）。閘極 Cgs/Cgd 的高頻反向耦合會造成 0.1–0.2° 的 PM 差，與閘極 L-C 法的結果一致。

## 附錄 A.2 數值結果檔

- `lg_results.json`：OP（11 顆電晶體的 gm/gds/gmbs/id/vgs/vds/vth/vdsat），以及每種斷迴路法的 DC/UGF/PM、PSRR、開迴路 supply gain。
- `ss_results.json` / `ss_model.out`：自寫節點矩陣的 T0、α_ea、α_pg、A_os、PSRR。
- `pz_test.out`、`pz_cl.out`：`.pz` 極零點與 CL 掃描。
- `tau_tr.out`：slice 步階的 pass 電流 / V(pg) / Vout settling。
- `hyb_A.json`、`hyb_scan.json` / `hyb_scan.out`、`delay_theory.out`、`trace_demo.out`、`refb_map.out`：主張 3 的所有數字。

## 附錄 B 檔案清單（`review/round1_c_files/`）

| 檔案 | 內容 |
|---|---|
| `sim_lg.py` | flat netlist 產生器 `core()`、Middlebrook 雙注入 `mb()`、Vout→分壓器 L-C（有/無 replica）`lc()`、閘極 L-C `gate()`、閉迴路 PSRR `psrr_cl()`、開迴路 supply gain `supply_open()`、`margins()` |
| `ss_model.py` | 從 OP 組 KCL 矩陣，算 T0 / A_os / PSRR，並與主張公式比較 |
| `pz_test.py`、`pz_cl.py` | ngspice `.pz`（M1 閘極以 1 Ω 接 DC 源，cur 輸入） |
| `tau_tr.py` | slice 大小的步階暫態 |
| `hybrid_beh.py`、`hybrid_scan.py`、`delay_theory.py`、`trace_demo.py`、`refb_map.py` | 主張 3 行為模型、掃描、延遲理論驗證、碼序列範例、REF-B 洞位置 |
| `mbv_IL0.cir`、`mbi_IL0.cir`、`lcr_IL0.cir`、`psr_IL0.cir`、`aos_IL0.cir`、`pz_IL0.cir` | 零載時實際送進 ngspice 的 netlist（Middlebrook 電壓/電流注入、replica L-C、PSRR、開迴路 supply、pz） |

注意：腳本把輸出寫到**腳本所在目錄**，要重跑請先把整個資料夾複製到 scratch 目錄；腳本之間以相對路徑互相 import，並從 `lg_results.json` 讀 OP。

關鍵 netlist 片段（Middlebrook，零載）：
```
* 電壓注入 (mbv_IL0.cir)                    * 電流注入 (mbi_IL0.cir)
VIN vin 0 DC 1.8                             VIN vin 0 DC 1.8
VREF vref 0 0.8                              VREF vref 0 0.8
Vinj r1t vout DC 0 AC 1                      Vsa vout j DC 0
IL vout 0 DC 0.0                             Vsb j r1t DC 0
.control                                     Iinj 0 j DC 0 AC 1
ac dec 40 1 1e10                             IL vout 0 DC 0.0
wrdata mbv_IL0.txt v(vout) v(r1t)            .control
.endc                                        ac dec 40 1 1e10
                                             wrdata mbi_IL0.txt i(Vsa) i(Vsb)
T_v = -v(vout)/v(r1t);  T_i = -i(Vsa)/i(Vsb);  T = (T_v*T_i - 1)/(T_v + T_i + 2)
```

行為模型核心（`hybrid_beh.py::simulate`，每個時脈）：
```python
up = (Ia > IH - os) & act;  dn = (Ia < I_LO + os) & ~up & act
k_cmd = clip(k_cmd + up - dn, 0, N);  hist.append(k_cmd); hist.pop(0); k_app = hist[0]   # d-clock latency
tgt = clip(loads - k_app, 0, IMAX)
Ia = tgt + (Ia - tgt)*exp(-1/tau)            # order 1   (order 2: exact ZOH state update)
```
