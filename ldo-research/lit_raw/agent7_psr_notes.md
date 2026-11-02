# agent7：capless LDO 中高頻 PSR 增強技術（2014 至今）

- 範圍：output-capacitorless / capless LDO 在 100 kHz～百 MHz 的 PSR 增強。對照專題條件：0.18 µm、Vin 1.8 V → Vout 1.6 V（dropout 200 mV）、10–100 mA、on-chip CL 100 pF–1 nF、只有 LTspice、不寫 Verilog。
- 方法：只用 WebSearch 的搜尋摘錄，共用了 **35 次**。學術網站被網路政策封鎖，**每一篇都沒開全文**，fulltext_status 一律填「僅摘要（搜尋摘錄，未開啟全文）」。
- 摘錄只有摘要時，表內只寫技術名稱，不寫電路怎麼接。標 [推論] 的是我依一般電路原理的判斷，不是出自該文獻。標 [專利] 的是專利文件，不是同儕審查論文。
- DOI 只填摘錄中明確出現的（PS01、PS02、PS05、PS06、PS11），**都沒有經 doi.org 驗證**。
- 去重：Tang/Jiang CICC 2024（NMOS cap-less、180 nm、−30 dB @10 MHz）已在 agent2 的 **A04**，本檔不重收，只引用 A04。另外引用既有的 A01、A03、A11、A12、A13、D12、F08，不重收。
- **合併腳本注意**：`merge_literature.py` 依 id 前綴決定 source_agent，目前只認 HB、SD、H、A、D、F。`PS` 開頭會在 `{"H":…}["P"]` 觸發 KeyError。我沒有改這個檔，需要主 agent 加上 `"PS": "agent7(PSR)"`。

---

## §1 技術分類表

| 技術 | 原理一句話（有來源才寫） | 文獻 id | 在本專題的可行性與代價 |
|---|---|---|---|
| Feedforward ripple cancellation／replica path（複製 ripple 到 PMOS pass gate） | PS04 摘要：用 buffer「replicate a supply ripple to the gate of pass transistor」。A01 摘要：用 replica 電路追蹤 supply noise 的 noise-cancellation 路徑。 | A01、PS04（F08 也是 0.18 µm 以外的高 PSR capless 參考） | **高**。純類比，不需時脈或 Verilog。額外元件：replica／buffer 路徑與偏壓。代價：Iq 增加（PS04 總 Iq 33 µA、A01 運作時 80 µA）；抵消量會隨負載改變，需要 adaptive 偏壓（見下兩列）。抵消路徑接在 gate 側，不和 pass device 串聯，所以不吃 200 mV dropout [推論]。 |
| Adaptive body／bulk 注入 | A03 摘要：把複製的 supply ripple adaptive 注入 body gate，壓掉 gate-pole-dominant LDO 的 PSR hump。PS01 摘要：注入 power transistor 的 bulk，寬負載下 PSR 改善維持穩定。 | A03（65 nm）、PS01 | **中**。PMOS pass 的 N-well 在標準 0.18 µm 製程通常可以單獨接，需查 PDK [推論]。代價：bulk 節點寄生電容大、body–source 接面有順偏風險 [推論]。PS01 只有 post-layout 模擬。 |
| Supply-referenced gate drive／在 pass gate 注入補償電流 | PS11 摘要：在功率管柵極注入與頻率相關的補償電流，改善中頻段 PSR。PS03 摘錄：pass transistor 的 parasitic gate-drain capacitance 在中低頻就會影響 PSR。 | PS11、PS03、A13（PSR 模型） | **中-高**。純類比。代價：PS11 自己說要做動態調整，才能減少壓差與負載變化對效果的影響，可見這類方法對 dropout 與負載敏感。 |
| Negative capacitance | PS09 摘要：用 negative-capacitance circuit 改善 PSR。電路怎麼接摘要沒寫。 | PS09（0.18 µm，−76 dB @1 MHz） | **中**。同製程、純類比、有量測。代價：摘要沒有寫。negative capacitance 一般需要匹配，也會壓縮穩定度餘裕 [推論]。要讀全文才能動手。 |
| NMOS pass（source follower）＋ charge pump | NMOS 由 source 輸出、drain 接 Vin，所以 Vin ripple 主要只能經 ro／Cds 耦合到輸出 [一般原理，非出自本批摘錄]。代價見專利摘錄：on-chip charge pump 會「introducing switching noise and increasing … die area」（US20140340058 [專利]）；charge pump 升壓的 ripple 漏到輸出，提高 output noise（US8248150 [專利]）。 | A04（180 nm，−30 dB @10 MHz）、PS06（180 nm n-type，−40 dB @1 MHz）、PS05（event-driven CP）、PS07 | **低-中**。1.8→1.6 V 時，gate 至少要 1.6 V＋VGS，超過 1.8 V，所以一定要 charge pump 或額外的高壓軌 [推論]。額外元件：振盪器（ring oscillator 可純類比）、CP、CP 輸出濾波。還要查 1.8 V 元件的閘極氧化層能不能承受高於 1.8 V 的 gate 電壓（PDK 確認）[推論]。LTspice 暫態要模擬很久。 |
| Cascoded／兩級 pass | PS10 摘要：cascaded 2-power-transistor，每級各有 PSR 增強，兩級合計 dropout 200 mV。 | PS10 | **中**。200 mV dropout 要分給兩顆 pass，每顆的 VDS 更小，W 要更大 [推論]。PS10 的數字只報到 100 kHz，MHz 以上沒有證據。 |
| 多迴路／快慢迴路（full-spectrum） | PS02 摘要：低增益快迴路負責高頻 PSR 與暫態，高增益慢迴路負責低頻 PSR 與 line/load regulation。 | D12（65 nm，DC–20 GHz < −12 dB）、PS02（65 nm）、PS06、A11（40 nm，−35 dB @10 MHz @200 mA） | **中**。純類比，但迴路多，補償難度高。「full-spectrum」的數字在高頻端只有 −12 dB 左右，意思是不放大，不代表抑制很強。 |
| Voltage subtractor 誤差放大器 | A12 比較（摘要）：voltage subtractor 的 PSR 最好，但雜訊也最大。 | A12、PS12（0.18 µm、200 mV dropout） | **高**。同製程、同 dropout，有學生論壇等級的設計可對照。代價：雜訊（A12）。PS12 的 PSR 數字沒取得。 |
| 寬 CL 範圍下的高頻 PSR | 摘錄未取得原理。 | PS08 | 待讀全文。專題 CL 100 pF–1 nF 正需要。 |
| RC filtered gate／embedded capacitor | 2014 年後的 capless 文獻**沒找到**（見 §4）。 | — | — |
| 限制／反面 | PS03 摘錄：「Series Feedback provides the best compromise with respect to PSR enhancement」。 | **PS03**（專門的取捨比較）、A12、A13；附帶證據：PS06（PSR 隨負載變差）、PS07（Iq 代價）、PS10（只到 100 kHz）、PS11（對壓差與負載敏感）、A03（需要 adaptive 才能涵蓋負載與 PVT） | 見 §3。 |

背景（專利，非同儕審查）：一份 capless 高 PSR 專利（US8754621 家族）的背景段落說，capless LDO 的 PSR 在 DC 通常高於 60 dB，到 1 MHz 會掉到接近 0 dB。我們的模擬結果（1 MHz 只剩 −5～−9 dB）屬於這種典型行為，不是模擬錯誤。

---

## §2 每篇摘要與可行性

**PS01 Lin et al., IJCTA（年份未確認），adaptive bulk-driven feedforward**
- 把 supply ripple 以 adaptive 方式注入 power transistor 的 bulk。摘要稱寬負載下 PSR 改善穩定，也降低 Iq、加快暫態。
- 數字：−75 dB @1 MHz，負載 1–100 mA，CL 100 pF，FoM 60 fs [S，post-layout]。製程與 Vin/Vout 摘錄未載。
- 可行性：中。條件（1 MHz、1–100 mA、100 pF）和專題幾乎一樣，是最好的模擬對照。但這是模擬結果，製程也未知。額外元件：feedforward 放大／注入路徑、adaptive 偏壓。要先確認 PDK 的 PMOS N-well 可單獨接 [推論]。

**PS02 Zheng et al., Electronics Letters 2024，push–pull FVF full-spectrum PSR**
- 65 nm FVF push–pull 架構，快迴路處理高頻 PSR，慢迴路處理低頻。
- 數字：全頻段 < −12 dB、Iq 58 µA、負載 10 µA–20 mA、CL 0–30 pF、暫態 2.4 ns [result_type 未知]。
- 可行性：中-低。架構是純類比，但電流與 CL 範圍和專題差很多。高頻端 −12 dB 只比我們 10 MHz 的 0 dB 好一點。可當「快慢迴路分工」的概念參考。

**PS03 Shylaja & Rincón-Mora, TCAS-II 2021（推定），High-PSR LDOs：取捨比較〔Crit〕**
- 在同一個 high-PSR core 上，用 SPICE 比較多種 PSR 增強法。結論是 series feedback 的折衷最好。
- 指出 pass transistor 的 Cgd 在中低頻就會影響 PSR。
- 可行性：不是電路，是選技術用的依據。作者頁有 PDF，但這次沒開。建議教授或同學從校內網路下載全文，看各技術的 Iq、面積、頻寬比較。

**PS04（作者未確認），double buffers technique，0.18 µm**
- 用一個 PMOS buffer 與一個 NMOS buffer，把 supply ripple 複製到 pass gate，並延伸負載範圍。
- 數字：PSR 改善最高 40 dB（頻段描述未確認）、Iq 33 µA、Imax 50 mA [S]。
- 可行性：**高**。同製程、純類比，而且只多兩個 buffer，是專題最直接能照做的 FFRC 形式。缺點是書目不完整（作者、出處、年份都沒有），引用前要補。

**PS05 Xie et al., J. Semicond. 2024，NMOS capless＋event-driven charge pump**
- NMOS pass 雙迴路，charge pump 迴路加 dynamic strength control，也處理大訊號穩定問題。重點在暫態，不在 PSR。
- 數字：比較表輸入範圍 0.85–3.3 V。PSR 沒能確認（比較表片段有「−32@1M」，但不知道是哪一列）。
- 可行性：低-中。這篇說明 charge pump 迴路本身就帶來穩定度問題，這是 NMOS 方案的代價之一。event-driven 是否需要數位邏輯未確認。

**PS06 Jeon et al., TPEL 2024，600 mA multifeedback n-type capless**
- n-type capless LDO，用多重回授迴路同時改善 PSR 與暫態。
- 數字：180 nm、Iq 27.5 µA、PSR −40 dB @1 MHz @100 mA、−25 dB @1 MHz @600 mA、1→600 mA undershoot 116 mV（邊沿時間未載）、0.063 mm² [M]。
- 可行性：中。製程相同，100 mA 時的 PSR 有參考價值。gate 驅動方式（CP 或額外電源軌）、Vin/Vout 都沒寫，要讀全文才知道 1.8→1.6 V 做不做得到。這篇也證明 PSR 會隨負載變差。

**PS07（作者未確認），World Scientific 2020，NMOS adaptive network**
- adaptive network 內的 NMOS 追蹤經 power transistor 的電源雜訊，把雜訊電流旁路到地。
- 數字：0.18 µm、低頻約 −125 dB、−60 dB @1 MHz @4 mA，1–10 mA 範圍內靜態功耗 1.35 mW。
- 可行性：中。原理簡單，但 1.35 mW 的靜態功耗以 10 mA 負載來說太大；若供電 1.8 V，約 0.75 mA [推算]。這篇可當「提升 PSR 犧牲 Iq」的例子。

**PS08 Zarate-Roldan et al., TVLSI 2016，寬 on-chip CL 範圍的高頻 PSR**
- 只確認書目（dblp），摘要與數字沒取得。
- 可行性：未知。標題正對專題的 CL 100 pF–1 nF 問題，建議優先找全文。和 A12 同為 TAMU Sánchez-Sinencio 組。

**PS09 Yun, Kim, Kim, TCAS-II 2017，negative capacitance，−76 dB @1 MHz**
- negative-capacitance circuit 改善 PSR，voltage damper 改善 FOM。
- 數字：0.18 µm、−76 dB @1 MHz、總 on-chip 電容 12.7 pF、FOM 96.3 fs [M，依摘要轉述]。負載條件未載。
- 可行性：中。本批 0.18 µm 量測中 1 MHz 數字最好，而且只用 12.7 pF。但摘要沒寫電路，不能憑摘要照做。和 A02 同一研究群，可一起讀。

**PS10 Han, Ki, Wu, Gao, SSC-L 2022，兩級 pass，200 mV dropout**
- cascaded 2-power-transistor，每級各有 PSR 增強，再用 reversed-phase supply-ripple cancellation reference buffer 進一步改善。
- 數字：Vin 1.1–1.2 V、Vout 0.9–1.0 V、無載 Iq 24.2 µA、PSR 優於 −95 dB 至 100 kHz [M]。製程只在一則搜尋摘要中看到 0.18 µm，未確認。
- 可行性：中。dropout 和專題一樣是 200 mV，但兩顆 pass 分這 200 mV，100 mA 時 W 會很大 [推論]。MHz 以上沒有數字，最大負載也沒寫。

**PS11 徐叶 et al., 电子学报 2022，pass gate 注入補償電流**
- 用 push-pull 放大器，省去複雜補償與片外大電容。在 pass gate 注入與頻率相關的補償電流，改善中頻段 PSR，並動態調整補償電流。
- 數字：0.11 µm、0.026 mm²、8 kHz–1 MHz 內 PSR 最大改善 21–37 dB（不同壓差與負載）[result_type 未知]。
- 可行性：中-高。純類比，對應「supply-referenced gate drive」。摘要自己說效果受壓差與負載影響，是限制證據。中文期刊，全文可能比較好取得。

**PS12 Silva et al., SBMicro SForum 2020，voltage subtractor，0.18 µm**
- 兩個 voltage subtractor 型 LDO，差在誤差放大器差動對是 PMOS 或 NMOS。
- 數字：0.18 µm TSMC、Vout 1 V、dropout 0.2 V [S]。PSR 數字沒取得。
- 可行性：高。同製程、同 dropout，難度是學生等級。用語上 capacitor-less 和 on-chip 電容的說法有矛盾，要看全文。

---

## §3 對專題的建議（若教授以 PSRR 為主要指標）

**首選：保留 PMOS pass，加一條 supply-ripple replica／feedforward 路徑，把 Vin ripple 複製到 pass gate（A01／PS04 型）；再加上依負載調整的 adaptive 偏壓。**

理由：
1. **同製程、同電壓有量測證據**。A01（0.18 µm、1.8 V 供電、50 mA）量到 PSR 優於 −56 dB 至 4 MHz，1 MHz 比未補償 LDO 改善 34 dB，4 MHz 改善 25 dB [M，摘要]。我們現在 1 MHz 只有 −5～−9 dB，正好落在這個技術見效的頻段。PS04 在 0.18 µm 模擬改善最高 40 dB，Iq 只有 33 µA。
2. **不需要 charge pump、時脈或 Verilog**，LTspice 的 `.ac` 就能驗證。NMOS＋CP（A04、PS06）在 1.8→1.6 V 時 gate 要高於 Vin，需要振盪器、CP、濾波，還要確認氧化層耐壓。專利也指出 CP 會帶來切換雜訊與面積代價 [專利]。
3. **不吃 dropout**。抵消路徑接在 gate 側，不和 pass device 串聯 [推論]。兩級 pass（PS10）要把 200 mV 拆給兩顆，而且只證明到 100 kHz。
4. **風險已知，也有應對文獻**。抵消效果會隨負載、壓差、PVT 改變：A03、PS01 都要做成 adaptive，PS11 也要動態調整，PS06 的 PSR 從 100 mA 到 600 mA 退了 15 dB。所以設計時一定要掃負載。

**次選**：negative capacitance（PS09，0.18 µm、−76 dB @1 MHz、12.7 pF）。數字比 A01 好，但摘要沒寫電路。拿到全文、確認做得出來之前，不建議當主方案。

**代價（要寫進報告）**：
- Iq 增加：PS04 總 Iq 33 µA，A01 運作時 80 µA。PS07 是反例，靜態功耗 1.35 mW。
- 對負載與製程敏感，需要 adaptive 偏壓。
- 抵消路徑的頻寬有限，10 MHz 以上的效果沒有 0.18 µm 的證據。本批 0.18 µm 文獻只有 A04 報到 10 MHz（−30 dB，NMOS）。

**LTspice 驗證步驟（建議）**：
1. 在 Vin 加 `AC 1`，報告 1 kHz、1 MHz、10 MHz、100 MHz 四個頻點的 PSR。
2. 用 `.step` 掃 Iload（10／50／100 mA）與 CL（100 pF／1 nF）。
3. 跑製程 corner 與溫度。
4. LTspice 不一定有 foundry mismatch 模型，所以手動把 replica 路徑的增益偏 ±10%，看 PSR 掉多少，當作敏感度指標 [建議]。

**HBM／SerDes 關心的 10–100 MHz**：本批 0.18 µm 文獻都沒有報到 100 MHz。那一段主要靠 on-chip CL 與 pass device 寄生電容的分壓 [推論]。建議另外比較 CL＝100 pF 與 1 nF 時 100 MHz 的 PSR，再把結果交給 agent5／agent6 的 jitter 分析使用。

---

## §4 沒查完的項目

- **RC filtered gate／embedded capacitor**：2014 年後的 capless 文獻沒找到。
- **專門分析 FFRC 失配或 Monte Carlo 敏感度的反面論文**：沒找到，只有間接證據（A03、PS01、PS11 都需要 adaptive）。
- **charge pump 漣波與雜訊的反面證據**：只有專利摘錄（US8248150、US20140340058，另有 US12456910 談 CP latch-up），沒有同儕審查論文。
- **書目缺漏**：
  - PS01：年份、製程。
  - PS04：作者、出處、年份。
  - PS07：作者、刊名。
  - PS08：摘要與數字。
  - PS05：PSR。
  - PS09：負載條件。
  - PS10：製程、Imax。
  - A04：Vin/Vout、是否用 CP。
- **沒列入 CSV 的線索**（之後可補）：
  - Lu, Ki, Yue, TPEL 2016〈An NMOS-LDO Regulated Switched-Capacitor DC–DC Converter With Fast-Response Adaptive-Phase Digital Control〉：摘錄說 NMOS source follower 需要 step-up CP 驅動。50 mV dropout 的 LDO 帶來 4.1% 效率、6.5% 面積開銷，20 mA 時 ripple < 2 mV。這是系統層數字，而且含數字控制。
  - ECNU〈A fast transient response capacitor-less LDO achieving 88 dB PSR〉：negative capacitance circuit，−88 dB @10 kHz [S]，只有低頻。
  - 長庚大學 NSTC 計畫「adaptive negative capacitance for high PSRR」：−80 dB @10 kHz @500 mA，是計畫頁，不是論文。
  - Kao et al. 0.18 µm FFRC：有 1 µF 外部電容，不是 capless。
  - US11782468／US12314071 current-mode FFRC 專利：宣稱 > 68 dB 至 2 MHz，負載 100 µA–250 mA。
  - TAMU 學位論文：ETD-TAMU-2010-12-8831 量到 −30 dB 至 420 kHz @50 mA；另一本 zero-Vt NMOS 論文不用 CP，−40 dB 至 10 MHz。兩本都是 2014 年前或學位論文。
  - ICTA 2022 22 nm capacitive bulk-driven feedforward；2026 Springer FVF-LDO enhanced bulk-driven feedforward；一篇 2024「capacitively coupled feedforward −60 dB @1–40 mA」，書目沒查出。
