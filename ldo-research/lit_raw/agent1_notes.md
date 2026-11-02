# Agent1：hybrid LDO 文獻筆記

## 0. 搜尋環境限制（請先讀）

- 本 session 的 **WebFetch 與 curl 對所有學術網站都被網路政策擋下**：ieeexplore.ieee.org、doi.org、api.crossref.org、knowledgecommons.lakeheadu.ca、thesis.lakeheadu.ca、www.lakeheadu.ca、researchgate、semanticscholar、openalex、core.ac.uk、mdpi、pmc、arxiv 等都連不上。要能讀全文，需要在 cloud environment 的 Network access 把這些網域加進 Allowed domains（或改用較寬的存取等級）。
- 因此 **本筆記所有內容都來自 WebSearch 結果的摘要轉述**（搜尋引擎整理的摘要片段、參考文獻字串、典藏頁 metadata），**沒有一篇全文被我實際打開閱讀**。
- **DOI 一律未能以 doi.org 或 IEEE Xplore 頁直接驗證**。CSV 的 `doi` 欄因此全部留空，候選 DOI 寫在 notes 並標「DOI 未驗證」。
- 搜尋到一半時，WebSearch 的每回合額度（200 次，所有 agent 共用）已經用完，所以有幾篇的作者/卷期還沒查完（見各篇註記）。

---

## 1. Leduc et al. 2025（H01）判定

### 書目
- **標題**：A 430-mA Capacitor Less Analog Assisted Hybrid LDO With Fast Transient Algorithm
- **作者**：Pierre Leduc, Ximing Fu, Yushi Zhou（Lakehead University, Canada；Zhou 是指導教授）
- **期刊**：IEEE Transactions on Circuits and Systems I: Regular Papers, **vol. 72, pp. 3733–3743, 2025**
  - 卷與頁碼取自一篇 2026 年 MDPI Electronics 論文（15(21):4988）的參考文獻，**issue 號未確認**。
  - ResearchGate 列為 2025 年 1 月（應為 early access 日期）。Lakehead 教師新聞頁（2025-02-04）寫這是 Leduc 第一篇被 TCAS-I 接受的期刊論文。
  - IEEE Xplore document 10884555：https://ieeexplore.ieee.org/document/10884555/
  - 搜尋結果裡的 PDF 路徑是 `ieeexplore.ieee.org/iel8/8919/11099062/10884555.pdf`（8919 = TCAS-I punumber，11099062 = issue id），屬付費、未開啟。
- **DOI**：**找不到、未驗證**。搜尋結果完全沒出現這篇的 DOI 字串，我也不推測。

### 全文取得狀態
| 來源 | URL | 狀態 |
|---|---|---|
| IEEE Xplore（出版社） | https://ieeexplore.ieee.org/document/10884555/ | 付費；看不出是否 OA；本 session 無法連線 |
| Leduc 碩士論文（Lakehead 2024） | https://knowledgecommons.lakeheadu.ca/bitstreams/78829c83-9740-4646-82d4-0d0844bdad2f/download | 典藏頁標示 embargo 到 **2025-09-23**，現在應已公開，但網域被封鎖，**未能打開** |
| ResearchGate / arXiv / HAL | — | 沒搜到作者版全文 |

**實際讀到的章節：只有摘要**（而且是搜尋結果轉述的摘要，不是我自己打開的 IEEE 頁面）。

### B/C 判定：**未確認（僅摘要）**

依規則，沒讀到全文就不下結論。以下只列摘要裡的線索。

**偏向 C（數位主導、類比輔助）的線索：**
1. 標題寫的是 "Analog Assisted Hybrid LDO"。依 Huang/Lu/Martins 的分類（H06），"analog-assisted" 通常指 AAD（數位為主體）。不過命名不等於實際分工。
2. 摘要原句（取自搜尋結果）："...composed of digital and analog loops of which the transient response is dictated by the digital portion."（< 25 字）
3. 主要創新是數位部分的 "fast approximation algorithm leveraging charge distribution"，並與 linear 和 SAR 搜尋比較。這表示 power transistor array 的導通數量由數位迴路決定。
4. 前作 MWSCAS 2024（H02）的摘要轉述：以 charge distribution 估算所需的 power transistor 大小；另加 analog error amplifier 負責零負載/輕載調節。這比較像類比只在輕載補位。
5. 碩士論文摘要說 hybrid 設計是針對「低 clock 頻率、大輸出電流」最佳化。

**偏向 B 或無法排除 B 的線索：**
1. 摘要沒說穩態下哪個迴路提供大部分負載電流。
2. 摘要沒說 DC 精度由誰決定。H02 摘要轉述提到 analog EA 有助於「better regulation」；如果 analog EA 在所有負載下都持續做精細調節，DC 精度其實由類比決定，會落在 B/C 中間的「digital coarse + analog fine」型態。
3. 摘要沒說數位迴路在穩態是否停止（freeze）或持續動作。

**結論**：要判定 B/C，必須讀到全文（或碩士論文 hybrid 章節）的方塊圖與穩態操作說明，特別是三件事：穩態電流由誰供應、DC 精度由誰決定、數位迴路穩態時是否停止。

### 電路關鍵數字（皆來自摘要轉述，**未讀全文**）
| 項目 | 值 | 註 |
|---|---|---|
| 製程 | TSMC 180 nm standard CMOS | 摘要（ResearchGate 轉載） |
| Imax | 430 mA | 標題/摘要 |
| Iq | 49 µA | 摘要 |
| 輸出電容 | 無外接電容（capacitor-less）；on-chip CL 數值未知 | 摘要 |
| Undershoot | 480 mV @ 430 mA，edge time 100 ns | 摘要（負載起點未知） |
| Settling | 225 ns（undershoot）、260 ns（overshoot） | 摘要 |
| Droop detector | 開啟後 undershoot 降 54%（"wide load range droop detector"，功耗 overhead 可忽略） | 摘要 |
| Vin / Vout / dropout | 摘要未提供 | — |
| PSRR / 面積 / clock 頻率 | 摘要未提供 | 前作 H02 用 10 MHz clock、Vout 1.2 V（模擬） |
| 實測或模擬 | 碩士論文摘要說兩個設計都有下線，並有模擬與量測結果；TCAS-I 摘要的轉述版本提到 droop detector 的效果是量測得到的，但我無法核對原句 → CSV 標「未知」 | — |

### 數位部分如何實作
**未確認**。摘要只提到三件事：
1. 用 charge distribution 的快速逼近演算法，比 linear 搜尋（shift-register 型）和 SAR 更快收斂；
2. 有 clock，前作用 10 MHz；
3. 有 inverter-based droop detector（依 H02 摘要轉述）。

是否用 synthesized logic/Verilog、比較器的形式、是否有 bidirectional shift register，摘要都沒寫。

### Leduc 相關前作（同實驗室）
| id | 書目 | 架構 | 狀態 |
|---|---|---|---|
| H02 | Leduc, Fu, Zhou, "A 3.04-fs FoM Hybrid LDO Regulator with Fast Transient Algorithm and Wide Load Range," IEEE MWSCAS 2024（IEEE Xplore 10658752） | hybrid（H01 的會議前作）；TSMC 180 nm post-layout sim；120 mA、Vout 1.2 V、10 MHz clock；full-range step 1.17 µs、max droop 253 mV | 僅摘要 |
| H03 | Leduc, Fu, Zhou, Elsankary, "A Dual Loop Current Mode Feedback Capacitor Less LDO for High Current Applications," IEEE NEWCAS 2024（IEEE Xplore 10666338） | 純類比雙迴路：voltage loop 負責精度、current loop 負責快速響應；有 feedforward line filter 改善 PSRR | 僅摘要 |
| H04 | P. Leduc, *The design of fast-transient cap-less low-dropout voltage regulators*, M.Sc. thesis, Lakehead University, 2024（handle 2453/5398） | 內含 H03 型 dual-loop 和 hybrid 兩個設計，都在 TSMC 180 nm 下線 | 全文存在，但網域被封鎖，未讀 |
| — | X. Fu, Y. Zhou, P. Leduc, K. Elsankary, "A High-Speed Capacitor Less LDO with Multi-Loop Fast Feedback and Bandwidth Enhancement Control," ISCAS 2023 | 純類比 | **未驗證存在**：只在 Lakehead 新聞頁的搜尋轉述中看到，沒找到 IEEE 頁面，所以沒列進 CSV |

---

## 2. 其他 hybrid LDO 論文（H05–H16）

所有數字都來自摘要（搜尋轉述），DOI 都未經 doi.org 驗證。

**H05 — Huang, Lu, U, Martins, "An Analog-Assisted Tri-Loop Digital LDO," JSSC 53(1):20–34, 2018**（候選 DOI 10.1109/JSSC.2017.2751512；ISSCC 2017 版候選 DOI 10.1109/ISSCC.2017.7870401）
- 架構屬 **C（AAD）**：主迴路是數位，再並聯一個 analog-assisted loop 處理負載階躍；coarse/fine 兩個數位迴路負責精度與恢復。
- 輸出待在 dead zone 一段時間後進入 freeze mode 以降低 Iq。
- 65 nm；10 mA/1 ns 負載階躍時 peak under/overshoot 105 mV；總電容 100 pF；FoM 0.23 ps（實測，摘要）。

**H06 — Huang, Lu, Martins, "Review of Analog-Assisted-Digital and Digital-Assisted-Analog LDOs," TCAS-II 68(1):24–29, 2021**（DOI 未找到）
- 類型 **R**：把 hybrid 分成 AAD 與 DAA 兩類，比較前作並整理 pros/cons 與適用情境。
- 可以當作 B/C 分類的正式依據（B≈DAA、C≈AAD）。

**H07 — Lu, Huang, Martins, "PID Control Considerations for Analog-Digital Hybrid LDOs," IEEE EDSSC 2019（invited）**（候選 DOI 10.1109/EDSSC.2019.8754302）
- 類型 **R/限制分析**：用古典 PID 觀點分類既有 LDO，並提出 hybrid LDO 的設計考量，例如哪個迴路當 P、哪個當 I。
- 可用來解釋兩迴路的分工與衝突。澳門大學 IME 網站有簡報 PDF（未開啟）。

**H08 — Huang, Lu, Sin, U, Martins, Ki, "Limit Cycle Oscillation Reduction for Digital LDOs," TCAS-II 63(9):903–907, 2016**（候選 DOI 10.1109/TCSII.2016.2534778）
- 類型 **Crit**：D-LDO 天生會有 limit cycle oscillation（LCO），以數位為穩態主體的 C 類 hybrid 也會繼承這個問題。
- 摘要指出兩種舊解法的代價：提高 ADC 解析度會增加複雜度；用 comparator dead-zone 會拖慢偵測並降低輸出精度。本文用 feed-forward compensation 降低 LCO。
- 澳門大學 IME 網站可能有全文 PDF（未開啟確認）。

**H09 — F. Chen, Yasu Lu, P. K. T. Mok, "A Fast-Transient 500-mA Digitally Assisted Analog LDO With 30-µV/mA Load Regulation and 0.0073-ps FoM in 65-nm CMOS," JSSC vol. 56（p. 511 起）, 2021**（候選 DOI 10.1109/JSSC.2020.3015527）
- 架構 **B（DAA）**：結合類比控制的緊密調節與寬負載範圍，以及數位控制的 power transistor 面積效率與快速暫態。
- 65 nm、500 mA、load regulation 30 µV/mA（標題/摘要）。

**H10 — D. Zhou, J. Jiang, Q. Liu, E. G. Soenen, M. Kinyua, J. Silva-Martínez, "A 245-mA Digitally Assisted Dual-Loop LDO," JSSC 55(8):2140–2150, 2020**（候選 DOI 10.1109/JSSC.2020.2987718）
- 架構 **B**：digital LDO 處理大電流擺動，analog LDO 負責穩態，另有 loop controller 協調兩個迴路。
- 搜尋轉述還提到 40 nm、Iq 300 µA、約 0.056 mm²、PSR 約 −42 dB@1 MHz，但片段有和他篇混淆的跡象，**沒填進數字欄，需要核對**。

**H11 — Z. Jin, G. Kim, D. H. Baek, "A Self-Triggered Digitally Assisted Hybrid LDO with 110 ns Settling Time in 65 nm CMOS," Electronics 12(15):3215, 2023（MDPI，OA）**（DOI 10.3390/electronics12153215，見於出版社頁，但未能用 doi.org 解析）
- 架構 **B**：analog LDO 負責穩態，digital LDO 只在大負載階躍時自觸發，使用 self-generated clock 與 flash ADC，並保留 analog LDO 的 PSRR。
- TSMC 65 nm；200 mA/10 ns 負載階躍：undershoot 82 mV/89 ns、overshoot 112 mV/110 ns；Iq 200 µA；FoM 4.48 ps；0.027 mm²（實測，摘要）。
- **開放全文**，適合當學生專題的 B 架構參考，但我本次沒能打開。

**H12 — J.-H. Jung, S.-K. Hong, O.-K. Kwon, "A Fast Transient Response Hybrid LDO With Highly Accurate DC Voltage Using Countable Bidirectional Binary Search and Soft Swap Switching," TCAS-II 67(12):3272–3276, 2020**（候選 DOI 10.1109/TCSII.2020.2992056；DBLP 另列 no.11、pp.2312–2316，有衝突）
- **0.18 µm、Vin 1.2–1.8 V、Vout 0.9 V**（實測），跟本專題製程與 Vin 範圍最接近。
- 架構：analog LDO + digital LDO + hybrid controller；CBBS 與 SSS 都用 **logic synthesis** 實作；SSS 透過控制 analog LDO 的開啟時機來微調電流，以得到高 DC 精度。
- arch **未確認**：看起來像 digital 粗調 + analog 細調，但誰供應穩態主電流不明。

**H13 — Y.-J. Lee et al.（Samsung）, "A 200-mA Digital LDO With Coarse-Fine Dual Loop in Mobile Application Processor," JSSC 52(1):64–76, 2017**（候選 DOI 10.1109/JSSC.2016.2614308）
- 架構 **D**：coarse-fine 兩個迴路都是數位。coarse loop 用 current-mirror flash ADC 供大電流，fine loop 處理小電流並降低 ripple。
- 摘要明說用 digital controller 防止兩迴路互相 contention，可當「雙迴路衝突」的佐證。
- 28 nm、1.1 V→0.9 V、200 mA、180 mA 階躍時約 120 mV 壓降、0.021 mm²（實測）。

**H14 — X. Liu et al.（Intel）, "A Modular Hybrid LDO with Fast Load-Transient Response and Programmable PSRR in 14nm CMOS…," ISSCC 2019, 14.7, pp. 234–236**（候選 DOI 10.1109/ISSCC.2019.8662343）
- 可以在 ALDO 與 DLDO 模式間重組。
- 摘要片段：ALDO 模式 PSRR 可程式至約 −42 dB、Iq < 27.3 µA；DLDO 模式在 >1 A/ns 負載變化下最差 droop 133 mV；暫態 < 90 ns。片段可靠度中等，**沒填數字欄**。arch 未確認。

**H15 — S. B. Nasir, S. Sen, A. Raychowdhury, "Switched-Mode-Control Based Hybrid LDO for Fine-Grain Power Management of Digital Load Circuits," JSSC 53(2):569–581, 2018**（候選 DOI 10.1109/JSSC.2017.2767183）
- 130 nm。以 switched-mode control 在數位與類比控制器之間瞬時切換，兼顧快速 droop recovery 與精確穩壓。
- 130 nm 會議版（IEEE Xplore 7598306）的摘要轉述：digital 負責快速響應、analog 負責穩態，10.3 mA 階躍暫態 18 ns。這個描述偏 B，但期刊版未確認，CSV 標未確認。
- **全文由 Georgia Tech 實驗室網站公開**（bpb-us-e1.wpmucdn.com/sites.gatech.edu/.../08119722.pdf），未能打開。

**H16 — "Embedded hybrid LDO topologies for digital load circuits"（IEEE Xplore 7803891；作者、會議、年份都未確認）**
- 類型 **Crit**：digital 與 analog controller 並聯；analog 的 GBW 越高越能壓 LCO。
- 但兩個控制器強度不均加上功耗限制，難以涵蓋寬操作範圍。這可以直接當 hybrid 限制的引用（確認書目後）。

### 其他候選（資訊不足，沒列入 CSV）
- "An Analog-Proportional Digital-Integral Multiloop Digital LDO With PSR Improvement and LCO Reduction"，JSSC vol. 55 no. 6, June 2020。作者未在搜尋結果中確認；澳門大學 IME 網站有 PDF（ime.um.edu.mo/wp-content/uploads/magazines/c8a7e9a799fe0604811af78d1501e948.pdf）。看名稱應屬 C，可能同時談 LCO。
- "Analog-Assisted Digital Capacitorless LDO Supporting Wide Load Range"，IEEE Trans. Ind. Electron. 66(3), March 2019, p.1799 起。130 nm、50 mA、Vin 1 V / Vout 0.8 V、0.0645 mm²。NSF PAR 有開放 PDF：https://par.nsf.gov/servlets/purl/10094502 。作者未確認，屬 C。
- "Hybrid Capacitor-less LDO with Switched-Mode Dead-Zone Control"，2021（IEEE Xplore 9547938；作者含 N. Laleni、A. Tsiougkos 等；會議名未確認）。180 nm X-FAB，10 µA–10 mA，跟 dead-zone 設計有關。
- "A Reconfigurable Hybrid Low Dropout Voltage Regulator for Wide-Range Power Supply Noise Rejection and Energy-Efficiency Trade-Off"（IEEE Xplore 8319450）。130 nm、四種模式；Georgia Tech 網站有 PDF（icsrl.ece.gatech.edu/files/2021/06/08319450-1.pdf）。作者、期刊未確認。
- "A 0.4V 430nA quiescent current NMOS digital LDO with NAND-based analog-assisted loop in 28nm CMOS"（ISSCC 2018；另有 JSSC 期刊版）。屬 C、超低 Iq，跟本專題的規格差很遠。
