# 結論草稿（供 Stage 6 對抗審查攻擊用；最終版在 REPORT.md）

**首選：A 純類比 capless LDO**
- 具體：NMOS 輸入 EA → PMOS source follower buffer → PMOS pass（L=0.18 µm），Miller 補償；加一條電容耦合式 slew-rate enhancement（只在大擾動導通）；明確的最小負載洩放（或 adaptive bias）。
- 量測：片上可程式負載（大 NMOS 開關陣列＋inverter 驅動，可選邊沿 ~1 ns / 100 ns / 1 µs）＋片上 Vout 監測 buffer。
- 理由（摘要）：
  1. 教授要求偏類比；學生無 Verilog。
  2. 本次模擬（ARCH_MATRIX.md、ANALYSIS.md）：最基本的 B（gate-sensing 數位粗調）在 5→95 mA、100 ns 邊沿 undershoot 313 mV（10 MHz）vs 純類比 127 mV；slice 導通時 PSRR@1 kHz 差 19 dB；窗口小於一片電流時 ~200 mV p-p limit cycle。B 的好處（DC load regulation、較小類比 pass）在 100 mA 規格下不大。
  3. A 的主要風險（輕載穩定、快邊沿 undershoot、高溫輕載漏電）都可以用類比手段處理，且可以在 LTspice 完整模擬。

**備案：B 類比主導 hybrid（gate-sensing thermometer 粗調）**
- 條件：教授要 hybrid 題目、或 Imax 提到 ≥200–300 mA、或 Leduc 2025 全文證實為簡單 B 型。
- 設計規則：窗口 ≥ 1.5× 一片電流（含 offset）、slice 邊沿放慢到 ~100 ns 級、加非同步 droop detector、數位與類比分開供電。

**排除：C 數位主導**：無強力理由（Vin 1.8 V 不缺 headroom、Imax 100 mA、無 Verilog、量化漣波 ∝ I_u/(CL·f_clk) 在 capless 下極大）。

**Leduc 2025**：未確認（僅摘要），摘要線索偏 C。

**會改變建議的新資訊**：Leduc 全文顯示為 B 且數位極簡；Imax 需求 ≥ 300 mA；Vin 可用 3.3 V 厚氧；平台有標準元件庫＋教授允許合成；教授以 PSR 為主要指標（→ A＋feedforward）。

**最大風險**：1 ns 級快邊沿的 undershoot（REF-A 742 mV @100 pF）——A 與 B 都必須靠額外暫態增強；以及 PTM 模型不是真實製程。
