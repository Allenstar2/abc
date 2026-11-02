# agent4 筆記：最接近學生條件的 LDO 實作（2014 至今）

對應 CSV：`agent4_feasible.csv`（F01–F14）。搜尋日期 2026-11-02。

## 先讀：這批資料的限制

1. **全文一篇都沒開成。** WebFetch 連到 doaj.org、www.mdpi.com、ieeexplore.ieee.org 都回 `ENOTFOUND`，這些網域被這個 session 的網路政策擋掉，所以停止再試其他網站。要開全文，得在環境設定的 Network access 把這些網域加入允許清單（至少 doi.org、ieeexplore.ieee.org、mdpi.com、ncbi.nlm.nih.gov、arxiv.org、oaktrust.library.tamu.edu、thesis.lakeheadu.ca、jsts.org、jos.ac.cn、iaescore.com）。
2. **數字全部是二手的。** 數字都來自 WebSearch 工具摘錄的摘要文字，這些摘錄本身經過模型整理，可能有誤，例如 F09 的「210mA to 100mA」。CSV 的 `numbers_source` 一律填「摘要」。`fulltext_url` 是搜尋結果中出現的全文連結，**沒有實際打開過**。
3. **DOI 都沒經 doi.org 開啟驗證。** 有填的 DOI 都出現在 DOAJ、dblp、ResearchGate、citedrive 或期刊列表頁的搜尋摘錄中。完全沒看到的 DOI 留空，並在 notes 註明「DOI 未驗證」。
4. **搜尋額度用完。** WebSearch 已達本輪上限（200 次，所有 agent 共用），所以 F01/F03/F04 的 CL 值、量測負載型式等細節沒能再補查。
5. **電晶體尺寸、補償元件值、量測 setup 都沒讀到。** 這三項只有開全文才拿得到。下面的「適合當參考電路」是依架構、製程、規格和全文能否公開取得來判斷，不是依已確認的電路細節。

---

## F01 Limpisawas & Wattanapanitch, IEEE Access 2022：Indirect-Direct Nested Miller OCL-LDO
- 架構與補償：純類比多級 OCL-LDO，用間接加直接的 nested Miller 補償，維持各種負載下的穩定與迴路增益。
- 關鍵數字 [M，摘要]：0.18 µm；Iq 14 µA；0–100 mA；CL 0–1 nF（最小負載 1 mA 時可到 10 nF）；load reg 0.025 mV/mA；line reg 0.5 mV/V。
- 量測 setup：暫態數字、邊沿時間、用 on-chip 還是外部負載，都未讀到。
- 參考價值：**很適合**。CL 0–1 nF 跟學生的 100 pF–1 nF 幾乎一樣，0.18 µm、100 mA、純類比，LTspice 可以照做。缺點是全文還沒開，電晶體尺寸未知。

## F02 Pérez-Bailón et al., Sensors 2018：0.18 µm LDO for impedance measurement SoC
- 架構與補償：capless 類比 LDO（Zaragoza 團隊），設計重點是用合理的 on-chip 補償電容和最小 Iq 達成穩定。
- 關鍵數字 [M，摘要]：UMC 0.18 µm 1P6M；Vin 1.94–3.6 V，Vout 1.8 V；Imax 50 mA；CL 最大 100 pF；Iq 7.45 µA；溫度 −40~100 °C。
- 量測 setup：摘要只說有實驗量測驗證，步階大小與邊沿時間未讀到。
- 全文：MDPI、PMC（PMC5982934）、Zaguan 典藏三處都是 OA，最容易拿到。
- 參考價值：**很適合**。實測、100 pF on-chip、50 mA，也是同一團隊多篇 0.18 µm LDO 系列的一篇，可以順著讀 Procedia 2016 和 Electronics 2021（後者只有後佈局模擬）。要注意輸入到 3.6 V，可能用了 3.3 V 元件 [H]。

## F03 Kao et al., IEEE Access 2024：Direct-Coupled Slew Rate Enhancement OCL-LDO
- 架構與補償：OCL-LDO 加直接耦合的 slew-rate enhancement 電路，用來改善暫態。
- 關鍵數字 [M，摘要]：0.18 µm；Vin 1.8–3.3 V，Vout 1 V；Iq 28.8 µA；負載 100 µA→100 mA，**邊沿 100 ns**；spike <43.5 mV；恢復 0.23 µs；core 0.0174 mm²。
- 量測 setup：邊沿時間有寫，負載型式未讀到。
- 參考價值：**適合**。0.18 µm、100 mA 實測，邊沿時間也有寫，可以直接拿來和學生的模擬比較。同組 2022 年的 F04 可以當前後對照。

## F04 Kao et al., IEEE Access 2022：Multipath OCL-LDO
- 架構與補償：multipath 的 OCL-LDO，不需要輸出電容，無載（<100 nA）也穩定。
- 關鍵數字 [M，摘要]：0.18 µm；Vin 1.2 V，Vout 1 V；Iq 0.6 µA（無載）/ 6.9 µA（滿載）；0→100 mA，**邊沿 100 ns**；undershoot **388 mV**；settling 2.2 µs；面積 0.0128 mm²；可容忍寄生 CL 最大 100 pF。
- 參考價值：中高。Iq 壓到 µA 以下，undershoot 就變成好幾百 mV。這是很好的反例，說明 Iq 和暫態要取捨，可以提醒學生 1.6 V 輸出能容許多少 droop。

## F05 Williams, Lakehead M.Sc. thesis 2024：multi-loop、zero-pole tracking LDO
- 架構與補償：multi-loop，加一個跟著主輸出極點移動的 zero-tracking 網路，用 Ahuja 補償取代 Miller 補償的前饋路徑。
- 關鍵數字 [M，摘要]：TSMC 180 nm；0–50 mA 內 PM ≥60°；Iq 486.67 nA；disabled 2.06 nA；峰值電流效率 99.96%。
- 量測 setup：摘要提到有 full-to-no-load 的暫態量測，數值未讀到。
- 全文：學位論文 PDF 是 OA（thesis.lakeheadu.ca）。
- 參考價值：**適合**。碩士論文通常完整交代設計推導、元件尺寸、佈局和量測板，最接近「學生能照著做」的文件。不過 Iq 只有 nA 級，暫態一定慢，學生做 10–100 mA 時偏壓要放大。

## F06 JSTS 2019（作者未取得）：Advanced Dynamic Biasing capless LDO
- 架構與補償：dynamic biasing 偵測負載暫態，不用外加大電阻和電容，只在暫態時加大偏壓電流。
- 關鍵數字 [M，摘要]：0.18 µm；輕載 Iq 2.0 µA；100 mA↔100 µA 時 settling <1.2 µs；面積 0.05 mm²。
- 量測 setup：邊沿時間未讀到。作者、DOI 都沒取得，年份是從檔案路徑推的。
- 參考價值：中。動態偏壓是純類比做法，在 LTspice 裡做得出來。但書目資料還不完整，要先補齊才能引用。

## F07 Cheng et al., J. Semicond. 2018：超低功耗 OCL-LDO 加 slew-rate enhancement
- 架構與補償：OCL-LDO 加 SRE 電路，以及超低輸出阻抗的 buffer 改善 line/load regulation。
- 關鍵數字 [M，摘要]：SMIC 0.18 µm；Iq ≈1.2 µA；負載 10 µA–200 mA；輸出變動 <40 mV（步階條件未讀到）。
- 參考價值：中。可以學 buffer 加 SRE 的思路。全文是否免費沒有確認。

## F08 Li et al., J. Semicond. 2014：capacitor-free high-PSR LDO
- 架構與補償：用 pole splitting 加 gm boosting 穩定，主打高 PSR。
- 關鍵數字 [M，摘要]：0.18 µm；Vin 2.5–5 V；Vout 1.79 V；Imax 100 mA。
- 參考價值：中低。輸入到 5 V，應該是高壓元件，電路不能直接搬到 1.8 V 供電。補償觀念可以參考。

## F09 Lin, Wang, Rhee, Wang, 2022（IEEE 研討會，推定 ICTA）：analog-assisted DLDO, 180 nm
- 架構（C 類）：DLDO 主迴路，用 DSM 加 FIR 濾波降漣波，exponential-ratio array 把負載範圍擴大到 5500 倍，暫態迴路則由 charge-pump LDO 做 analog-assisted。
- 關鍵數字 [摘要，M/S 未知]：漣波 0.37 mV；undershoot 78 mV，摘要寫的負載變化是「210mA to 100mA」，疑似筆誤。
- 參考價值：hybrid 架構的參考。需要 DSM、FIR、控制邏輯，學生沒有 Verilog，要複製很難。比較適合放在報告的「為什麼不選 hybrid」段落。

## F10 Qaisar et al., 2024：analog-assisted DLDO 加 charge-pump fine loop, 180 nm
- 架構（C 類）：coarse loop 用 dual-edge-triggered shift register；AA 迴路壓 undershoot；穩態用 voltage-to-interval converter 加 charge pump 消除漣波。
- 關鍵數字 [M，摘要]：180 nm 設計並下線；面積 0.253 mm²；漣波 <140 µV。另一則摘錄提到 20 mV dropout、75 mA，但沒能二次確認，所以沒填。
- 參考價值：hybrid 參考。同組另有 ISCAS 2024 的純數位 tri-loop DLDO（180 nm，0.22 mm²），沒放進 CSV。數位部分量很大，不適合當學生的參考電路。

## F11 Ameziane et al., IJECE 2019：full on-chip LDO（Crit 警示）
- 架構：fast detector amplifier 偵測輸出變化，強化 50 mA 步階的暫態。
- 數字 [S，摘要與全文片段]：0.18 µm；**1.8 V→1.6 V**（和學生規格一樣）；Iq 14 µA；50 mA 步階。
- 警示理由：(1) 全文片段寫的是模擬，沒有晶片；(2) settling 928/883 ns、rise/fall 500 ns 這些片段語境不完整，條件無法確認；(3) 摘要沒提下線。
- 用法：可以當同規格的模擬對照，看別人在 1.8→1.6 V 下怎麼取捨，**不要**當實測基準。

## F12 Alapati & Rao, IJEECS 2018：multi-loop capless LDO（Crit 警示）
- 架構：adaptive biasing、bulk modulation 加 fast loop。
- 數字 [未知 M/S，摘要]：0.18 µm 1P6M；Iq 16 µA；0→100 mA，40 pF；ΔV 134.23 mV；settling 240.8 ns；load reg 0.095 µV/mA。
- 警示理由（客觀）：(1) 0.095 µV/mA 換算成閉迴路輸出阻抗約 0.095 mΩ，比 F01 的 0.18 µm 實測值 0.025 mV/mA 小約 260 倍。16 µA Iq 的 capless 設計很難做到，必須看量測或模擬條件。(2) 摘要寫「integrated noise 31.027 pV²/Hz」，積分雜訊的單位不應該帶 /Hz。(3) 摘要只寫「designed using」，沒提下線或量測。(4) 沒寫負載邊沿時間，240.8 ns 的 settling 無法和其他論文比較。

## F13 Gao et al., Electronics 2023：1.8 V/300 mA fully integrated LDO（Crit 警示）
- 架構：功率管閘極用 transient-enhanced biased class-AB super source follower 驅動，再加以快速比較器為核心的 active capacitor，加速暫態充放電。
- 數字 [S，摘要]：0.18 µm；Vin 2–5 V，Vout 1.8 V；Iq 66.4 µA；3→300 mA，**邊沿 300 ns**；overshoot/undershoot 67/86 mV；settling 400 ns；load reg 1.94 µV/mA；PSR −60 dB @1 kHz。
- 警示理由：第 3 節是「simulation results and comparisons with other LDO」，模擬值和別人的值並列比較，不對等。1.94 µV/mA 也比 F01 的實測值小約 13 倍，是模擬的理想值。優點是邊沿時間有寫。
- DOI 依 MDPI 命名規則應該是 10.3390/electronics12061409，但沒驗證，所以 CSV 留空。

## F14 Chen et al., Micromachines 2024：transient-enhanced capless LDO（Crit 警示）
- 架構：在主迴路外加暫態增強輔助電路，摘要說不影響穩態穩定性。
- 數字 [S，摘要]：180 nm；Vin 1.2–1.8 V，Vout 1 V。其他數字未讀到。
- 警示理由：標題主打 fast transient，但搜尋摘錄指出設計是「validated through simulation results」，沒有晶片量測。
- 用法：可以當模擬架構的點子來源，數字不能當實測基準。

---

## 有找到但沒放進 CSV 的候選（給後續 agent 參考）
- Lu, Wang, Pan, Ki, Yue, TCAS-I 2015：65 nm，140 pF on-chip，0→10 mA 時邊沿 200 ps，量測 under/overshoot 43/82 mV [M，摘要]。製程不符。
- Lu, Yang, Chen, Mok：500 mA digitally assisted analog LDO，65 nm；同團隊另有 HKUST 2020 年的 Fan Yang 學位論文（lbezone.hkust.edu.hk/rse/?p=57106）。製程不符。
- Jin, Kim, Baek, Electronics 2023（10.3390/electronics12153215）：self-triggered digitally assisted hybrid LDO，TSMC 65 nm。是 M 還是 S 沒確認。
- Engür & Shoaran, arXiv 2310.18998：capless LDO，65 nm，0→15 mA 時邊沿 80 ns，undershoot 100 mV [M，摘要]。製程不符，但 arXiv 全文 OA。
- Park, Baek, Hong, IDEC JICAS 2022（10.23075/jicas.2022.8.4.003）：0.18 µm，100 mA，9 µA。典藏標示非 OA，M/S 也不明。
- Lee, Ajou University 碩士論文 2019 與 IET CDS 2019：0.18 µm，50 mA，undershoot 降低 53.3%。論文沒有可下載檔。
- Farooq et al., ISCAS 2024：tri-loop DLDO，180 nm，0.22 mm²。純數位（D 類）。
- Guan, TAMU 碩士論文 2019（OAKTrust 1969.1/186255）：capless，Iq 5.7 µA，100 mA 時迴路增益 54 dB。製程和是否下線都沒確認。
- Wang (Mengde), TAMU 碩士論文 2014：capless 寬頻 PSR LDO，有 capacitance multiplier。製程和是否下線都沒確認。
- Pérez-Bailón et al., Electronics 2021（10.3390/electronics10172108）：180 nm，1.2 V 輸出，8.6 µA。只有後佈局模擬，摘要有誠實標示。
- Mixed-mode LDO, JCSC 2022（10.1142/S0218126622503005）：180 nm，1.6–2 V→1.2 V，100 mA。付費，而且兩個列表給的數字互相矛盾。
- 年份或製程不符而排除：arXiv 1203.5778（2012）、arXiv 1405.0806（20 V bipolar，只有模擬）、Milliken TAMU 論文（0.35 µm，2007 年以前）。
