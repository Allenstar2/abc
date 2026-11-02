# 審查輪 1(b)：引用數字與來源一致性查核

- 查核日期：2026-11-02；查核者：事實查核 subagent（未上網、未搜尋；未修改任何既有檔案）
- 受查文件：ARCH_MATRIX.md、PAPER_SELECTION.md、ANALYSIS.md、CONCLUSION_DRAFT.md、DEVICE_CHAR.md、DECISIONS.md
- 可用來源：`lit_raw/agent1–4_notes.md`、`lit_raw/agent*.csv`、`literature.csv`、`ext/DLDO-survey/DLDO survey.xlsx`（commit 68e94cc，pandas 3.0.5 + openpyxl 3.1.5 讀取）、`sim/results/*.json`／`*.log`／`*_tr.txt`、`sim/models/180nm_bulk.pm`、`sim/netlists/*.cir`
- 縮寫：ARCH＝ARCH_MATRIX.md、PS＝PAPER_SELECTION.md、AN＝ANALYSIS.md、CONC＝CONCLUSION_DRAFT.md、DEV＝DEVICE_CHAR.md、DEC＝DECISIONS.md；數字後的「:n」是行號
- 判定：**一致**（容許四捨五入）／**不一致**（數字、條件或 id 與來源不符）／**標記錯誤**（數字有來源，但證據標記或「摘要值」性質標錯，或用僅摘要文獻推電路細節）／**無法查證**（現有來源沒有可對照的原值）

---

## A. 文獻引用（60 項）

| # | 文件:位置 | 引用內容 | 來源檔與原文/原值 | 判定 | 建議修正 |
|---|---|---|---|---|---|
| L01 | ARCH:17、DEC:14（D-010） | H01 摘要「transient response is dictated by the digital portion」、數位逼近演算法、判定未確認 | agent1_notes §1：同一句原文；"fast approximation algorithm leveraging charge distribution" | 一致 | — |
| L02 | ARCH:26 | H01：TSMC 180 nm、Imax 430 mA、Iq 49 µA、無外接 CL、480 mV／430 mA（起點未知）／100 ns、M/S 未知、僅摘要 | agent1_hybrid.csv H01：430 mA、49 uA、480 mV、430 mA（起點未確認）、100 ns、result_type 未知 | 一致 | — |
| L03 | ARCH:27 | H02：TSMC 180 nm、Vout 1.2 V、120 mA、253 mV／full range、S | agent1 CSV H02：1.2 V、120 mA、253 mV（max droop, full-range step）、S（post-layout sim） | 一致 | — |
| L04 | ARCH:28 | H11：65 nm、Iq 200 µA、82 mV(−)/112 mV(+)、200 mA、10 ns、0.027 mm²、M | agent1 CSV H11 同值，result_type M | 一致 | 來源之間有衝突：agent4_notes「是 M 還是 S 沒確認」。建議在證據欄加「M（agent1 摘要；agent4 未確認）」 |
| L05 | ARCH:28 | H11 Imax = 200 mA | agent1 CSV H11 `imax_ma` 為空；200 mA 是負載階躍 ΔI | 標記錯誤 | 表頭說「空白＝摘要沒有」，所以 Imax 應留「—」，或改寫成「≥200（由 ΔI 推）[D]」 |
| L06 | ARCH:29 | H09：65 nm、500 mA、M、B | agent1 CSV H09：65 nm、500 mA、M、B | 一致 | — |
| L07 | ARCH:30 | H05：65 nm、100 pF(total)、105 mV／10 mA／1 ns、M、C | agent1 CSV H05 同值；DLDO 資料集 ISSCC 2017 版摘要也寫 "Undershoot of 105mV with a 10mA/1ns load step"，註記 "Coupling capacitor is taken as Cout" | 一致 | — |
| L08 | ARCH:31 | A01：0.18 µm、1.8 V、50 mA（PSR 量測）、Iq 80/55 µA、capless、優於 −56 dB 至 4 MHz @50 mA、0.14 mm²(core)、M | agent2 CSV A01 同值；capless 取自標題 "External Capacitor-Less" | 一致 | — |
| L09 | ARCH:32 | A02：180 nm、Iq 25.32 µA、125.9 mV、CL/ΔI/邊沿未載明、M/S 未知 | agent2 CSV A02：25.32、125.9 (max undershoot)、未知 | 一致 | — |
| L10 | ARCH:33 | A04：180 nm、300 mA、50 pF、18 mV／1→272 mA／100 ns、優於 −30 dB @10 MHz、M、NMOS pass | agent2 CSV A04 同值 | 一致 | — |
| L11 | ARCH:34 | A05：0.18 µm、100 mA、Iq 14 µA、0–1 nF、M/S 未確認 | agent2 CSV A05：result_type 未知 | 一致 | 合併時被去重的 F01（agent4）寫的是 [M，摘要]，另有 load reg 0.025 mV/mA。這個衝突在 literature.csv 中消失了，建議在 notes 欄保留 |
| L12 | ARCH:35 | A06：180 nm（他人表）、100 mA、30 µA、dropout 200、197 mV(+)／≈100 mA／≈1 µs（由 99.9 mA/µs 推） | agent2 CSV A06 同值，並註明他人比較表與 [D] | 一致 | — |
| L13 | ARCH:36 | D13：0.18 µm、capless、166 mV／9→40 mA／350 ps、0.21 mm²、未知 | agent3 CSV D13 同值 | 一致 | — |
| L14 | ARCH:37 | F03：0.18 µm、1.8–3.3/1.0 V、100 mA、28.8 µA、<43.5 mV／0.1→100 mA／100 ns、0.0174、M | agent4 CSV F03 同值 | 一致 | — |
| L15 | ARCH:38 | F04：1.2/1.0 V、100 mA、Iq 0.6–6.9 µA、388 mV／0→100 mA／100 ns、0.0128、M | agent4 CSV F04 同值 | 一致 | — |
| L16 | ARCH:38 | F04 dropout = 200 mV | agent4 CSV F04 `dropout_mv` 空白；200 是 1.2−1.0 推得 | 標記錯誤 | 改成「(200，Vin−Vout 推) [D]」或留空 |
| L17 | ARCH:38 | F04 歸類 A3（暫態增強） | agent4：「multipath OCL-LDO，無載（<100 nA）也穩定」，摘要沒提 SRE、adaptive bias | 無法查證 | 摘要只支持「multipath 補償」，A3 子類沒有依據，建議改 A1 或「A（子類未確認）」 |
| L18 | ARCH:39 | F02：UMC 0.18 µm、1.94–3.6/1.8 V、50 mA、7.45 µA、≤100 pF、M | agent4 CSV F02 同值 | 一致 | A1 子類同樣沒有摘要依據（摘要只說 capless＋on-chip 補償電容），可改「A」 |
| L19 | ARCH:40 | F11：0.18 µm、1.8/1.6 V、50 mA、14 µA、片上、—/50 mA/—、S | agent4 CSV F11 同值 | 一致 | — |
| L20 | ARCH:40 | F11 dropout = 200 mV | agent4 CSV F11 `dropout_mv` 空白；由 1.8−1.6 推得 | 標記錯誤 | 同 L16 |
| L21 | ARCH:41 | F13：2–5/1.8 V、300 mA、66.4 µA、86 mV(−)／3→300 mA／300 ns、−60 dB @1 kHz、S | agent4 CSV F13 同值 | 一致 | — |
| L22 | ARCH:42 | D02 Hazucha dropout = **300** mV | agent3 CSV D02 `dropout_mv` = 「200（摘要：@100 mA 最小 dropout）」 | **不一致** | 改成 200（@100 mA，摘要）。300 只是 Vin−Vout 的差，並非摘要報告的 dropout |
| L23 | ARCH:42 | D02 子類「A2-like」（FVF 類） | agent3 CSV/notes：arch_class 只寫 A，沒有任何 FVF 描述 | 無法查證 | 這是來源以外的知識，或從僅摘要文獻推電路結構。改「A」，或標 [H] |
| L24 | ARCH:42 | D02 其餘：90 nm、1.2/0.9 V、100 mA、0.6 nF 片上、90 mV(p-p)／100 mA、0.008 mm²、M | agent3 CSV D02 同值 | 一致 | — |
| L25 | ARCH:43 | D12：1.2/1.0 V、10 mA、140 pF、43 mV(−)／0→10 mA／200 ps、優於 −12 dB DC–20 GHz、M | agent3 CSV D12 同值 | 一致 | 製程欄寫「—」與 agent3 一致，但 agent4_notes 寫 D12 為 65 nm，來源有衝突，建議加註 |
| L26 | ARCH:43 | D12 dropout 200、面積 0.0234 | agent3 CSV：「200（Vin−Vout 推得）」「0.0234（260×90 µm² 推得）」 | 標記錯誤 | 表格宣稱都是摘要值，推得值要加 [D] |
| L27 | ARCH:44 | Tang ESSCIRC 2018（資料集列）：180 nm、0.7/0.6 V、100 mA、6.3 µA、dropout 100、106 mV、150 ns、M | xlsx 第 22 列：Vin 0.7、Vout 0.6、Imax 100、Iq 6.3、dropout 0.1 V、droop 106、edge 150 | 一致 | — |
| L28 | ARCH:44 | Tang CL = **0.03 nF** | xlsx 欄位 Output cap = 0.03 nF；**同列 Abstract 寫 "Using only 20 pF of on-chip output capacitor"**，審閱註記 "output capacitor (20pF) … probe parasitic (10pF)" | **不一致** | 改成「20 pF（摘要）；資料集計 FoM 用 30 pF」。ARCH:52 本身就拿這列當 CL 定義不一的例子，表格卻沿用 30 pF |
| L29 | ARCH:44 | Tang ΔI 填「—」 | xlsx：Max (tested) load current change = 90 mA；摘要 "90 mA load current step" | **不一致** | 補上 90 mA |
| L30 | ARCH:44 | 列 id 用「X01」、「類」欄填「0.18 µm pseudo-digital」 | literature.csv X01 是整個資料集，不是 Tang 2018 這篇。xlsx 分類：nested／AMS power FET／synchronous；agent3 notes：NMOS pass＋latched comparator＋charge pump | 標記錯誤 | id 改「X01-r22（Tang 2018）」；「類」欄填類別代號（例如 C 或「未確認」），不要填製程 |
| L31 | ARCH:50 | 資料集 46/58 列有 t_edge、0.015–4000 ns、中位數 2 ns | pandas 重算：數值 edge 46 列，min 0.015、max 4000、median 2.0；s7_dataset_stats.json 相同 | 一致 | — |
| L32 | ARCH:50 | X. Wang CICC 2019：1 ns 185 mV、10 ns 88 mV | xlsx 第 2、7 列：droop 185／88、edge 1／10、ΔI 100、Iq 4.9 | 一致 | — |
| L33 | ARCH:52 | 11 列用總電容或耦合電容當 Cout | xlsx 審閱註記：第 0,1,2,3,7,11,15,16,48,49 列明寫（10 列），加上第 22 列（Tang）列出總電容組成，共 11 列 | 一致 | 計數口徑（含 Tang 列）建議在文中註明 |
| L34 | ARCH:52 | Tang 總電容含探棒 10 pF | xlsx 第 22 列註記 "probe parasitic (10pF)" | 一致 | — |
| L35 | ARCH:53 | 「上表 0.18 µm 文獻的 Vin 從 1.2 V 到 5 V」 | 同表 ARCH:44 的 Tang（0.18 µm）Vin = 0.7 V | 不一致（輕微） | 改成「0.7 V（Tang，pseudo-digital）到 5 V」，或明說只算類比列 |
| L36 | ARCH:53 | 「Vin ≥ 2.5 V 的設計用了厚氧元件 … [D]」 | agent4_notes：F08「應該是高壓元件 [H]」、F02「可能用了 3.3 V 元件 [H]」，沒有一篇讀到元件類型 | 標記錯誤 | 證據應為 [H]（僅摘要，不知道實際元件），措辭改「很可能用了」 |
| L37 | ARCH:59 | C 類「量化誤差＋dead zone，需類比細調才有 mV 級精度 [文獻摘要 D06、D11]」 | D06 摘要講暫態的功耗-速度取捨與 PSR 弱；D11 講 ALDO 漣波與 PSR 領先。講 dead-zone 降低輸出精度的是 **H08** 摘要（"comparator dead-zone 會拖慢偵測並降低輸出精度"） | **不一致**（id 對錯篇） | 改引 [文獻摘要 H08]；「需類比細調才有 mV 級」可再加 H12 摘要（SSS 微調類比電流得高 DC 精度）或改標 [D] |
| L38 | ARCH:60 | limit cycle 是本質問題 [H08/D04 摘要] | agent1 H08：「D-LDO 天生會有 limit cycle oscillation」 | 一致 | — |
| L39 | ARCH:62、AN:180 | 資料集 8/58 列有 PSRR；Nasir 2015 −5 dB @1 MHz | pandas：PSRR 數值 8 列，全部 @1 MHz，範圍 −46 到 −5；第 51 列 Nasir ISSCC 2015 = −5 | 一致 | — |
| L40 | ARCH:11–15 | 分類表各 id 的類別（A／B：H09,H10,H11／C：H05,F09,F10／D：D01,D03,D05,H13／R-Crit-Mx）與重複對應 H06=D07、H08=D04、A12=D09、A14=D11 | literature.csv `arch_class`、merge_literature.py 的 dups | 一致 | H04、H12、H14、H15（未確認）沒有列在任何一類，可補一列「未確認」 |
| L41 | PS:18 | H01 書目：TCAS-I 2025、Xplore 10884555、DOI 未驗證、undershoot 480 mV | agent1 §1 同 | 一致 | — |
| L42 | PS:19 | H04：handle 2453/5398、embargo 至 2025-09-23 | agent1 §1、agent1 CSV H04 同 | 一致 | — |
| L43 | PS:20 | A05：10.1109/ACCESS.2022.3185630、OA 有報導、0.18 µm、0–100 mA、0–1 nF、14 µA | agent2 CSV A05；literature.csv `oa_reported` = 全文-出版社OA | 一致 | — |
| L44 | PS:21 | A06：10.3390/mi13101594、OA 有報導、100 mA、200 mV、他人表 99.9 mA/µs | agent2 CSV A06 同 | 一致 | — |
| L45 | PS:21 | A06「電容耦合 SRE 只多幾顆電晶體」 | 來源只有摘要（Cm、Ct 耦合到 current booster）；「只多幾顆電晶體」是 agent2_notes 的可行性判斷，沒有讀到電路 | 標記錯誤 | 僅摘要文獻被拿來推電路複雜度。改成「[H] 推測只多幾顆電晶體，待全文確認」 |
| L46 | PS:22 | F03：10.1109/ACCESS.2024.3398290、OA 有報導、0.1→100 mA、100 ns、<43.5 mV、Vin 1.8–3.3 V | agent4 CSV F03 同 | 一致 | — |
| L47 | PS:23 | A01：10.1109/JSSC.2013.2289897（間接驗證）、0.18 µm、1.8 V、Iq 80/55 µA | agent2 §1：ADS 2014IJSSC..49..486P 比對 | 一致 | — |
| L48 | PS:24 | A02：10.1109/ISCAS48785.2022.9937778（間接驗證）、180 nm、125.9 mV | agent2 §1：Korea Univ. Pure 記錄比對 | 一致 | — |
| L49 | PS:25 | H11：65 nm、self-triggered、OA 有報導 | agent1 CSV H11；`oa_reported` = 全文-出版社OA | 一致 | — |
| L50 | PS:26 | A12 Torres：給出 DOI 10.1109/MCAS.2014.2314263，沒有寫驗證狀態 | agent3 CSV D09（同一篇）：「DOI 待驗證：只有單一摘錄來源，故 doi 欄留空」；agent2 A12 只說「DOI 都是間接驗證」 | 標記錯誤 | 其他入選篇都標了「未驗證／間接驗證」。這篇應加「（DOI 未驗證，單一搜尋摘錄）」，literature.csv A12 也要同步 |
| L51 | PS:27 | D08＋X01：Wang、Kim、Seok 等；github.com/mgseok/DLDO-survey | agent3 CSV D08；xlsx README 引用格式 "M. Seok, Z. Wang, S. J. Kim" | 一致 | — |
| L52 | PS:29 | 「主要排除理由（其餘 44 筆）」 | literature.csv 共 54 列；入選 10 項含 11 個 id（第 10 項是 D08＋X01）→ 54−11 = **43** | **不一致** | 改成 43 筆，或說明計數方式 |
| L53 | PS:33–34 | A03 65 nm、A09 65 nm、A11 40 nm、H09 65 nm、H13 28 nm、H14 14 nm；F02 1.94–3.6 V、F08 2.5–5 V、F13 2–5 V | literature.csv 各列 `process`、`vin_v` | 一致 | — |
| L54 | PS:36 | F12 load regulation 與實測文獻差約 260 倍 | agent4 F12：0.095 µV/mA vs F01 0.025 mV/mA（≈263×） | 一致 | — |
| L55 | AN:111 | ISCAS 2022 voltage damper＋body loop「從摘要看是這類」，且聲明不推論電路細節 | agent2 §1 A02 摘要描述 | 一致 | 這段是正確處理「僅摘要」的範例 |
| L56 | AN:149 | Leduc 2025 droop detector 讓 undershoot 降 54% | agent1 §1 表：「開啟後 undershoot 降 54%」 | 一致 | — |
| L57 | AN:183 | DLDO 原始動機：0.5 V 下類比做不起來 [文獻摘要 D01] | agent3 D01：「傳統 op-amp 回授的 LDO 在 0.5 V 下無法工作 [M]」 | 一致 | — |
| L58 | DEC:15（D-011） | 已收集 59 筆記錄 | 4 個 CSV 共 16+15+14+14 = 59 列 | 一致 | — |
| L59 | CONC:17 | Leduc 2025 未確認（僅摘要），摘要線索偏 C | agent1 §1、D-010 | 一致 | — |
| L60 | AN:170 | C 類原理 [文獻摘要 D06、H06] | H06 摘要把 hybrid 分成 AAD/DAA；D06 摘要比較 ALDO/DLDO | 一致 | — |

---

## B. 模擬數字（68 項）

| # | 文件:位置 | 引用內容 | 來源檔與原值 | 判定 | 建議修正 |
|---|---|---|---|---|---|
| S01 | DEV:18 | NMOS L=0.18：Vth 0.413、4.99、11.8、6.7、11.4 | s0_device_char.json n_L0.18：0.4128、4.994、11.8、6.7、11.4 | 一致 | — |
| S02 | DEV:19 | NMOS L=0.5：0.495、4.09、59.2、31.7、69.5 | n_L0.5：0.495、4.086、59.2、31.7、69.5 | 一致 | — |
| S03 | DEV:20 | NMOS L=1.0：0.446、3.92、96.9、20.1、101.1 | n_L1.0：0.4459、3.918、96.9、20.1、101.1 | 一致 | — |
| S04 | DEV:21 | PMOS L=0.18：0.278、1.83、14.4、2.1、10.1 | p_L0.18：0.2779、1.83、14.4、2.1、10.1 | 一致 | — |
| S05 | DEV:22 | PMOS L=0.5：0.473、1.17、37.7、34.5、58.4 | p_L0.5：0.4725、1.17、37.7、34.5、58.4 | 一致 | — |
| S06 | DEV:23 | PMOS L=1.0：0.446、1.02、75.0、42.3、99.1 | p_L1.0：0.4461、1.017、75.0、42.3、99.1 | 一致 | — |
| S07 | DEV:36 | Pass Id/(W=1 mm)：93.6／84.8／74.6／63.0／49.8 mA | pass_pmos_W1000u：93.64、84.78、74.62、63.01、49.83 | 一致 | — |
| S08 | DEV:38 | 100 mA 需 W ≈ 1.34 mm（Vg=0.4 V） | 100/74.62 = 1.340 mm | 一致 | — |
| S09 | DEV:9（及 LOG） | version 改 3.3.0 後 gm=598.8 µS、gds=7.59 µS、Id=90.9 µA 完全相同 | sim/results 沒有任何 log 或 json 存這個比較（grep 不到） | 無法查證 | 補存比較的 netlist 與 log（例如 `results/s0_version_check.log`） |
| S10 | DEV:8,11,27 | `level=49 version=3.1`、`lmin=lmax=0.18 µm`、PMOS Eta0 = 8.5、模型含 tref/xl/rd/rs | 180nm_bulk.pm：version=3.1、lmin=lmax=1.8e-7、PMOS Eta0=8.5（NMOS 0.22）、Tref/xl/rd/rs 都在 | 一致 | 「ngspice 印出 BSIM3v1 (3.1)」在現存 log 中找不到，只能算部分查證 |
| S11 | DEV:1 | 標題「元件特性**實測**」 | 內文說「所有數字皆為 [X]（本次模擬）」 | 標記錯誤 | 「實測」在本 repo 代表 [M]（論文實測），改成「元件特性（模擬）」 |
| S12 | DEV:28 | 「Vth 隨 Vsd 大幅變動 → 關不掉的漏電與輕載行為對 Vin 很敏感 [X]」 | s0 只量 Vds=0.6 V 的 Vth；漏電對 Vin 的敏感度沒有模擬 | 標記錯誤 | 改 [D]/[H]，或補一個 Vin 掃描 |
| S13 | AN:11 | gm_p = 347 mS、gds_p = 260 mS、比值 1.33（100 mA） | tmp_op.log／hvs_op_CL100p_Cc5p_0.1.log：mp gm 0.3470、gds 0.2600；s2 json Ap = 1.334 | 一致 | — |
| S14 | AN:12 | gm_p·R_o 13.2 → 1.33；T0 53.0 → 33.7 dB | s2 json Ap 13.16／1.334；sim T0 52.99／33.74 | 一致 | — |
| S15 | AN:13 | C_gg = **5.3 pF（輕載）**～7.9 pF（滿載），W = 4 mm | s2 json Cpg：REF-A（Imin=200 µA）0 mA = **5.54 pF**、100 mA = 7.87 pF；5.345 pF 是**原始 Imin=50 µA 設計**的值 | **不一致** | 改成 5.5 pF（REF-A），或註明 5.3 pF 屬原始設計 |
| S16 | AN:13 | Cox·W·L＋2·Cov·W ≈ 8.1 pF [D] | 模型 PMOS tox 4.2 nm → Cox 8.22 fF/µm²；Cgso=Cgdo=2.786e-10 F/m → 5.92＋2.23 = 8.15 pF | 一致 | — |
| S17 | AN:14 | 100 mA dropout 94 mV，Vin ≈ 1.674 V 開始掉 | s3 json dropout_full_V = [0.0943, 1.674] | 一致 | — |
| S18 | AN:15 | Cox ≈ 8.2 fF/µm² → 1 nF ≈ 0.12 mm² | 1 nF ÷ 8.22 fF/µm² = 0.122 mm² | 一致 | — |
| S19 | AN:44 | CL100p/Cc5p, 0 mA：53.2/53.0、2.50/2.45、66.4/66.4、p2 7.8、p_b 29.0、誤差 +2.2/+2.3/+0.1% | s2 json：53.18/52.99、2.505/2.448、66.43/66.37、7.82、28.98、2.23/2.31/0.09 | 一致 | — |
| S20 | AN:45 | 10 mA：53.9/53.8、2.66/2.62、82.3/86.3、270、20.9、PM −4.7% | s2 json：53.94/53.84、2.656/2.616、82.28/86.29、270.3、20.89、−4.65 | 一致 | — |
| S21 | AN:46 | 100 mA：33.7/33.7、1.61/1.60、86.6/87.9、939、20.5、−1.4% | s2 json：33.71/33.74、1.606/1.598、86.60/87.86、939.0、20.48、−1.43 | 一致 | — |
| S22 | AN:47 | CL1n/Cc20p 0 mA：53.2/53.0、0.54/0.53、54.2/54.7、0.80、29.0、≤2.3% | s2 json：53.18/52.99、0.539/0.527、54.20/54.67、0.799、28.98、最大 2.31 | 一致 | — |
| S23 | AN:48 | 原始設計：52.6/52.3、2.54/2.42、30.8/28.1、1.98、29.6、UGF +5.0%、PM +9.5% | s2 json：52.56/52.33、2.536/2.415、30.76/28.10、1.979、29.55、4.99、9.47 | 一致 | LOG.md 16:48 那條寫「52.5、2.55、PM ~29°」，與 json 不同（LOG 不在本次受查範圍） |
| S24 | AN:59–61、DEC:12 | Imin=50 µA：Cc=3 pF → 28°、Cc=10 pF → 52°；1 nF 到 Cc=40 pF 仍 ≤41°；Imin=200 µA：66°（100 pF/5 pF）、55°（1 nF/20 pF） | s1_refA_sweep.json（Imax=100）：28.1、52.3；1 nF/50 µA/40 pF：39.9（Imax=10 時 41.0）；66.4、54.7 | 一致 | — |
| S25 | AN:61、DEC:12 | Iq 131 → 287 µA（增加約 150 µA） | q_IL0.log（R=16 k，原始設計）iin = 130.6 µA；s3 json Iq_total = 286.66 µA；差 156 µA | 一致 | — |
| S26 | AN:65–66、ARCH:45–46 | 0→100 mA undershoot：1 ns 742（100 pF）/497（1 nF）；100 ns 236/345；1 µs 111/151 | s3 json／x2 json：742.2、496.8；235.5、345.5；111.0、151.2 | 一致 | — |
| S27 | AN:67 | 1 µs 邊沿、100 pF，起點 0/1/10 mA → 111/52/21 mV | x2_edge_time.json：111.0、51.7、21.4 | 一致 | — |
| S28 | AN:68 | 卸載 overshoot 206 mV（＝1.8−1.594） | s3 json overshoot 0.2064 V（從 v_heavy 1.5932 起算） | 一致 | — |
| S29 | AN:68 | 「與 1 nF 波形約 1.5–2 µs 的回復一致 [X]」 | 1 ns 邊沿的 1 nF 波形沒有存檔；現存的 c_ltr_tr.txt／cr_tr_tr.txt 是 1 µs 邊沿 | 無法查證 | 把 recovery time 寫進 s3 json |
| S30 | AN:68 | SF 50 µA／7.9 pF ≈ 6.3 V/µs；擺 0.46 V 需 ~73 ns | op log：mb Id 46 µA（0 mA）／52 µA（100 mA）；Vpg 1.5949 → 1.1278 = 0.467 V；0.467/6.33 = 74 ns | 一致 | — |
| S31 | AN:75–76 | PSRR 100 mA：−33.7（推）vs −33.3 dB（模擬）；0 mA：0.253/(0.253+0.125) → −56.7 vs −55.3 dB | s3 json psrr 100mA@1k −33.3、0mA@1k −55.3；hvs_op_..._0.log mp gds 0.2534 mS；1/(8 kΩ) = 0.125 mS | 一致 | — |
| S32 | AN:77 | 「PSRR … 升到 −5～−8 dB @1 MHz」 | s3 json（100 pF）@1 MHz：0 mA −8.3、10 mA **−8.7**、100 mA −5.3 | 不一致（輕微） | 改「−5～−9 dB」並註明負載 |
| S33 | AN:78 | gds_p/(2π·CL) 轉折 414 MHz [D]；模擬 100 MHz 仍 +0.1 dB | 0.26/(2π·100 pF) = 413.8 MHz；s3 json 100mA@1e8 = +0.1 | 一致 | — |
| S34 | AN:82、AN:191 | SF-like 125 °C 零負載 Vout 1.6525 V（+46 mV）；FF-like 125 °C +20 mV | s6_corners.json：SF-like 125 °C vout_0 1.6525；FF-like 125 °C 1.6266；TT 27 °C 1.6061 → +46.4／+20.5 | 一致 | — |
| S35 | AN:103 | 「C_pg≈8 pF、ΔV_g≈**0.52 V（1.649→1.128 V）**[X]」→ ~0.8 mA、16 倍 | **1.6495 V 是原始 Imin=50 µA 設計的零負載 Vpg**（q_IL0.log vpg_op、hvs_lg_orig_..._0.log）；REF-A 零負載 Vpg = **1.5949 V**（hvs_op_CL100p_Cc5p_0.log）→ ΔV_g = 0.467 V | **不一致** | 改成 0.47 V（1.595→1.128）→ I_drive ≈ 0.75 mA（約 15×）。AN:68 已經用 0.46 V，兩處應統一 |
| S36 | AN:117 | REF-B：pass 800 µm、8 片、每片 W=130 µm、12.2 mA @Vsd=0.2 V、時脈 1/10/50 MHz | ldo_hybrid.py HDEF：Wp=800、N=8、Ws=130；s0 json 93.64 mA/mm × 0.13 = 12.17 mA | 一致 | — |
| S37 | AN:117 | 類比 pass「最大約 30–35 mA」 | results 中沒有 REF-B 類比部分的 I–V 或最大電流；由 D-006 的 43 mA/mm 外插約 34 mA（Vg≈0.9 V） | 無法查證 | 這是推導值，標 [D]；也和 ARCH:47 公式中的「20」矛盾（見 S57） |
| S38 | AN:130 | 寬窗 3–18 mA：碼 1/3/5/7，全部穩定（1/10/50 MHz） | x3_hybrid.json X3a wide：code_final 1/3/5/7，toggles 0 | 一致 | — |
| S39 | AN:131–133 | 窄窗 20 mA：1 MHz 5 次/229 mV；10 MHz 14 次/216 mV；50 MHz 21 次/191 mV；其餘負載穩定 | X3a narrow：toggles 5/14/21；vout_pp 229.4/216.0/190.8；45/70/95 mA toggles 0 | 一致 | — |
| S40 | AN:140 | t_drv 1/30/300 ns → 尖峰 82.6/71.4/34.5 mV | x3e_glitch_fo4.json max_pos_mV：82.61、71.40、34.47 | 一致 | — |
| S41 | AN:146–148、ARCH:61、CONC:8 | 5→95 mA：REF-A 499（1 ns）/127（100 ns）；REF-B 10 MHz 756/313；50 MHz 756/238 | X3b：498.9/127.5；756.2/313.1；756.3/237.6 | 一致 | — |
| S42 | AN:152 | 碼凍結：碼 0 輕載 53.1 dB；碼 3/5/7 → 22.8/18.7/16.0 dB；UGF 2.4 → 0.4–0.75 MHz | x3d json：53.1（2.44 MHz）；22.8/18.7/16.0；UGF 0.75/0.52/0.39 | 一致 | — |
| S43 | AN:153、ARCH:62、CONC:8 | 70 mA PSRR @1 kHz：REF-A −38.2、REF-B（碼 5）−18.8，差 19 dB；@100 kHz −25.6 vs −13.3 | x3_hybrid.json X3c：−38.2／−18.8；−25.6／−13.3 | 一致 | — |
| S44 | AN:154、ARCH:59 | 「95 mA 時 Vout 1.5975 V（**REF-A 1.5932 V**）」 | REF-B 95 mA：X3a vout_mean 1.59747 ✓。**REF-A 1.5932 是 100 mA 的值**（s3 json vout @100 mA = 1.593221）；REF-A 在 95 mA 實為 **1.5936 V**（x3b_A_tr.txt，5→95 mA 穩態） | **不一致**（條件錯配） | 改成「REF-A 1.5936 V（95 mA）」；結論方向不變 |
| S45 | AN:161、AN:178 | PTM FO4 = 54–60 ps | x3e json fo4：tplh 53.87、tphl 60.25 ps | 一致 | — |
| S46 | AN:159、ARCH:64 | 8 個 DFF＋每位元 3×AND2＋1×OR3（32 閘）＋1 個 NOR2；2 個時脈比較器 | ldo_hybrid.py digital_block：每位元 Aa/Ab/Ac（and2）＋Ao（or3）＋Af（d_dff）；Ahold nor2；2 個 B-source 比較器經 adc_bridge 取樣 | 一致 | — |
| S47 | AN:176–177 | ΔV_ripple：12.2 mA/100 pF/10 MHz → 6 V；50 mV 需 1 mA@100 MHz 或 0.1 mA@10 MHz（1000 片） | 6.1 mA/(100 pF·10 MHz) = 6.1 V；其餘算術正確 [D] | 一致 | — |
| S48 | AN:204–207 | 500 µA 洩放：PM 58.4°（1 nF/10 pF）、43.3°（1 nF/5 pF）、70.4°（100 pF/3 pF）、REF-A 66.4° | s1_refA_sweep.json（Imax=100）：58.4、43.3、70.4、66.4 | 一致 | — |
| S49 | AN:206 | 100 pF、500 µA、Cc=3 pF、1 µs → 72 mV | fx_tr_tr.txt（fx_tr.cir：R=1.6 k、Cc=3 p、CL=100 p、1 µs 邊沿）重算 71.97 mV | 一致 | 這是最後一次執行留下的檔案，其他設定已被覆寫 |
| S50 | AN:204–206 | 其餘 undershoot：458/261/104、456/213/89、687/185 mV | 沒有對應的 json；fx_* 暫存檔只剩最後一組設定 | 無法查證 | 把公平性檢查的結果寫入 json（例如 `s8_fairness.json`） |
| S51 | AN:215–216 | Imax 10 mA 兩列：69.7°/54.4°、33.4 dB、10.2 mV、289 µA、−33.1/−5.3 與 −33.0/−0.2、308/152/46 與 277/262/98 | s8_sensitivity.json：69.7/54.4、33.4、10.2、289.4、−33.1/−5.3、−33.0/−0.2、307.6/152.1/45.6、276.6/262.2/98.3 | 一致 | — |
| S52 | AN:217–218 | Imax 50 mA 兩列：68.8°/55.2°、33.7、12.0、288、−33.3/−5.4 與 −0.4、552/185/81 與 388/319/132 | s8 json：68.8/55.2、33.7、12.0、288.0、−5.4/−0.4、551.9/185.1/81.4、388.3/319.3/131.6 | 一致 | — |
| S53 | AN:219–220 | Imax 100 mA 兩列：66.4°/54.7°、33.7、12.8、287、−33.3/−5.3 與 −0.4、742/236/111 與 497/345/151 | s8 json：66.4/54.7、33.7、12.8、286.7、−5.3/−0.4、742.2/235.5/111.0、496.8/345.5/151.2 | 一致 | — |
| S54 | AN:224–226 | 滿載 DC 迴路增益「都約 33.5 dB」；100 ns：152 → 236 mV | s8：33.4–33.7 dB；152.1 → 235.5 | 一致 | — |
| S55 | ARCH:45 | REF-A 100 pF：Iq 287、dropout 94、236/742 mV、PSRR −55 dB@1 kHz(0 mA)、−33 dB@1 kHz(100 mA)、−5 dB@1 MHz | s3 json：286.66 µA、94.3 mV、235.5/742.2、−55.3、−33.3、@1 MHz：100 mA −5.3（0 mA 為 −8.3） | 一致 | −5 dB@1 MHz 補上負載條件「(100 mA)」 |
| S56 | ARCH:46 | REF-A 1 nF：345/497 mV、−16 dB @100 kHz | s3 json：345.5/496.8；@100 kHz：0 mA −16.2、10 mA −16.2、100 mA −12.3 | 一致 | 補上負載條件「(0–10 mA)」 |
| S57 | ARCH:47 | REF-B Imax「116（20+8×12.2）」 | 20 + 8×12.2 = **117.6**；而且 AN:117 說類比部分最多約 30–35 mA，公式中的 20 mA 沒有出處 | **不一致** | 改成「≈118（20+8×12.2）」並說明 20 mA 的條件，或依 30–35 mA 改成 128–133 mA，兩份文件要統一 |
| S58 | ARCH:47 | REF-B Iq「≈290＋數位」 | x3 系列沒有任何 Iq 輸出（x3c_B.log 只印 Vout/Vpg） | 無法查證 | 標 [D]（由 REF-A 類比核心推估），或補一次 OP |
| S59 | ARCH:47 | REF-B 313 mV（10 MHz）／5→95 mA／100 ns；−18.8 dB @1 kHz（70 mA） | X3b 313.1；X3c −18.8 | 一致 | — |
| S60 | ARCH:50–51 | 0→100 mA：0.1 ns 748、1 µs 111；10 mA 起 1 µs 21；1 ns 起點 0/1/10 → 742/627/452 | x2 json：748.2、111.0、21.4；742.2、626.7、451.9 | 一致 | — |
| S61 | ARCH:59–62 | DC 迴路增益 53 → 34 dB；1 nF 需 Cc=20 pF＋200 µA 才有 PM 55°；1 ns 742 mV；313 vs 127；−18.8 vs −38 | s3、s1、x3 json 對應值 | 一致 | 「需」說得太強：s1 顯示 500 µA＋Cc 10 pF 也有 58.4°。改成「例如」 |
| S62 | ARCH:63 | B 類「切換瞬間每片 12 mA 步階造成尖峰；**時脈饋通** [X]」 | AN:156 自己寫「本模型的數位是理想的，**沒有時脈饋通**」；X3e 只模擬 slice 切換尖峰 | 標記錯誤 | 拆開寫：「slice 切換尖峰 [X]；時脈饋通 [H]（未模擬）」 |
| S63 | CONC:8、CONC:21 | 313 mV vs 127 mV；PSRR 差 19 dB；~200 mV p-p limit cycle；REF-A 742 mV @100 pF | X3b、X3c、X3a（190.8–229.4 mV）、s3 | 一致 | — |
| S64 | CONC:13 | 設計規則「窗口 ≥ 1.5× 一片電流」「slice 邊沿放慢到 ~100 ns 級」 | X3a 只驗過寬窗 15/12.2 = 1.23×（無 LC）與窄窗 0.49×（有 LC）；X3e 只測 1/30/300 ns | 標記錯誤 | 這兩條是推論，沒有模擬支撐，應標 [D]/[H]，或補 1.5× 與 100 ns 的模擬點 |
| S65 | DEC:10（D-006） | Vsd=0.2 V、Vg≈0.9 V 約 43 mA/mm，留 ~1.7× 餘裕 | s0 只量到 Vg=0.8 V（49.83 mA/mm）；以斜率 −6.6 mA/0.1 V 外插 ≈ 43；4 mm × 43 = 172 mA → 1.72× | 一致 | 註明是外插 [D] |
| S66 | DEC:12（D-008） | R1=R2=4 kΩ、Cc 5/20 pF、Imin 50 µA 時 PM ≤41°、66°/55°、Iq +150 µA | cr_tr.cir R=4000；s1 json；q_IL0.log → 156 µA | 一致 | — |
| S67 | DEC:7（D-003） | version=3.3.0 時單點 OP 結果相同 | 同 S09，沒有存檔 | 無法查證 | 同 S09 |
| S68 | DEC:9（D-005） | Vref 0.8 V、偏壓 10 µA 理想源、SF body 接 source、Miller Cc 從 Vout 接 ea | q_IL0.cir：VREF 0.8、Ibias 1e-05、`Mb 0 ea pg pg`、`Cc vout ea` | 一致 | — |

---

## C. 範圍外但相關的發現（未計入統計）

1. **x4_sre.json 與 CONCLUSION 的 SRE 建議方向相反，且沒有被任何文件引用。** SRE 版本在 1 ns 邊沿 undershoot 從 742.2 降到 654.6 mV（−12%），但 **100 ns 邊沿從 235.5 惡化到 283.8 mV**。CONC:4 把「加電容耦合式 SRE」列入首選方案，CONC:9 說 A 的風險「都可以用類比手段處理」，這兩點目前沒有 [X] 支撐，反而有反證。另外 `sim/scripts/` 在查核期間出現 s9_sre.py、s9b_sre_sweep.py、ldo_sre.py、learn.py 等新檔，可能還有其他 session 在跑，結果仍會變動。
2. AN:16 寫「見 REPORT g 節」，但 REPORT.md 不存在。
3. LOG.md 16:48 那條的手算數字（52.5 dB、2.55 MHz、PM ~29°）與 s2_hand_vs_sim.json（52.56、2.54、30.8°）不同。
4. 來源之間的 M/S 衝突在合併時消失了：A05/F01（agent2 未知 vs agent4 M）、H11（agent1 M vs agent4 未確認）、D12 製程（agent3 未給 vs agent4 65 nm）。
5. 「OA 有報導」與「已讀全文」：受查文件都沒有混用，PS 一律寫「OA 有報導」，ARCH:5 明說唯一實際開啟的是資料集。PS:23、AN:111 的「你讀過」指的是使用者，不是 agent。這部分沒有發現問題。

---

## D. 統計

| 判定 | 文獻引用（A） | 模擬數字（B） | 合計 |
|---|---|---|---|
| 一致 | 44 | 53 | **97** |
| 不一致 | 6 | 5 | **11** |
| 標記錯誤 | 8 | 4 | **12** |
| 無法查證 | 2 | 6 | **8** |
| 合計 | 60 | 68 | **128** |

**不一致清單**：L22（D02 dropout 300→200）、L28（Tang CL 30 pF→摘要 20 pF）、L29（Tang ΔI 漏填 90 mA）、L35（0.18 µm Vin 範圍漏了 0.7 V）、L37（dead-zone 引用 id 錯，應為 H08）、L52（排除 44→43 筆）、S15（C_gg 5.3 pF 取自原始設計）、S32（PSRR @1 MHz −8.7 超出 −5～−8）、S35（ΔV_g 0.52 V 取自原始設計，REF-A 應為 0.47 V）、S44（REF-A 1.5932 V 是 100 mA 的值，95 mA 為 1.5936 V）、S57（20+8×12.2 = 117.6 ≠ 116）。

**標記錯誤清單**：L05（H11 Imax 由 ΔI 推）、L16／L20／L26（推得的 dropout、面積當成摘要值）、L30（X01 id 指向資料集而非 Tang；類別欄填製程）、L36（厚氧應為 [H]）、L45（A06「只多幾顆電晶體」，用僅摘要推電路）、L50（A12 DOI 沒有驗證狀態）、S11（DEVICE_CHAR 標題「實測」）、S12（漏電敏感度標 [X]）、S62（時脈饋通標 [X] 但沒有模擬）、S64（1.5×、~100 ns 設計規則沒有模擬支撐）。
