# Round 2（a）對抗審查：試圖推翻 `CONCLUSION_DRAFT.md` v2

> 審查對象：`CONCLUSION_DRAFT.md`（v2），輔以 `REVIEW_LOG.md`、`ANALYSIS.md`、`ARCH_MATRIX.md`、`DECISIONS.md`、`GAPS.md`、`sim/scripts/{ldo_ref,ldo_hybrid,s12_fairB,s10_vco_supply,s6_corners}.py`、`sim/results/*.json`、`lit_raw/agent5_hbm_notes.md`、`review/round1_*`。
> 依指示**不重複**第 1 輪已處理的論點（REF-B 類比 pass 太小、1 nF 加 Rz 可改善慢邊沿、SRE 效果）。本輪找的是新的反例：補償在 corner 與佈局寄生下的穩健性、規格本身、應用面、量測方法學、結論內部一致性。
> 模擬全部在 scratch（`/tmp/claude-0/-home-user/24b1423c-959f-5794-9f98-bbcbade8908e/scratchpad/review_r2a/`），repo 內既有檔案**未修改**。`common.py`、`ldo_ref.py`、`ldo_hybrid.py` 複製到 scratch，只改輸出路徑；corner 用 `s6_corners.py` 的 Vth/Tox 平移法（`corners.py`，另加 NFactor、Pclm、U0、Cgdo、PMOS Eta0 的擾動）。腳本與小型 json 已複製到 `review/round2_a_files/`。
> 模型：`sim/models/180nm_bulk.pm`（PTM，ngspice-42）。標註沿用 repo：[X] 本審查模擬、[D] 推導、[H] 假設或推測；「審查者記憶，未查證」是指本輪禁止網路，我只能憑記憶提出的文獻線索。

---

## 0. 總判定

| # | 論點 | 嚴重度 | 對首選的影響 |
|---|---|---|---|
| 1 | 理由 3「HBM/SerDes 在意 MHz–百 MHz PSRR，B/C 在這個指標上結構性吃虧」與數據不符：10–100 MHz 時 A 與公平 B 都約 0 dB，差 ≤0.6 dB | **推翻（理由 3）** | 理由 3 不能用來區分 A 與 B |
| 2 | 第 1 輪後採用的 nulling-resistor 設計點（1 nF/8 pF/10 kΩ、100 pF/3 pF/10 kΩ）在 FF −40 °C＋偏壓 +30%＋Cc 底板寄生下**會持續振盪**（146–170 mV p-p）。改成穩健的 Rz 之後，「1 nF＋Rz 在各種邊沿都優於 REF-A」不再成立 | **推翻（ANALYSIS 附錄採納的「1 nF＋Rz 全面優於」）／需修正（首選規格裡的 Rz）** | A 仍是首選，但基準補償要改回 Rz=0，或限制 Rz ≤ ~3 kΩ |
| 3 | 規格本身（1.8→1.6 V、100 mA）是整個方案最脆弱的一環：Vin 只降 5% 在 SS 125 °C 就失去調節；pass 加寬救 dropout 又會讓高溫漏電惡化；片上 IR 會再吃掉 20–80 mV dropout [H] | **需修正** | 要問教授的第一個問題應該是規格，不只是「要不要 hybrid」 |
| 4 | 若採用 HBM/SerDes 應用動機，A 裡面該選的子類會從 A1（PMOS＋Miller）換成 A4（NMOS source-follower pass）：1–10 MHz PSRR 好 15–20 dB，但 Vin=1.8 V 時 Vout 必須降到 ≤1.0–1.2 V | **需修正（條件式改變首選子類）** | A 的類別不變，子類與規格改變 |
| 5 | v2 列出的兩個「B 的真實優點」在學生量測情境下站不住：高溫漏電失效只要 \|Vthp\| 多 50 mV 就消失（PTM 的假象）；0.5 vs 6–13 mV 的 load regulation 會被片上 IR 與熱蓋掉 | **需修正**（結果對 A 有利） | 強化 A |
| 6 | G1（量測方法學）做為量測設計有價值，但當成「研究缺口」偏弱：有前例；1 ns 角落需要 3–10 mA 的監測 buffer；用單一顆 LDO 無法示範「FoM 排名改變」 | **需修正** | 不影響架構，影響專題定位 |
| 7 | 量測陷阱：量測板在 Vout 腳位加 1 nF–100 nF 去耦電容，最輕載 PM 會掉到 19–30° | **小問題→需寫進量測計畫** | A、B 對稱 |
| 8 | 熱與 IR、Vref/bandgap、偏壓來源 | **小問題** | A、B 對稱 |
| — | 檢查過、沒發現問題：片上 NMOS 負載確實接近電流源（D-007 成立）；PM 對 PTM 模型參數不敏感（±2.5°）；\|Vthp\| +150 mV 時 4 mm pass 仍能供 100 mA | — | 支持 A |

**一句話**：首選的「類別」不必改（A 仍優於 B/C），但 v2 對 A 的**具體配置**（Miller＋Rz、1 nF＋Rz 較佳）有一個會振盪的設計點；理由 3 用錯了指標；如果要應用動機，A 的子類和規格都要換。

---

## 1.【推翻】理由 3：MHz–百 MHz 的 PSRR 分不出 A 與 B

v2 理由 3 寫：「應用面（HBM/SerDes）在意的是 MHz–百 MHz 的 PSRR：開著的 slice 是 Vin→Vout 的低阻抗開關，B/C 在這個指標上結構性吃虧（X3c、X5…）」。但 X3c 和 s12 量的是 **1 kHz**。我把同一組電路掃到 100 MHz（`r2_1_psrr_hf.py`，碼凍結，CL=100 pF）[X]：

| PSRR (dB) | 1 kHz | 100 kHz | 1 MHz | 10 MHz | 100 MHz |
|---|---|---|---|---|---|
| **70 mA** REF-A（4 mm，100 pF） | −38.2 | −25.6 | −6.7 | **+0.6** | +0.2 |
| 公平 B（Wa 2.4 mm），碼 3 | −30.1 | −21.7 | −4.1 | **+0.7** | +0.6 |
| 公平 B，碼 5 | −24.2 | −17.6 | −1.9 | **+0.8** | +0.7 |
| REF-A 1 nF（Cc 8 p、Rz 10 k） | −38.2 | −21.7 | −5.9 | −3.4 | −7.7 |
| **20 mA** REF-A（100 pF） | −49.2 | −27.9 | −8.5 | +0.6 | −0.1 |
| 公平 B，碼 0 / 碼 1 | −46.1 / −35.8 | −27.5 / −24.5 | −8.2 / −5.9 | +0.4 / +0.7 | +0.2 / −0.1 |

- 10–100 MHz：A 與 B **都在 0 dB 附近**，差 ≤0.6 dB。1 MHz 時差 0.3–4.8 dB。8–14 dB 的差距只出現在 ≤100 kHz。
- 在 10–100 MHz 真正有效的旋鈕是 **CL**：1 nF 比 100 pF 好 4–16 dB，和架構無關。
- 推導 [D]：在迴路頻寬以上，PSRR ≈ G_inj/(G_inj + jωCL)。70 mA 時 A 的 G_inj 約 0.15 S（滿載 gds_p 0.26 S），B 是 slice＋類比 pass 的電導 0.24–0.31 S（第 1 輪 r2）。兩者都大於 ωCL（10 MHz 時 0.0063 S；100 MHz、100 pF 時 0.063 S），所以 PSRR 都 → 0 dB（100 MHz 時 A 約 −0.7 dB [D]）。B 的「低阻抗開關」在這個頻段並沒有比 A 的 triode pass 更糟，因為 A 的 pass 本身也是 triode 的低阻抗路徑。
- X5 自己的數字也說明了這點：REF-A 在 10 MHz 是 +1.3 dB（**放大**漣波）。

**建議**：刪掉理由 3，或改成「≤100 kHz 的 PSRR 差 8–14 dB；≥1 MHz 兩者都差，由 CL 決定」。應用面的含意改寫到第 4 節。

---

## 2.【推翻／需修正】Nulling resistor：第 1 輪採用的設計點在冷角＋佈局寄生下會振盪

v2 的首選規格是「Miller 補償＋nulling resistor（需跨負載/corner 驗證）」；`ANALYSIS.md` 附錄也採納了「1 nF、Cc=8 pF、Rz=10 kΩ → 431/185/80 mV，全面優於 REF-A」。我做了那個「需跨 corner 驗證」。

### 2.1 機制：Rz 讓迴路增益出現一段平台，高度是 β·gm1·Rz [D]

在 f_z = 1/(2π·Rz·Cc) 以上，Cc 近似短路。EA 的小訊號電流 gm1·v_t 全部流過 Rz，所以 v_ea − v_out ≈ gm1·Rz·v_t。只要 G2/(ωCL) ≫ 1（頻率低於 p2），pass 會讓 v_ea ≈ 0，因此

```
|T| ≈ β · gm1 · Rz        （f_z < f < p2 = G2/(2π·CL)，中重載時這段很寬）
```

如果平台裡出現任何寄生極點（例如 Rz 和 Cc 中點的寄生 Cp 形成 1/(2π·Rz·Cp)，或 buffer 極點 p_b），相位在平台內就會掉到 −180°，GM 約等於 −20·log(β·gm1·Rz)。

`r2_5h_gm1.py` 從 OP 抽出 gm1 [X]：

| 條件 | gm1 | β·gm1·Rz（10 kΩ） | 預測 GM | β·gm1·Rz（3 kΩ） | 預測 GM |
|---|---|---|---|---|---|
| TT 27 °C | 182 µS | 0.91 | 0.8 dB | 0.27 | 11.3 dB |
| FF −40 °C、Ibias +30% | 266 µS | **1.33** | **−2.5 dB** | 0.40 | 8.0 dB |
| SS 125 °C、Ibias −30% | 114 µS | 0.57 | 4.9 dB | 0.17 | 15.3 dB |

Rz=10 kΩ 在標稱條件下已經到 1/(β·gm1) 的 92%。EA 輸入對在弱反轉，gm1 ∝ I/(n·U_T)，所以低溫和偏壓偏高都會讓平台超過 0 dB。

### 2.2 模擬驗證 [X]

**(a) 單一擾動**（`r2_5_robust.py`，負載 0–100 mA 共 8 點，取最差）：

| 設計 | 標稱 PM/GM | 5 corner × 3 溫度的最差 PM | 模型參數（NFactor ×0.7/1.4、Pclm ×0.5/2、U0 ±20%、Cgdo ±50%、Eta0p ×0.5） | 被動元件（Rz ±20%、Cc ±15%、CL ±20%） | Cpg +2 pF / Cea +0.3 pF |
|---|---|---|---|---|---|
| D1 REF-A 100 p/Cc 5 p/Rz 0 | 66.4° / 18.4 dB | 60.7°（SS/FS 125） | 64.9–67.5° | 62.9–69.4° | 65.8° / 65.4° |
| D2 100 p/Cc 3 p/Rz 5 k | 73.2° / 20.8 dB | 61.9°（TT 125） | 70.8–75.0° | 68.0–77.6° | 71.7° / 70.0°（GM 13.2 dB） |
| D3 1 n/Cc 8 p/Rz 10 k | 62.3° / 16.5 dB | 52.4°（SS 125） | 60.1–64.2° | 57.8–67.6° | 61.8° / 60.7°（**GM 7.9 dB**） |

→ PM 對 PTM 模型參數不敏感（±2.5°），這是 A 的好消息。問題出在**佈局寄生**與**偏壓偏移**。

**(b) Cc 底板寄生**（`r2_5b_parasitic.py`、`r2_5c_verify.py`）。MIM 底板寄生約 5–15% Cc [H]。如果底板接在 Rz 那一側（中點 ncz），就形成 1/(2π·Rz·Cp) 的極點：

| D3 + 中點寄生 Cp | 10 mA PM / GM | 30 mA GM | 10→12 mA、1 ns 小步階 |
|---|---|---|---|
| 0 | 135.5° / 18.4 dB | 16.5 dB | 無振鈴 |
| 0.4 pF（5%） | 139° / 7.0 dB | 5.7 dB | — |
| **0.8 pF（10%）** | **18.2° / 3.6 dB**（0 dB 第二次穿越在 19.4 MHz） | 3.2 dB | **21.2 MHz 振鈴**（預測 1/(2π·10 kΩ·0.8 pF) = 19.9 MHz），步階後 100–300 ns 仍有 12.3 mV p-p |
| 1.2 pF（15%） | 7.6° / 1.7 dB | 2.2 dB | 18.7 MHz，300–1000 ns 仍有 15.2 mV p-p（幾乎不衰減） |
| 0.8 pF，Rz 改 5 kΩ | 110.6° / 12.2 dB | 11.0 dB | 無振鈴 |

**(c) 冷角組合**（FF −40 °C、Ibias +30%、Cp=10% Cc、Cea +0.3 pF；`r2_5d_window.py`、`r2_5e_tran.py`、`r2_5f_100p.py`）：

| 設計 | 最差 PM / GM | 時域 |
|---|---|---|
| D3 1 n/8 p/**10 k**（第 1 輪採用） | **−3.9° / −1.1 dB** | 10 mA、30 mA 加 2 mA 小擾動後**持續振盪 146 / 170 mV p-p**（4–6 µs 後仍未衰減） |
| 100 p/3 p/**10 k**（第 1 輪表中的 100 pF 對照） | **−12.5° / −3.4 dB** | — |
| D2 100 p/3 p/5 k | 74.4° / **4.0 dB** | — |
| 100 p/5 p/3 k | 82.5° / 9.0 dB | — |
| **D1 REF-A（Rz=0）** | **63.8° / 18.4 dB** | — |

這是刻意的悲觀組合（各項同時取最差），但每一項都在常見範圍內：電阻定義的偏壓 ±20–30%、MIM 底板 5–15%、−40 °C [H]。而且學生只有 LTspice，佈局後的寄生抽取（PEX）看不到這個中點電容 [H]。

### 2.3 1 nF 的 Cc×Rz 設計窗口，以及穩健點的暫態代價

`r2_5d_window.py`，四種條件（標稱／加寄生／SS 125 °C＋被動 −15/+20%／冷角＋寄生），格式為最差 PM° / GM dB [X]：

| Cc / Rz | β·gm1·Rz | 標稱 | 加寄生 | SS 125 組合 | 冷角＋寄生 |
|---|---|---|---|---|---|
| 8 p / 10 k | 0.92 | 62.3 / 16.5 | 13.6 / 2.9 | 44.2 / 26.9 | **−3.9 / −1.1** |
| 8 p / 5 k | 0.46 | 50.5 / 25.1 | 49.6 / 10.1 | 38.7 / 33.1 | 53.2 / 5.3 |
| 12 p / 5 k | 0.46 | 59.9 / 25.4 | 59.4 / 9.4 | 46.2 / 34.4 | 63.5 / 4.8 |
| 12 p / 7 k | 0.64 | 65.4 / 21.3 | 64.8 / 6.0 | 48.8 / 31.3 | **12.5 / 1.8** |
| 16 p / 3 k | 0.28 | 60.4 / 31.4 | 60.3 / 14.5 | 49.1 / 39.1 | 62.7 / 9.6 |

只有 Rz ≈ 3 kΩ、Cc ≈ 16 pF 這一點**勉強**同時通過（PM ≈ 49°、GM ≈ 10 dB）。窗口的兩側都被卡住：Rz 小時 PM 不夠，Rz 大時平台增益太高。

穩健點的暫態（0→100 mA，`r2_5e_tran.py`、`r2_5g_100p_tran.py`）[X]：

| 設計 | 冷角＋寄生是否穩定 | 1 ns | 100 ns | 1 µs |
|---|---|---|---|---|
| REF-A 100 p/Cc 5/Rz 0 | 是（GM 18 dB） | 742 | 236 | 111 |
| 100 p/Cc 5/Rz 3 k（穩健） | 是（GM 9 dB） | 792 | **211** | **94** |
| 100 p/Cc 3/Rz 10 k（第 1 輪） | **否** | 872 | 178 | 70 |
| D3 1 n/Cc 8/Rz 10 k（第 1 輪） | **否** | 431 | 185 | 80 |
| 1 n/Cc 12/Rz 5 k | 邊緣（GM 4.8 dB） | 455 | 249 | 106 |
| 1 n/Cc 16/Rz 3 k（穩健） | 是（GM 9.6 dB） | **469** | **291** | **122** |
| 1 n/Cc 20/Rz 0（REF-A 1 nF） | 是 | 497 | 346 | 151 |

結論：
- 「1 nF＋Rz 在 1 ns/100 ns/1 µs **全面**優於 REF-A」只對一個在冷角會振盪的設計點成立。穩健的 1 nF 只在 **1 ns** 邊沿較好（−37%），100 ns 差 23%，1 µs 差 10%。
- 對 100 pF 來說，穩健的 Rz（3 kΩ）只帶來 10–15% 的慢邊沿改善，1 ns 還變差 7%。
- 純 Miller（Rz=0）的 REF-A 是本輪所有擾動中最穩健的配置：PM ≥59°、GM ≥14.8 dB。

### 2.4 建議
1. 首選規格改為「**Miller 補償，基準 Rz=0**」。若要 Rz，寫成設計規則：**β·gm1,max·Rz ≤ 0.3**（本設計約 3 kΩ）；gm1,max 要取冷角與偏壓上限。偏壓若用 constant-gm（gm1 ∝ 1/R_bias），而且 R_bias 和 Rz 用同一種電阻，β·gm1·Rz 就變成電阻比值，跨 corner 會穩很多 [D]。
2. 佈局規則：Cc 的 MIM 底板接 Vout（低阻抗端），不要接 Rz 端。在 LTspice 的 schematic 手動加上 10–15% Cc 的底板寄生，以及 ea 節點 +0.3 pF，再跑 corner。
3. `ANALYSIS.md` 附錄與 `LEARNING_ANSWERS` 的「1 nF＋Rz 全面優於」改成：「在 PM 與 GM 都穩健的補償下，1 nF 只在 ns 級邊沿較好；慢邊沿與 100 pF 相當或略差」。
4. 若想要「可解釋」的實驗：做一顆可用傳輸閘切換的 Rz（預設 0），量振鈴頻率是否等於 1/(2π·Rz·Cp)。這是學生可以手算、模擬、量測三方對照的現象（選做；預設狀態必須穩定）。

---

## 3.【需修正】規格本身：1.8→1.6 V、100 mA 是最脆弱的一環

### 3.1 Vin 容差（`r2_2_vin_tol.py`，REF-A，|Vout−1.6 V| < 1%）[X]

| corner / 溫度 | Wp | 100 mA 時最低 Vin | Vin=1.71 V（−5%）、100 mA | Vin=1.62 V（−10%）、100 mA / 50 mA |
|---|---|---|---|---|
| TT 27 | 4 mm | 1.684 V | 1.5888 ✔ | 1.528 ✘ / 1.573 ✘ |
| SS 27 | 4 mm | 1.690 V | 1.5878 ✔ | 1.521 ✘ / 1.570 ✘ |
| TT 125 | 4 mm | 1.714 V | 1.5826 ✘ | 1.495 ✘ / 1.558 ✘ |
| SS 125 | 4 mm | 1.724 V | **1.5758 ✘** | 1.485 ✘ / 1.553 ✘ |
| SS 125 | 6 mm | 1.678 V | 1.5924 ✔ | 1.531 ✘ / 1.575 ✘ |
| TT 125，**零載** | 6 mm | — | Vin=1.8 V 時 Vout = **1.6184（+18 mV）✘** | — |

- 200 mV dropout 只能容許約 −4%（室溫）到 −2%（高溫）的 Vin 誤差。若 Vin 來自晶片的 1.8 V 電源（±10%），100 mA 在任何架構下都做不到。B 的 slice 總寬相同，同樣受限。
- **W 被兩頭擠壓**：pass 加到 6 mm 可以救 Vin −5%，但 TT 125 °C 零載 Vout 會高 18 mV。在 PTM 下，沒有一個 W 能在 200 µA 洩放時同時滿足兩者。
- 片上 IR 會再吃掉 dropout [D/H]：Vout 匯流排長 300 µm、寬 30 µm（10 方塊），頂層厚金屬 20–40 mΩ/□、一般金屬 70–80 mΩ/□ [H] → 0.2–0.8 Ω → 100 mA 時 20–80 mV。若分壓器在負載端 Kelvin 取樣，這段 IR 直接從 200 mV dropout 扣掉（TT 27 °C 的最低 Vin 變成 1.70–1.76 V）；若不在負載端取樣，它會以 20–80 mV「load regulation」的形式出現。

### 3.2 改規格的效果（`r2_3_vout_alt.py`、`r2_11_dropout_AB.py`）[X]

| Vout（Vin 1.8 V） | Wp | 滿載 DC 迴路增益 | PSRR@1 kHz（100 mA） | PSRR@1 MHz / 10 MHz（100 mA） | 100 mA 最低 Vin | 0→100 mA、100 ns undershoot | 最差 PM |
|---|---|---|---|---|---|---|---|
| 1.6 V | 4 mm | 33.7 dB | −33.3 dB | −5.3 / +0.5 | 1.672 V（−7%） | 236 mV | 66.4° |
| **1.4 V** | 4 mm | **48.6 dB** | **−46.4 dB** | −9.2 / +0.5 | **1.508 V（−16%）** | 234 mV | 63.3° |
| 1.2 V | 1.5 mm | 46.5 dB | −43.3 dB | −10.1 / +0.3 | 1.602 V | 282 mV | 63.4° |

- 只把 Vout 降 200 mV，pass 就離開 triode：滿載迴路增益 +15 dB、低頻 PSRR +13 dB、Vin 容差從 −7% 變 −16%。暫態與穩定度不變。
- **較大 dropout 時 B 更吃虧**：Vout=1.4 V、70 mA 時，PSRR@1 kHz 為 A −48.6 dB、B −37.5（碼 2）／−28.1 dB（碼 3），差 11–20 dB（1.6 V 時是 7–14 dB）。原因是 slice 閘極接 0 V 時永遠在深 triode，而 A 的 pass 會進入飽和。每片 slice 的電流也大約變成 2 倍，窗口必須重設計 [X/D]。
- **較低 Imax（10 mA）**：B 的 slice 失去存在理由（每片 ~1 mA，數位迴路只是在處理類比本來就能處理的範圍）[D]。
- 結論：改規格**不會讓首選變成 B**。較大 dropout 或較低 Imax 反而讓 A 更佔優勢。但 v2 沒有寫出建議的設計點（Imax？Vout？），而規格對 A 本身的穩健度影響比 A/B 之爭還大。

**建議**：「先問教授」清單的第一題改成：**Vin 從哪來、容差多少？Vout 一定要 1.6 V 嗎？Imax 一定要 100 mA 嗎？** 若都可調，建議 Vout 1.2–1.4 V、Imax 20–50 mA。「是否要 hybrid」排在第二題。

---

## 4.【需修正】若要 HBM/SerDes 應用動機：A 的子類要換成 NMOS pass，規格也要換

v2 的「會改變建議的新資訊」裡有「PSRR 為主要指標（→ A＋PSR 增強）」，但使用者已經明說對 HBM/SerDes 有興趣，`agent5_hbm_notes.md` §3 也指出那類應用的關鍵是 MHz–百 MHz 的 PSRR。這不是「可能出現的新資訊」，而是**已經存在的條件**，應該直接評估。

### 4.1 PMOS pass（A1）的旋鈕都救不了 1–10 MHz（`r2_8_clock_ldo.py`，10 mA 負載）[X]

| 設定 | PSRR 1 k / 100 k / 1 M / 10 M / 100 MHz (dB) |
|---|---|
| Wp 4 mm、100 pF、1.6 V（現行 REF-A） | −51.7 / −28.1 / −8.7 / +0.6 / −1.6 |
| Wp 400 µm、100 pF、1.6 V | −33.1 / −23.5 / −5.3 / +0.3 / −2.7 |
| Wp 400 µm、1 nF（Cc 8 p、Rz 5 k）、1.6 V | −33.1 / −19.8 / −3.6 / −3.5 / −21.0 |
| Wp 200 µm、100 pF、1.2 V | −45.8 / −29.8 / −10.3 / +0.3 / −5.4 |
| Wp 200 µm、1 nF、1.2 V | −45.8 / −25.8 / −7.3 / −6.2 / −25.0 |

（我原本假設「依 10 mA 縮小 pass 可改善高頻 PSRR」，**不成立**：縮小後 pass 在 10 mA 進入 triode，gds 反而更大。）

### 4.2 NMOS source-follower pass（A4）（`r2_10_nmos_ldo.py`，最簡版、未最佳化）[X]

Vin 1.8 V、Vout 1.0 V、NMOS pass W=1000 µm、EA 同 REF-A 的 5T OTA、Cc 5 pF 接地、CL 100 pF：

| 負載 | DC 迴路增益 | PM | PSRR 1 k / 100 k / 1 M / 10 M / 100 MHz (dB) |
|---|---|---|---|
| 0 | 33.1 dB | 73.6° | −34.4 / −34.2 / **−26.7 / −19.1** / −37.7 |
| 1 mA | 32.0 dB | 86.8° | −33.1 / −32.9 / **−26.4 / −16.8** / −24.3 |
| 10 mA | 22.7 dB | 92.8° | −24.2 / −24.2 / **−22.6 / −16.7** / −17.1 |

- 1–10 MHz 比 PMOS 版好 **15–20 dB**。低頻較差，是因為這個 EA 沒有最佳化（輸出接 Vin 參考的 PMOS mirror），可另外改善 [D]。
- **代價：headroom**。NMOS pass（body 接地、無 deep N-well）供 10 mA（W=400 µm）需要的閘極電壓：Vout 1.6 V → **2.38 V**；1.2 V → 1.89 V；1.0 V → 1.65 V；0.8 V → 1.41 V [X]。Vin 1.8 V、Vout 1.6 V 的規格下，NMOS pass 必須加 charge pump（時脈電路，增加風險）或用 native/3.3 V 元件。所以「A＋PSR 增強」在現行規格下**不是小改**，必須同時改規格。
- Jitter 換算（沿用 X5：TIE 與供電漣波成線性，解析與模擬差 ≈1%）[D]：Vin 加 10 mV@1 MHz，無 LDO 時 925 ps，經 REF-A（−8.6 dB）為 335 ps，經 NMOS pass 版（1 mA 時 −26.4 dB）約 **44 ps**，好約 7.6 倍。

### 4.3 建議
- 若教授要應用動機：題目改成「時脈／VCO 供電用、高中頻 PSRR 的 capless LDO」。規格改為 Vout ≈ 1.0–1.2 V、Imax 5–20 mA、CL 100 pF–1 nF，主要指標是 PSRR(f)、輸出雜訊，以及 ring oscillator 的 TIE/spur（可片上量）。首選子類 = **A4 NMOS-pass**（或 PMOS＋A5 feedforward，但 GAPS G3 已指出 0.18 µm、1.8 V 的 A5 有人做過）。這個方向的類比純度比 A1 更高，沒有理由轉向 B/C。
- 若教授要求維持 1.6 V、100 mA：就不要宣稱 HBM/SerDes 動機。A1 在 ≥1 MHz 沒有供電隔離能力（REF-A 在 10 MHz 是 +1.3 dB）。

---

## 5.【需修正】v2 列的兩個「B 的真實優點」在學生量測情境下站不住

### 5.1 高溫輕載漏電：主要是 PTM PMOS 的低 Vth 造成（`r2_6_ptm_leak.py`、`r2_7b_hot.py`）[X]

PTM PMOS（L=0.18 µm、W=10 µm）的特性：
- 定電流 Vth（|Vsd|=0.05 V）：TT 27 °C 0.324 V、SF 27 °C 0.274 V。DIBL 41–50 mV/V。
- Ioff（Vsd=0.2 V）：TT 27 °C 0.23 nA/µm、TT 125 °C 9.5 nA/µm、SF 125 °C 25 nA/µm（4 mm → 101 µA）。
- 一般 1.8 V 0.18 µm logic 製程的 \|Vtp\| 常見 0.4–0.5 V，Ioff 在 pA/µm 等級 [H，審查者記憶，未查證]。PTM 很可能低了 0.1–0.2 V，漏電因此高 1–2 個數量級。
- 另外，模型卡寫的是 `lmin=lmax=0.18 µm`（只擬合 L=0.18），EA 與偏壓用的 L=1 µm 元件都是外插（第 1 輪只提到 wmax）。

SF-like 125 °C、零載、200 µA 洩放時的 Vout，對 PMOS Vth 再平移的敏感度：

| \|Vthp\| 額外 +ΔV | 0 | +50 mV | +100 mV | +150 mV |
|---|---|---|---|---|
| Wp 4 mm | **1.6525（+46 mV）** | **1.6139** | 1.6091 | 1.6073 |
| Wp 8 mm | 1.7346 | 1.6237 | 1.6109 | 1.6084 |

\|Vthp\| 只多 50 mV，A 的「失效」就回到和 TT 125 °C（1.614）相同的水準。這是 PDK 相依的設計檢查項，不是架構差異。而且學生是在**室溫**的實驗桌上量 1–5 顆晶片，125 °C 本來就不在量測範圍內。

（附帶確認 [X]，`r2_7_vth_real.py`：\|Vthp\| +150 mV 時，4 mm pass 仍能供 100 mA（pg 從 1.128 V 降到 0.974 V），最差 PM 66.9°，但會用掉 buffer 的下擺幅。A 的穩定度不受影響，只是 headroom 減少。）

### 5.2 DC load regulation（B 0.5 mV vs A 6–13 mV）在量測上看不出來 [D/H]
- 片上 IR：第 3.1 節估計 Vout 匯流排有 20–80 mV [H]；load 的 GND bond wire 50–100 mΩ [H] × 100 mA = 5–10 mV。
- 熱：100 mA × 1.6 V = 160 mW 集中在片上負載。等效半徑 11 µm 的熱源（約 20×20 µm²）的擴散熱阻 ≈ 1/(4·k_Si·a) ≈ 154 K/W → 局部 +25 °C，時間常數 a²/D ≈ 1.3 µs（5 µs 的負載脈衝就幾乎達到穩態）。若分散成約 100×100 µm²，降到 30 K/W（+5 °C）[D]。EA 離熱源 50 µm 時，輸入對兩側溫差約 1.4 K，對應 ~2.8 mV offset ×(1/β)=2 → **~5.5 mV**；離 200 µm 時降到 ~0.35 mV [D，點熱源半無限近似]。
- 所以 0.5 vs 6–13 mV 的差距必須靠 Kelvin 取樣、負載與 EA 分開地、EA common-centroid 且遠離負載才看得到。否則量到的是佈局，不是架構。

**建議**：v2 首選說明的「B 的優點」改成「DC load regulation 理論上較好（需 Kelvin 佈局才量得出）；高溫漏電優勢依賴 PTM 的低 \|Vthp\|，換真實 PDK 前不應列為優點」。這兩點修正對 A **有利**，但結論應該照實寫。

---

## 6.【需修正】G1：做為量測設計有價值，做為「研究缺口」偏弱

### 6.1 新穎性
- 「負載邊沿時間改變 ΔV 與 FoM 排名」已被正式處理過：Guo & Leung（JSSC 2010，90 nm capless LDO）的 FoM 引入了邊沿時間校正因子 K [審查者記憶，未查證]；repo 的 Seok 資料集本身就有 t_edge 欄位，GAPS 也提到「edge-adjusted FoM」。
- 「片上量 supply droop」有成熟的前例：Alon、Stojanovic、Horowitz（JSSC 2005）的片上電源雜訊取樣量測 [審查者記憶，未查證]。片上負載開關在 capless LDO 論文中也很常見 [H]。
- 用**一顆** LDO 只能示範「同一電路的 ΔV 隨邊沿改變」，這已經在模擬（748 vs 21 mV）和資料集（X. Wang 185 vs 88 mV）裡了。要示範「FoM 排名改變」，片上至少要有**兩個**變體。

### 6.2 1 ns 角落需要很貴的監測 buffer（`r2_9_monitor.py`）[X]
輸入是 REF-A 0→100 mA 的真實 Vout 波形（1 ns 邊沿 droop 742 mV）。buffer 用 NMOS source follower（汲極接獨立 1.8 V，DC 增益 0.83）。下表是 buffer 輸出看到的 droop 除以 0.83，再除以真實 droop：

| C_pad＋封裝＋探棒 | I_b = 0.3 mA | 1 mA | 3 mA | 10 mA |
|---|---|---|---|---|
| ~4 pF（主動探棒）[H] | 54% | 82% | 97% | 98% |
| ~13 pF（10× 被動探棒）[H] | 48% | 54% | 79% | 97% |
| 100 ns 邊沿（13 pF） | 89% | 96% | 99% | 100% |

1 ns 角落要 3–10 mA 的 buffer 偏壓（負載電流的 3–10%，而且要獨立電源與地），外加 ≥1 GHz 的探棒。G1 規劃的「片上 buffer vs 直接 pad 對照」在 1 ns 時主要量到的是量測治具的頻寬，不是 LDO。

### 6.3 量測陷阱：Vout 腳位的板上電容（`r2_12_offchip.py`）[X]
Vout pad 經 2 nH＋0.1 Ω 接到板上電容 C_ext（ESR 10 mΩ）時，REF-A 在 0/1/10/100 mA 的最差 PM：

| C_ext | 0 | 10 pF | 1 nF | 10 nF | 100 nF | 1 µF |
|---|---|---|---|---|---|---|
| 最差 PM | 67° | 65.5° | **30.1°** | **18.7°** | **20.8°** | **30.6°** |

「每個電源腳都加去耦電容」是常見習慣，但會把 capless LDO 推到邊緣穩定。量測板規格要寫明：Vout 只接高阻抗監測，不加去耦；DC load regulation 也要用片上負載量，不接外部電子負載。A、B 都一樣。

### 6.4 片上負載本身：D-007 成立，但「100 mA」不受控（`r2_4_nmos_load.py`）[X]
- NMOS 開關負載（W=139 µm、Vgs 1.8 V，TT 27 °C 時 100 mA）在 Vout 1.6→0.8 V 時只從 100 降到 88.6 mA。0→100 mA 的 undershoot 與理想電流源相比：1 ns 715 vs 742、10 ns 467 vs 450、100 ns 225 vs 236 mV（差 ≤4%）。所以 **D-007（以理想電流源模擬）成立**。
- 但同一顆負載在不同 corner／溫度（27–75 °C）下電流是 87.5–105.5 mA。ΔI 必須另外量（例如負載 GND 獨立 pad＋感測電阻，或片上 replica）。

### 6.5 建議的 G1 改寫
- 定位改為「**量測設計與手算—模擬—量測對照**」，不要寫成研究缺口。這對大學部專題反而更有價值：教授要看的是「做得出、量得到、解釋得了」。
- 邊沿矩陣改為 ~10 ns / 100 ns / 1 µs。1 ns 改成選做（需要 ≥3 mA buffer 與主動探棒）。
- 若要示範「排名隨邊沿改變」，片上放兩個**都穩健**的變體。REF-A 100 pF（Cc 5 p）vs 1 nF（Cc 20 p），兩者 Rz 都是 0：1 ns 時 742 vs 497 mV（1 nF 好 33%），100 ns 時 236 vs 346 mV（100 pF 好 32%），1 µs 時 111 vs 151 mV [X]。排名翻轉明顯，而且不用冒 Rz 的風險（代價是 ~0.12 mm² 的 MOS 電容）。

---

## 7.【小問題】Vref、偏壓來源未定

- v2 的 A 規格沒有寫 Vref 怎麼產生。片上 bandgap 會加入 start-up 風險、低頻 PSRR 地板，以及雜訊 ×(1/β)=2 [H]。最低風險的做法是 **Vref 由 pad 外部提供**（可選加一顆片上 reference 當對照），還能順便量 Vref→Vout 的轉移。
- 10 µA 偏壓若由電阻定義，絕對值 ±20–30% [H]。第 2 節顯示這直接影響 Rz 設計的穩定度（gm1 上限）。建議 constant-gm 偏壓，或外部偏壓 pad。

---

## 8. 結論 v2 的內部一致性清單

| v2 的敘述 | 問題 | 依據 |
|---|---|---|
| 首選規格「Miller＋nulling resistor」 | 第 1 輪採用的 Rz=10 kΩ 在冷角＋寄生會振盪；Rz 要限制在 β·gm1,max·Rz ≤ 0.3，或用 Rz=0 | §2 |
| 理由 3「B/C 在 MHz–百 MHz PSRR 結構性吃虧」 | 10–100 MHz 時 A 與 B 都是 0 dB | §1 |
| B 的優點「DC load regulation、高溫漏電」 | 前者被 IR/熱蓋住；後者依賴 PTM 的低 \|Vthp\| | §5 |
| 「會改變建議的新資訊：PSRR 為主要指標（→ A＋PSR 增強）」 | 使用者已表示 HBM/SerDes 興趣，這是已知條件；而且在 Vout 1.6 V 下「PSR 增強」需要 charge pump 或改規格 | §4 |
| 首選沒有寫設計點（Imax、Vout、CL） | Imax=10 mA 時 B 沒有意義；100 mA 在 200 mV dropout 時對 Vin 容差極敏感 | §3 |
| 「最大風險：1 ns 級快邊沿 undershoot」 | 這是規格與物理（ΔI/CL），與架構無關；而且需要 3–10 mA 的 buffer 才量得到。真正的最大風險是補償在寄生與 corner 下的穩健性，以及 dropout/headroom | §2、§3、§6.2 |
| 「首選/備案順序取決於教授是否要求 hybrid」列為第一題 | 規格（Vin 來源、Vout、Imax、主要指標）對方案的影響更大，應排第一 | §3、§4 |
| 「Vin 可用 3.3 V」列為會改變建議的資訊 | 方向沒寫。3.3 V 會讓 NMOS-pass（A4）變可行，所以是改變 A 的**子類**，不是讓首選變 B | §4.2 |

---

## 9. 檢查過但沒有發現問題的項目（避免只報壞消息）

| 檢查 | 結果 |
|---|---|
| 片上 NMOS 負載 vs 理想電流源（D-007） | undershoot 差 ≤4%，成立（§6.4） |
| PM 對 PTM 模型參數（NFactor、Pclm、U0、Cgdo、Eta0）| 三種補償都只變 ±2.5°（§2.2a） |
| \|Vthp\| +150 mV（較接近真實製程 [H]） | 4 mm pass 仍能供 100 mA，PM 66.9°（§5.1） |
| REF-A（Rz=0）在所有 corner、被動、寄生組合下 | PM ≥59.0°、GM ≥14.8 dB |
| 較大 dropout 或較低 Imax 會不會讓首選變 B | 不會，反而更有利於 A（§3.2） |

---

## 10. 建議的結論改寫（可替換 v2 對應段落）

> **首選：A 純類比 capless LDO（類別不變），但具體配置與規格要先確定。**
> - 先問教授（依序）：(1) Vin 來源與容差、Vout 是否一定是 1.6 V、Imax 是否一定是 100 mA、主要指標是暫態還是 PSRR/jitter；(2) 是否要求 hybrid。
> - **若維持 1.8→1.6 V、暫態為主**：A1（NMOS 輸入 EA → PMOS SF buffer → PMOS pass），**Miller 補償 Rz=0 為基準**（所有 corner/寄生組合 PM ≥59°、GM ≥15 dB）。若加 Rz，必須滿足 β·gm1,max·Rz ≤ 0.3（約 3 kΩ），而且 MIM 底板接 Vout。1 nF 只在 ns 級邊沿較好。Vin 必須由實驗室電源提供（≥1.75 V），Vout 用 Kelvin 取樣。Vref 由 pad 外部提供。
> - **若教授要應用動機（HBM/SerDes 時脈供電）**：改規格為 Vout 1.0–1.2 V、Imax 5–20 mA，子類改 **A4 NMOS-pass**（1–10 MHz PSRR 比 A1 好 15–20 dB）。以 PSRR(f)、輸出雜訊、片上 ring oscillator 的 TIE 為主要量測。
> - 理由：(1) A 與合理設計的 B 性能接近；B 要贏暫態需要脆弱的非同步路徑（第 1 輪）；(2) ≤100 kHz 的 PSRR A 好 8–14 dB，≥1 MHz 兩者都差，由 CL 或子類決定；(3) B 的 DC 精度優勢量測上被 IR/熱蓋住，高溫漏電優勢是 PTM 相依；(4) 較大 dropout 或較低 Imax 都讓 A 更有利。
> - **最大風險**：補償對佈局寄生與偏壓偏移的穩健性（只有 LTspice、沒有 PEX）；200 mV dropout 的 headroom（Vin 容差＋片上 IR）；量測治具（Vout 腳不可加去耦、1 ns 需 ≥3 mA buffer）。

---

## 11. 重現方式

```
cd review/round2_a_files        # 或 scratch 目錄；腳本會寫到同目錄下的 res/
python3 r2_1_psrr_hf.py         # §1  A vs 公平 B 的 PSRR 1 kHz–100 MHz
python3 r2_2_vin_tol.py         # §3.1 Vin 容差 × corner × Wp
python3 r2_3_vout_alt.py        # §3.2 Vout 1.6/1.4/1.2 V
python3 r2_11_dropout_AB.py     # §3.2 較大 dropout 時 A vs B 的 PSRR
python3 r2_4_nmos_load.py       # §6.4 NMOS 片上負載 vs 理想電流源
python3 r2_5_robust.py          # §2.2a 三種補償 × corner/模型參數/被動/寄生
python3 r2_5b_parasitic.py      # §2.2b ea 與 Rz–Cc 中點寄生
python3 r2_5c_verify.py         # §2.2b 時域振鈴頻率驗證
python3 r2_5d_window.py         # §2.3 1 nF 的 Cc×Rz 窗口
python3 r2_5e_tran.py           # §2.2c 冷角持續振盪＋穩健點暫態
python3 r2_5f_100p.py           # §2.2c 100 pF 設計的冷角
python3 r2_5g_100p_tran.py      # §2.3 100 pF 穩健 Rz 的暫態
python3 r2_5h_gm1.py            # §2.1 gm1 與 β·gm1·Rz
python3 r2_6_ptm_leak.py        # §5.1 PTM PMOS Vth/DIBL/Ioff
python3 r2_7_vth_real.py; python3 r2_7b_hot.py   # §5.1 |Vthp| 平移
python3 r2_8_clock_ldo.py       # §4.1 PMOS pass 的 PSRR 旋鈕與 NMOS 閘極需求
python3 r2_9_monitor.py         # §6.2 監測 buffer
python3 r2_10_nmos_ldo.py       # §4.2 NMOS-pass LDO
python3 r2_12_offchip.py        # §6.3 Vout 腳的板上電容
```

`common.py` 的 `MODEL` 寫死為 `/home/user/abc/ldo-research/sim/models/180nm_bulk.pm`，`RES`／`NET` 是腳本目錄下的 `res/`、`net/`。每個腳本在 ngspice-42 上都在 15 秒內跑完。結果 json 在 `review/round2_a_files/res/`（只放 `r2_*.json`，沒有波形）。
