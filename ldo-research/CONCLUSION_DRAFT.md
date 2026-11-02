# 結論草稿 v2（第 1 輪審查後；最終版在 REPORT.md）

**首選：A 純類比 capless LDO（不變），但理由改寫。**
- 具體：NMOS 輸入 EA → PMOS source follower buffer → PMOS pass（L=0.18 µm），Miller 補償＋nulling resistor（需跨負載/corner 驗證）；明確的最小負載洩放（或 adaptive bias）；片上可程式負載＋片上 Vout 監測 buffer。
- **SRE 從首選規格中移除**：電容耦合 class-B SRE 在本次模擬中最好只改善 8–15%，部分參數讓 100 ns 邊沿 undershoot 惡化 20%（X4）。改列為「選做，必須 corner 驗證才保留」。
- 理由（v2）：
  1. **A 與合理設計的 B 在性能上接近，A 勝在整合與驗證風險低**。公平版 B（類比 pass 2.4 mm、總寬 3.44 mm）5→95 mA undershoot 553/154/33 mV vs A 499/127/27 mV（1 ns/100 ns/1 µs），差 11–21%；PSRR@1 kHz（70 mA）差 8–14 dB（依窗口位置）[X，作者重現審查者]。B 的優點：DC load regulation（0.4–0.5 mV vs A 6–13 mV）、高溫輕載漏電較不敏感（SF-like 125 °C：B +9 mV vs A +46 mV，審查者 [X]）。
  2. **B 要在暫態上贏 A，需要非同步 droop 路徑；審查者試的 8 組設定全部在某個負載平台出現 45–360 mV p-p limit cycle 或卡住**（審查者 [X]，作者未獨立重現；可能部分為 XSPICE 事件排序假象）。不加快速路徑的 B 穩定但暫態與 PSRR 都略遜於 A。
  3. **應用面（HBM/SerDes）在意的是 MHz–百 MHz 的 PSRR**：開著的 slice 是 Vin→Vout 的低阻抗開關，B/C 在這個指標上結構性吃虧（X3c、X5、agent5 文獻摘要）。
  4. 學生無 Verilog：B 的數位部分可手畫（已在 XSPICE 閘級驗證），但 metastability、上電、窗口 offset 等驗證要另外做——是風險，不是不可能。
- **教授推薦 hybrid 論文本身是選 B 的理由**：首選/備案的最終順序**取決於教授是否要求 hybrid**（列為第一個問題）。

**備案：B 類比主導 hybrid（gate-sensing thermometer 粗調）**
- 若做：類比 pass 不要縮太小（Wa 是 B 唯一的主要取捨旋鈕：小則暫態/PSRR 差，大則 B 的面積優勢消失）；窗口 > 一片電流＋比較器 offset 餘裕；**先不加非同步 droop 路徑**，若要加需大量模擬與可關閉的設計。

**排除：C 數位主導**：Vin 1.8 V 不缺 headroom；slice 開關使中高頻 PSRR 天生接近 0 dB；快速暫態需非同步路徑（在 B 已顯示很脆弱）；教授偏類比；無 Verilog。（「量化漣波極大」只適用於粗 slice，不再當主要理由。）

**Leduc 2025**：未確認（僅摘要），摘要線索偏 C。

**會改變建議的新資訊**：教授明確要 hybrid；Leduc 全文顯示為簡單 B；Imax ≥ 300 mA；Vin 可用 3.3 V；平台有標準元件庫且允許合成；PSRR 為主要指標（→ A＋PSR 增強）。

**最大風險**：1 ns 級快邊沿的 undershoot（任何架構在 100 pF 下都 >400 mV）；模型不是真實製程；Rz/補償的跨 corner 穩健性。
