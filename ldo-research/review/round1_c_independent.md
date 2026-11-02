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

（第 3 節內容在掃描完成後補上。）
