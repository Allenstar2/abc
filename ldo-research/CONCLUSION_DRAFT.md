# 結論草稿 v3（第 2 輪 (b) 查核後；第 2 輪 (a)(c) 待回報；最終版在 REPORT.md）

**首選：A 純類比 capless LDO（不變）。**
- 具體：NMOS 輸入 EA → PMOS source follower buffer → PMOS pass（L=0.18 µm），Miller 補償（必要時加 nulling resistor，需跨負載/corner 驗證）；明確的最小負載洩放（或 adaptive bias）；片上可程式負載＋片上 Vout 監測 buffer。
- **SRE 不在首選規格內**：class-B 電容耦合 SRE 最好只改善 8–15%，參數掃描最差讓 100 ns 邊沿 undershoot 從 236 惡化到 348 mV（+48%）（X4、X4b）。列為選做，必須 corner 驗證才保留。
- 理由：
  1. **性能上 A 與合理設計的 B 接近**：公平 B（類比 pass 2.4 mm、總寬 3.44 mm）5→95 mA undershoot 553/154/33 mV vs A 499/127/27 mV（1 ns/100 ns/1 µs）；PSRR@1 kHz（70 mA）B 差 8–14 dB（依窗口位置），**但到 1 MHz 兩者都接近 0 dB（A −6.7、B −4.1 dB，審查者 [X]）**——B 的 PSRR 劣勢主要在 100 kHz 以下。
  2. **B 的真實優點**：同條件（20→95 mA）DC load regulation 0.5 mV vs A 6.1 mV；高溫輕載漏電：SF-like 125 °C 零載公平 B +28 mV vs A +46 mV（A 洩放加到 300 µA 約 +26 mV）；數位 reset 後可降級成 88.5 mA 的類比 LDO（審查者 [X]）。
  3. **A 勝在整合與驗證風險低**：B 要在暫態上贏 A 需要非同步 droop 路徑，審查者試的 8 組設定全部在某個負載平台出現 limit cycle 或卡住（審查者 [X]、作者未重現、可能含 XSPICE 假象）；B 的同步器若不配合 blanking 會在 11/31 負載點 limit cycle（`s13` [X]）。A 沒有這類離散狀態問題。
  4. **應用面（HBM/SerDes）**：這兩個領域都要求低 jitter；B/C 的時脈與碼切換會在 Vout 上產生週期性擾動（slice 切換尖峰 34–83 mV [X]），打到 VCO 會變成 spur [H，agent6]。但「B 的 MHz PSRR 較差」**不成立**（見理由 1），不能當作排除 B 的理由。
- **教授推薦 hybrid 論文本身是選 B 的理由**：首選/備案順序**取決於教授是否要求 hybrid**（第一個要問的問題）。

**備案：B 類比主導 hybrid（gate-sensing thermometer 粗調）**
- 若做：類比 pass 不要縮太小（Wa 是主要取捨旋鈕）；窗口 > 一片電流＋比較器 offset 餘裕；若加 d 級同步器，shift register **每 d+1 個時脈才更新**（÷(d+1)，s13 驗證）；保留「數位 reset → 純類比」的降級模式；**先不加非同步 droop 路徑**。

**排除：C 數位主導**：Vin 1.8 V 不缺 headroom；快速暫態需非同步路徑（在 B 已顯示脆弱）；教授偏類比；無 Verilog；細解析度需要大量 slice 或高時脈（「量化漣波極大」只適用於粗 slice）。

**Leduc 2025**：未確認（僅摘要），摘要線索偏 C。

**會改變建議的新資訊**：教授明確要 hybrid；Leduc 全文顯示為簡單 B；Imax ≥ 300 mA；Vin 可用 3.3 V；平台有標準元件庫且允許合成；PSRR 為主要指標（→ A＋feedforward，但滿載受 triode 限制，X6）。

**最大風險**：1 ns 級快邊沿的 undershoot（100 pF 下任何架構 >400 mV）；模型不是真實製程；Rz/補償的跨 corner 穩健性。
