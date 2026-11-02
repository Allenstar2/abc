# Stage 3：選文（深入研究清單）

> **先講清楚限制**：這次 session 的網路政策擋掉所有學術網站（D-009），**10 篇入選論文沒有一篇讀到全文**。
> 依使用者規則，「僅摘要」的論文不能當作深入分析的主要依據，所以本次 Stage 4 的電路分析以**我的推導 [D] 與本次模擬 [X]** 為主，
> 這份清單是「早上開了網路權限、或你自己去圖書館下載後」的**閱讀計畫**，每篇都寫了「讀全文時要確認什麼」。
> 你早上檢查時如果不同意，直接改這份；我是照自己的判斷先繼續。

## 選文條件（使用者給的）

類比優先、無 Verilog、0.18 µm、要能下線量測、大學部時程。我另外加兩條：
- 規格接近：Vin ≤ 1.8–2 V（只用 1.8 V 核心元件）、Imax 50–100 mA 級、CL ≤ 1 nF on-chip。
- 有可能拿到開放全文（OA 期刊、學位論文、作者版）。

## 入選 10 篇

| # | id | 論文 | 入選理由 | 讀全文時要確認 |
|---|---|---|---|---|
| 1 | H01 | Leduc, Fu, Zhou, *A 430-mA Capacitor Less Analog Assisted Hybrid LDO With Fast Transient Algorithm*, IEEE TCAS-I 2025（Xplore 10884555；DOI 未驗證） | 教授指定；同為 TSMC 180 nm、capless | **B 或 C**：穩態誰供電、DC 精度由誰決定、數位迴路穩態是否停止；數位部分是否需合成；undershoot 480 mV 的負載起點與 CL；clock 頻率 |
| 2 | H04 | Leduc, Lakehead 碩士論文 2024（handle 2453/5398；embargo 至 2025-09-23） | H01 的完整版，學位論文通常有電晶體尺寸、佈局、量測板 | 同上；另看 hybrid 的數位部分是 Verilog 還是手畫；量測 setup（片上負載？） |
| 3 | A05 | Limpisawas & Wattanapanitch, IEEE Access 2022（10.1109/ACCESS.2022.3185630，OA 有報導） | 規格最接近：0.18 µm、0–100 mA、CL 0–1 nF、Iq 14 µA；純類比 nested Miller | 是否實測；負載暫態邊沿時間與起點；在 CL=1 nF 與零負載下 PM；面積 |
| 4 | A06 | Ni et al., Micromachines 2022（10.3390/mi13101594，OA 有報導） | 100 mA、200 mV dropout 與本專題相同；電容耦合 SRE；推測只多幾顆電晶體 [H，待全文確認]，可能是學生做得出的「暫態增強」 | 是否實測；Vin/Vout；SRE 在零負載是否誤觸發；他人表的 99.9 mA/µs 是否正確 |
| 5 | F03 | Kao et al., IEEE Access 2024（10.1109/ACCESS.2024.3398290，OA 有報導） | 0.18 µm 實測，0.1→100 mA、邊沿 100 ns 有明寫，<43.5 mV | Vin 範圍 1.8–3.3 V 是否用厚氧元件（若是，不能直接比）；片上還是外部負載；CL 定義 |
| 6 | A01 | Park, Onabajo, Silva-Martinez, JSSC 2014（10.1109/JSSC.2013.2289897，間接驗證） | 你讀過；0.18 µm、1.8 V；PSR 增強的代表作 | feedforward 路徑對負載變化的敏感度；Iq 80/55 µA 的條件；在 200 mV dropout 是否仍有效 |
| 7 | A02 | Kim, Kwak, Kim, ISCAS 2022（10.1109/ISCAS48785.2022.9937778，間接驗證） | 你讀過；180 nm；voltage damper + body loop | 是否 capless、是否實測；125.9 mV undershoot 的 ΔI、CL、邊沿；body loop 需要 deep n-well 或獨立 n-well 嗎（0.18 µm 平台是否有） |
| 8 | H11 | Jin et al., Electronics/MDPI 2023（self-triggered digitally assisted hybrid，65 nm，OA 有報導） | 摘要明確是 B 類（數位只在大暫態觸發），可當備案 B 的參考 | 觸發條件與 dead band；穩態時數位是否完全靜止；PSRR；數位如何實作 |
| 9 | A12 | Torres et al., IEEE CAS Magazine 2014（10.1109/MCAS.2014.2314263，**DOI 未驗證，單一搜尋摘錄**） | 反面/限制：同一 0.6 µm 製程實作 5 種 capless 架構，證明排名隨指標改變 | 各架構的 PSR、settling、Iq 數字；哪個最適合 0.18 µm |
| 10 | D08＋X01 | Wang, Kim, Seok 等 DLDO review（D08）＋ 公開資料集 github.com/mgseok/DLDO-survey | 唯一能實際開啟的資料（二手整理）；支持「FoM 不可比較」與 hybrid/數位的 PSR 弱點 | review 正文提出的新 FoM 定義；hybrid 類設計的 PSRR |

## 主要排除理由（其餘 43 筆：54 列減去入選的 11 個 id，第 10 項含 D08 與 X01）

| 排除類型 | 例子 | 理由 |
|---|---|---|
| 製程差太多 | A03（65 nm）、A09（65 nm）、A11（40 nm）、H09（65 nm）、H13（28 nm）、H14（14 nm） | 元件特性、電壓、pass device 行為不同，電路可借鏡但數字不能用 |
| 用厚氧/高 Vin | F02（1.94–3.6 V）、F08（2.5–5 V）、F13（2–5 V） | 本專題 Vin=1.8 V；高 Vin 讓 pass gate 有大 Vsg、EA 有大 headroom，難度不同 |
| NMOS pass | A04 | Vin 1.8 V、Vout 1.6 V 時 NMOS 閘極要 ~2.1 V 以上，需 charge pump，增加下線風險 |
| 只有模擬或量測不完整 | F11、F12、F13、F14(=A07) | F11 規格正好 1.8→1.6 V 但只有模擬；F12 load regulation 數字與實測文獻差約 260 倍（agent4 notes）；作為「哪些數字不可信」的例子保留在 literature.csv |
| 數位主導或需要合成 | H05、F09、F10、D01、D03、D05、H13 | 教授不走數位主導；學生無 Verilog |
| 回顧類 | H06(=D07)、H07、D06、D10、A14(=D11) | 讀摘要即可；H06 的 AAD/DAA 分類已用於 ARCH_MATRIX.md |
| 背景/經典 | D02 Hazucha 2005、D01 Okuma 2010 | FoM 的來源，不必深讀 |

## 如果早上只能讀 3 篇

1. **H04 Leduc 碩士論文**（最可能是開放全文，能一次解決 B/C 判定）
2. **A05 Limpisawas 2022**（規格最接近的純類比）
3. **A12 Torres 2014**（同製程比較架構，最適合跟教授討論「為什麼選 A」）
