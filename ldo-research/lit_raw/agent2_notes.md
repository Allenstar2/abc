# agent2：純類比 capacitor-less LDO 文獻筆記（2014 至今）

對應 CSV：`agent2_analog.csv`（A01–A15）。標註：[M] 論文實測、[S] 論文模擬、[D] 由讀到的數字推導、[H] 推測（沒讀全文，依一般 capless LDO 架構常識判斷）。

## 0. 取得方式與限制（先讀）

- **全文一篇都沒有實際打開。** 本 session 的 WebFetch 對 `oaktrust.library.tamu.edu`、`api.crossref.org`、`manuscript.isc.ac` 回 DNS 失敗，Bash curl 對 doi.org、IEEE Xplore、arXiv、Semantic Scholar、OpenAlex 也被代理擋（403）。所以書目與數字都來自 WebSearch 回傳的摘要與索引片段（IEEE Xplore 摘要、機構典藏、ADS、DOAJ、MDPI/PMC 頁）。
- **DOI 都是間接驗證**：用 DOI 字串搜尋，比對到 ADS、機構典藏或出版社記錄裡同一篇論文；沒有經過 doi.org 解析。A04、A09 沒有 DOI。
- **WebSearch 額度用完**（每輪 200 次，所有 agent 共用），所以 A01 的 Vout/CL、A03 的 Imax 等細節沒查完。
- 「fulltext_status」記的是**可取得性**（依搜尋結果與期刊 OA 性質判斷），不是「已讀」。CSV 每列的 notes 都有寫「未開啟」。
- 要補齊：在環境設定（cloud environment → Edit → Network access）把 `ieeexplore.ieee.org`、`doi.org`、`arxiv.org`、`oaktrust.library.tamu.edu`、`www.mdpi.com`、`pmc.ncbi.nlm.nih.gov` 加進允許網域，再讓我重跑全文核對。

## 1. 兩篇指定論文的確認結果

### A01 — Park, Onabajo, Silva-Martinez, JSSC 2014（已確認）
- 書目：IEEE JSSC vol. 49, no. 2, pp. 486–501, Feb. 2014；DOI 10.1109/JSSC.2013.2289897（ADS 記錄 2014IJSSC..49..486P 比對）；IEEE Xplore 6675881。
- 架構原理：分析 supply noise 從 Vin 到輸出的各條路徑，加上 power-supply noise cancellation 電路，並用 replica 電路在 PVT 變動下追蹤主路徑的 supply noise（屬前饋式 ripple cancellation）。
- 補償/主導極點：摘要沒寫。[H] 典型 capless 兩級架構的主導極點在 EA 輸出/pass gate，用 Miller 電容拉開；需全文確認。
- 關鍵數字（摘要）：PSR 優於 -56 dB 到 4 MHz @50 mA [M]；相對未補償 LDO 改善 34 dB @1 MHz、25 dB @4 MHz [M]；0.18 µm、1.8 V；core 0.14 mm²；Iq 80 µA（operation）/55 µA（standby）。邊沿時間未載明（PSR 論文）。
- 開放全文：**沒找到**。ResearchGate 無全文；OAKTrust 找不到 Park 本人的學位論文。同組開放背景資料：Ganta 2010 碩士論文《Power Supply Rejection Improvement Techniques in LDO》OAKTrust PDF（2014 前，網址有，未開啟）。core.ac.uk 85461616 有一本 TAMU 系的 bulk-driven feedforward capless LDO 學位論文（目標 -60 dB @1 MHz @50 mA、130 nm），作者未確認，不能當成 Park 的論文。
- 其他符合「JSSC 2014 + capless + PSR enhancement」的：**沒找到第二篇 JSSC 2014**。同組相關：Park/Silva-Martinez(/Onabajo)〈Design techniques for external capacitor-less LDOs with high PSR over wide frequency range〉（MWSCAS 2014，IEEE Xplore 6908422；片段寫 0.18 µm、PSR 優於 -50 dB 到 4 MHz，未完整驗證）。
- 可行性：製程、Vin、負載等級和專題幾乎一樣，最適合當 PSR 的基準論文。replica 匹配需要跑 corner；建議先做未補償版本，再加前饋路徑。

### A02 — H. Kim, S. S. Kwak, Y. S. Kim, ISCAS 2022（已找到）
- 書目：〈LDO Regulator Optimized on Power Efficiency and Load Transient Response with Voltage Damper and Body Loop Feedback〉，IEEE ISCAS 2022（Austin），pp. 3571–3574；DOI 10.1109/ISCAS48785.2022.9937778（DOI 字串搜尋比對到 Korea Univ. Pure 記錄）；IEEE Xplore 9937778。
- 架構原理：op-amp 設計成低 Iq 高 slew rate；voltage damper 負責快速負載暫態；body feedback loop 調 pass transistor 的 body，處理較慢的輸出偏移。等於快慢兩條路徑分工。
- 補償/主導極點：摘要沒寫。[H] 主迴路的主導極點應在 pass gate；body loop 頻寬較低，作為慢速第二迴路。
- 關鍵數字（摘要）：180 nm；最大 undershoot 125.9 mV；Iq 0.02532 mA；FOM 摘要寫作 0.177 ns/µm（單位看起來是排版問題）。摘要用「test results」一詞，量測或模擬**未確認**。負載步階、CL、邊沿時間未載明。
- 注意：標題沒寫 capless，是否完全無輸出電容要看全文。同組（Yong Sin Kim，高麗大學）有 J. E. Kim & Y. S. Kim 的 capless voltage damper + body bias feedback 韓國國內論文（0.18 µm、0.026 mm²、9.32 pF on-chip），以及 Lee/Im/Lee/Kim 的 ISOCC 2022（dual feedback loop + voltage dampers）。學生記得的可能混了這幾篇。
- 可行性：180 nm、Iq 約 25 µA 可行；PMOS pass 在 n-well 裡，body 可以獨立接，body loop 做得出來。damper 是非線性輔助路徑，要模擬切換時的穩定度。

## 2. 其他論文

### A03 — Lim et al., JSSC 2018（adaptive supply-ripple cancellation）
- 原理：把 supply ripple 以適應增益注入 pass transistor 的 body-gate，抵消 Vin 經 pass device 漏到輸出的 ripple（前作 ASP-DAC 2018 標題寫明注入 body-gate）。屬前饋 PSR 增強。
- 補償/主導極點：摘要未寫；[H] 主導極點在 pass gate。
- 數字（摘要）：65 nm、Vin 1.2 V、CL 240 pF；PSR < -36 dB，10 kHz–1 GHz 全頻段，且跨負載電流、dropout 與 PVT 都成立 [M]。Imax 未取得；邊沿時間未載明（PSR 論文）。
- 可行性：0.18 µm PMOS 的 body 注入在物理上做得到，但 adaptive 增益的校準對大學部偏難，適合當 PSR 加分項。

### A04 — Tang, Jiang et al., CICC 2024（NMOS pass + super source follower）
- 原理：NMOS pass transistor + dual-loop；adaptive biasing 加 zero compensation，維持 0.1–300 mA 全範圍穩定；N-SSF 加上 small/large-signal conflict-softening filter 提升 slew。
- 補償/主導極點：NMOS source follower 輸出阻抗低；[H] 主導極點較可能在 pass gate，輸出極點因 1/gm 而偏高頻。
- 數字（摘要）：180 nm；重載頻寬達 44.6 MHz；undershoot 18 mV，負載 1→272 mA、**邊沿 100 ns**、on-chip CL 50 pF [M]；PSR 優於 -30 dB @10 MHz（1 mA 與 100 mA）[M]。DOI 未驗證。ResearchGate 同名條目另有一組不同數字（可能是期刊版），未採用。
- 可行性：製程對得上，但 Vin 1.8 V、Vout 1.6 V 時 NMOS 閘極要高於約 Vout+Vth，等於要 charge pump 或額外高壓偏壓，下線複雜度高。SSF buffer 的概念可以移植到 PMOS 版本。

### A05 — Limpisawas & Wattanapanitch, IEEE Access 2022（indirect-direct nested Miller）
- 原理：三級放大加 indirect 與 direct 兩種 nested Miller 補償，目標是在寬負載電流與寬負載電容下都穩定。
- 主導極點：[H] nested Miller 典型做法下，主導極點在第一級輸出，pass gate 與輸出為非主導極點；要用全文確認。
- 數字（摘要）：0.18 µm（ResearchGate 片段）；0–100 mA；CL 0–1 nF；Iq 14 µA。M/S 未確認；暫態數字與邊沿時間未取得。
- 可行性：規格和專題（0.18 µm、10–100 mA、100 pF–1 nF）幾乎重疊，而且是 OA。**最推薦當主架構參考**，要先讀全文確認量測條件。

### A06 — Ni et al., Micromachines 2022（電容耦合式 slew-rate enhancement）
- 原理：補償電容 Cm、Ct 在負載暫態時把輸出變化耦合到 current booster（電容耦合快速路徑），booster 加速 pass gate 的 slew；feed-forward 轉導級和 pass transistor 組成 push-pull，加速輸出節點。
- 補償/主導極點：Cm/Ct 兼作頻率補償；[H] 主導極點在 EA 輸出。
- 數字：摘要寫 Iq 30 µA、dropout 200 mV、Imax 100 mA。以下引自他人比較表（Micromachines 2024 640 nA OCL-LDO，PMC11356146），未對原文核對：180 nm、0.001–100 mA、負載 slew 99.9 mA/µs（約 1 µs 邊沿 [D]）、overshoot 197 mV。M/S 未確認。
- 可行性：100 mA、200 mV dropout 跟專題完全一樣，SRE 只多幾顆電晶體，可行性高，而且是 OA。

### A07 — Chen et al., Micromachines 2024（super source follower buffer）
- 原理：RIPO（rail-to-rail input、push-pull output）放大器 + SSFB 驅動 pass gate。SSF 的低輸出阻抗把 pass gate 的極點推到高頻，同時提供大電流 slew。
- 主導極點：[H] 主導極點在 RIPO 輸出（SSF 輸入端），pass gate 極點被 SSF 推高。
- 數字（摘要）：180 nm；Vin 1.2–1.8 V、Vout 1.0 V；圖說顯示 20 mA 負載、無負載電容的暫態模擬 [S]。undershoot/Iq 數字未取得；邊沿時間未載明。
- 可行性：SSF 結構簡單，適合學生；但只有模擬，需要自己驗證 CL 100 pF–1 nF 下的穩定度。

### A08 — Lu et al., Electronics 2022（FVF + dynamic bias）
- 原理：FVF 型 OCL-LDO，用 MOS 感測輸出變化，動態調整 Ibias1/Ibias2，快速充放電 pass transistor 的大 Cgs，宣稱不增加靜態功耗。
- 主導極點：[H] FVF 的 shunt feedback 讓輸出阻抗很低，主導極點通常在 pass gate。
- 數字：0.18 µm。片段出現 248 mV、260 mV、177 ns，但沒標示是什麼，未採用。邊沿時間未載明。
- 可行性：0.18 µm、FVF 電晶體數少，可行。要確認 1.8→1.6 V 的 headroom 和 100 mA 時 pass device 尺寸（gate 電容會很大）。

### A09 — Engür & Shoaran, arXiv 2023（FVF + SSF + dual-range bias）
- 原理：FVF + super source follower buffer 驅動 pass transistor，用 bias switching 在兩個負載檔（0–500 µA / 5–15 mA）間切換，宣稱 Iq 比傳統做法低約 14 倍。
- 主導極點：[H] 同 A08，在 pass gate，SSF 降低該節點阻抗。
- 數字（摘要）：65 nm；Vin 1.5 V、Vout 1.2 V；Iq 3 µA / 50 µA [M]；0→15 mA、**邊沿 80 ns** 時 undershoot 100 mV（量測或模擬未確認）；FOM 0.21 ps；電流效率 99.98%。
- 可行性：負載規模只有 15 mA，dual-range 切換對專題可能是過度設計；FVF+SSF 的組合值得參考。arXiv 開放全文。

### A10 — Ning et al., Electronics 2023（DFC + comparator 型快速迴路）
- 原理：damping-factor-control（DFC）補償確保穩定，另加 comparator 型 fast feedback loop 處理大訊號暫態。
- 主導極點：[H] DFC 架構沿用 Leung & Mok 2003 的思路，主導極點在第一級輸出，DFC 區塊控制非主導複數極點的阻尼。
- 數字（摘要）：0–100 mA 穩定；模擬相位裕度在負載範圍內 > 50° [S]。製程未確認；片段中的其他數字（3.3–4.5 V、200 mA、33/37 mV）來源段落不明且與摘要矛盾，未採用。
- 可行性：DFC 是經典 capless 補償，學生做得到；但這篇的規格要讀全文確認後才能引用。

### A11 — Lim et al., TVLSI 2017（loop-gain stabilizer，寬負載 PSR）
- 原理：capless LDO 的 EA 輸出 DC 準位會隨負載漂移，讓 loop gain 與 UGF（也就是 PSR）跟著變。stabilizer 把該準位固定在最佳值，使 UGF 在至 200 mA 都維持高。
- 補償：4 pF on-chip 補償電容（不是負載電容）。[H] 主導極點在 pass gate。
- 數字（摘要）：40 nm；Vin 1.1 V、dropout 0.1 V；200 mA 時 PSR -60 dB @1 MHz、-35 dB @10 MHz [M]；Iq 275 µA（stabilizer 7 µA）；0.008 mm²；load reg 19 µV/mA；line reg 0.75 mV/V。邊沿時間未載明。
- 可行性：思路可以移植到 0.18 µm，但要多一個迴路。對專題主要的價值是提醒量測時 PSR **要掃負載電流**，不能只報一個點。

### A12 — Torres et al., IEEE CAS Magazine 2014（限制/比較，Crit）
- 內容：在同一個 0.6 µm 製程下比較五種 capless LDO 架構。摘要明說拿掉外部電容會讓穩定度與暫態變差。
- 結論（摘要）：voltage subtractor PSR 最好、differentiator settling 最快、transimpedance Iq 最低（critical load 下 50 µA）但 DC loop gain 低所以 PSR 差；輸入對較小的 subtractor 雜訊最大。結論是沒有一種架構在所有指標都贏。
- 為何算反面/限制：直接說明 capless 的代價，並證明「同製程、同條件」比較時排名會隨指標改變，間接支持「跨論文 FoM 不可直接比」。
- 可行性：必讀，用來選架構；0.6 µm 的數字不能直接套到 0.18 µm。

### A13 — Joo, Kim, Kim, IEICE Trans. Electron. 2017（PSR 模型分析，Crit）
- 內容：建立不同 active load 與 pass transistor 組合下 capless LDO 的 DC 與高頻 PSR 模型，給出「高 DC PSR」或「平坦頻寬」的設計準則；模型以 SPICE 與 0.18 µm 量測驗證 [M]。
- 為何算限制：它說明 PSR 在中高頻變差是 pass device Cgs/Cgd 與 active load 選擇造成的結構性限制，不是調參數就能消除。（這是限制分析，不是嚴格意義的反面意見。）
- 具體數字未取得。
- 可行性：很適合拿來推 PSR 手算公式，再跟本專案 `sim/` 的 ngspice 結果對照。

### A14 — Chyan et al., IEEE Access 2022（類比 LDO 回顧，R）
- 內容：回顧近年類比 LDO 架構並比較性能與應用；摘要指出主要取捨是負載暫態、PSR、regulation 與低 Iq、低 dropout 之間的拉扯，並指出類比 LDO 在輸出漣波與 PSR 上優於數位 LDO。
- FoM 比較表內容未取得。引用比較表時要自己統一邊沿時間與 CL，不能直接排名。
- 可行性：OA，可以當專題比較表的起點。

### A15 — Pereira-Rial, Carrillo, López, TCAS-I 2024（bulk-driven vs gate-driven）
- 內容：EA 採 unity-gain feedback，避免大阻值 on-chip 電阻；在同一 LDO 結構下比較 bulk-driven 與 gate-driven EA。
- 數字（摘要）：180 nm、最高供電 1.8 V；相同參考電壓與負載條件下，最低供電 bulk-driven 0.6 V、gate-driven 1 V [M]。負載與暫態數字未取得。
- 可行性：專題 Vin 1.8 V，不需要 sub-1 V，所以 bulk-driven 不是必要；但可以當 A02 body loop 的元件層背景（body 轉導 gmb、latch-up 風險）。USC 典藏列有開放 PDF（未開啟）。

## 3. 主題覆蓋與缺口

| 主題 | 涵蓋論文 |
|---|---|
| adaptive / dynamic biasing | A04、A08、A09 |
| slew-rate enhancement | A06、A04 |
| FVF | A08、A09 |
| super source follower buffer | A04、A07、A09 |
| 電容耦合 / differentiator 快速路徑 | A06；A12（differentiator 架構比較） |
| Miller / nested Miller | A05 |
| damping-factor control | A10 |
| multi-loop / 快慢雙迴路 | A02、A04、A10、A11 |
| 前饋 ripple cancellation | A01、A03 |
| NMOS pass | A04 |
| 0.18 µm 且 50–100 mA | A01、A05、A06（，A04 180 nm 300 mA） |
| 限制 / 反面 | A12、A13（A11、A14 也提供限制證據） |

缺口（沒有找到並驗證到可列入的 2014 後論文，下一輪要補）：
- **Q-reduction**、**pole-zero tracking**：沒有驗證到合適的 2014 後純類比 capless 論文。有一篇 TPEL 2026 的 adaptive zero compensation + bulk negative capacitance 0.18 µm capless LDO（ResearchGate 片段，DOI 10.1109/TPEL.2026.3681330），作者無法確認，所以沒列。
- **charge-pumped gate**：沒找到。
- **專門批評 FoM / 邊沿時間的論文**：沒有驗證到。搜尋時看到近期論文（例如 MDPI Energies 的 500-mA dual-mode NMOS OCL-LDO「for 5-ns edge times」）引入 edge-time scaling factor K_T = T_EDGE/T_EDGE,min，出處以 [7] 引用，原始出處未能確認。下一輪可查 K 因子的原始出處（可能是 Guo & Leung 2010 JSSC 的 6-µW OCL-LDO，**未驗證，勿直接引用**）。

## 4. 量測條件提醒（給比較表用）

- 有寫邊沿時間的只有 A04（100 ns、1→272 mA、CL 50 pF）和 A09（80 ns、0→15 mA）；A06 只有他人表格的 slew 99.9 mA/µs。其他都是「邊沿時間未載明」。
- 例子：A04 的 18 mV 是 100 ns 邊沿下量到的，如果同一顆晶片用 1 ns 邊沿量，undershoot 會不同 [H]。跨論文比 ΔV 或 FoM 時，要把邊沿時間、CL、ΔI 列在旁邊。
- PSR 數字要附負載電流（A01 @50 mA、A04 @1/100 mA、A11 @200 mA）。A11 與 A12 都說明 capless LDO 的 PSR 和穩定度會隨負載改變。
