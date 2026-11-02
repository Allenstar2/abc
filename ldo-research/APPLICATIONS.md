# 應用背景：HBM 與高速 SerDes 中的 LDO（使用者追加主題）

> **證據限制**：學術網站被網路政策擋（D-009），本章所有文獻**都只讀到搜尋摘錄（僅摘要）**；專利、廠商文件、二手報導只放在 `lit_raw/agent5_hbm_notes.md`（HBS1–HBS13）與 `lit_raw/agent6_serdes_notes.md`，不當主要依據。
> [X] 為本次模擬（PTM 180nm，只看趨勢）。

## 1. 一句話結論

HBM 與 SerDes 的 LDO 文獻同時在意兩件事：**droop/settling**（HBM 介面 LDO 的標題指標，HB05–HB07）與**中高頻供電雜訊造成的 jitter**（HB08–HB09、SD03、SD10）。對 SerDes 時脈而言，後者（MHz 級 PSRR＋低雜訊）是主要規格 [H，agent6 綜合 SD10、SD03]。
這**不改變首選架構（A 純類比）**，但改變**評估指標與設計重點**：專題若要掛這兩個應用，應該把「PSRR 對頻率曲線」與「供電漣波 → jitter」列為主要量測，而不是只比 undershoot。

## 2. HBM（agent5，12 篇＋13 補充來源）

### 2.1 讀到的事實（僅摘要/公開新聞稿）
| 項目 | 內容 | 來源 id |
|---|---|---|
| 電源 rail | HBM2E：VDDQ、VDDC 1.2 V；HBM3：1.1 V，host 介面 0.4 V low-swing；HBM4：VDDQ 0.7–0.9 V（vendor-specific）、VDDC 1.0/1.05 V | HB03、HB01、HB02 |
| HBM 介面專用 LDO 論文 | 只找到首爾大學團隊三篇：ISSCC 2025 command-aware hybrid LDO（標題：Iq 150 µA、20 pF、droop <10 mV、settling 400 ps）、JSSC 2026 期刊版、CICC 2026 strobe-triggered digital LDO＋local replica regulators（droop 10.7 mV、settling 1.4 ns）。製程、負載電流、電路架構**都沒讀到** | HB05、HB06、HB07 |
| 問題本質 | HBM I/O 的 PSIJ 由 VDDQ PDN、多通道同時切換、clock 經 3–5 級 buffer 的供電敏感度疊加而成；高頻 PSIJ 是主要挑戰 | HB08、HB09、HB12 |
| 替代路線 | interposer-level IVR（模擬）、regulator 位置比較（越靠近負載越好） | HB10、HB11 |

### 2.2 對專題的意義
1. **1.6 V 不是 HBM rail**（HBM rail 0.4–1.2 V）。專題不能說「做 HBM 用 LDO」，只能說「以 HBM PHY 的 clock/IO 供電需求為動機的 0.18 µm 縮放示範」。
2. HBM 文獻的 LDO 是 hybrid/digital，但其優勢建立在「controller 事先知道 command/strobe 時序」與先進製程速度上（HB05、HB07 標題）。單獨下線的學生 LDO 沒有 memory controller → hybrid 的主要好處用不到 [H，agent5]。
3. HB05 用 20 pF 換 400 ps settling；學生在 0.18 µm 用 100 pF–1 nF。一階 droop ≈ ΔI·t/C：本次 REF-A 在 100 pF、1 ns 邊沿 100 mA 步階量到 742 mV [X]——ps 級反應在 0.18 µm 不可行。
4. 可借用的評估方式：週期性 burst 負載（片上負載開關用外部方波驅動）、多負載同時切換、PSRR 曲線看中高頻。這些都不需要數位控制。
5. 可選延伸 [H，agent5 構想，非 HB05 電路]：外部 trigger 腳在負載切換前預先加大 EA/buffer 偏壓（類比 feedforward），模仿 command-aware 概念；量測時可關掉對照。

## 3. 高速 SerDes（agent6，15 篇：SD01–SD15）

### 3.1 讀到的事實（僅摘要）
| 位置 | 內容 | 來源 id |
|---|---|---|
| PLL/VCO/ring oscillator 供電（最常見） | >100 Gb/s link 的 ring PLL 用 supply-regulated 架構，50 mVpp 漣波下 spur < −54 dBc、immunity 改善 31.4 dB [M] | SD03（JSSC 2026） |
| 從 VCO 推 LDO 規格（教學） | 5 GHz LC VCO 的 LDO：PSRR 40 dB 撐到 10 MHz、雜訊 50 nV/√Hz @1 MHz、PN 惡化 ≤1 dB、≤1 mW | SD10（Razavi，SSC Magazine 2022） |
| TX driver | 112 Gb/s PAM4 TX 擺幅由外接 LDO 設定；10.24 Gb/s TX 晶片內 capless LDO（PSRR −50 dB <1 MHz，轉述） | SD02、SD11 |
| RX front-end | 只找到 SiGe 224 Gb/s 的 dual-loop regulator | SD12 |
| 0.18 µm 例子 | supply-regulated PLL（1.8 V，2.4 GHz，3.29 ps rms，注入 50 mV supply tone）[M]；180 nm LDO＋5 級 RO（**只有模擬**） | SD14（2006，背景）、SD04 |
| 反面/限制 | regulator 吃 headroom（低壓先進製程）；LDO 耗功率面積；用 adaptive filter 取代 LDO（LPDDR5 clock，27.84→4.28 ps rms）；180 nm 補償電路不用 LDO | SD07、SD01、SD13、SD06 |

### 3.2 對專題的意義
1. **SerDes 時脈 rail 的 LDO 主要用途是換低 jitter（寬頻 PSRR＋低雜訊＋mW 級功耗），不是應付大負載暫態** [H，agent6 依 SD10、SD03 摘要綜合；TX driver 的 LDO（SD02、SD11）另有擺幅設定用途]。
2. **電流不匹配**：SerDes 時脈 rail 是 mW 級（SD10 ≤1 mW、SD09 320 µW），學生的 10–100 mA 比較像整個 TX/多 lane。建議 ring oscillator 只當數 mA 的示範負載，另放 10–100 mA 可程式負載 [H，agent6]。
3. **不要包裝成「SerDes LDO」**：0.18 µm 例子都在 2.5 GHz 以下（SD14、SD15）。
4. **headroom 批評在 0.18 µm 較弱**：SD07 的批評針對 ~1 V 製程；1.8→1.6 V 相對寬裕，但 200 mV、100 mA 需要大 PMOS（本專案 4 mm）。
5. **「LDO 供電片上 RO、量 supply-induced spur」**：在 PLL 論文裡常見（regulator 屬於 PLL 的一部分）；以「獨立類比 LDO＋RO 當應用負載」為題最接近的是 SD04（180 nm，只有模擬）。2014 後**沒找到** 0.18 µm 實測——可當區隔點，但**不能宣稱首創**（只有摘要、搜尋 42 次）。→ GAPS.md G6。
6. **與 X5 模擬的關係**：在窄頻 FM（調變指數 β = Kvdd·A/f_m ≪ 1）時，有/無 LDO 的 spur 差等於該頻率的 PSRR [D]。X5 在 1 MHz 的 β 已達 4.4（無 LDO）與 1.6（經 LDO），**不在窄頻區**，所以改用 TIE 比：925/335 ps ≈ 2.76 倍 = 8.8 dB，與該負載 PSRR −8.6 dB 一致（TIE 與漣波振幅成正比，不受 β 限制）[X]。要用 spur 量 PSRR，VCO 上的漣波需小到 β ≲ 0.2：1 MHz 時 < ~0.45 mV、100 kHz 時 < ~45 µV（Kvdd=440 MHz/V）[D]。

## 4. 本次模擬：供電漣波 → ring oscillator jitter（X5，`sim/scripts/s10_vco_supply.py`）

目的：把「LDO 的 PSRR」和 SerDes/HBM 在意的「jitter」用 0.18 µm 可做的電路接起來，並做手算 vs 模擬對照。

**電路**：7 級 inverter ring（Wn/Wp = 1/2.5 µm、L = 0.18 µm、每節點 30 fF），由 REF-A（CL = 100 pF）供電；對照組直接接理想 1.6 V。
**ring 特性** [X]：f0 = 764 MHz @1.6 V；f(1.5/1.55/1.6/1.65/1.7 V) = 718/742/764/786/806 MHz → **Kvdd ≈ 440 MHz/V**；平均電流 0.43 mA。

**解析** [D]：供電漣波 A·sin(2πf_m t) → 頻率調變 Kvdd·A → 相位 φ = (Kvdd·A/f_m)·sin(·) → **峰值 TIE = Kvdd·A/(2π·f_m·f0)**。（調變指數 β = Kvdd·A/f_m；β ≪ 1 時旁波 ≈ 20log(β/2) dBc。1 MHz 時 β > 1，旁波公式不適用，以 TIE 為準。）

**Vin 漣波 10 mV，結果**：
| f_m | 路徑 | VCO 上的漣波振幅 | 峰值 TIE 解析 | 峰值 TIE 模擬 | 誤差 |
|---|---|---|---|---|---|
| 1 MHz | 無 LDO（漣波直接上 VCO） | 10 mV | 916 ps | 925 ps | +1.0% |
| 1 MHz | 經 REF-A（PSRR −8.6 dB） | 3.70 mV（模擬 p-p 7.4 mV） | 339 ps | 335 ps | −1.0% |
| 100 kHz | 經 REF-A（PSRR −28.3 dB） | 0.39 mV | 354 ps | — | — |
| 10 MHz | 經 REF-A（PSRR **+1.3 dB**，放大） | 11.6 mV | 107 ps | — | — |

**解讀**：
1. 手算與共模擬差 ~1%，說明「PSRR(f) × Kvdd → jitter」這條鏈可以用手算預測 [X/D]。
2. 簡單 capless LDO（REF-A）在 1 MHz 只擋 8.6 dB、10 MHz 甚至放大。**對迴路頻寬低於 ~1 MHz 的 PLL**，這正是 PLL 壓不住、最需要 LDO 擋的頻段 [H]；但高速 SerDes 的 ring PLL 頻寬可 >100 MHz（SD03，agent6 §4.2），那時關鍵頻段更高，0.18 µm 的類比 LDO 只能靠 CL 分流。
3. 自由振盪 ring 的 335 ps TIE 對 764 MHz（週期 1.31 ns）是巨大的；實際 SerDes 有 PLL，數字只用來比較 LDO 的相對效果。
4. **這是學生做得到的「應用示範」**：片上放一個由 LDO 供電的 ring oscillator（或 inverter delay line），量測時在 Vin 注入漣波、用頻譜儀看 spur 或用示波器量週期抖動，間接量到 LDO 在 MHz 的 PSRR。是否已有人做過、新穎性如何，見 §3 與 GAPS.md 更新。

## 5. 對首選/備案的影響（agent6 已回報；agent7 PSR 技術待補）

| 若教授想要的應用動機 | 首選 | 設計重點 | 主要量測 |
|---|---|---|---|
| 無特定應用（一般 SoC） | A | 輕載穩定、暫態（片上負載、3 檔邊沿） | 負載/線性暫態、PSRR、Iq、dropout |
| HBM 介面 | A（＋可選類比 feedforward trigger） | 中高頻 PSRR、burst 負載 | PSRR 曲線、burst droop |
| SerDes/clock | A 的子類要換：**NMOS-pass**（審查者模擬 1–10 MHz PSRR 比 PMOS-pass 好 15–20 dB，`review/round2_a_files/res/r2_10_nmos_ldo.json`，作者未重現），代價是 Vin 1.8 V 時 Vout 要降到 ~1.0–1.2 V，或用 charge pump 讓閘極到 ~2.4 V；若維持 PMOS pass，則加 PSR 增強（見 §6）；Imax 可降到數 mA–10 mA 以符合時脈 rail 的電流量級（注意：W 等比縮小時 PSRR 本身不變，`s8_sensitivity.json`；PSRR 要靠 PSR 技術或較大 dropout）[X/H] | 1–100 MHz PSRR、輸出雜訊（SD10：40 dB 至 10 MHz、50 nV/√Hz） | PSRR 曲線、ring oscillator spur/TIE（有/無 LDO 對照） |

## 6. 若教授以 PSRR 為主要指標：PSR 增強技術（agent7，12 篇：PS01–PS12）與本次驗證

### 6.1 文獻整理（僅摘要）
| 技術 | 0.18 µm 證據 | 在 1.8→1.6 V、無 Verilog 下的可行性 |
|---|---|---|
| Feedforward／replica ripple 抵消（PMOS pass 不變） | A01（0.18 µm、1.8 V，優於 −56 dB 至 4 MHz @50 mA [M]）；PS04（0.18 µm，改善最高 40 dB，Iq 33 µA [S]） | 高：純類比、不吃 dropout [推論，agent7] |
| Negative capacitance | PS09（0.18 µm，−76 dB @1 MHz [M]，電路未讀到） | 中：要讀全文 |
| NMOS pass＋charge pump | A04、PS06（180 nm，−40 dB @1 MHz @100 mA） | 低-中：1.8→1.6 V 時閘極需高於 Vin，必須 charge pump；氧化層耐壓要查 PDK |
| 兩級 pass | PS10（200 mV dropout，只報到 100 kHz） | 中：200 mV 要拆給兩顆 |
| 限制 | PS03（Rincón-Mora 2021：series feedback 是最佳折衷）；PS06 PSR 隨負載變差 15 dB；PS11、A03 都要 adaptive | — |

agent7 的建議：保留 PMOS pass，加 replica/feedforward（A01/PS04 型）＋依負載調整的 adaptive 偏壓。

### 6.2 本次推導與理想行為級驗證（X6，`sim/scripts/s14_ff_psrr.py`）
推導 [D]（由第 1 輪審查 (c) 的精確式延伸）：
```
PSRR_LF = R_o·[gds_p + gm_p·(1 − α_pg)] / (1+T0)   →   完全抵消需要 α_pg = 1 + gds_p/gm_p
```
REF-A 的 gds_p/gm_p：零載 0.051、10 mA 0.074、100 mA **0.75**（triode）[X，OP]。所以需要的「過追蹤」量隨負載變 15 倍——**在 200 mV dropout 的規格下，固定增益的 feedforward 不可能跨負載抵消**，這解釋了為什麼文獻都要 adaptive（PS01、PS11、A03）。

驗證：在 pg 注入理想 VCCS I = gff·(Vin−1.8)（只有 AC），掃 gff [X]：
| gff (mS) | 0 mA：1 kHz / 1 MHz | 10 mA：1 kHz / 1 MHz | 100 mA：1 kHz / 1 MHz |
|---|---|---|---|
| 0（REF-A） | −55.3 / −8.3 dB | −51.7 / −8.7 | −33.3 / −5.3 |
| 0.06 | **−68.6** / −8.9 | −59.8 / −9.2 | −34.0 / −5.6 |
| 0.1 | −57.8 / −9.3 | **−68.5** / −9.5 | −34.5 / −5.8 |
| 1.0 | −31.2 / **−27.9** | −32.2 / **−29.0** | −46.0 / −12.7 |

解讀：
1. 低頻最佳 gff 隨負載移動（0 mA 在 0.06 mS、10 mA 在 0.1 mS、100 mA 要 ≥1 mS）——印證上面的推導 [X/D]。
2. 1 MHz 要大很多的 gff（1 mS）才有 ~20 dB 改善，而且會讓輕載的 1 kHz 變差（過度抵消）。合理做法是讓 feedforward 路徑**只在迴路 UGF 以上作用（high-pass）**，低頻交給迴路增益 [D，未模擬]。
3. 滿載 1 MHz 即使 gff=1 mS 也只有 −12.7 dB：triode 下的 gds_p 太大，是本規格的根本限制 [X]。
4. 這是理想 VCCS，不是電路；實作要考慮 replica 的頻寬、匹配、Iq。**這組數字只用來說明方向，不是可達到的設計值。**
