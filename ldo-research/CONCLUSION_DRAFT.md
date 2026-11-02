# 結論草稿 v4（第 2 輪 (a)(b) 後；第 2 輪 (c) 待回報；最終版在 REPORT.md）

**先決條件：規格要先和教授確認。** 1.8 V→1.6 V、100 mA 是整個題目最脆弱的一環：SS-like 125 °C 時 Vin 只容許 −4.7%（最低 1.716 V）；改 Vout=1.4 V 則容許 −13%，滿載迴路增益 +15 dB、PSRR@1 kHz +13 dB（`s17` [X]）。

**首選：A 純類比 capless LDO（類別不變；配置更新）。**
- 基準配置：NMOS 輸入 EA → PMOS source follower buffer → PMOS pass，**純 Miller 補償（Rz=0）**——所有測過的角落＋寄生下 PM ≥ 52.8°（作者）／59°（審查者）。Rz 只用小值（3–5 kΩ）且必須跑角落；Rz=10 kΩ 在 FF −40 °C＋Ibias+30%＋Cc 底板寄生下會振盪（PM −5°，`s16` [X]）。
- 最小負載洩放（或 adaptive bias）；片上可程式負載；片上 Vout 監測 buffer；**量測板 Vout 腳不放去耦電容**（1–10 nF 會讓 PM 掉到 18–29°，`s18` [X]）。
- SRE 不在基準內（最好 −8～15%、最差 +48%）。
- 理由：
  1. **性能上 A 與合理設計的 B 接近**：公平 B 5→95 mA undershoot 553/154/33 vs A 499/127/27 mV；PSRR 差距只在 ≤100 kHz（8–14 dB），1–100 MHz 兩者差 ≤0.6 dB（審查者 [X]）。
  2. **B 的優點比原先估計小**：同條件 load regulation 0.5 vs 6.1 mV 會被片上 IR 與熱蓋掉 [H]；高溫輕載漏電優勢可能是 PTM 假象（|Vthp|+50 mV 時 A 的失效即消失，審查者 [X]）；數位 reset 可降級成 88.5 mA 類比 LDO 是真實的降低風險手段。
  3. **A 勝在離散狀態的驗證風險低**：B 的同步器需 blanking（否則 2 級同步器時 26/31 負載點 limit cycle，`s13`）；要贏暫態所需的非同步 droop 路徑在審查者 8 組設定全部失效；學生無 Verilog、無功能模擬流程。
  4. **時脈雜訊**：B/C 的碼切換在 Vout 造成 34–83 mV 尖峰（`x3e`），若應用是時脈供電會變成 spur [H]。
- **教授推薦 hybrid 論文本身是選 B 的理由**：首選/備案順序也取決於教授是否要求 hybrid（第二個要問的問題）。

**HBM/SerDes 應用動機時**：A 的子類應換成 **NMOS-pass**（審查者：1–10 MHz PSRR 好 14–18 dB（審查者 json，只測 0–10 mA、Vout 1.0 V），作者未重現），代價是 Vout ≤ ~1.2 V 或需 charge pump；或維持 PMOS pass＋feedforward（X6 顯示需 adaptive，滿載受 triode 限制）。

**備案：B 類比主導 hybrid**：類比 pass 不要縮太小；窗口 > 一片電流＋offset；同步器配 ÷(d+1) 更新；保留數位 reset→純類比降級模式；先不加非同步 droop 路徑。

**排除：C 數位主導**：Vin 1.8 V 不缺 headroom；快速暫態需非同步路徑（在 B 已顯示脆弱）；教授偏類比；無 Verilog。

**Leduc 2025**：未確認（僅摘要），摘要線索偏 C。

**會改變建議的新資訊**：教授明確要 hybrid；Leduc 全文顯示為簡單 B；Imax ≥ 300 mA；Vin 可用 3.3 V；平台有標準元件庫且允許合成；PSRR/jitter 為主要指標（→ A 的 NMOS-pass 或 feedforward 子類）。

**最大風險**：規格（1.8→1.6 V 在角落下失去調節）；1 ns 級快邊沿 undershoot（100 pF 下 >400 mV，任何架構）；模型不是真實製程（PTM 的 PMOS Vth/DIBL 可能造成假失效）。
