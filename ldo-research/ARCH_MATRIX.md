# Stage 2：架構分類與比較矩陣

> **證據等級提醒**：本次所有文獻都只讀到搜尋摘錄（D-009、D-012），表中文獻數字一律是「摘要值」，**不能**拿來推電路細節。
> [M]/[S] 指的是「摘要說是實測/模擬」，不是我核對過全文。
> 唯一實際開啟的資料是 Seok 等人的 DLDO survey 資料集（X01，屬二手整理）。[X] 是本次 ngspice 模擬（PTM 180nm，不是真實製程）。

## 1. 分類法（依「誰決定穩態 Vout」與「誰負責快速暫態」）

| 類別 | 穩態 DC 精度由誰決定 | 主要負載電流由誰供應 | 快速暫態由誰負責 | 典型子類 | 文獻例（literature.csv id） |
|---|---|---|---|---|---|
| **A 純類比** | 類比 EA | 類比 pass device | 類比（Miller、buffer、SRE、FVF 等） | A1 兩/三級 Miller（含 nested Miller）；A2 FVF/CAFVF；A3 暫態增強（電容耦合 SRE、adaptive/dynamic bias、super source follower）；A4 NMOS pass；A5 PSR 增強（feedforward ripple cancellation）；A6 類比雙迴路（快慢迴路都是類比） | A01, A02, A03, A04, A05, A06, A07, A08, A09, A10, A11, A15, D02, D12, D13, F02–F08, F11–F13, H03 |
| **B 類比主導 hybrid**（digital-assisted analog, DAA） | 類比 EA | 類比＋數位 slice 分擔；數位只「粗調/重新置中」 | 類比為主；數位可能加快大步階 | B1 數位感測類比 pass 閘極或電流（本次 REF-B）；B2 數位在大暫態時觸發（self-triggered） | H09, H10, H11（摘要歸類為 B）；REF-B [X] |
| **C 數位主導、類比輔助**（analog-assisted digital, AAD） | 數位迴路（量化）＋類比細調或無 | 數位 slice 陣列 | 數位為主，類比只補量化或輕載 | C1 同步 DLDO + 類比快速路徑；C2 演算法式搜尋（SAR、charge-distribution）| H05, F09, F10；H01/H02 摘要線索偏 C 但**未確認** |
| **D 純數位**（只作背景） | 比較器＋數位控制 | 數位 slice | 數位 | 同步、event-driven、computational | D01, D03, D05, H13 |
| R/Crit/Mx | 回顧、反面意見、量測方法 | | | | H06(=D07), H07, H08(=D04), A12(=D09), A13, A14(=D11), D06, D08, D10, D14, H16, X01 |

**Leduc 2025（H01）＝未確認（僅摘要）**。摘要有「transient response is dictated by the digital portion」與「數位逼近演算法」等偏 C 線索，但穩態由誰供電、DC 精度由誰決定、數位迴路穩態是否停止，摘要都沒寫（D-010）。

## 2. 文獻數字矩陣（摘要值；跨論文**不可直接比較**）

欄位：製程｜Vin/Vout (V)｜Imax (mA)｜Iq (µA)｜CL｜dropout (mV)｜ΔV / ΔI / 邊沿｜PSRR@f｜面積 (mm²)｜M/S｜證據
空白＝摘要沒有。

| id | 類 | 製程 | Vin/Vout | Imax | Iq | CL | dropout | ΔV / ΔI / 邊沿 | PSRR | 面積 | M/S | 證據 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H01 Leduc 2025 | 未確認 | TSMC 180 nm | — | 430 | 49 | 無外接；片上值未知 | — | 480 mV / 430 mA(起點未知) / 100 ns | — | — | 未知 | 僅摘要 |
| H02 Leduc 2024 MWSCAS | 未確認 | TSMC 180 nm | —/1.2 | 120 | — | — | — | 253 mV / full range / — | — | — | S | 僅摘要 |
| H11 Jin 2023 | B | 65 nm | — | —（ΔI=200 mA）| 200 | — | — | 82 mV(−) 112 mV(+) / 200 mA / 10 ns | — | 0.027 | M | 僅摘要 |
| H09 Chen 2021 | B | 65 nm | — | 500 | — | — | — | — | — | — | M | 僅摘要 |
| H05 Huang 2018 | C | 65 nm | — | — | — | 100 pF(total) | — | 105 mV / 10 mA / 1 ns | — | — | M | 僅摘要 |
| A01 Park 2014 JSSC | A5 | 0.18 µm | 1.8/— | 50(PSR 量測) | 80/55 | capless | — | — | 優於 −56 dB 至 4 MHz @50 mA | 0.14(core) | M | 僅摘要 |
| A02 Kim 2022 ISCAS | A(未確認 capless) | 180 nm | — | — | 25.32 | 未載明 | — | 125.9 mV / 未載明 / 未載明 | — | — | 未知 | 僅摘要 |
| A04 Tang 2024 CICC | A4 | 180 nm | — | 300 | — | 50 pF | — | 18 mV / 1→272 mA / 100 ns | 優於 −30 dB @10 MHz | — | M | 僅摘要；NMOS pass |
| A05 Limpisawas 2022 | A1 | 0.18 µm | — | 100 | 14 | 0–1 nF | — | 未取得 | — | — | 未確認 | 僅摘要（OA 有報導） |
| A06 Ni 2022 | A3 | 180 nm(他人表) | — | 100 | 30 | — | 200 | 197 mV(+) / ≈100 mA / ≈1 µs（由 99.9 mA/µs 推）| — | — | 未確認 | 僅摘要＋他人比較表 |
| D13 Mandal 2019 | A3/A4 | 0.18 µm | — | — | — | capless | — | 166 mV / 9→40 mA / 350 ps | — | 0.21 | 未知 | 僅摘要 |
| F03 Kao 2024 | A3 | 0.18 µm | 1.8–3.3/1.0 | 100 | 28.8 | capless | — | <43.5 mV / 0.1→100 mA / 100 ns | — | 0.0174 | M | 僅摘要 |
| F04 Kao 2022 | A3 | 0.18 µm | 1.2/1.0 | 100 | 0.6–6.9 | capless | (200，Vin−Vout 推)[D] | 388 mV / 0→100 mA / 100 ns | — | 0.0128 | M | 僅摘要 |
| F02 Pérez-Bailón 2018 | A1 | UMC 0.18 µm | 1.94–3.6/1.8 | 50 | 7.45 | ≤100 pF | — | — | — | — | M | 僅摘要 |
| F11 Ameziane 2019 | A | 0.18 µm | 1.8/1.6 | 50 | 14 | 片上 | (200，Vin−Vout 推)[D] | — / 50 mA / — | — | — | **S** | 僅摘要（品質警示） |
| F13 Gao 2023 | A | 0.18 µm | 2–5/1.8 | 300 | 66.4 | 片上 | — | 86 mV(−) / 3→300 mA / 300 ns | −60 dB @1 kHz | — | **S** | 僅摘要 |
| D02 Hazucha 2005 | A2-like | 90 nm | 1.2/0.9 | 100 | — | 0.6 nF 片上 | 200（@100 mA 最小 dropout）| 90 mV(p-p) / 100 mA / — | — | 0.008 | M | 僅摘要（背景） |
| D12 Lu 2015 | A | — | 1.2/1.0 | 10 | — | 140 pF | (200，Vin−Vout 推)[D] | 43 mV(−) / 0→10 mA / 200 ps | 優於 −12 dB DC–20 GHz | (0.0234，260×90 µm² 推)[D] | M | 僅摘要 |
| X01-r22 Tang ESSCIRC 2018（資料集第 22 列；論文本身未收進 literature.csv）| 未確認（資料集分類 nested）| 180 nm | 0.7/0.6 | 100 | 6.3 | 20 pF（摘要）；資料集算 FoM 用 30 pF（含探棒 10 pF）| 100 | 106 mV / 90 mA / 150 ns | — | — | M | **資料集（實際開啟）** |
| **REF-A（本次）** | A1 | PTM 180nm | 1.8/1.6 | 100 | 287（含 200 µA 洩放） | 100 pF | 94 @100 mA | 236 mV / 0→100 mA / 100 ns；742 mV / 1 ns | −55 dB @1 kHz(0 mA)；−33 dB @1 kHz(100 mA)；−5 dB @1 MHz | 未佈局 | [X] | 本次模擬 |
| **REF-A（本次）** | A1 | PTM 180nm | 1.8/1.6 | 100 | 287 | 1 nF | 94 | 345 mV / 0→100 mA / 100 ns；497 mV / 1 ns | −16 dB @100 kHz | 未佈局 | [X] | 本次模擬 |
| **REF-B（本次）** | B1 | PTM 180nm | 1.8/1.6 | ≈131（類比 33＋8×12.2）| 289（碼 0，未含數位功耗）| 100 pF | — | 313 mV(10 MHz) / 5→95 mA / 100 ns | −18.8 dB @1 kHz（70 mA，碼凍結） | 未佈局 | [X] | 本次模擬 |

**為什麼不能直接比較**（具體例子，詳見 lit_raw/agent3_notes.md §3）：
1. 邊沿時間：Seok 資料集 46/58 列有 t_edge，範圍 **0.015–4000 ns**、中位數 2 ns（本次以 pandas 重算，與 agent3 一致）[資料集]。同一顆 X. Wang CICC 2019：1 ns 邊沿 185 mV、10 ns 邊沿 88 mV [資料集]。本次 REF-A 同一電路：0→100 mA 在 0.1 ns / 1 µs 邊沿分別 748 / 111 mV；起點改 10 mA、1 µs 邊沿只剩 21 mV [X]。
2. 起始電流：同一電路 1 ns 邊沿，起點 0 / 1 / 10 mA → 742 / 627 / 452 mV [X]。文獻常不寫起點（H01 即是）。
3. CL 定義：資料集有 11 列用總電容或耦合電容當 Cout；Tang ESSCIRC 2018 的總電容含探棒 10 pF [資料集註記]。
4. 製程與電壓：上表 0.18 µm 文獻的 Vin 從 0.7 V（Tang 2018，pseudo-digital）到 5 V。Vin ≥ 2.5 V 的設計**很可能**用了厚氧元件（摘要沒寫元件類型）[H]；若是，pass device 的 Vsg 可遠大於本專題的 1.8 V，結果不能直接套用 [D]。

## 3. 架構層級比較（本專題條件：0.18 µm、1.8→1.6 V、10–100 mA、CL 100 pF–1 nF、無 Verilog）

| 準則 | A（純類比，REF-A 類） | B（類比主導 hybrid，REF-B 類） | C（數位主導） |
|---|---|---|---|
| 穩態精度 | 由 EA 增益決定；滿載時 pass 在 triode，DC 迴路增益從 53 dB 掉到 34 dB [X] | 數位迴路有積分作用，類比 pass 每個負載都被拉回同一工作點 → DC load regulation 較好（95 mA 時 Vout 1.5975 vs REF-A 1.5936）[X] | comparator dead zone 會降低輸出精度 [文獻摘要 H08]；要 mV 級精度需類比細調 [D] |
| 穩定度 | 最差在最輕載（p2≈G2/CL）。CL 越大越難：1 nF 需 Cc=20 pF＋200 µA 洩放才有 PM 55° [X] | 類比部分同 A；另加數位迴路的 limit cycle 條件（dead band 要大於一片電流）[X] | limit cycle 是本質問題 [H08/D04 摘要] |
| 大步階暫態 | 受 pass gate slew 限制：t_r ≈ C_pg·ΔV_g/I_drive；1 ns 邊沿 742 mV(100 pF) [X] | 只靠 gate-sensing 的 B 比 A 更差（5→95 mA, 100 ns：313 vs 127 mV）[X]；要加 droop detector 或多片同時開 | 依時脈與演算法；需快時脈或非同步觸發 |
| PSRR | 低頻受 EA 增益限制，中頻 ~0 dB 附近 [X] | slice 導通時 Vin→Vout 是低阻抗路徑：70 mA 時 1 kHz PSRR −18.8 dB vs A 的 −38 dB [X] | 資料集 8/58 列有 PSRR（皆 @1 MHz）：−5～−46 dB、中位 −27 dB，多為 PSR 增強的 hybrid；不能據此說 B/C 本質較差 [資料集] |
| 漣波/EMI | 無時脈 | 切換瞬間每片 12 mA 步階造成 34–83 mV 尖峰 [X]；時脈饋通 [H]（未模擬，數位為理想） | 時脈相關漣波 |
| 數位實作（無 Verilog） | 不需要 | 8-bit 雙向 thermometer shift register＋2 個時脈比較器，可閘級手畫（8 個 DFF＋每位元 3 個 AND2 與 1 個 OR3，共 32 個閘＋1 個 NOR2；本次 XSPICE 即用此閘級結構）[D] | 演算法式控制（SAR、charge distribution）通常需要合成，閘級手畫風險高 [H] |
| 量測難度 | 標準 LDO 量測＋片上負載 | 加上時脈、碼的觀測、limit cycle 判讀 | 同 B，且量化行為更複雜 |
| 符合教授「偏類比」 | 完全符合 | 符合（類比主導） | 不符（預設排除） |
