# agent5 筆記：HBM 相關的 LDO／電壓調節文獻（2014 至今）

對應 CSV：`agent5_hbm.csv`（HB01–HB12）。搜尋日期 2026-11-02。WebSearch 用了 39 次（上限 45）。

## 先讀：這批資料的限制

1. **全文一篇都沒開。** 依指示，這個 session 擋掉學術網站，所以沒有試 WebFetch/curl。所有內容都來自 WebSearch 摘錄，CSV 的 `fulltext_status` 一律是「僅摘要（搜尋摘錄，未開啟全文）」。
2. **摘錄本身經過搜尋工具整理，可能有誤。** 數字只填摘錄裡出現的。HB05 的數字全部來自論文標題，HB07 的數字來自 researchr 列表。
3. **DOI 都沒經 doi.org 驗證。** 有填的四個（HB04、HB08、HB09、HB11）都出現在 openalex、KAIST 典藏或 NSF PAR 的搜尋摘錄。其餘留空。
4. **HBM 專用 LDO 的論文很少。** 能直接對上「HBM 介面裡的 LDO」的學術論文，只找到首爾大學 Jaehyouk Choi 團隊的三篇（HB05–HB07），而且都只讀到標題或列表，沒有讀到製程、電流、電路架構。HBM PHY 內 DLL/PLL 專用 LDO 的論文沒找到，只找到專利。
5. **[H]** 表示我的推論或計算，沒有文獻來源。

`id` 規則：CSV 收 12 篇（HB01–HB12）。只在本筆記引用、沒放進 CSV 的補充來源編為 HBS1–HBS12（見 §2 最後），大多是專利、廠商文件、商業媒體或只讀到片段的論文。

---

## §1 HBM 電源架構概觀（只用有來源的資訊）

### 1.1 各世代 rail 電壓（摘錄讀到的值）

| 世代 | 讀到的電壓 | 來源 | 備註 |
|---|---|---|---|
| HBM（第一代） | 1.2 V；8 channel、1024-bit I/O、4 die TSV 堆疊、29 nm | HBS1（SK hynix ISSCC 2014；EE Times Japan 報導） | 1.2 V 是哪一條 rail，摘錄沒細分 |
| HBM2E | VDDQ 1.2 V、VDDC 1.2 V | HB03（Samsung Foundry HC2020 poster，引用 JESD235B）；HBS2（Intel Agilex 7 HBM2E 文件：I/O 1.2 V、DRAM core 1.2 V） | Intel 文件另有接 2.5 V 的 pump power supply 腳位；摘錄沒說它是不是 DRAM 的 VPP |
| HBM3 | operating voltage 1.1 V；host interface 用 0.4 V low-swing signaling | HB01（JEDEC JESD238 新聞稿）；HBS8（Synopsys：core 由 1.2 V 降到 1.1 V，I/O signaling 由 1.2 V 降到 400 mV） | 0.4 V 對應哪條 rail（是否叫 VDDQL）**未確認** |
| HBM3E | 摘錄未讀到電壓值 | — | HB04 只讀到架構關鍵字 |
| HBM4 | VDDQ 0.7 / 0.75 / 0.8 / 0.9 V（vendor-specific）；VDDC 1.0 / 1.05 V | HB02（JEDEC JESD270-4 新聞稿） | 現行版 JESD270-4A（2025-12，v1.1）是否改電壓表未確認 |

VPP、VBLH 等 DRAM 內部電壓的 HBM 專用數值**沒有讀到**。

### 1.2 堆疊端（DRAM die 與 base die）的 power delivery

- HBM 是多顆 DRAM die 靠 TSV 疊在 base die 上，第一代就是 4 die TSV 堆疊（HBS1）。
- SK hynix 的 HBM3E（16-high、1280 GB/s）用 "all-around power TSV"。標題和摘要把它和 TSV area optimization 放在一起，但 IR drop 改善了多少，摘錄沒寫（HB04）。
- 日文 ASCII 報導（二手，HBS7）提到：base die 和 DRAM die 共用一個 PDN，所以很難分析；在堆疊周邊加 power TSV 可以降電阻，但製造成本較高；訊號速度上升後，光靠加 TSV 不夠，因為 decap 沒辦法放在 base die 附近。
- HBM4 的 base die 改用 logic 製程：Samsung 用 SF4，SK hynix 用 TSMC N12（SemiAnalysis 報導，HBS6，二手）。同一報導說 SK hynix 的 VPP IR drop 最多低 75%，這是二手數字，沒放進 CSV。
- 一份專利（HBS4）描述 buffer die（base die）上有 LDO，供電給 driving circuit、TSV 區與 HBM PHY。專利說選 LDO 是因為頻寬寬，driver 高速工作時供電仍穩定。這是專利，不是量測論文。
- 一份 3D DRAM 專利（HBS13）描述 VPP/VBB 產生器放在 master chip，再經 TSV 把 VPP 電流送到各 slave chip；另一種做法是每顆 chip 都放 VPP down-converter。這也是專利，HBM 實際產品怎麼做沒讀到。

### 1.3 Host 端（SoC/GPU 的 HBM PHY）

- HBM I/O 的 PSIJ 由 VDDQ PDN、simultaneous switching current、clock 與 I/O buffer 的 supply sensitivity 疊加而成（HB09）。
- PHY 內的 clock 從 address/command 的 clock generator 經多級 buffer 分配到各 data word（DWORD）的 Tx。buffer 間距 0.41 mm，依位置有 3–5 級，每一級都對供電敏感（HB09）。
- 早一篇把 4 Gbps HBM 介面拆成 power/ground、channel、Tx clocking、Rx clocking 四部分，在頻域建模 jitter（HB08）。
- 首爾大學團隊直接把 LDO 拿來壓 HBM 介面的 PSIJ：ISSCC 2025 的 command-aware hybrid LDO（HB05）、JSSC 2026 的期刊版（HB06），以及 CICC 2026 的 strobe-triggered digital LDO 加 local replica regulators（HB07）。
- 專利 HBS9（DDR RCD，不是 HBM）說明為什麼 clock 電路要用 LDO：LDO 只能濾掉自己 regulation bandwidth 內的雜訊，更高頻的雜訊會直接進到 clock path。同次搜尋另一份 DLL 專利也說，超過 DLL loop bandwidth 的供電雜訊無法用延遲調整消除，所以需要 LDO。
- 一份 HBM PHY 相關專利（HBS4）描述用 LDO 供電給 HBM PHY 區域裡的 inverter-based driver。

### 1.4 替代路線：IVR 和 switching regulator

- KAIST 提出 interposer-level IVR（IIVR），把 switching regulator 的主動電路放在 active interposer、電感放在 package substrate，用來壓 HBM I/O 的 SSN，並隔離外部寬頻雜訊。只有模擬（HB10）。
- 另一篇 KAIST 論文比較 off-chip、on-interposer、on-chip 三種位置的 regulator。interposer IVR 的 module footprint 最小，regulator 越靠近負載，暫態與雜訊抑制越好（HB11）。
- 處理器端的 FlexWatts（HBS5，不是記憶體）說明 LDO 效率會被 Vout/Vin 限制：某個 graphics 例子大約 0.5/0.9 ≈ 55%。它的解法是 IVR/LDO 雙模式切換。

---

## §2 每篇重點

### HB01 JEDEC JESD238 HBM3 新聞稿（2022）— App
- HBM3 的 operating voltage 降到 1.1 V，host interface 改用 0.4 V low-swing signaling，以提升能效。
- 0.4 V 屬於哪條 rail 沒有說明，我沒有確認 "VDDQL" 這個名稱。
- 關聯：只當背景數字。學生的 1.6 V 輸出不是 HBM 的 rail。

### HB02 JEDEC JESD270-4 HBM4 新聞稿（2025）— App
- VDDQ 可選 0.7/0.75/0.8/0.9 V（vendor-specific），VDDC 可選 1.0/1.05 V。同一 controller 可以兼容 HBM3/HBM4。
- 現行版是 JESD270-4A（2025-12，v1.1），電壓表有沒有改未確認。
- 關聯：說明 HBM 的 rail 一代比一代低（1.2 → 1.1 → 0.7–1.05 V）。在低 Vout 下，LDO 從較高電壓降壓的效率問題會變嚴重（[H]，見 §3）。

### HB03 Samsung Foundry，HBM2E PHY poster（Hot Chips 2020）— App
- Host 端的 3.2 Gbps/pin HBM2E PHY test chip，主打 low-power I/O 和 enhanced training，用於 2.5D SiP。
- HBM2E 是 8 channel，VDDQ 1.2 V、VDDC 1.2 V。poster 有 0.75 V/1.2 V 條件下的 power 與 valid-window-margin 量測，但 0.75 V 對應哪個 rail 沒說。
- PHY 內有沒有 LDO 沒讀到。
- 關聯：低。只用來說明 host 端 PHY 的供電條件。

### HB04 SK hynix，HBM3E 16-high 1280 GB/s（ISSCC 2024）— App
- 新設計：all-around power TSV、6-phase RDQS、byte-mapping swap、WDQS voltage-drift compensator。
- power TSV 的電性細節（IR drop 數字）沒讀到。
- 關聯：低。TSV 堆疊的 power delivery 學生完全做不到，只能在背景中說明「HBM 的電源問題有一大部分出在堆疊內 IR drop」。

### HB05 首爾大學，Command-Aware Hybrid LDO for Advanced HBM Interfaces（ISSCC 2025, 8.5）— 未確認（hybrid）
- 數字只來自標題：Iq 150 µA、on-chip C 20 pF、droop <10 mV、settling 400 ps。
- 製程、Vin/Vout、負載電流、步階型式都沒讀到。"command-aware" 的機制也沒讀到，不推論電路細節。
- 這是找到的論文中最直接的「HBM 介面專用 LDO」。
- 關聯：概念高、實作低。可借它的 problem statement（HBM 介面要極小 droop、極快 settling 來壓 PSIJ）和評估指標（droop、settling、Iq、C_on-chip）。20 pF 搭配 400 ps 的組合在 0.18 µm、100 mA 的條件下不可能做到（[H]，見 §4）。

### HB06 Han et al.，Command-Aware Hybrid LDO … PSIJ Mitigation in HBM Interfaces（JSSC 2026-01）— 未確認（hybrid）
- 只在實驗室出版列表看到，co-first author 是 M. Han 和 J. Kim。
- 標題直接把 LDO 的目的定為「HBM 介面的 PSIJ mitigation」。
- 可能是 HB05 的期刊延伸版，但摘錄沒確認。數字、卷期、DOI 都沒讀到。
- 關聯：可在專題動機中引用（「LDO 在 HBM 介面的角色就是壓 PSIJ」）。引用前要先開全文確認內容。

### HB07 Han et al.，Strobe-Triggered Digital LDO and Local Replica Regulators for HBM PSIJ（CICC 2026）— 未確認（DLDO + replica）
- researchr 列表：droop 10.7 mV、settling 1.4 ns；列表註明缺 abstract。
- 從標題只能確定它用了 strobe-triggered 的 digital LDO 和多個 local replica regulator 兩種元件。兩者怎麼分工沒讀到。
- 關聯：中。「全域 regulator 加多個 local regulator」的分散式概念可以借。strobe-triggered DLDO 需要數位控制邏輯，學生沒有 Verilog，不適合照做。

### HB08 Shin et al.，System-Level PSIJ for 4 Gbps HBM I/O（EDAPS 2021）— Crit
- 把 4 Gbps HBM 介面拆成 power/ground、channel、Tx clocking、Rx clocking 四部分，在頻域建 jitter spectrum 後整合，用 SPICE 驗證。
- 找出能在 critical frequency range 降低 jitter 的設計參數，但頻率數值沒讀到。
- 屬於限制面：HBM 介面的 jitter 主要來自供電雜訊經 clocking 電路轉換。
- 關聯：中。可借來說明「PSRR 要在特定頻段夠高」，而不是只看 DC PSRR。

### HB09 Park et al.，PSIJ Modeling, Analysis, and Optimization of HBM I/O（EMC+SIPI 2023）— Crit
- HB08 的延伸：對 HBM1/2/2E（1/2/3.2 Gbps）建模 VDDQ PDN、SSN 電流、clock 與 I/O buffer 的 jitter sensitivity。對 SPICE 平均誤差 4.26%（S）。
- driver 用 65 nm 模型，0.4 pF 負載下 rise/fall 約 110/60/38 ps；clock buffer 間距 0.41 mm、3–5 級。
- 用 ML 指引 on-chip 與 on-interposer decap 擺放。結論是 high-frequency PSIJ 是主要挑戰。
- 有 NSF PAR 公開版（未開啟），是這批裡最容易拿到全文的一篇。
- 摘錄沒讀到它討論 LDO 或 PSRR。它的對策是 decap，不是 regulator。
- 關聯：中高。「clock 經多級 buffer、每級對 supply 敏感」可以直接當學生 LDO 的負載情境描述。

### HB10 Kim et al.，Interposer-level IVR for HBM I/O Power Noise Suppression（DesignCon 2019）— IVR
- IIVR 是 switching regulator，主動電路放在 active interposer、電感放在 package substrate。
- 依時域與頻域模擬，可壓制內部 SSN、隔離外部寬頻雜訊，支援次世代 HBM 4 Gbps。只有模擬（S）。
- 關聯：學生做不到（要 interposer 和電感），但可以在報告中作為 LDO 的對照：「業界研究也考慮用 IVR 取代或補強 LDO」。

### HB11 Power Integrity Comparison of Off-chip, On-interposer, On-chip VRs in 2.5D/3D ICs（EDAPS 2019）— IVR
- 比較三種 regulator 位置。interposer IVR 的 effective module footprint 最小。依搜尋摘要，regulator 越靠近負載，暫態與雜訊抑制越好，且 two-stage 設計效率較高。
- 作者欄沒讀到（KAIST 典藏）。
- 關聯：中。支持學生把 LDO 和 CL 都做在 on-chip（靠近負載）的動機。效率結論則提醒：LDO 只適合 Vin−Vout 小的那一級（[H]）。

### HB12 KAIST 碩士論文，Adaptive Compensator for SSN in Multi-Channel Transmitters（2024）— Crit
- 分析用 LDO-regulated supply 的多通道 transmitter 的 SSN，提出 switched-capacitor pull-up current compensation，再用 sign-sign LMS 在晶片上調補償強度。
- 28 nm 模擬，4 個並聯 transmitter，SSN 從 9.8 降到 2.3 mVrms，只用 20 pF de-cap（S）。
- 摘錄沒說是 HBM，但「多通道、LDO 供電、同時切換」正是記憶體介面的情境。
- 屬於限制面：光有 LDO 壓不住多通道同時切換造成的雜訊。
- 關聯：中。可借「多個負載同時切換」當暫態測試情境。

### 補充來源（只在本筆記引用，未列入 CSV）
- **HBS1**：D.-U. Lee et al.（SK hynix），"A 1.2V 8Gb 8-channel 128GB/s high-bandwidth memory (HBM) stacked DRAM …"（標題後半未逐字確認），ISSCC 2014 25.2，pp. 432–433，DOI 10.1109/isscc.2014.6757501（摘錄所見，未驗證）。JSSC 2015 vol. 50 no. 1 有期刊版。內容：1.2 V、128 GB/s、29 nm、4 die TSV、microbump I/O 測試。
- **HBS2**：Intel，High Bandwidth Memory (HBM2E) Interface Agilex 7 M-Series FPGA IP User Guide：I/O 1.2 V、DRAM core 1.2 V、2.5 V pump power supply 腳位。
- **HBS3**：Synopsys white paper，"Power Supply Noise Effects on Jitter in Clock Synchronous Systems with Emphasis on LPDDR5X, DDR5 and HBM3"：用 jitter transfer function (JTF) 描述供電雜訊頻率和 timing jitter 的關係。下載需登入，摘錄沒提 regulator PSRR。年份未讀到。
- **HBS4**：US 專利 12656801 "Low dropout regulators"（assignee 未讀到）：base die 上的 LDO 供電給 driving circuit、TSV 區和 HBM PHY，選 LDO 是看中寬頻寬。
- **HBS5**：J. Haj-Yahya et al.，"FlexWatts: A Power- and Workload-Aware Hybrid Power Delivery Network for Energy-Efficient Microprocessors"，MICRO 2020（arXiv 2009.09094 有公開版，未開啟）。LDO 效率約等於 Vout/Vin，例子是 0.5/0.9 ≈ 55%；IVR/LDO 雙模式；video playback 平均功耗降 11%（TDP 4–50 W）。這是處理器，不是記憶體。
- **HBS6**：SemiAnalysis 的 ISSCC 2026 報導（二手）：Samsung HBM4 Paper 15.6 是 36 GB 12-high，用 1c DRAM 疊在 SF4 base die 上，靠 ABB 和 4 倍 TSV 數達到最高 13 Gb/s/pin。SK hynix HBM4 base die 用 TSMC N12，Micron 用自家 CMOS。正式標題沒讀到。
- **HBS7**：ASCII.jp（2026-05，日文，二手）談 HBM4/5 的供電極限，以及 Samsung 的 package co-design。
- **HBS8**：Synopsys "What is High Bandwidth Memory 3" glossary：core 1.1 V（HBM2E 為 1.2 V），I/O signaling 400 mV（HBM2E 為 1.2 V）。
- **HBS9**：US 專利 12724441 "LDO regulator circuit apparatus capable of attenuating supply voltage noise"（DDR RCD 例）：LDO regulation bandwidth 以上的雜訊會進到 clock path。
- **HBS10**：延世大學（依 yonsei.elsevierpure 典藏頁；作者未讀到）"A Low Power TSV I/O with Data Rate up to 10 Gb/s for Next Generation HBM"，JSSC 2023 vol. 58 no. 11，DOI 10.1109/JSSC.2023.3285896（摘錄所見，未驗證）：65 nm，用降低的供電，0.179–0.185 pJ/b/pF @ 5–10 Gb/s。低壓 rail 怎麼產生沒讀到。
- **HBS11**：J. Choi，"A 6.4Gb/s/pin HBM3 Digital PHY with Low-Power, Area Efficient Techniques for Chiplet-Based AI processors in 12-nm CMOS"，A-SSCC 2024：只讀到標題，沒有電源資訊。
- **HBS12**："A 192-Gb 12-High 896-GB/s HBM3 DRAM With a TSV Auto-Calibration Scheme and Machine-Learning-Based Layout Optimization"，JSSC vol. 58 no. 1，2023，pp. 256–269：摘要提到 internal low-voltage signaling，所屬公司沒在摘錄中確認。
- **HBS13**：US 專利 8913443 "Voltage regulation for 3D packages …"：master chip 上的 VPP 產生器經 TSV 供電給 slave chip。
- 2014 年以前的背景：Sturcken et al.，2.5D IVR on silicon interposer（ISSCC 2012 / JSSC 2013），是 interposer IVR 的起點。

---

## §3 HBM 對 LDO 的典型需求

| 項目 | 有來源的內容 | 沒有來源（[H]） |
|---|---|---|
| 負載電流 | **沒讀到任何 HBM LDO 的負載電流數值**（HB05–HB07 都沒有） | HBM PHY 有上千條 I/O、多個 channel，總電流應遠大於單一 LDO 能供的量，所以文獻走 local/分散式 regulator（HB07 標題）[H] |
| PSRR 頻段 | 雜訊超過 LDO regulation bandwidth 就會進 clock path（HBS9）；超過 DLL loop bandwidth 的雜訊無法靠延遲調整消除（同次搜尋的 DLL 專利）；high-frequency PSIJ 是主要挑戰（HB09）；有 critical frequency range（HB08），但沒讀到數值 | 關鍵頻段大約在 DLL/PLL loop bandwidth 以上、clock 頻率以下，也就是 MHz 到數百 MHz 一帶。這段高頻最後要靠 on-chip decap，不能只靠 LDO 迴路 [H] |
| 暫態型態 | 跟 command/strobe 同步（HB05 "command-aware"、HB07 "strobe-triggered"，都只從標題得知）；多通道同時切換造成 SSN（HB08、HB09、HB12） | 負載是週期性的突發，不是單次步階；而且可以從 controller 事先知道何時發生，所以適合 feedforward [H] |
| droop / settling | <10 mV / 400 ps（HB05）；10.7 mV / 1.4 ns（HB07） | — |
| Iq | 150 µA（HB05） | — |
| on-chip 電容 | 20 pF（HB05）；SSN 補償用 20 pF de-cap（HB12，非 HBM） | HBM 介面的 LDO 要用很小的 C 換速度，學生則是用大 C（100 pF–1 nF）換穩定，兩者取捨方向相反 [H] |
| 面積 | 沒讀到 | — |
| 效率 | LDO 效率上限約 Vout/Vin，例子 0.5/0.9 ≈ 55%（HBS5，處理器） | 若 HBM3 的 0.4 V 由 1.1 V 經 LDO 產生，效率上限約 36%（0.4/1.1）。**實際怎麼產生沒讀到**，這只是假設計算 [H]。學生的 1.8→1.6 V 上限約 89% |

---

## §4 對 0.18 µm 學生專題的啟示

### 4.1 能借用的部分
1. **專題動機。** 可以寫：「HBM 等高頻記憶體介面中，clock 經多級 buffer 分配，每級都對供電敏感，供電雜訊會轉成 PSIJ（HB08、HB09），因此需要 on-chip regulator 隔離（HB05–HB07、HBS9）。」本專題在 0.18 µm 以 1.8→1.6 V 縮放示範這類 regulator 的核心取捨。**不要宣稱做的是「HBM 用 LDO」**：HBM 的 rail 是 0.4–1.2 V，1.6 V 不是 HBM 的 rail。
2. **評估指標。** 除了 DC 的 load/line regulation，也要報告：PSRR 對頻率的曲線（重點放在中高頻，不只看 DC）、步階的 droop 和 settling，並和 Iq、on-chip C 一起列表。HB05 標題列的就是 Iq、C、droop、settling 四項，可以照這個格式寫比較表。
3. **暫態測試型態** [H]：除了單次 10→100 mA 步階，再加一組週期性 burst 負載，讓 on-chip load switch 用外部方波驅動，模擬 command/strobe 同步的負載。這不需要 Verilog。
4. **jitter 代理指標** [H]：如果有面積，可以在 LDO 輸出掛一條 inverter delay line 或 ring oscillator 當「clock-like 負載」，量 LDO 開/關（或 bypass）時的延遲變化，把 droop 換算成 timing 誤差。這是借用 HB09「clock buffer 的 supply sensitivity」的概念。0.18 µm 可以做，但會增加量測複雜度，屬於選做。
5. **feedforward 想法** [H]：HB05 的 "command-aware" 字面上表示 regulator 事先知道負載何時來。它實際怎麼做沒讀到。學生可以用類比方式做類似的東西：加一個外部 trigger 腳，在負載開關前預先拉高 pass device 的 gate 驅動或 error amp 偏壓。這是我的延伸構想，不是 HB05 的電路。

### 4.2 做不到的部分
1. **ns 以下的 settling 加上 20 pF 的組合（HB05）。** 一階估算 [H]：droop ≈ ΔI·t_resp / C。ΔI = 90 mA、C = 1 nF 時，迴路要在 1 ns 內反應 droop 才只有約 90 mV；C = 100 pF、1 ns 時約 900 mV（等於失控）。所以學生在 0.18 µm 必須**放慢負載邊沿**（例如 100 ns 等級，參考 agent4 的 F03/F04 都用 100 ns 邊沿），或縮小步階。HBM 文獻那種 ps–ns 級的反應在學生條件下做不到。
2. **TSV、base die、interposer IVR、package 電感**（HB04、HB10、HB11）：製程不可得。
3. **strobe-triggered digital LDO**（HB07）：需要數位控制和時序邏輯，學生沒有 Verilog。
4. **HBM 實際電壓與訊號**（0.4 V low-swing、0.7–0.9 V VDDQ）：0.18 µm 1.8 V 元件的 Vth 太高，不適合在這些電壓下示範 [H]。

### 4.3 會不會改變「純類比 vs hybrid」的選擇？
**不改變：仍建議純類比（A），或在 A 之上加一個類比 feedforward 輔助。** 理由：
1. HBM 文獻（HB05–HB07）確實走 hybrid/digital，但它們的優勢建立在 regulator 事先知道 command/strobe 時序，以及先進製程的速度上。單獨下線的學生 LDO 沒有 memory controller 提供時序，hybrid 的主要好處用不到 [H]。
2. HBM LDO 用小 C（20 pF）換速度。學生規格是 100–1000 pF 的 on-chip CL、10–100 mA，這組條件跟 agent4 整理的 0.18 µm 類比 OCL-LDO（F01：CL 0–1 nF、100 mA；F03：100 mA、100 ns 邊沿）比較接近，跟 HBM LDO 不接近。
3. 沒有 Verilog 時，數位主導（C/D）的控制邏輯要手畫，驗證風險高。HB07 的 DLDO 正好說明這類架構依賴數位觸發。
4. HBM 背景真正帶來的改變在**評估方式**，不在架構：PSRR 要看中高頻，暫態要測 burst 和多負載同時切換（HB09、HB12）。這些都能用類比 LDO 加外部負載開關完成。
5. 如果想讓專題「看起來更接近 HBM」，風險最低的做法是在類比 LDO 上加外部 trigger 的 feedforward 腳（§4.1 第 5 點）。它不需要數位邏輯，量測時也可以關掉，和純類比版本對照 [H]。

---

## §5 沒查完的項目與建議關鍵字

1. **HB05/HB06/HB07 的製程、Vin/Vout、負載電流、架構、PSRR**：最關鍵，要開 IEEE Xplore 10904806 和 JSSC 2026-01。關鍵字：`"command-aware" LDO HBM JSSC 2026 Han Choi`、`ISSCC 2025 8.5 hybrid LDO HBM`。
2. **HBM PHY 內 DLL/PLL 專用 LDO 的學術論文**：沒找到，只有專利。關鍵字：`HBM PHY DLL regulator`、`memory interface DLL replica regulator PSRR`、`GDDR6 PHY LDO PSRR`（GDDR6 有一份 high-PSR regulator 專利，可作旁證）。
3. **DRAM die 內部電壓產生器（VPP、VBLH、VCORE）在 HBM 的論文**：沒找到 HBM 專用的。關鍵字：`HBM DRAM internal voltage generator TSV`、`3D stacked DRAM VPP charge pump TSV sharing`。
4. **HBM3 0.4 V rail 的名稱與產生方式**（是否叫 VDDQL、由誰產生）：需要 JESD238 原文或 PHY datasheet。關鍵字：`HBM3 VDDQL`、`JESD238 power supply`。
5. **Samsung ISSCC 2026 HBM4 Paper 15.6 的正式標題**，以及 SK hynix HBM4 的 ISSCC 論文：關鍵字 `ISSCC 2026 15.6 HBM4`。
6. **商用 GPU/加速器的 HBM PHY 是否用 IVR/FIVR 供電**：沒找到。關鍵字：`Ponte Vecchio HBM PHY FIVR`、`MI300 HBM power delivery`、`CoWoS IVR HBM`。
7. **作者欄缺的兩篇**：HB11（KAIST 典藏 10203/311845）、HB12（10203/321663），開典藏頁就能補。
8. **HBM PDN 的 TSV 電容論文**（NSF PAR purl/10314296，DesignCon 2021?）：只讀到內容，標題和作者沒讀到，所以沒列入。關鍵字：`voltage-dependent P/G TSV capacitance HBM PDN`。
9. **HB09 的 NSF PAR 公開全文**：開放網路後優先讀，可以拿到 HBM clock 分配和 VDDQ PDN 的具體數字。
