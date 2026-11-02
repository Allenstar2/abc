# Round 1（a）對抗審查：試圖推翻「首選 A」

> 審查對象：`CONCLUSION_DRAFT.md`（輔以 `ANALYSIS.md`、`ARCH_MATRIX.md`、`DECISIONS.md`、`LOG.md`、`sim/scripts/ldo_ref.py`、`ldo_hybrid.py`、`s5_exp_hybrid.py`、`sim/results/x3_hybrid.json`、`s3_refA_char.json`）。
> 我自己的模擬全部在 scratch（`/tmp/claude-0/-home-user/24b1423c-959f-5794-9f98-bbcbade8908e/scratchpad/review_r1a/`），**沒有修改 repo 內任何既有檔案**。`common.py`、`ldo_ref.py` 複製到 scratch，只把輸出路徑改到 scratch；`hyb2.py` 是 `ldo_hybrid.py` 的擴充版（加 droop 路徑、slice 開／關邊沿分開設定、Wa 可調）。模型仍用 `sim/models/180nm_bulk.pm`（PTM，只看趨勢）。
> 證據標註沿用 repo：[X] 本審查的 ngspice 模擬、[D] 推導、[H] 推測。

## 0. 先確認基準可重現

`python3 r0_baseline.py`：REF-A 5→95 mA undershoot **498.9 / 127.5 mV**（1 ns / 100 ns 邊沿），REF-B（10 MHz）**756.2 / 313.1 mV**，和 `x3_hybrid.json` 完全一致 [X]。以下的比較都用同一個測試條件（CL=100 pF、Cc=5 pF、200 µA 洩放、理想電流源負載），只改我標明的參數。

---

## 1. 總判定

| 問題 | 判定 |
|---|---|
| 首選 A 是否要改？ | **不改，但理由要大改。** 對這位學生（一次下線、只有 LTspice），A 仍然是整合風險最低的選擇。 |
| 結論草稿的理由 2（「B 313 vs 127 mV、PSRR 差 19 dB」）| **推翻（作為架構比較）。** 這些數字只描述 Wa=800 µm 的 B。合理設計的 B（Wa=2.4 mm）差距只剩 11–21% 和 8 dB。 |
| 理由 1（教授偏類比、無 Verilog）| **需修正。** 依草稿自己的分類，B 也是「類比主導」；B 的數位部分是 8 個 DFF＋33 個閘，和學生做過的東西同一等級。這條理由分不出 A 和 B。 |
| 理由 3（A 的風險都能用類比手段處理）| **需修正。** 沒有驗證過，而且對 A、B 不對稱：A 用尚未模擬的 SRE 抵帳，B 的修法卻被記成成本。我量化了其中一項代價：高溫輕載要把洩放加大 4 倍。 |
| 「1 nF 慢邊沿反而較差」| **需修正。** 只在 Rz=0 時成立。加一顆 nulling resistor 後慢邊沿幾乎一樣，1 ns 邊沿 1 nF 好 2 倍。 |
| C 的排除 | **小問題。** 排除本身成立，但「量化漣波」的論證只適用於 8 片的粗 slice。 |

A 真正站得住的理由和草稿寫的不同：**B 加上任何快速（非同步）路徑後，會出現新的雙迴路 limit cycle，而且對閾值非常敏感**（第 3 節）。B 不加快速路徑則可以穩，但暫態和 PSRR 仍比 A 差一截。

---

## 2.【推翻（理由 2 的數字）】REF-B 是稻草人：差距主要來自類比 pass 只有 800 µm

### 2.1 機制（推導）[D]

- **暫態**：負載快速上升時，Vout 的下降經 Cc 幾乎 1:1 耦合到 ea，再經 SF 傳到 pg（`dbg1.py`：100 ns 斜坡第 20 ns，Vout −177 mV、pg −185 mV [X]）。因此 undershoot ≈「pass 要供應 ΔI 所需的 ΔV_g」減去 EA 積分的貢獻。ΔV_g(ΔI) 大致 ∝ 1/W，所以 **pass 越窄，undershoot 越大**。這和數位時脈快慢無關。
- **PSRR**：類比 pass 在 triode 時 gm ≈ β·V_sd ∝ W（與電流幾乎無關），低頻 PSRR ≈ G_inj /(β·A_EA·A_SF·gm_a)。在相同 Vin、相同 EA 下，**A、B 的 PSRR 差 ≈ 20·log[(G_inj,B/gm_a,B)/(G_inj,A/gm_p,A)]**。

### 2.2 PSRR 拆解（`r2_psrr.py`、`r9`，70 mA、碼凍結）[X]

| 設定 | 類比 gm (mS) | 總注入 G_inj (mS) | 預測差距 | 模擬 PSRR@1 kHz | 模擬差距 |
|---|---|---|---|---|---|
| REF-A 4 mm | 352.6 | 145.9 | — | −38.2 dB | — |
| REF-B 原設定 Wa=800、碼 5（類比 ~9 mA）| 66.4 | 309.8 | 21.0 dB | −18.8 dB | 19.4 dB |
| 窗口上移：碼 4（類比 ~21 mA）| 69.4 | — | — | −19.6 dB | 18.6 dB |
| 窗口再上移：碼 3（類比 ~33 mA）| 64.8 | — | — | −19.0 dB | 19.2 dB |
| slice 閘極改接 Vin−1.8（診斷：去掉 gm·v_in 注入）| 66.4 | — | — | −19.6 dB | 18.6 dB |
| **Wa=1600、碼 4** | 137.6 | — | — | −25.6 dB | 12.6 dB |
| **Wa=2400、碼 3** | 208.0 | 236.7 | 8.8 dB | **−30.1 dB** | **8.1 dB** |

結論：
- 19 dB **不受**窗口位置影響（±0.8 dB）。slice 閘極接地帶來的 gm 注入也只佔 0.8 dB（slice 在深 triode，gm/gds≈0.10）。
- 差距**幾乎完全由 Wa 決定**：gm 比貢獻約 14.5 dB，slice 深 triode 的額外注入（每 mA 的電導比 A 的 pass 大）貢獻約 6.5 dB。推導預測與模擬相差 ≤1.6 dB。
- 1 MHz 時兩者都接近 0 dB（A −6.7、B800 −0.5、B2400 −4.1 dB），所以差距只在約 100 kHz 以下有意義。

### 2.3 面積較對等的 B：Wa=2.4 mm＋8×130 µm（總 PMOS 寬 3.44 mm，A 是 4 mm）

`r6_bigWa.py`：沿用原本的 gate-sensing、10 MHz、**不加任何 droop 路徑**，窗口 3–18 mA（VL=1.335 V、VH=1.455 V，由 `r6a_idvg.py` 的 I_D–V_G 求得）[X]：

| 5→95 mA undershoot | 1 ns | 100 ns | 1 µs |
|---|---|---|---|
| REF-A（4 mm）| 498.9 mV | 127.5 mV | 27.4 mV |
| REF-B 原設定（Wa=800）| 756.2 mV | 313.1 mV | — |
| **B，Wa=2400** | **552.9 mV（+11%）** | **153.7 mV（+21%）** | **32.9 mV（+20%）** |

- 20/45/70/95 mA 各平台都**沒有 limit cycle**（碼穩定、Vout p-p 0.0 mV）[X]。含降載的序列（5→95→45→20 mA，`r1g_bigWa_seq.py`）也全部通過，平均 Vout 1.5984–1.6013 V [X]。
- DC load regulation（20→95 mA）：B2400 **0.5 mV**、REF-B 0.46 mV，A **6.1 mV**（`r10` DC 掃描）[X]。
- PSRR@1 kHz（70 mA）：−30.1 vs −38.2 dB（見 2.2）。

**建議改寫**：把「313 vs 127 mV、PSRR 差 19 dB」改成「**Wa=800 µm 的 B** 比 A 差 2.5 倍／19 dB；把 Wa 提到 2.4 mm，差距縮到 11–21%／8 dB，代價是 B 的面積優勢幾乎消失」。草稿把「較小的類比 pass」列為 B 的好處，其實它正是 B 的暫態和 PSRR 變差的原因。

---

## 3.【需修正】「加 droop detector → 數位變複雜」的說法不對；真正的問題是交互作用造成的 limit cycle

我做了最便宜的非同步路徑：比較器輸出經 DFF 的非同步 **set** 端組成 ripple-set 鏈，`set_k = droop AND q_{k−1}`（AND 延遲 τ）。只需 1 顆比較器＋8 個 AND2，**沒有新時脈、不需要 Verilog**。所以「閘數變多」不是問題。（XSPICE 片段在 `hyb2.py` 的 `digital_block()`。）

但模擬結果顯示，**穩健性才是問題**（`r1_*.py`、`r1e_map.py`，5→95 mA，CL=100 pF）[X]：

| droop 偵測方式 | 100 ns undershoot | 穩態問題 |
|---|---|---|
| 不加（REF-B）| 313 mV | 無 |
| pg < 1.0 V（類比已飽和）| 308 mV | 無；pg 跟 Vout 一起掉，pg 到 1.0 V 時 Vout 已掉 280 mV，觸發太晚 |
| pg < 1.12 V | 253 mV | 無 |
| Vout < 1.57 V | 252 mV | **輕載弛張振盪 219–243 mV p-p**（負載小於一片電流時，開著的 slice 把 Vout 推到 Vin−I·R_on≈1.72 V，EA windup；最後一片關掉時又觸發 droop）。slice 慢關（300 ns／1 µs）也無法消除 |
| Vout<1.57 V **且** pg<1.20 V，t_off=300 ns | 184 mV | 20 mA 平台 **Vout 停在 1.695 V（+97 mV）**，3 片 slice 沒被移除 |
| 同上，pg<1.20 V，t_off=1 µs | 184 mV | 20 mA：132.8 mV p-p |
| 同上，pg<1.25 V，t_off=300 ns | 158 mV | 95 mA：62.2 mV p-p；20 mA 停在 1.695 V |
| 同上，pg<1.25 V，t_off=1 µs | 158 mV | 20 mA：122.5 mV p-p |
| 同上，pg<1.30 V，t_off=300 ns | **122 mV（< A 的 127）** | 95 mA：55.8 mV p-p（碼 7↔8）；20 mA：154 mV p-p |
| 同上，pg<1.30 V，t_off=1 µs | 122 mV | 45 mA：97.9 mV p-p；20 mA：104.5 mV p-p |
| 同上，pg<1.35 V，t_off=300 ns／1 µs | 606 mV（步階前已失效）| 5 mA 時 Vout 停在 1.774 V；其他平台 45–360 mV p-p，或停在 1.656／1.739 V |

`r1f_map2.py` 用同一個測試序列（5 mA → 95 mA（100 ns 邊沿）→ 45 mA → 20 mA，每個平台 10 µs，取最後 5 µs），判定標準為各平台平均 Vout 與標稱值相差 <10 mV 且 p-p <20 mV [X]：
- **無 droop 的 B（t_off=1 ns 或 300 ns）：4 個平台全部通過。**
- **8 組閘控 droop 設定（pg 閾值 1.20/1.25/1.30/1.35 V × t_off 300 ns/1 µs）：全部至少有一個平台失效。**
- 「Vout 停在 1.695 V」的那組，slice 閘極都是乾淨的 0／1.8 V（不是 XSPICE 的 X 態），pg=1.8 V，DN 應該成立，但 slice 沒被移除。同一組參數只要多掛幾顆觀測用的 dac_bridge（改變數位事件的時序），就變成約 120 mV p-p 的弛張振盪（`dbg5.py`）。這表示行為對數位事件時序極度敏感（類似 set／clock race）。**我沒有追到確切根因，不排除部分是 XSPICE 事件排序造成的模擬假象**；但無論是哪一種，都不是可以交給學生下線的狀態。

另外，**1 ns 邊沿時任何數位路徑都沒用**：所有 pg 型版本都是 756 mV。前 2–3 ns 的電荷缺口由類比 pass 的寬度決定，比較器加 set 鏈的延遲（≥2–4 ns）來不及。

**含意**：
- 草稿說「要改善就需要非同步 droop detector 或一次開多片——數位部分隨即變複雜」。應改成：「**非同步路徑閘數很少，但會引入新的雙迴路 limit cycle／卡死狀態**。在我試的 8 組閾值與邊沿設定中沒有一組在 5–95 mA 全部正常，而能把 undershoot 壓到 A 水準（122 mV）的設定，在 20 mA 和 95 mA 都振盪（55–154 mV p-p）。」
- 這反而是**支持 A 最有力的證據**，比草稿引用的 313/127 mV 有說服力得多。
- REF-B 的 slice 開關邊沿 1 ns 對步階測試其實是**有利於 B**的設定，不是稻草人；稻草人在 Wa。

---

## 4.【需修正】理由 1 分不出 A 和 B；教授推薦 hybrid 論文是 B 的直接證據

- 依 `ARCH_MATRIX.md` §1 的分類，B 的定義是「類比 EA 決定 DC 精度；數位只粗調」，就是**類比主導**。「教授要求偏類比」對 A 和 B 都成立。
- 教授**主動推薦一篇 hybrid 論文**（Leduc 2025），這是使用者給的事實，草稿卻只把它當成「備案條件：教授要 hybrid 題目」。比較合理的讀法是：教授的意圖未知，而且偏向 B 的機率不低。
- 「無 Verilog」也分不出 A 和 B：`ANALYSIS.md` 自己寫了 B 的控制器是 8 個 DFF＋33 個閘，可以閘級手畫，和學生做過的 DFF、除頻器同一等級。

**新增的 B 論點（目前最強的反方論證）——B ⊇ A 的優雅降級**（`r8_fallback.py`）[X]：Wa=2.4 mm 的 B 把數位 reset（8 片全關）之後，就是一顆純類比 LDO：

| | Vout 誤差 ≤16 mV（1%）的最大負載 | 最差 PM（0–50 mA）|
|---|---|---|
| A（4 mm）| 140 mA | 66.4° |
| B2400，數位 reset | **88.5 mA** | **68.3°** |
| B800，數位 reset | 32.5 mA | 69.9° |

也就是說，只要 Wa 取約 2.4 mm 並留一根 reset／force-code pin，「數位部分出問題就整顆失敗」的風險是有界的：最壞情況退化成一顆 ~88 mA 的 A。草稿用「一次下線、風險低」支持 A，這個理由因此弱了一截。代價是多出的 pin（clk、reset、可能 VL/VH）、數位電源，以及 slice 的漏電與 Vout 寄生電容。

**建議**：結論第一行改成「**A 與合理設計的 B 技術上接近；A 勝在整合與驗證風險（見第 3 節）。最終選擇取決於教授推薦 hybrid 論文的意圖，應先問教授。**」並把「B 用 Wa≈2.4 mm、寬窗口、純 gate-sensing、不加 droop、加 reset pin」寫成 B 的建議形態。

---

## 5.【需修正】理由 3 不對稱、未驗證：A 的修法也有可量化的代價

草稿把 A 的風險寫成「都可以用類比手段處理」（SRE、adaptive bias、加大洩放），但**沒有一項經過模擬**。B 的修法（droop）則被當成扣分項。

量化其中一項：**高溫輕載漏電**（`r3_hot.py`、`r3b_hot.py`、`r7_bleed_bias.py`；與 `s6_corners.py` 相同的 Vth 平移法，模型寫在 scratch）[X]，條件是 SF-like（Vthn+50 mV、|Vthp|−50 mV）、125 °C、零外部負載：

| 架構（200 µA 洩放）| Vout | 相對各自 TT 27 °C 的誤差 |
|---|---|---|
| A 4 mm | 1.6525 V | **+46 mV**（失去調節，與作者一致）|
| B，Wa=800 | 1.6132 V | **+9 mV** |
| B，Wa=1600 | 1.6221 V | 約 +17 mV |
| B，Wa=2400 | 1.6334 V | +28 mV |

| A 的洩放電流 | 200 µA | 300 µA | 400 µA | 600 µA | 800 µA |
|---|---|---|---|---|---|
| Vout（SF-like，125 °C）| 1.652 | 1.632 | 1.624 | 1.617 | 1.614 |

- B 的 slice 閘極被數位硬拉到 Vin（Vsg=0；每片 125 °C 漏電 3.2 µA），類比 pass 又只有 1/5，所以天然避開 A 的失效模式 1。這個優勢隨 Wa 增加而縮小，和第 2 節的 PSRR／暫態改善**方向相反**：Wa 是 B 唯一的主要取捨旋鈕。
- A 若只靠加大洩放，要約 **800 µA** 才能達到 B800 在 200 µA 時的誤差，Iq 約從 287 µA 變成 **~890 µA**。另一條路是讓 buffer 把 pg 拉到 Vin（rail-to-rail buffer 或 pg pull-up 開關），代價是設計複雜度，草稿沒有評估。
- SRE（草稿的首選配置裡就有）沒有模擬。`ANALYSIS.md` A3 自己列了誤觸發、局部正回授等風險，這和我在 B 的 droop 路徑上看到的問題是同一類。**結論不能在 A 用「之後加 SRE」抵帳、在 B 卻把同類修法記為成本。**

**建議**：理由 3 改成 [H]，並在首選說明裡寫出兩個具體代價：「洩放電流需 ≥600–800 µA，或 pg 要能拉到 Vin」，以及「SRE 尚未模擬，須在下線前驗證有無誤觸發和 limit cycle」。

---

## 6.【需修正】「1 nF 慢邊沿反而較差」只在 Rz=0 時成立

先排除我自己的一個假設：問題**不是** EA slew（I_tail/Cc）。把 tail 從 20 µA 加到 100／200 µA（同時縮小輸入對，維持 gm1）後，1 nF 的 100 ns undershoot 仍是 315–352 mV（原本 345 mV），`r4_1nF.py` [X]。作者的「UGF 下降」解釋是對的。

但在 Cc 串一顆 nulling resistor（教科書 Miller 補償的標準變體）之後，結論就變了（`r4c_rz_fine.py`，11 個負載點 0–100 mA，0→100 mA 步階）[X]：

| CL / Cc / Rz | 最差 PM | 最差 GM | 1 ns | 100 ns | 1 µs |
|---|---|---|---|---|---|
| 100 pF / 5 pF / 0（REF-A）| 66.4° | 18.4 dB | 742 mV | 236 mV | 111 mV |
| 1 nF / 20 pF / 0（REF-A 1 nF）| 54.7° | 27.1 dB | 497 mV | 346 mV | 151 mV |
| 100 pF / 3 pF / 10 kΩ | 87.7° | 12.4 dB | 872 mV | **178 mV** | **70 mV** |
| **1 nF / 8 pF / 10 kΩ** | **62.3°** | 16.7 dB | **431 mV** | **185 mV** | **80 mV** |

- 兩邊都加 Rz 後，慢邊沿差距從 +46%／+36% 縮到 **+4%（100 ns）／+15%（1 µs）**，已在 PTM 模型的不確定度範圍內。1 ns 邊沿則是 1 nF **好 2 倍**。
- 新發現的取捨：Rz 會削弱 Cc 的快速耦合路徑。100 pF 的 1 ns undershoot 從 742 惡化到 **872 mV**，而 1 ns 正是草稿列的「最大風險」。
- 另一個含意：REF-A 本身也還沒最佳化（加 Rz 後 100 ns 改善 25%），所以 A 和 B 的比較兩邊都還有空間。

**建議**：`ANALYSIS.md` 的附錄結論改成「**在 Rz=0 的 Miller 補償下**，1 nF 慢邊沿較差；加 nulling resistor 後慢邊沿差異 ≤15%，1 ns 邊沿 1 nF 好 2 倍」。「最大風險」一段應加上「CL=1 nF＋Rz 是對 1 ns 邊沿最有效的類比手段（431 vs 742 mV），代價約 0.12 mm² MOS 電容」。

---

## 7.【小問題】REF-A 的理想化假設：逐項檢查後，多數是對稱的，或反而對 B 有利

| 假設 | 檢查 | 結果 | 對 A/B 是否不對稱 |
|---|---|---|---|
| 理想偏壓電流源 | `r7`：Ibias 改成 Vin→bn 的 124 kΩ 電阻（最粗糙的偏壓）| A PSRR@1 kHz（70 mA）−38.2→−37.0 dB；B800 −18.8→−18.7；B2400 −30.1→−29.6 [X] | 不重要 |
| 理想 Vin（無 pad／bond wire）| `r5_bondwire.py`：1–2 nH＋0.1–0.2 Ω，片上 Cin 200 pF–1 nF | A：1 ns 499→**536–599 mV**（+7–20%），100 ns 127→134–139；B：756→804–841、313→319–329 [X] | 大致對稱（A 在 1 ns 的相對惡化略大）。1 ns 的絕對值被低估最多約 100 mV；地線 bond wire 沒有建模 |
| 理想 Vref | 沒有模擬 | 真實 bandgap 的 Vref 漣波會被 1/β=2 放大，使低頻 PSRR 有 −40～−55 dB 的地板 [H]；主要影響 A 的 −55 dB（0 mA）這個數字 | 模擬裡對稱；實際上 B 的數位雜訊會耦合進 Vref／偏壓，**對 B 更不利** |
| B 的比較器理想（無 offset、metastability、kickback）、slice 驅動無電源電流 | 作者已註明 | 這些都讓 B 在模擬裡看起來比實際好 | **對 B 有利** |
| 電流源負載、200 µA 洩放 | A、B 共用 | — | 對稱 |
| 無 junction 電容 | log 有「Pd = 0 is less than W」：沒給 AD/AS/PD/PS，ngspice 不算 drain/source junction 電容 | 4 mm drain 在 Vout 上少了約數 pF [D/H]，略有利於 1 ns 數字 | 大致對稱 |
| W 超出模型範圍 | 模型 `wmax=1.0e-4`（100 µm），pass 4000 µm、slice 130 µm 都超過 | 應改用 m=（finger）寫法以免外插 [H] | 對稱 |

**結論**：「A 被美化」不是 A 勝出的原因。模型層面的理想化反而對 B 較有利；B 吃虧的是**設計點的選擇**（Wa，第 2 節）。建議在報告裡明列「1 ns 數字未含 bond wire，可能再惡化 7–20%」以及「W>wmax，量產前改用 multiplier」。

---

## 8.【小問題】C 的排除：結論成立，但量化漣波的論證要改

草稿用 `ΔV ≈ (I_u/2)/(CL·f_clk)` 和 8 片 12.2 mA 的 slice 得到 6 V，據此說 C「根本無法調節」。但 thermometer shift register 是逐位元重複的結構，8 位元和 128 位元的設計工作量相同（一個 bit cell 陣列化，不需要 Verilog）。

[D]：128 片（I_u = 0.78 mA）、CL = 1 nF、f_clk = 50 MHz 時，ΔV ≈ 0.39 mA × 20 ns / 1 nF ≈ **7.8 mV**；CL=100 pF 時約 78 mV。考慮迴路延遲造成的多週期 limit cycle 模式，要再乘 2–3 倍。

C 真正該排除的理由是：Vin=1.8 V 沒有 DLDO 的 headroom 動機；slice 是 Vin→Vout 的開關，中高頻 PSRR 天生接近 0 dB；粗細兩段的快速暫態需要非同步路徑（第 3 節顯示這類路徑在 B 就已經很脆弱）；以及教授偏類比。

**建議**：保留排除，但把「量化漣波極大」限定為「在 8–16 片粗 slice 時」。

---

## 9. 建議的結論改寫（可直接替換 CONCLUSION_DRAFT 的對應段落）

> **首選：A 純類比 capless LDO（與合理設計的 B 技術上接近；先向教授確認是否要 hybrid 題目）**
> 理由：
> 1. **整合與驗證風險**：單一迴路、無時脈、無雙迴路交互。本次在 hybrid 上加最簡單的非同步 droop 路徑（比較器＋DFF set 鏈），8 組閾值／邊沿設定**全部**在 5/20/45/95 mA 的某個平台出現 limit cycle（45–360 mV p-p）或 Vout 卡高（+97 mV 以上）；不加 droop 的 B 則全部正常，但 100 ns 邊沿的 undershoot 是 A 的 1.2–2.5 倍（依 Wa 而定）。
> 2. **面積相近時 A 仍有中等優勢**：與 Wa=2.4 mm 的 B 相比，5→95 mA undershoot 低 11–21%，PSRR@1 kHz（70 mA）好 8 dB。（Wa=0.8 mm 的 B 差 2.5 倍／19 dB，那是設計點造成的，不代表架構。）
> 3. B 的實際優勢：DC load regulation（20→95 mA：0.5 vs 6.1 mV）；高溫輕載漏電（SF-like 125 °C：B800 +9 mV vs A +46 mV）；數位 reset 時可降級為約 88 mA 的類比 LDO（Wa=2.4 mm）。
>
> **A 必須付的代價**（目前寫成「可用類比手段處理」，應改為明確的代價）：高溫輕載要 ≥600–800 µA 洩放（Iq 約 0.9 mA）或讓 pg 能拉到 Vin；SRE 要先模擬再承諾；1 ns 邊沿考慮 CL=1 nF（＋Rz）。
>
> **B（若教授要 hybrid）的建議形態**：Wa≈2.4 mm、窗口 ≥1.5 片電流、純 gate-sensing、**不加**非同步 droop（或只加經過完整 limit-cycle 掃描的閘控版本）、slice 慢關、留 reset／force-code pin。

---

## 10. 重現方式

```
cd /tmp/claude-0/-home-user/24b1423c-959f-5794-9f98-bbcbade8908e/scratchpad/review_r1a
python3 r0_baseline.py      # 重現 REF-A/REF-B 基準（res/r0_baseline.json）
python3 r1_fairB_step.py    # pg 型 droop（res/r1_fairB_step.json）
python3 r1b_fairB_vout.py   # Vout 型 droop（res/r1b_fairB_vout.json）
python3 r1c_fairB.py        # slice 慢關＋各 droop 版本的輕載振盪（res/r1c_fairB.json）
python3 r1d_fairB.py        # 閘控 droop＋REF-A 1/10/100/1000 ns 對照（res/r1d_fairB.json）
python3 r1e_map.py          # 閘控 droop 穩健性地圖，只看 p-p（res/r1e_map.json；會漏掉「卡高」，以 r1f 為準）
python3 r1f_map2.py         # 同上＋各平台平均 Vout＋無 droop 對照（res/r1f_map2.json）
python3 dbg5.py             # 加觀測節點後同一設定改成弛張振盪（時序敏感度）
python3 r2_psrr.py          # PSRR 拆解（res/r2_psrr.json）
python3 r3_hot.py; python3 r3b_hot.py   # 高溫漏電（res/r3_hot.json, r3b_hot.json）
python3 r4_1nF.py; python3 r4c_rz_fine.py  # 1 nF：tail 電流、Rz（res/r4_1nF.json, r4c_rz_fine.json）
python3 r5_bondwire.py      # Vin bond wire（res/r5_bondwire.json）
python3 r6a_idvg.py; python3 r6_bigWa.py   # Wa=2.4 mm 的 B（res/r6_bigWa.json）
python3 r7_bleed_bias.py    # A 洩放掃描、電阻偏壓 PSRR（res/r7_bleed_bias.json）
python3 r8_fallback.py      # B 數位 reset 降級（res/r8_fallback.json）
python3 r1g_bigWa_seq.py    # Wa=2.4 mm 的 B 跑含降載的完整序列（res/r1g_bigWa_seq.json）
```

每個腳本都在 ~20 秒內跑完（ngspice-42）。scratch 目錄屬於本次 session，可能被清除；關鍵的 netlist 改動是 `hyb2.py` 的 `digital_block()`（DFF set 端接 `AND(droop, q_{k−1})`，droop 來源可選 `pg`／`vout`／`both`，`dac_bridge` 的 t_fall=t_on、t_rise=t_off）。若要保存，請把整個目錄複製進 repo。
