# Agent 3 筆記：數位 LDO、回顧/教學、FoM 批評、on-chip 負載暫態量測

對應 CSV：`agent3_digital_review.csv`（D01–D14）。
證據標註沿用 README：[M] 論文實測、[S] 論文模擬、[D] 推導（含本次對公開資料集的統計）、[H] 假設或推測。

## 0. 執行條件與限制（先讀）

- **本 session 的網路政策封鎖了幾乎所有全文來源**：doi.org、ieeexplore.ieee.org、arxiv.org、iopscience、jos.ac.cn、researching.cn、ADS、PMC/NCBI、MDPI、Columbia Academic Commons、Stanford vlsiwiki、UM IME、HKUST、TAMU OAKTrust、Semantic Scholar、OpenAlex、Crossref API 都連不上（WebFetch 回 ENOTFOUND；curl 回 proxy 403）。要開放這些網域，需在環境設定的 Network access 中加入。
- 只有 **WebSearch**（伺服器端，回傳摘錄與摘要）和 **GitHub**（可 git clone 公開 repo）可以用。
- **WebSearch 在任務中途用完共享額度（200 次/turn）**，所以 event-driven JSSC 2017、Kim/Mok 的 limit cycle 論文、computational DLDO、OJ-SSCS 綜述、片上量測 buffer 等項目沒有再查下去（見 §5）。
- 結果是：**14 篇都沒有開啟過論文全文**，CSV 的 `fulltext_url` 全部留空。找到的 OA 全文候選 URL 都寫在 notes 欄，但都沒有實際開啟。
- 唯一實際開啟並讀過的一手資料，是 D08 的配套公開資料集 `github.com/mgseok/DLDO-survey`（commit 68e94cc，2021-11-06）。內容是 51 個 DLDO 設計、58 列量測條件，包括 README 中的 FoM 定義與審閱註記。§3 的統計都是本次從這份 xlsx 算出來的 [D]；表內數值是 Columbia 團隊從原論文整理或估算的，不是我讀原文得到的。
- **DOI 規則**：doi.org 和 Xplore 都無法直接解析，所以只有在 ≥2 個獨立記錄一致（出版社 URL、典藏記錄、書目庫）時才填 doi 欄（D02、D06、D11、D12）。其他 DOI 都寫在 notes 並標「未驗證」或「待驗證」。
- 數字欄只填摘要或比較表讀到的值，`numbers_source` 有註明。WebSearch 給的是模型整理後的摘錄，可能有誤，正式引用前應以全文核對。

## 1. 每篇重點

**D01 Okuma et al., CICC 2010（背景，D）**
- 經典 DLDO 原型：用比較器加移位暫存器控制 PMOS 開關陣列，完全不用類比電路。
- 動機是 0.5 V 近臨界邏輯。摘要說傳統 op-amp 回授的 LDO 在 0.5 V 下無法工作 [M]。
- 65 nm、Vin 0.5 V、Vout 0.45 V、98.7% current efficiency、Iq 2.7 µA（@200 µA）[M，摘要]。
- Seok survey 註記 Cout 為 **off-chip 100 nF**，ripple 3 mV [表格]。用片上 100 pF–1 nF 的條件不能直接比。
- 對本專題：Vin 1.8 V 下 op-amp 可以正常工作，所以 DLDO 最原始的存在理由在本專題不成立 [D]。

**D02 Hazucha et al., JSSC 2005（背景，A）**
- 90 nm、1.2→0.9 V、100 mA 步階、0.6 nF 片上電容下 droop 90 mVpp，response time 0.54 ns，94% current efficiency [M，摘要]。
- regulator 本體只有 0.008 mm²，但 0.6 nF MOS 電容另佔 0.090 mm² [摘要]。由此可見面積其實由電容決定。
- 常被引為 ps-FoM 的出處（形式為 CL·ΔV·Iq/ΔI²，見 §3）。本次沒有讀到原文公式，未逐字核對。
- 摘要沒有說明負載步階如何產生，也沒有給邊沿時間。

**D03 Nasir, Gangopadhyay, Raychowdhury, ISSCC 2015（D）**
- 130 nm 全數位 LDO，用 adaptive control 和細粒度 clock gating，在 50× 負載範圍內維持 >90% current efficiency [M，摘要]。
- 大 droop 時暫態時間縮短 8×（「reduced dynamic stability」的取捨）[摘要]。
- Seok 比較表：PSRR **−5 dB @1 MHz**，Cout 1 nF，Iq 24 µA（Iq,min），Vin 未指定，edge time 未報告 [表格]。
- 同作者的 limit cycle 分析 APEC 2015（pp.371–376）只確認到書目。OA 預印本 arXiv:1501.00579 的索引詞含 limit-cycle oscillations，指出 LCO 來自比較器的硬量化（搜尋摘錄）。兩者都未讀。

**D04 Huang et al., TCAS-II 2016「Limit Cycle Oscillation Reduction for Digital LDOs」（D，limit cycle 分析）**
- 搜尋摘錄：計算 LCO 的模態與振幅，並加入 feedforward 路徑降低 LCO。
- 同團隊後續在 AAD-LDO（JSSC 2018）加入 freeze mode 消除 LCO，在 APDI LDO（JSSC 2020，DOI 10.1109/JSSC.2020.2967540，未直接驗證）中，負載小於 1 LSB 電流時改由類比比例路徑接手（搜尋摘錄）。
- 卷期是從澳門大學典藏 PDF 的標頭推定的，DOI 未驗證。

**D05 Kim D., Kim J., Ham, Seok, ISSCC 2017（D，event-driven）**
- 用 event-driven 的 PI 控制取代固定時脈，透過 PI 控制器的細粒度平行化降低回授延遲 [摘要]。
- 0.5 V Vin、0.1 nF 全片上 Cout、1.44 mA 負載變化下輸出變化 <7.6%、99.2% peak CE [M，摘要]。
- 比較表：droop 34 mV，Iq 12.2 µA（由 FoM 反推），**edge time 未報告** [表格]。
- 這類設計針對時脈頻率和暫態/功耗的取捨：固定時脈的 DLDO 要反應快就得提高 fclk，Iq 隨之上升（D06 也有同一論點）。
- OA 學位論文：Doyun Kim, Columbia Ph.D.。摘要稱第二個設計的 FoM 比當時 state of the art 好 17× 以上，只用 100 pF（搜尋摘錄）。未能開啟。

**D06 Huang, Lu, Martins, J. Semicond. 2020（R，OA）**
- 先比較 ALDO 與 DLDO 的一般優缺點，再整理 DLDO 的快速暫態與 PSR 改善技巧，最後討論趨勢 [摘要]。
- 摘要直接寫到兩個 DLDO 弱點：(1) 同步控制的傳統 DLDO 暫態受**功耗-速度取捨**限制，本質偏慢；(2) PSR 弱，因為**全開的功率開關直接暴露在電源漣波下**。
- 出版社免費全文，但本 session 沒能開啟。

**D07 Huang, Lu, Martins, TCAS-II 2021（R）**
- 把 hybrid LDO 分成 AAD（analog-assisted digital）和 DAA（digital-assisted analog）兩類，整理優缺點與應用情境 [摘要]。
- 前提：傳統類比和數位 LDO 在某些情境下都難以同時兼顧暫態與 PSR [摘要]。
- 對本專題：教授要求偏類比，若加入數位輔助，就屬於 DAA。

**D08 Wang, Kim, Bowman, Seok, CICC 2022（R，FoM 批評主來源）**
- 回顧並 benchmark 超過 50 個 DLDO，從五個面向分類：控制律、觸發方式、功率 FET、數位-類比混合、單一或分散式 [摘要]。
- 提出新 FoM 以補既有 FoM 的缺點 [摘要]。新 FoM 的公式沒讀到。配套資料集 README 定義了 edge-adjusted ps-FoM 與 pC-FoM（§3），但未確認是否就是論文中的「新 FoM」。
- 配套資料集是本次唯一實際開啟的一手資料，§3 的統計都來自它。

**D09 Torres et al., IEEE CAS Magazine 2014（Crit/R）**
- 摘要明說：各文獻的製程和規格不同，所以很難比較。
- 作者因此在**同一個 0.6 µm CMOS**製程中設計、下線並量測 5 種 capless LDO 拓撲 [M，摘要]。
- 這是「FoM/規格跨論文不可比」最直接的方法論回應，也是本專題選 capless 拓撲時最該讀的一篇。

**D10 Razavi, SSC Magazine 2019（R，教學）**
- 「A Circuit for All Seasons」專欄，vol.11 no.2 pp.8–13。屬大學部可讀的 LDO 入門。
- 全文未取得，內容未讀，只確認書目。

**D11 Tan et al., IEEE Access 2022（R，OA）**
- 類比 LDO 架構綜述 [摘要]。
- 摘要指出：相較 DLDO，ALDO 在**低輸出漣波與高 PSR** 上領先。這支持本專題偏類比的方向。

**D12 Lu, Wang, Pan, Ki, Yue, TCAS-I 2015（A，sub-ns 邊沿量測例）**
- 全片上 capless LDO：1.2→1.0 V，0→10 mA 步階、**200 ps 邊沿**，undershoot 43 mV、overshoot 82 mV [M，摘要]。
- response time 1.15 ns，FoM 5.74 ps，PSR 在 DC–20 GHz 優於 −12 dB [M，摘要]。
- 晶片 260×90 µm²，其中含 140 pF 堆疊片上電容 [摘要]。
- ISSCC 2014 會議版題名中的數字（0.65 ns、3.01 ps FOM）與期刊版不同，不要混用。摘要沒有說明 200 ps 邊沿怎麼產生。

**D13 Mandal, Desai, Bakkaloglu, Kiaei, TCAS-II 2019（A，0.18 µm）**
- 0.18 µm NMOS capless LDO，用 adaptive biasing 在滿載時把迴路頻寬與 slew rate 提高 100%，不增加無載 Iq [摘要]。
- 9→40 mA、**350 ps 邊沿**、undershoot 166 mV、settling 19 ns，面積 0.21 mm² [摘要，搜尋摘錄]。
- 對本專題的意義：同製程下有論文以 sub-ns 邊沿報告負載暫態，可作為量測條件的參考。負載是否片上、數字是量測還是模擬，都未確認。

**D14 Alon, Stanford Ph.D. 論文（Mx）**
- 片上電源雜訊量測：只用**兩個 on-chip sampler** 加 VCO-based converter，量出電源雜訊的週期性時變統計特性與頻譜 [M，VLSI 2004 摘要]。
- 量測系統做在 0.13 µm 的高速 link transceiver 內 [摘要]。
- 第 2 章談量測電路，可借用來片上監測 LDO 的 Vout。OA 全文候選未能開啟，年份未確認。

## 2. 補充來源（只用於論證，未列入 CSV）

- Bulzacchelli et al., JSSC 2012, vol.47 no.4 pp.863–874（IBM 頁與 Seok survey 一致：10.1109/JSSC.2012.2185354）。45 nm SOI、8 個分散式 µregulator，負載反應 <500 ps。**用 CMOS delay line 的 jitter 讀數推得輸出雜訊約 28 mVpp**（IBM 研究頁摘要）。這是另一種片上監測法，見 §4 M4。
- Oh et al., ISSCC 2020（480 mA 可合成 DLDO）。摘要：除了 pass gate 與 210 fF 電容，**整顆以 script-based APR 合成**（Seok survey 收錄的摘要）。
- Bang et al., ISSCC 2020（10 nm 分散式全數位 LDO）。摘要：每個單元**完全以標準元件庫加業界 APR 工具合成**（同上）。
- Fahmy et al., ESSCIRC 2017：只用數位標準元件做的可合成 time-based LDO，0.13 µm、15 mA、Iq 最低 140 µA、暫態 <600 ns（同上）。
- Sun et al., ISSCC 2019（UW，computationally regulated DLDO，平均 settling 2.79 cycle）與 Ahmed et al., JSSC 2020（22 nm variation-adaptive computational DLDO，500 mA 時 droop 100 mV、settling <20 ns）。這兩篇是 computational DLDO 的代表，只在 Seok 資料集中讀到摘要，沒有另外用 WebSearch 驗證，因此不列入 CSV。
- **Tang et al., ESSCIRC 2018「A 0.7V Fully-on-Chip Pseudo-Digital LDO Regulator with 6.3µA Quiescent Current and 100mV Dropout Voltage in 0.18-µm CMOS」**（Seok 資料集列 10.1109/ESSCIRC.2018.8494307；**只在資料集讀到，沒有用 WebSearch 驗證，建議優先驗證**）。
  - 和本專題同為 0.18 µm、100 mA、片上小電容。架構是 NMOS 功率管，加上 latched comparator、2× charge pump 和 RC 網路組成的 pseudo-digital 迴路，元件少且多為閘級。
  - 摘要：20 pF 片上 Cout、10 MHz 比較器時脈下，90 mA 步階、**150 ns 邊沿**，undershoot 106 mV；Iq 6.3 µA，active area 0.08 mm² [M，資料集所收摘要]。
  - 審閱註記：輸出漣波隨負載增加，但所有負載條件下都 <15 mV；FoM 用的總電容包含探棒寄生 10 pF。
- 「A 0.6 VIN 100 mV Dropout Capacitor-Less LDO with 220 nA IQ for Energy Harvesting System」（PMC10222239，OA）。搜尋摘錄：同一顆 LDO 在 1 ns 邊沿下 230 mV / 5 µs，在 1 µs 邊沿下 140 mV / 3.5 µs [S]。作者與 DOI 未確認。
- Guo & Leung, JSSC 2010（6 µW capless LDO，90 nm）。摘要：100 ns 邊沿、全負載變化下 over/undershoot <66 mV。K（邊沿時間比）FoM 是否由此文首創**未能確認**。DOI 10.1109/JSSC.2010.2053859 只見於搜尋摘錄，未驗證。
- Wang/Kim/Bowman/Seok 之外的 DLDO 綜述：「Design Trends and Perspectives of DLDO for Low Voltage Mobile Applications: A Review」，IEEE Access 2023, vol.11 pp.85237–85258（搜尋摘錄給 10.1109/ACCESS.2023.3303809，單一來源，未驗證），OA。

## 3. FoM 不可比較的具體原因清單

公式（取自 Seok survey README，D08）：
- ps-FoM =（Cout·ΔV/ΔI）·（Iq/ΔI）。這是常歸於 Hazucha 2005（D02）的形式。
- pF-FoM =（ΔV/(Vout·ΔI)）·Cout·Iq。
- edge-adjusted ps-FoM =（Cout·ΔV/ΔI + 0.5·t_edge）·（Iq/ΔI）。
- pC-FoM =（Cout·ΔV/ΔI + 0.5·t_edge）·Iq。

1. **負載邊沿時間差了 5 個數量級，而 ps-FoM 不含邊沿時間。**
   - Seok 資料集 58 列中，46 列有報告 t_edge，範圍 **0.015–4000 ns**，中位數 2 ns [D，本次統計；來源 D08 資料集]。
   - 同一顆晶片就能證明邊沿影響 FoM：X. Wang et al., CICC 2019 charge-pump LDO，ΔI 100 mA、Iq 4.9 µA 都相同。1 ns 邊沿時 droop 185 mV，10 ns 邊沿時 88 mV，ps-FoM 從 0.0038 ps 變成 0.0018 ps，**邊沿越慢、FoM 看起來越好**（約 2.1×）[表格，D08 資料集]。
   - 題名掛「0.29 ps transient FoM」的 J. Lee et al., VLSI 2019，邊沿是 **400 ns**。改用 edge-adjusted FoM 後變成約 250 ps [D，資料集計算]。
   - 同樣情況：Y.-J. Lee et al., ISSCC 2016（200 mA，28 nm）t_edge 4000 ns，ps-FoM 9.57 → 1232 ps；Kundu et al., ISSCC 2018 t_edge 1240 ns，1.38 → 9921 ps [D]。
   - 改用 edge-adjusted FoM 後排名會變。45 列同時有兩種 FoM 時，Spearman ρ = 0.79，前 10 名只重疊 7 個，單列最大名次變動 26/45 [D，本次統計；同一設計可能占多列]。
   - 類比 capless LDO 也一樣：PMC10222239 的同一設計，1 ns 邊沿時 230 mV、1 µs 邊沿時 140 mV [S，搜尋摘錄]。OCL-LDO 文獻因此常乘上 K = t_edge / 比較組中最小 t_edge（多篇 MDPI/PMC 論文使用；**首創者未確認**）。
2. **「CL」的定義不一致。**
   - 資料集中 8 列 Cout = 0（cap-free）。這時 ps-FoM 的 C 只能改用總電容、耦合電容或寄生電容，**有 11 列在審閱註記中寫明以 Ctotal 或耦合電容當作 Cout** [D08 資料集註記]。
   - 例：Oh et al. ISSCC 2020 自報的 FoM 0.00041 ps，是把 Ctotal 當 Cload 算的 [註記]。
   - Okuma 2010（D01）用 off-chip 100 nF，ps-FoM 為 270000 ps [表格]，與片上 pF 級設計根本不在同一尺度。
   - 例：Tang et al. ESSCIRC 2018（0.18 µm）的片上輸出電容是 20 pF，但 Seok 團隊計算 FoM 時用 30 pF。審閱註記列出的總電容包含**探棒寄生 10 pF**。可見量測探棒電容是否算進 CL，會直接改變 FoM [D08 資料集註記]。
3. **Iq 的條件不一致，且常是反推值。**
   - 18 列的 Iq 是 Seok 團隊從論文自報的 FoM 或 current efficiency 反推的 [註記]。
   - Nasir 2015（D03）用 Iq,min 計算 [註記]。
   - 有的論文報無載 Iq，有的報滿載 Iq，Iq 又會隨負載和時脈頻率改變。DLDO 的 Iq 含時脈與控制器功耗，和 fclk 綁在一起（D06：功耗-速度取捨）。
4. **ΔI 的定義不一致，且 ps-FoM 對 ΔI 是平方反比。**
   - 註記中有論文「用負載電流取代 ΔIload」，也有論文「用約略的 0.5 A ΔI」算出自報 FoM [D08 資料集註記]。
   - 由公式推得：CL、Iq 固定時，若 ΔV 大致與 ΔI 成正比，ps-FoM ∝ 1/ΔI。所以**用越大的負載步階量測，FoM 越好看** [D]。
5. **數值常從圖上估計，甚至把模擬當實測。**
   - 13 列有「estimated from figure」註記，2 列註記「edge time = 2 ns is simulated data」，1 列「edge time estimated from figure」[D08 資料集註記]。
6. **FoM 只量負載暫態，不含 PSR、漣波和精度，但這些正好是 DLDO 的弱點。**
   - 58 列中只有 **8 列有 PSRR 數值**，全部只量 1 MHz 一個頻點，範圍 −5 dB（Nasir 2015）到 −46 dB（Intel hybrid）。ripple 只有 24 列有報告 [D，本次統計]。
   - D06 指出 DLDO 的 PSR 本質較弱，D11 指出 ALDO 在漣波與 PSR 上領先 [摘要]。D08 自己也說既有 FoM 有缺點，所以提出新 FoM [摘要]。
7. **製程、電壓、規格不同。**
   - D09 摘要明說各文獻製程與規格不同，所以難以比較，作者因此在同一 0.6 µm 製程實作 5 種拓撲比較 [摘要]。
   - 資料集中的 Vin 從 0.4 V 到 1.8 V（雙軌），製程從 180 nm 到 5 nm [D08 資料集]。
8. **response time 與 settling time 的定義也不一。**
   - 資料集對 settling 的定義是「回到 Vref 的某個小百分比以內」，各論文百分比不同。有一列註記「FoM ps = 244.8 using reported Tresponse」，表示該論文以自定義的 T_response 計算 [D08 資料集註記]。
9. **量測方式本身會改變 CL 和邊沿（大部分屬推測）。**
   - Vout 直接接 pad 和探棒，會把 pad、ESD 和探棒電容併入 CL，壓低 ΔV [H]。Tang 2018 的總電容把探棒寄生 10 pF 算進去，是唯一讀到的佐證（第 2 點）[D08 資料集註記]。
   - 外部負載受 bond wire 電感限制，邊沿變慢，也會壓低 ΔV [H]。
   - 「capless LDO 量測因此被美化」的說法，本次**沒有找到明文論證的論文**，只有上面第 1 點的邊沿依賴性數據可以間接支持。

## 4. on-chip 負載暫態量測方法

| 方法 | 原理 | 邊沿時間（有來源才寫） | 需要的額外電路 |
|---|---|---|---|
| M1 片上開關電流負載（NMOS 開關＋電阻，或可程式電流源陣列） | 在 Vout 端放大尺寸 NMOS（或電流鏡陣列），用片上反相器鏈驅動閘極，產生快速 ΔI，避開 bond wire 電感 | 有報告 sub-ns 邊沿的例子：200 ps（D12，0→10 mA）、350 ps（D13，0.18 µm，9→40 mA）、0.1–0.2 ns（Seok 團隊 VLSI 2018/2019）、15–16.5 ps（Intel 14/22 nm hybrid LDO）[摘要或表格]。**這些摘要都沒寫負載是否片上**；能做到 sub-ns 應該要靠片上負載 [H] | 負載電晶體陣列（可分段設定 ΔI）；閘極驅動 inverter chain；觸發輸入（pad 或片上脈衝產生器）；最好讓負載電流走獨立的 ground pad，避免共用 ground 的 IR/L·di/dt 汙染量測 [H] |
| M2 外部負載（PCB 上的 MOSFET、電子負載或 SMU） | 負載在晶片外，經過 pad 和 bond wire | 資料集中較慢的例子：150 ns（Tang ESSCIRC 2018）、400 ns（Lin ISSCC 2018；J. Lee VLSI 2019）、1240 ns（Kundu ISSCC 2018）、4000 ns（Y.-J. Lee ISSCC 2016）[表格]。這些是否外部負載未確認 [H] | 片上不需額外電路；但邊沿慢，ΔV 會被低估（§3 第 1 點） |
| M3 Vout 監測：on-chip buffer / source follower 驅動 pad | 片上低輸出阻抗 buffer 把 Vout 搬到 pad，讓示波器探棒和 pad 電容不掛在 Vout 上 | **本次未找到附數字的文獻**（搜尋額度用完）[H] | buffer 頻寬要明顯高於 LDO 反應頻寬；source follower 有 Vgs 位移和非線性，需要 replica 或校正；buffer 最好用獨立電源，避免吃到被測 LDO 的漣波 [H] |
| M4 片上取樣器 / 時間域讀出 | (a) 兩個片上 sampler 加 VCO-based converter，量電源雜訊的統計特性與頻譜（D14）；(b) 用片上 delay line 的 jitter 推估供電雜訊，Bulzacchelli 2012 推得約 28 mVpp（§2） | 不是單次波形，而是統計或等效時間取樣；邊沿數字未讀到 | 取樣開關、比較器或 VCO 加計數器、時脈與觸發同步；面積和設計量都高於 M1 和 M3 |

對本專題的建議 [H]：0.18 µm、10–100 mA 的條件下，**M1（片上 NMOS 負載加 inverter 驅動）加 M3（片上 source follower 或 unity-gain buffer 監測）** 是成本最低的組合。D13 顯示同製程論文以 350 ps 邊沿報告負載暫態，可作為目標量級。量測報告務必同時寫出 t_edge、ΔI、CL（含 pad 和寄生）、Iq 的量測條件，以及 Vout 是怎麼取出的。

## 5. 未完成或未驗證項目（需要網路或搜尋額度）

- Kim & Seok JSSC 2017（event-driven explicit time-coding）、Nasir TPEL 2016、Nasir APEC 2015 LCO：只確認書目，沒讀內容。
- 使用者提到的「Kim/Mok 的 limit cycle」論文：未找到，以 D04（Huang 2016）替代。
- Mok 或 Ki 的 LDO tutorial、OJ-SSCS 的 LDO 綜述：一次搜尋沒找到，額度用完後未能再查。
- K（邊沿時間比）FoM 的首創者：未確認。
- 片上 buffer 或 source follower 監測 Vout 的專門論文或學位論文：未找到。
- 所有 DOI 都沒能用 doi.org 或 Xplore 直接解析；所有 OA 全文都沒能開啟。若網路放行，優先開這些：D06（JoS OA）、D11（IEEE Access OA）、D14（Stanford 論文）、D05 的 Columbia 論文、arXiv:1501.00579、D12 的作者版 PDF。
