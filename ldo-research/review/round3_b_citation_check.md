# Round 3（b）引用與數字查核：REPORT.md 逐項核對

> 查核者：第 3 輪 (b) 事實查核（獨立 subagent，未修改 repo 既有檔案；未使用網路／WebSearch）。
> 查核對象：`REPORT.md`，**sha256 50188e1c…dca91，mtime 2026-11-02 17:59:48 UTC**。查核期間 REPORT/ANALYSIS/APPLICATIONS/REVIEW_LOG、`s13_hybrid_sync.json`、`x5_vco_supply.json` 被作者同步更新（17:57–17:59），本表以上述版本與當時的結果檔為準；行號 L# 指該版本。
> 來源：`sim/results/*.json|*.log`、`review/round*_files/res/*.json` 與 `review/round2_c_files/results/*.json`、`review/round*.md`、`literature.csv`、`REFERENCES.md`、`lit_raw/agent*_notes.md`、`ext/DLDO-survey/DLDO survey.xlsx`（pandas 重算）、`ANALYSIS.md`、`APPLICATIONS.md`、`GAPS.md`、`DECISIONS.md`、`REVIEW_LOG.md`、`LOG.md`。
> 判定：一致／不一致／無法查證／標記錯誤／誇大／路徑錯誤。容許四捨五入。

---

## 1. 逐項核對表

### 0. 標頭與 a 節（一頁結論）

| # | REPORT 位置 | 內容 | 來源與原值 | 判定 | 建議修正 |
|---|---|---|---|---|---|
| 1 | L5 | 「93 筆文獻**全部**只讀到搜尋摘錄（僅摘要）」 | `literature.csv`：92 筆「僅摘要」，**X01 為「全文-開放（本次實際開啟，commit 68e94cc）」**；`REFERENCES.md` 標頭寫「除 X01 外」；REPORT 自己在 L48、L232 也說 X01 實際開啟 | 不一致 | 改「93 筆中 92 筆僅摘要；X01（DLDO 資料集）實際開啟」。L114、L211、L219 同步修 |
| 2 | L5 | DOI 未經 doi.org 解析（D-009） | DECISIONS D-009 | 一致 | — |
| 3 | L13 | SS-like 125 °C 最低 Vin 1.716 V、−4.7% | `s17_spec_alt.json` minVin_100mA_SS125 = 1.716；(1.716−1.8)/1.8 = −4.67% | 一致 | — |
| 4 | L13 | Vout 1.4 V 容許 −13% | s17 Vout1.4 minVin_SS125 = 1.560 → −13.3% | 一致 | — |
| 5 | L13 | 滿載迴路增益 +15 dB、PSRR@1 kHz +13 dB | s17 dc_db(100 mA) 48.6 vs 33.7（+14.9）；psrr 1 kHz −46.4 vs −33.3（+13.1） | 一致 | — |
| 6 | L15 vs L21 | 備案條件「Imax ≥ 200–300 mA」 vs 會改變建議「Imax ≥ 300 mA」 | CONCLUSION_DRAFT 只寫 ≥300 mA；repo 中無任何推導或模擬支持此門檻 | 不一致（內部）／無法查證 | 統一為「≥ 300 mA [H]」 |
| 7 | L16 | 排除 C：「要贏暫態需要的非同步路徑在 B 上就已經很脆弱」 | 只有第 1 輪 (a) 審查者模擬；作者未重現（ANALYSIS 附 3、REPORT L113、L207 自己也這樣標） | 標記錯誤（缺標註） | 加「（審查者 [X]，作者未重現）」 |
| 8 | L17 | Leduc 摘要句 "transient response is dictated by the digital portion"；D-010 | `lit_raw/agent1_notes.md:39` 原句；D-010 | 一致 | — |
| 9 | L18 | 公平比較 undershoot 差 11–21% | `s12_fairB.json`：552.9/498.9 = +10.8%、153.7/127.5 = +20.5%、32.9/27.4 = +20.1% | 一致 | — |
| 10 | L18 | 「PSRR **只在 ≤100 kHz** 差 8–14 dB」 | `review/round2_a_files/res/r2_1_psrr_hf.json`（70 mA）：1 kHz 差 8.1（碼 3）/14.0（碼 5）；100 kHz 差 3.9/8.0；**1 MHz 差 2.6/4.8**（A −6.7、B −4.1/−1.9）；10–100 MHz 差 ≤0.5。審查者原文：「1 MHz 時差 0.3–4.8 dB」 | 不一致（表述） | 改「1 kHz 差 8–14 dB、100 kHz 4–8 dB、1 MHz 3–5 dB；≥10 MHz 差 ≤0.6 dB」。L122 e#1 同 |
| 11 | L19 | 1 ns、100 mA、100 pF 下 undershoot >400 mV | 最小值：A 5→95 mA 499、A 10→100 mA 452（`x2_edge_time.json`）、公平 B 553 | 一致 | — |
| 12 | L19 | 「**任何架構**都做不到小於 ~200 mV [X/D]」 | repo 中找不到此推導或模擬（ANALYSIS、CONCLUSION_DRAFT 只寫「>400 mV，任何架構」）；C 未模擬 | 無法查證 | 刪除，或補推導（如 ΔI·t_resp/CL、t_resp ≥ 數個 FO4）並標 [D/H] |
| 13 | L20 | 「理由已被兩輪審查削弱三次」 | REVIEW_LOG：R1(a) 削弱理由 1、2；R2(b) 撤回理由 3；R2(a) 再削弱 B 的優點（對 A 有利） | 無法查證（判斷性計數） | 改「多次」，或列出是哪三次 |
| 14 | L20 | 非同步 droop、NMOS-pass 標「審查者模擬、作者未重現」 | REVIEW_LOG 第 1 輪 (a)、第 2 輪 (a) | 一致 | — |
| 15 | L22 | HBM rail 0.4–1.2 V；SerDes 時脈 rail mW 級 | APPLICATIONS §2.2-1、§3.2-2；agent5 notes:164；agent6 notes:198 | 一致 | — |

### b 節

| # | REPORT 位置 | 內容 | 來源與原值 | 判定 | 建議修正 |
|---|---|---|---|---|---|
| 16 | L36 | 公平 B：類比 2.4 mm＋8×130 µm slice | s12 Wa_um 2400；`ldo_hybrid.py` HDEF N=8、Ws=130 | 一致 | — |
| 17 | L38 | 5→95 mA undershoot A 499/127/27、B 553/154/33 mV | s12：498.9/127.5/27.4、552.9/153.7/32.9 | 一致 | — |
| 18 | L39 | PSRR@1 kHz（70 mA）A −38.2、B −24.2 dB（碼 5） | s12 psrr_1kHz_70mA | 一致 | — |
| 19 | L39 | B「～−30.1 dB（碼 3）[X]」 | 只有審查者算過碼 3：`round1_a_files/res/r7_bleed_bias.json`、`round2_a_files/res/r2_1_psrr_hf.json`；作者 s12 只做碼 5。ANALYSIS 正確寫「審查者在碼 3 量到」 | 標記錯誤（審查者模擬混入作者 [X]） | 改「−30.1 dB（碼 3，審查者 [X]）」 |
| 20 | L39 | C 欄「**摘要**：DLDO PSR 弱（Nasir 2015 −5 dB@1 MHz，資料集）」 | xlsx：Nasir ISSCC 2015 −5 dB @1 MHz 正確；但資料集 8 列 PSRR 全在 1 MHz，範圍 **−5～−46 dB（中位 −27 dB）**，另一顆 fully digital（Kundu ISSCC 2018）−37.5 dB；REF-A 在 1 MHz 只有 −5.3～−8.7 dB（`s3_refA_char.json`）。來源是資料集，不是摘要 | 誇大（選擇性引用）＋標記錯誤 | 改「資料集 8 列 PSRR@1 MHz −5～−46 dB（中位 −27 dB），差異大，不足以說 DLDO PSR 一定較弱 [資料集]」。ANALYSIS C 節同步 |
| 21 | L40 | 「PSRR **1–100 MHz**：A ≈0 dB；B ≈0 dB（與 A 差 ≤0.6 dB，審查者）」 | r2_1_psrr_hf（70 mA）：A 1 MHz **−6.7**、10 MHz +0.6、100 MHz +0.2；B 碼 3/5 1 MHz −4.1/−1.9；審查者原文是「**10–100 MHz** 差 ≤0.6 dB；1 MHz 差 0.3–4.8 dB」；s3：REF-A 1 MHz −5.3～−8.7 dB；REVIEW_LOG 第 2 輪 (a) 也寫 10–100 MHz | 不一致 | 列名改「PSRR 10–100 MHz」，另加一列「1 MHz：A −6.7、B −1.9～−4.1 dB」。L81 同 |
| 22 | L41 | 同條件 load reg（20→95 mA）A 6.1、B 0.5 mV | `s15_rz_loadreg.json` REF-A_loadreg_20to95_mV 6.13；s12 plateaus 1.6006→1.6001 V | 一致 | （s15 未列在 d.1，見 #88） |
| 23 | L42 | 離散狀態風險「比較器 offset … [X]」 | offset 效應只有第 1 輪 (c) 行為模型；作者電路沒有模擬 offset | 標記錯誤（輕微） | 「（offset 為審查者行為模型）」 |
| 24 | L43 | 數位實作「8 DFF＋33 閘＋2 比較器」 | `ldo_hybrid.py`：每位元 3 AND2＋1 OR3＋1 DFF，另 1 NOR2 → 8 DFF＋33 閘正確；但 L83 與 e#5 都要求再加 2 級同步器（up/dn 各 2 = 4 DFF）＋÷3 計數器 | 不一致（內部，低估） | 改「8 DFF＋33 閘＋2 比較器＋同步器 4 DFF＋÷3 計數器」 |
| 25 | L47 | A01：PSR 優於 −56 dB 至 4 MHz @50 mA [M] | literature.csv A01 psrr、result_type M | 一致 | — |
| 26 | L47 | A05：0–100 mA、CL 0–1 nF、Iq 14 µA | csv A05 | 一致 | — |
| 27 | L47 | F03：0.1→100 mA、100 ns、<43.5 mV [M]、Vin 1.8–3.3 V | csv F03（deltaV「<43.5（spike）」） | 一致 | — |
| 28 | L47 | F04：0→100 mA、100 ns、388 mV [M] | csv F04 | 一致 | — |
| 29 | L47 | H01：430 mA、100 ns、480 mV、Iq 49 µA（未加 M/S） | csv H01（result_type 未知） | 一致 | — |
| 30 | L47 | `ARCH_MATRIX.md` §2、`literature.csv` 93 列 | 檔案存在、§2 為文獻數字矩陣、93 列 | 一致 | — |
| 31 | L48 | 「Seok DLDO 資料集（唯一實際開啟的**一手**資料）」 | csv X01 numbers_source：「資料集（作者群整理之 reported/estimated 值，非原論文）」 | 標記錯誤 | 改「唯一實際開啟的來源（二手整理資料集）」 |
| 32 | L48 | 46/58 列有邊沿時間，0.015–4000 ns，中位 2 ns | xlsx（pandas，'-' 視為缺值）：58 列、46 列、min 0.015、max 4000、median 2.0；`s7_dataset_stats.json` 相同 | 一致 | — |
| 33 | L48 | X. Wang CICC 2019：1 ns 185 mV、10 ns 88 mV | xlsx 第 2、7 列 | 一致 | — |
| 34 | L48 | 748 mV（0.1 ns）、111 mV（1 µs）、10 mA 起點 1 µs 21 mV | `x2_edge_time.json` 748.18、110.99、21.44 | 一致 | — |
| 35 | L51 | HBM 12 篇＋13 補充來源 | csv HB01–HB12；agent5 notes 列到 HBS13（notes:13 自寫 HBS1–12，為來源本身的矛盾） | 一致 | — |
| 36 | L51 | 首爾大學三篇（ISSCC 2025、JSSC 2026、CICC 2026）；<10 mV、400 ps、20 pF | agent5 notes:45、81、153 | 一致 | — |
| 37 | L51 | 三篇「都是 hybrid/digital、**靠 command/strobe 時序**」 | agent5 notes:152：「只從標題得知」；機制未讀 | 標記錯誤（僅標題，未標） | 加「（標題層級）」 |
| 38 | L52 | SerDes 15 篇；SD10 40 dB 至 10 MHz、50 nV/√Hz；0.18 µm 例子 <2.5 GHz | agent6 notes:3、37、197；csv SD01–SD15 | 一致 | — |
| 39 | L53 | 7 級 ring、764 MHz、Kvdd 440 MHz/V | `x5_vco_supply.json` f0 764.2、Kvdd 439.9 | 一致 | — |
| 40 | L53 | TIE 334/915 ps（正弦擬合）、手算 339/916、差 ≤1.3% | x5（17:59 版）tie_sinefit_amp 334.06/914.9；analytic 338.59/916.12 → −1.34% / −0.13% | 一致（1.34% 四捨五入，邊界值） | 可寫「≤1.4%」較穩 |
| 41 | L53 | 第 2 輪審查另一振盪器 3 個頻率誤差 ≤2.9% | round2_c §1.4：CS5 −0.2%～−2.9%（INV7 3 MHz 為 −3.0%，非「另一振盪器」） | 一致 | — |
| 42 | L53 | 1 MHz 只擋 8.6 dB、10 MHz 放大 1.3 dB | x5 psrr −8.6 / +1.3 | 一致 | — |
| 43 | L54 | 過追蹤量隨負載變 15 倍 | s14 docstring；round2_b 第 33 項：0.051→0.749 = 14.7× | 一致 | — |
| 44 | L54 | 滿載 1 MHz 最好約 −13 dB | `x6_ff_psrr.json` 100 mA、1 MHz 最佳 −12.7 dB（gff = 1 mS，在掃描上限） | 一致 | 可註「最佳點在掃描邊界」 |
| 45 | L54 | NMOS-pass「1–10 MHz 好 15–20 dB」（審查者） | 審查者原文 15–20 dB；但 `r2_10_nmos_ldo.json` 對 s3 同負載：0 mA 18.4/16.0 dB、10 mA **13.9**/17.3 dB（1/10 MHz）；只測 0–10 mA，且 Vout = 0.994 V（非 1.6 V） | 不一致（輕微；照抄審查者原文，但 JSON 為 14–18 dB） | 改「14–18 dB（0–10 mA、Vout 1.0 V，審查者 [X]）」。L208 同 |
| 46 | L54、L198 | 代價 Vout ≤ ~1.2 V 或 charge pump | round2_a §4.2：Vout 1.0–1.2 V；但 W=400 µm、10 mA 時 Vout 1.2 V 已需閘極 1.89 V（> Vin 1.8 V） | 一致 | 建議註「1.2 V 時閘壓已略高於 Vin，實際約 1.0 V」 |

### c 節

| # | REPORT 位置 | 內容 | 來源與原值 | 判定 | 建議修正 |
|---|---|---|---|---|---|
| 47 | L62–65 | T0、p1、p2、GBW、z、p_b、PSRR_LF 公式 | ANALYSIS A1 小訊號模型；精確式見 round1_c | 一致 | — |
| 48 | L67 | 零載 53.2/53.0 dB、2.50/2.45 MHz、66.4/66.4°；滿載 33.7/33.7 dB、1.61/1.60 MHz | `s2_hand_vs_sim.json` | 一致 | — |
| 49 | L67 | 全部誤差 <10%，最大為原始設計 PM +9.5% | s2：orig 0 mA PM +9.47%（次大 −7.6%） | 一致 | — |
| 50 | L67 | Middlebrook 差 <0.3% | round1_c_independent.md:12「≤0.3%」 | 一致 | — |
| 51 | L67 | p2 公式比 `.pz` 低 12% | round1_c：7.81 vs 8.89 MHz | 一致 | — |
| 52 | L68、L70 | 「洩放 50 µA 時 PM 28°（100 pF）」；失效情境 (1)「洩放降到 50 µA → PM 28°」 | `s1_refA_sweep.json`（100 mA/100 pF/50 µA）：**Cc=3 pF 28.1°、Cc=5 pF 37.8°**；`learn_answers.json` Q4（REF-A Cc=5 pF）37.8°。REF-A 用 Cc=5 pF | 不一致（條件遺漏） | 改「洩放 50 µA：原始 Cc=3 pF 時 28°；REF-A 的 Cc=5 pF 時 38°」 |
| 53 | L68 | 200 µA＋Cc 5 pF → 66°；Iq 131→287 µA | s1 66.4°；learn Q4 Iq 130.6/286.7 µA | 一致 | — |
| 54 | L69 | gm_p/gds_p = 1.33；53→33.7 dB；PSRR@1 kHz −55→−33 dB | s2 Ap 1.334；s3 dc 53.0/33.7；s3 PSRR 1 kHz −55.3/−33.3 | 一致 | — |
| 55 | L70 | (2) 1 ns 0→100 mA → 742 mV | x2/s3 742.2 | 一致 | — |
| 56 | L70 | (3) SF-like 125 °C 零載 +46 mV；Vsg≈41 mV；漏 ~0.2 mA | `s6_corners.json` 1.6525（+46.4 mV）；`sim/results/chk_sf.log` vpg 1.7594、iin 259 µA；`round1_a_files/res/r3b_hot.json` I_pass 206.6 µA | 一致 | 41 mV／0.2 mA 只在 ad hoc 的 chk_sf.log（見 #75） |
| 57 | L70 | \|Vthp\|+50 mV 即消失（第 2 輪審查） | round2_a §5.1：+50 mV → 1.6139 V | 一致 | — |
| 58 | L73 | FVF slew ≈ 6.3 V/µs | 50 µA / 7.9 pF（ANALYSIS [D]） | 一致 | — |
| 59 | L74 | SRE「小訊號**完全**不變」 | `x4_sre.json` PM 66.4→66.7°、DC 與 PSRR 相同；`x4b_sre_sweep.json` pm0 66.4–67.4° | 誇大（輕微） | 改「幾乎不變（PM 差 ≤1°）」 |
| 60 | L74 | 最佳 −8～15%；掃描最差 +48%（100 ns：236→348 mV） | x4b：最佳 100 ns 217（−7.9%）、最佳 1 ns 625（−15.8%）；最差 100 ns 348（+47.8%）；s3 基準 235.5 | 一致 | 15.8% 建議寫 16% |
| 61 | L74 | 第一版偏壓因 DIBL 靜態導通而整顆失效 | LOG 17:07（Vout = Vin、Iq 3.59 mA）；沒有 json | 一致（只有 LOG） | — |
| 62 | L75 | 兩迴路頻寬分開 5–10 倍 [D/H] | ANALYSIS A6 [H] | 一致 | — |
| 63 | L78 | 分界點 ≈ 1＋offset 和＋d；「第 1 輪審查行為模型＋**作者電路驗證**」 | round1_c §3（行為模型）；作者電路（s13）只驗證延遲 d，沒有驗 offset 與欠阻尼 | 誇大（輕微） | 改「offset／欠阻尼：審查者行為模型；延遲 d：作者 s13 電路驗證」 |
| 64 | L79 | 窄窗比值 0.49；20 mA LC 191–229 mV p-p | `x3_hybrid.json` X3a 窄窗 20 mA：190.8/216.0/229.4 mV；6/12.2 = 0.49 | 一致 | — |
| 65 | L79 | 寬窗 1.23；無同步器 10/50 MHz 0/31；1 級 11/31；2 級 26/31；÷(d+1) 0/31；初版接法錯誤說明 | `s13_hybrid_sync.json`（17:58 版）：0/31、0/31、11/31、26/31、sync1÷2 0/31、sync2÷3 0/31；round2_c §3.3–3.4；`ldo_hybrid.py` 的 Vclkr 已與 Vclk 同相 | 一致 | — |
| 66 | L80 | slice 邊沿 1/30/300 ns → 82.6/71.4/34.5 mV | `x3e_glitch_fo4.json` | 一致 | — |
| 67 | L81 | PSRR 低頻差 8–14 dB；「1–100 MHz 與 A 相同（≈0 dB）」 | 同 #10、#21 | 不一致 | 改「≥10 MHz 相同；1 MHz 差 3–5 dB」 |
| 68 | L83 | 每位元 1 DFF＋3 AND2＋1 OR3（XSPICE 即閘級結構）＋2 級同步器＋÷3 計數器 | `ldo_hybrid.py` digital_block 相符 | 一致 | 註：模擬中 ÷3 是理想分頻時脈源（Vclkr），不是閘級計數器，可列入「XSPICE 與閘級的差距」 |
| 69 | L84 | 數位 reset 後 88.5 mA、PM 68°（審查者） | `round1_a_files/res/r8_fallback.json`：B2400 Imax_within16mV 88.5、PM 最小 68.3° | 一致 | — |
| 70 | L87 | 8 片 12.2 mA、100 pF、10 MHz → 6 V | 6.1 mA/(100 pF·10 MHz) = 6.1 V；12.2 mA = 130 µm × 93.6 mA/mm（s0） | 一致 | — |
| 71 | L87 | I_u = 1 mA 要 ~100 MHz | ANALYSIS：「要 50 mV 漣波」時；0.5 mA/(100 pF·50 mV) = 100 MHz | 一致（條件遺漏） | 補「（50 mV 漣波）」 |
| 72 | L87 | FO4 54–60 ps | x3e fo4：tplh 53.9、tphl 60.3 ps | 一致 | — |
| 73 | L88 | DLDO 原始動機：0.5 V 以下類比做不起來 [摘要 D01] | agent3_notes:19：「摘要說傳統 op-amp 回授 LDO 在 0.5 V 下無法工作 [M]」 | 一致 | — |

### d 節

| # | REPORT 位置 | 內容 | 來源與原值 | 判定 | 建議修正 |
|---|---|---|---|---|---|
| 74 | L94 | 隔離副本約 2 分鐘＋新增項 | LOG 17:16「完整重跑 1m53s」（當時還沒有 s10–s18） | 一致 | — |
| 75 | L94（與 L162、L70、L129） | 「一鍵重跑」涵蓋報告的 [X] | **0.72 mA/µm 來自 `sim/netlists/nload.cir` → `sim/results/nload.log`；pg 1.759 V／41 mV／0.2 mA 來自 `sim/results/chk_sf.log`**；兩者都沒有腳本產生，也不在 run_all.sh（ANALYSIS 寫「`s6_corners.py` 同條件重跑 OP」，但 s6 不輸出 vpg） | 路徑錯誤（可重現性） | 把這兩個 OP 併入 s11 或 s6 並存 json，或在報告註明是 ad hoc netlist |
| 76 | L97 | X0：NMOS gm/gds 12→59→97；PMOS L=0.18、Vsd 0.2 V gm/gds 2.1；Vth 對 L 不單調 | `s0_device_char.json` 11.8/59.2/96.9；p_L0.18 2.1；Vth 0.41/0.50/0.45 | 一致 | — |
| 77 | L98 | X1：126 組；「**全部**最差點在最輕載」 | s1：126 筆；124/126 在 0 mA；2 筆（CL=1 nF、Imin 50 µA、Cc=1 pF，PM 17.3°/15.7°）最差在 0.1 mA／1 mA | 不一致（輕微） | 改「124/126 組在 0 mA；其餘 2 組（本已不穩，PM<18°）在 0.1–1 mA」 |
| 78 | L98 | CL=1 nF、洩放 50 µA、Cc ≤ 40 pF 都 ≤41° | s1 最大 41.0° | 一致 | — |
| 79 | L100 | Iq 287 µA、load reg 12.8 mV、dropout 94 mV、line reg 4.6 mV/V | `s3_refA_char.json` 286.7/12.84/94.3/4.61 | 一致 | — |
| 80 | L100 | 線性暫態（1.8↔1.98 V、1 µs、50 mA）±12 mV | s3 line_tr：up 12.36、down 13.13 mV；條件與 s3 腳本相同 | 一致（近似） | 改「+12/−13 mV」 |
| 81 | L101 | X2：748→21 mV | x2 | 一致 | — |
| 82 | L102 | X3 腳本 s5、s5b、s5c、s12、s13 | 皆存在、皆在 run_all.sh | 一致 | — |
| 83 | L103 | X4：−8～15% 到 +48% | 同 #60 | 一致 | — |
| 84 | L104 | X5：手算 vs 模擬 ~1% | 同 #40（0.1%／1.3%） | 一致 | — |
| 85 | L105 | X6：「**最佳增益**隨負載變 15 倍」 | 15 倍是「所需過追蹤量 gds_p/gm_p」（0.051→0.75）；模擬最佳 gff 是 0.06/0.1/≥1 mS（**≥17 倍**，100 mA 最佳值在掃描上限外）；APPLICATIONS §6.2 與 REPORT L54 都寫對 | 不一致 | 改「所需過追蹤量隨負載變 15 倍；模擬最佳 gff 0.06→≥1 mS」 |
| 86 | L106 | s8、s16、s17、s18「見 a、e、g」 | s8 的結果在 a、e、g 都沒有被引用（只有 h.6 間接相關） | 路徑錯誤（引用不完整，輕微） | 改「s8 見 ANALYSIS 附錄」或在 a/h 引用 |
| 87 | L107 | 最差 PM 49.4°（FS-like 125 °C、1 nF/Cc 20 pF）；最大 1 µs undershoot 283 mV（SF-like 125 °C、1 nF） | `s6_corners.json` 49.4、283.1（全表最大） | 一致 | — |
| 88 | d.1 整表 | 實驗清單 | REPORT 用到但 d.1 沒列的腳本：`s7_dataset_stats.py`（b.3 資料集統計）、`s11_misc_checks.py`、`s15_rz_loadreg.py`（6.1 mV）、`learn.py`（Iq 131 µA）；都在 run_all.sh | 路徑錯誤（不完整，輕微） | 補列 |
| 89 | L110 | PTM、BSIM3v1、lmin=lmax=0.18 µm；角落 = Vth ±50 mV、Tox ±5%、三溫度 | MODEL_ATTRIBUTION、DEVICE_CHAR、s6 case 名稱 | 一致 | — |
| 90 | L113 | NMOS-pass、非同步 droop：只有審查者 | REVIEW_LOG | 一致 | — |
| 91 | L114 | 文獻「全部」僅摘要 | 同 #1 | 不一致（輕微） | 同 #1 |

### e 節

| # | REPORT 位置 | 內容 | 來源與原值 | 判定 | 建議修正 |
|---|---|---|---|---|---|
| 92 | L122 | 原想法「差 2.5 倍、PSRR 差 19 dB」 | x3_hybrid X3b 313.1/127.5 = 2.46；X3c −38.2 vs −18.8 = 19.4 dB | 一致 | — |
| 93 | L122 | 現在版本「11–21%、PSRR 只在 ≤100 kHz 差 8–14 dB」 | 同 #9、#10 | 不一致（同 #10） | 同 #10 |
| 94 | L123 | Rz=10 kΩ 角落振盪；穩健小 Rz 下 1 nF 只在 1 ns 占優 | `s16_rz_robust.json`（−5.1°、−4.4°；Rz 3 kΩ 468 vs 742 mV）；round2_a §2 | 一致 | — |
| 95 | L124 | 作者 X4：−8～15%、+48% | x4b（作者自己的模擬，歸屬正確） | 一致 | — |
| 96 | L125 | 審查者量 1 MHz A −6.7、B −4.1 dB | `round1_a_files/res/r7_bleed_bias.json`（ideal bias）：A −6.7、B2400 碼 3 −4.1；round2_b_citation_check:13 | 一致 | — |
| 97 | L126 | 2 級同步器 26/31 → ÷3 0/31；11/31 只等於 d=1 | s13（17:58 版）；round2_c §3 | 一致 | — |
| 98 | L127–128 | e#6、e#7 | round1_c §3；round2_a §5.1 | 一致 | — |
| 99 | L129 | pg ~1.65 V → 實際 1.759 V | LOG 17:10；`chk_sf.log` vpg 1.759398 | 一致 | 來源只在 ad hoc log（#75） |
| 100 | L130 | HB05–07 指標是 droop/settling | round2_b 第 2 項 | 一致 | — |
| 101 | L131 | X5 在 1 MHz β = 4.4 | 440 MHz/V × 10 mV / 1 MHz = 4.4 | 一致 | — |
| 102 | L132 | 監測 buffer 3–10 mA；板上電容 PM 18–30° | `r2_9_monitor.json`；`s18_offchip_cap.json` 18.2–30.4° | 一致 | — |
| 103 | L133 | 規格列第一題、Vout 1.4 V 替代 | round2_a §3；D-014 | 一致 | — |

### f、g、h、i 節

| # | REPORT 位置 | 內容 | 來源與原值 | 判定 | 建議修正 |
|---|---|---|---|---|---|
| 104 | L143–148 | G1–G6 判定 | GAPS.md 各列相同 | 一致 | — |
| 105 | L143 | SD04：180 nm，只有模擬 | agent6 notes:81、165 | 一致 | — |
| 106 | L154 | 「平台、PDK、面積上限與時程都未知（D-002）」 | D-002 只講規格假設（Vin/Vout/Imax/CL）；平台、面積、時程寫在 STATE.md「未解問題」 | 標記錯誤（引用 ID 不符） | 改「（D-002、STATE.md）」 |
| 107 | L159 | 閘極 720 µm² | 4000 × 0.18 | 一致 | — |
| 108 | L160 | Cox ≈ 8.2 fF/µm²、~0.012 mm² | 模型 PMOS Tox 4.2 nm → 8.22 fF/µm²（NMOS 4.0 nm → 8.63）；100 pF/8.2 fF = 0.0122 mm² | 一致 | — |
| 109 | L161 | 1 nF MOS 0.12–0.15 mm²；MIM 1–2 fF/µm² → 0.5–1 mm² | 0.122 mm²；算術成立 | 一致 | — |
| 110 | L162 | NMOS 負載 0.72 mA/µm [X] → ~140 µm | `nload.log`：W=100 µm → 72.09 mA；round2_a §6.4 W=139 µm → 100 mA | 一致 | 可重現性見 #75 |
| 111 | L163、L175 | Pads「約 16–20 個」 | g.3 清單逐項相加：VIN 2–3＋GND(LDO) 2＋GND(負載) 2–3＋VOUT_SENSE＋VOUT_MON＋MON_VDD＋LOAD_TRIG＋LOAD_SEL 3–4＋VREF_EXT＋IBIAS_EXT = **15–18 個** | 不一致（算術） | 改「15–18 個」，或補列漏掉的 pad（例如 MON_GND、G6 的 RO_OUT/RO_EN） |
| 112 | L166 | 1 nH × 100 mA/1 ns ≈ 100 mV；111 vs 742 mV | 算術；x2 | 一致 | — |
| 113 | L167 | 4–8 段、~1/20/200 ns、起點 0/1/10 mA、160 mW | GAPS「G1＋G6 做法」；100 mA × 1.6 V | 一致 | — |
| 114 | L168 | 審查者估 3–10 mA；路徑 `review/round2_a_files/res/r2_9_monitor.json` | 檔案存在；4 pF/3 mA、13 pF/10 mA 看到 80%（÷0.83 後 97%） | 一致 | — |
| 115 | L169 | 1/10/100 nF → 28.7°/18.2°/19.9°；2 nH | s18 | 一致 | — |
| 116 | L172 | 7 級 RO、<100 MHz、100 kHz–10 MHz | GAPS 做法第 4 點 | 一致 | — |
| 117 | L188 | −4.7% → −13%、+15 dB | s17 | 一致 | — |
| 118 | L193–195 | 0.12–0.15 mm²；21–748 mV；~200 µA | #109；x2；D-008 | 一致 | — |
| 119 | L207 | 非同步 droop：只有審查者 | REVIEW_LOG 第 1 輪 (a) | 一致 | — |
| 120 | L208 | NMOS-pass 15–20 dB | 同 #45 | 不一致（輕微） | 同 #45 |
| 121 | L211 | 文獻數字全部僅摘要 | 同 #1（資料集數字不是摘要） | 不一致（輕微） | 同 #1 |

### j 節（參考文獻 vs `literature.csv`）

| # | 條目 | REPORT | literature.csv | 判定 | 建議修正 |
|---|---|---|---|---|---|
| 122 | H01 | Leduc, X. Fu, Y. Zhou；TCAS-I vol 72 pp 3733–3743, 2025；ieeexplore 10884555；DOI 未找到 | doi 空；url 相同；venue 相同（issue 未確認）；agent1 notes：Ximing Fu、Yushi Zhou | 一致 | — |
| 123 | H04 | knowledgecommons …5f4ff6e9-7347-4087-a2a8-d81dc708904c | url 相同 | 一致 | — |
| 124 | A01 | JSSC 49(2):486–501, 2014；DOI 10.1109/JSSC.2013.2289897 | 相同 | 一致 | — |
| 125 | A02 | ISCAS 2022 pp 3571–3574；DOI 10.1109/ISCAS48785.2022.9937778 | 相同 | 一致 | — |
| 126 | A05 | IEEE Access 2022；DOI 10.1109/ACCESS.2022.3185630 | 相同 | 一致 | — |
| 127 | A06 | Micromachines 13(10):1594；DOI 10.3390/mi13101594 | 相同 | 一致 | — |
| 128 | A12 | CAS Magazine 2014；DOI 10.1109/MCAS.2014.2314263（未驗證） | 相同 | 一致 | — |
| 129 | F03 | IEEE Access 12:66539–66555, 2024；DOI 10.1109/ACCESS.2024.3398290 | 相同 | 一致 | — |
| 130 | F04 | IEEE Access 2022；DOI 10.1109/ACCESS.2022.3157717 | 相同（csv 另有 vol 10 pp 27185–27196） | 一致 | — |
| 131 | H11 | Electronics 12(15):3215；mdpi URL | url 相同；csv doi 空 | 一致 | — |
| 132 | H06 | 「M. Huang et al., … 2021（見 REFERENCES.md）」，無 venue／DOI／URL | csv：IEEE TCAS-II 68(1):24–29；url semanticscholar …7d1e43a6… | 不一致（不完整） | 補「IEEE TCAS-II 68(1):24–29」與 URL |
| 133 | X01 | github.com/mgseok/DLDO-survey；commit 68e94cc；本次實際開啟 | url 相同；`ext/DLDO-survey` git log = 68e94cc | 一致 | — |
| 134 | L219 | 「本報告直接引用的主要條目（**全部**「僅摘要」…）」 | 同一清單內的 X01 是實際開啟 | 不一致（內部） | 改「X01 以外全部僅摘要」 |
| 135 | L233–234 | HB01–HB12、SD01–SD15、PS01–PS12；notes 路徑；MODEL_ATTRIBUTION、CC BY 4.0、SJTU repo | csv id 齊全；檔案存在；MODEL_ATTRIBUTION 相同 | 一致 | — |

---

## 2. 檔案路徑與 `sim/run_all.sh`

- REPORT 提到的檔案全部存在：`ARCH_MATRIX.md`、`APPLICATIONS.md`、`ANALYSIS.md`、`GAPS.md`、`REVIEW_LOG.md`、`REFERENCES.md`、`literature.csv`、`DECISIONS.md`、`sim/run_all.sh`、`sim/results/x2_edge_time.json`、`review/round2_a_files/res/r2_9_monitor.json`、`lit_raw/agent5_hbm_notes.md`、`lit_raw/agent6_serdes_notes.md`、`lit_raw/agent7_psr_notes.md`、`sim/models/MODEL_ATTRIBUTION.md`、`review/`。
- REPORT 提到的腳本（s0、s1、s2、s3、s4、s5、s5b、s5c、s6、s8、s9、s9b、s10、s12、s13、s14、s16、s17、s18）**全部存在且都在 run_all.sh**；s7、s11、s15、learn.py 也在 run_all.sh。
- 問題：REPORT 的兩個 [X] 數字（0.72 mA/µm、pg 1.759 V/41 mV/0.2 mA）只存在於 ad hoc 的 `sim/netlists/nload.cir`／`sim/results/nload.log` 與 `sim/results/chk_sf.log`，沒有腳本產生，run_all.sh 也重現不了（#75）。`s1_refA_quick.py` 不在 run_all.sh，但 REPORT 沒有引用它。

## 3. 證據標記、僅摘要文獻、誇大

- **僅摘要文獻推電路細節**：沒有發現 REPORT 用摘要推電路結構；Leduc 標「未確認」、A01/F03/F04 只用摘要數字。唯一越界是 #37（HBM 三篇「靠 command/strobe 時序」只來自標題）。
- **審查者模擬寫成作者的**：#19（碼 3 −30.1 dB 標成一般 [X]）、#23（offset 的 [X]）、#7（非同步路徑脆弱，未標審查者）。
- **未重現寫成已重現**：#63（「作者電路驗證」實際只驗了延遲 d）。同步器數字已依第 2 輪 (c) 更正（#65、#97），沒有再寫成「2 級 11/31」。
- **誇大／選擇性引用**：#20（只引 Nasir −5 dB 說 DLDO PSR 弱，資料集另 7 列 −12～−46 dB，多數比 REF-A 的 −5～−9 dB 好）是本輪最實質的問題；#59「完全不變」為輕微誇大。
- **來源性質標錯**：#31（資料集稱「一手資料」）、#20（資料集數字標「摘要」）、#1/#91/#121/#134（「全部僅摘要」與 X01 實際開啟矛盾）。

## 4. REPORT 與 ANALYSIS／APPLICATIONS／REVIEW_LOG 交叉一致性

| # | 數字／主張 | REPORT | 其他文件 | 判定 | 建議 |
|---|---|---|---|---|---|
| X1 | A/B PSRR 相同的頻段 | L40、L81「1–100 MHz」 | REVIEW_LOG 第 2 輪 (a)「10–100 MHz」；round2_a 原文同；CONCLUSION_DRAFT 也誤寫 1–100 MHz | 不一致 | 全部改 10–100 MHz |
| X2 | X5 TIE 主值 | 334/915 ps（正弦擬合） | APPLICATIONS §3.2-6 仍以 925/335 → 8.8 dB 為主、§4-3 用 335 ps；表內附擬合值 | 不一致（輕微） | APPLICATIONS 改以擬合值為主（915/334 ≈ 2.74 倍 ≈ 8.8 dB，結論不變） |
| X3 | 同步器 LC 點數 | 1 級 11/31、2 級 26/31 | ANALYSIS、REVIEW_LOG 第 2 輪 (c) 已更正；**REVIEW_LOG L36（第 1 輪 (c) 列）仍寫「2 級同步器 11/31」** | 不一致（歷史列未加註） | L36 加「（第 2 輪 (c) 更正為 d=1；真 2 級 26/31）」 |
| X4 | X6 的 15 倍 | d.1「最佳增益 15 倍」 | APPLICATIONS §6.2：過追蹤量 15 倍；最佳 gff 0.06/0.1/≥1 mS | 不一致 | 同 #85 |
| X5 | 洩放 50 µA 的 PM | c.1「28°」未寫 Cc | ANALYSIS 前文寫 Cc=3 pF、失效情境 2 未寫 Cc；LEARNING_ANSWERS Q4（Cc=5 pF）37.8° | 不一致 | 同 #52 |
| X6 | C 的 PSRR 證據 | b.2 只引 Nasir −5 dB | ANALYSIS C 節同樣只引 −5 dB | 誇大（兩處） | 同 #20 |
| X7 | 其餘共用數字：11–21%、1 kHz 8–14 dB、6.1/0.5 mV、1.716 V/−4.7%/−13%/48.6 dB/−46.4 dB、28.7/18.2/19.9°、742/236/111 mV、88.5 mA/68°、−8～15%/+48%、過追蹤 15 倍、Kvdd 440、β 4.4、553/154/33 vs 499/127/27 | — | ANALYSIS、APPLICATIONS、REVIEW_LOG 數值相同 | 一致 | — |

## 5. 統計

- 核對範圍：REPORT 全文的實質數字約 350 個（含重複出現；不含條目編號與重複的規格常數 0.18 µm/1.8 V/1.6 V），加上 j 節 12 條的卷期頁／DOI／URL 約 45 項；檔案路徑 16 個、腳本 23 個。
- 主表 135 列＋交叉一致性 7 列，共 142 列：

| 判定 | 列數 |
|---|---|
| 一致 | 105 |
| 不一致 | 22（#1、6、10、21、24、45、52、67、77、85、91、93、111、120、121、132、134；X1–X5） |
| 無法查證 | 2（#12、#13；#6 兼屬無法查證） |
| 標記錯誤 | 6（#7、19、23、31、37、106；#20 兼有標記錯誤，計入誇大） |
| 誇大 | 4（#20、59、63、X6） |
| 路徑錯誤 | 3（#75、86、88） |

- 一句話：數字層級的抄寫錯誤很少（主要數值都能在 json 對到）。問題集中在 (1) **PSRR 頻段的表述**（「1–100 MHz ≈0 dB」「只在 ≤100 kHz 差」與審查者原始數據不符）；(2) **C 的 PSRR 只引最差的一筆資料集數字**；(3) 「全部僅摘要」與 X01 實際開啟互相矛盾；(4) 少數條件遺漏（Cc=3 vs 5 pF、50 mV 漣波）與標記歸屬（審查者 vs 作者）；(5) 兩個 [X] 數字無法用 run_all.sh 重現。
