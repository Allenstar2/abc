# Stage 7：研究缺口

> **查證限制**：WebSearch 額度在本次 session 已用完、學術網站被擋（D-009、D-011）。
> 「是否已有人做過」只能用已收集的 54 筆記錄（literature.csv、lit_raw/*notes.md、DLDO 資料集）判斷，**全部標為「未完整查證」**。
> 早上若能搜尋，請優先用下表「建議的搜尋關鍵字」補查。

## 判定規則
已有人做過 → 刪除；大學部在 0.18 µm＋LTspice＋無 Verilog 做不到 → 刪除。

| # | 缺口候選 | 已收集記錄中是否有人做過 | 大學部可行性 | 判定 |
|---|---|---|---|---|
| G1 | **同一顆 capless LDO，在片上可程式負載下系統化量測 ΔV 對（邊沿時間 × 起點電流 × Vout 取出方式）的依賴**，並據此示範 FoM 排名如何被量測條件改變 | 部分有：X. Wang CICC 2019 同晶片量了 1 ns 與 10 ns 兩種邊沿（185 vs 88 mV）[資料集]；PMC10222239 有 1 ns vs 1 µs 的**模擬**比較（agent3 notes，未讀全文）；Seok 資料集註記指出探棒 10 pF 被算進 CL [資料集]。**未找到**同時掃三個條件、且用片上 buffer 與直接 pad 對照的量測 | 高：片上 NMOS 負載陣列＋inverter 驅動（邊沿用可選 RC 或 starved inverter 調）＋source follower 監測 buffer，全是類比/閘級電路；本次模擬已示範同電路 0→100 mA undershoot 可從 21 mV 到 748 mV [X] | **保留（主推）**，但定位是「量測方法學的小貢獻」，不是新架構。未完整查證 |
| G2 | **類比主導 hybrid 的 dead band「洞」**：窗口電流 < 一片電流時只在特定負載出現 limit cycle；加入比較器 offset 與溫漂後，求最小窗口設計規則，並在晶片上用可調 VL/VH 量測 | 很可能已有：H07（Lu 2019, PID control considerations for hybrid LDO）、H08/D04（Huang 2016 limit cycle reduction）、資料集有 Vdz（dead zone）欄位。是否有人以「gate-sensing B 型」量測「洞」的分佈，未找到 | 中：數位部分可閘級手畫（本次 XSPICE 即閘級結構）；但要做 B 架構，晶片複雜度與量測量都加倍 | **保留（弱）**：只有在選備案 B 時才有意義；新穎性很可能不足。未完整查證 |
| G3 | 0.18 µm、1.8 V 下的 capless LDO PSR feedforward 抵消 | **已有**：A01 Park 2014 JSSC（0.18 µm、1.8 V，PSR 優於 −56 dB 至 4 MHz [摘要]）；A13 Joo 2017（0.18 µm PSR 模型）；A03 Lim 2018 | — | **刪除**（已有人做過） |
| G4 | 電容耦合 SRE / FVF / SSF 的快速暫態 capless LDO | **已有**大量：A06、A07、A08、A09、F03、F04、D13 | — | **刪除**（已有人做過；本次模擬也顯示簡單 SRE 改善僅 8–15% [X]，不是容易的新貢獻） |
| G5 | 大 PMOS pass 在高溫輕載的漏電使調節失效（本次 SF-like 125 °C 輕載 Vout +46 mV [X]）的系統研究 | 屬於教科書級的「最小負載電流」設計問題；不構成研究缺口 | 高 | **刪除**（不是研究缺口，是設計檢查項目） |

## G1 的具體做法（若教授同意）

1. 晶片上：REF-A 類 LDO（首選）＋片上負載：4–8 段二進位加權 NMOS（總 0–100 mA，或依教授定的 Imax），每段閘極由 inverter 驅動；最後一級 inverter 的 PMOS/NMOS 可切換尺寸（或串電阻）得到 ~1 ns / ~20 ns / ~200 ns 邊沿。
2. Vout 取出兩條：(a) 直接 pad；(b) 片上 PMOS/NMOS source follower 或 unity-gain buffer → pad。
3. 量測矩陣：t_edge ×3、起點電流 ×3（0、1 mA、10 mA）、取出方式 ×2，報告 ΔV、settling、以及用三種 FoM 定義（ps-FoM、edge-adjusted FoM）算出的值。
4. 風險：負載電流走獨立 GND pad；片上負載的 IR drop 與熱；示波器頻寬（1 ns 邊沿需 ≥ 500 MHz 探棒/示波器 [H]）。

## 建議的搜尋關鍵字（早上補查用）
- "load transient" "edge time" capacitor-less LDO measurement on-chip load generator
- "FoM" LDO "edge time" comparison methodology
- hybrid LDO "dead zone" "limit cycle" analog-dominant digitally assisted
- Leduc thesis Lakehead "hybrid" LDO（解決 B/C 判定）
