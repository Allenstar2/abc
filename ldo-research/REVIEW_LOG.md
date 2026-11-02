# REVIEW_LOG（對抗審查紀錄）

每輪開全新 subagent，不給作者推理過程，只給 repo 內容。原始審查報告在 `review/`。

## 第 1 輪（2026-11-02）

### (b) 引用與數字抽查 — `review/round1_b_citation_check.md`
- 共查 128 項（文獻 60、模擬 68）：一致 97、不一致 11、標記錯誤 12、無法查證 8。
- **已修正**（同日）：
  - 不一致：D02 dropout 300→200 mV；Tang 2018 CL 改為摘要 20 pF（資料集算 FoM 用 30 pF）、補 ΔI 90 mA、id 改 X01-r22；0.18 µm Vin 範圍改 0.7–5 V；dead-zone 引用改 H08；排除筆數 44→43；C_gg 5.3→5.5 pF（原值屬舊設計）；ΔV_g 0.52→0.47 V、I_drive 0.8→0.75 mA；REF-A 95 mA Vout 1.5932→1.5936 V；PSRR@1 MHz 範圍改 −5.3～−8.7 dB；REF-B Imax 改 ≈131 mA（類比部分實測 33 mA，`s11_misc_checks.py`）。
  - 標記錯誤：推得的 dropout/面積加 [D]；H11 Imax 改「—（ΔI=200 mA）」；厚氧改 [H]；A06「只多幾顆電晶體」改 [H，待全文]；A12 DOI 加「未驗證」；DEVICE_CHAR 標題「實測」→「模擬」、漏電對 Vin 敏感改 [D/H]；時脈饋通改 [H]（未模擬）；B 的設計規則改標 [D]/[H] 並寫明模擬只驗過 1.23× 與 0.49×。
  - 無法查證：補 `s11_misc_checks.py` 存檔 BSIM v3.1/v3.3.0 比較、1 nF overshoot 回復 2.2 µs（原寫「約 1.5–2 µs」，已更正）、REF-B 類比最大 33 mA 與 Iq 289 µA、500 µA 洩放公平性表。
- **對結論的影響**：數字修正不改變方向；但審查者指出 `x4_sre.json` 顯示 SRE 讓 100 ns undershoot 從 235.5 惡化到 283.8 mV，與結論草稿「首選＝A＋SRE」相衝 → 列入結論修訂（見本輪結論變動）。

### (a) 找反例推翻首選 — `review/round1_a_counterexample.md`（腳本與 json：`review/round1_a_files/`）
審查者結論：**首選 A 不必改，但支持 A 的三條理由有兩條站不住、一條沒驗證**。

| 審查論點 | 嚴重度 | 作者處理 |
|---|---|---|
| REF-B 是稻草人（Wa=800 µm）；Wa=2.4 mm 時 undershoot 只差 11–21%、PSRR 差 8 dB | 推翻（理由 2） | **接受**。作者以 `s12_fairB.py` 獨立重現：553/154/33 vs 499/127/27 mV（完全一致）；PSRR 差 14 dB（碼 5），審查者 8 dB（碼 3）→ 改寫為 8–14 dB |
| B 加非同步 droop 路徑後 8/8 組設定出現 limit cycle 或卡死 → 這才是 A 最有力的理由 | 需修正 | **接受為主要理由之一**，但標明「審查者 [X]、作者未獨立重現、可能含 XSPICE 假象」 |
| 理由 1（教授偏類比）分不出 A 與 B；教授推薦 hybrid 論文反而支持 B | 需修正 | **接受**。首選/備案順序改為「取決於教授是否要求 hybrid」，列為第一個要問的問題 |
| A 靠未驗證的 SRE 抵帳 | 需修正 | **接受**。SRE 已在 X4 模擬：最佳只改善 8–15%、參數掃描最差惡化 48%（236→348 mV，100 ns 邊沿） → 從首選規格移除，改列選做 |
| 「1 nF 慢邊沿較差」只在無 Rz 時成立 | 推翻 | **接受**。作者重現：1 nF＋Cc=8 pF＋Rz=10 kΩ → 431/185/80 mV，優於 REF-A 742/236/111 mV；ANALYSIS、LEARNING_ANSWERS 已更正 |
| 高溫輕載：A 需洩放 ~800 µA 才達到 B（200 µA）的漏電水準 | 需修正 | 接受，列為 B 的真實優點 |
| 理想偏壓、bond wire 對 A、B 大致對稱；理想比較器/Vref 對 B 有利 | 小問題 | 記錄於報告限制節 |
| C 的「量化漣波極大」只對粗 slice 成立 | 小問題 | 接受，C 的排除理由改寫 |

**本輪結論變動**：首選仍為 A，但（1）理由從「B 性能差很多」改為「性能接近，A 的整合/驗證風險低，且 B 要贏暫態所需的非同步路徑很脆弱」；（2）SRE 移出首選規格；（3）首選/備案順序明確依賴教授是否要求 hybrid；（4）1 nF 結論反轉。→ `CONCLUSION_DRAFT.md` v2。**首選架構未改變，但理由有重大變動**，依規則需繼續第 2 輪。

### (c) 獨立重做推導與模擬 — `review/round1_c_independent.md`（`review/round1_c_files/`）
| 主張 | 審查者結果 | 作者處理 |
|---|---|---|
| 1. REF-A 迴路增益（DC/UGF/PM） | **成立**：Middlebrook 雙注入法零載 52.99 dB、2.448 MHz、66.2°；滿載 33.74 dB、1.598 MHz，差 <0.3%。p2 公式 7.81 MHz vs `.pz` 8.89 MHz（低 12%，p2 與 buffer 極點靠近；CL ≤ 50 pF 時合併成複數極點，公式失效） | 接受；ANALYSIS 的手算表維持（誤差 <30%） |
| 2. 低頻 PSRR ≈ gds_p·R_o/(1+T0) | **大致成立**（差 <0.5 dB），但 pg 只跟到 Vin 的 0.948–0.994，近似偏樂觀 0.6–2.2 dB；給出精確式 | 接受，ANALYSIS 與 LEARNING_ANSWERS H2 加入精確式 |
| 3. 窗口 > 一片電流就不 limit cycle | **部分成立**：只在「類比一個時脈內 settle、無 offset、無決策延遲」時分界點=1；offset → 1+offset 和；d 個時脈延遲 → d+1；欠阻尼類比響應 → 1.05 到 >3.6。窄窗約 44% 負載會 LC。50 MHz 寬窗無法確認 | **接受並以電路級驗證**（`s13_hybrid_sync.py`）：無同步器 10/50 MHz 皆 0/31；2 級同步器 11/31；2 級同步器＋shift register ÷3 時脈 0/31。ANALYSIS「實作時要 2 級 DFF 同步器」的建議**本身會製造 limit cycle**，已改為「同步器＋每 d+1 個時脈更新」 |

**第 1 輪總結**：首選 A 不變；理由、1 nF 結論、SRE 地位、B 的設計規則（同步器/blanking）都有重大修正 → 需第 2 輪。

## 第 2 輪

### (b) 新增內容的引用與數字抽查 — `review/round2_b_citation_check.md`
- 105 項：一致 60、不一致 32、標記錯誤 7、誇大 4、無法查證 2。審查者同時指出 REVIEW_LOG 第 1 輪 (a) 段落**淡化**了審查者論點。
- **已修正**：
  - 公平 B 引錯設計點：高溫輕載「B +9 mV」其實是 Wa=800 µm；公平 B 是 +28 mV、A 加洩放到 300 µA 約 +26 mV → 「B 漏電優勢」大幅縮小。
  - load reg 比較條件不同 → 改為同條件 20→95 mA：B 0.5 mV vs A 6.1 mV（`s15_rz_loadreg.py` 存檔）。
  - SRE 惡化「20%」→ 掃描最差 +48%（236→348 mV）。
  - **「B/C 的 MHz PSRR 結構性吃虧」撤回**：X3c 只到 100 kHz、X5 只模擬 REF-A；審查者量到 1 MHz 時 A −6.7、B −4.1 dB。改寫為「B 的 PSRR 劣勢在 100 kHz 以下」。
  - Rz 的 PM 崩潰負載點 50 mA → 10 mA；Rz 結果改由 `s15_rz_loadreg.py` 存檔重現（原本是未存檔的內嵌指令）；補記 Rz 讓 100 pF 的 1 ns undershoot 742→822 mV。
  - LEARNING：H1 差 3%→約 4%；H2「30 倍/30 dB」→ 21 倍/26 dB；開頭「全部 [X]」改為分段標註；σ=5 mV 標 [H]；SRE 數字更新；同步器規則（每 d+1 個時脈更新）傳到 Q&A 13、15 與結論。
  - APPLICATIONS 誇大：第 8 行改為「droop/settling 與 jitter 都重要」；「spur 差＝PSRR」加上 β≪1 條件（X5 在 1 MHz β=4.4，不適用，改用 TIE 比）；「PLL 頻寬以上」加條件（SD03 類 PLL 頻寬 >100 MHz）；「Imax 降低換高 PSRR」改正（W 等比縮小時 PSRR 不變）。
- **補記第 1 輪 (a) 被淡化的論點**（審查者原文）：
  1. B 數位 reset 後降級成 88.5 mA、PM 68° 的類比 LDO——審查者稱為最強的反方論證之一；已寫入 ANALYSIS 與 CONCLUSION v3。
  2. 審查者要求寫明 A 的代價（為達到 B 的高溫漏電水準需加洩放）；更正後的數字是 300 µA（對公平 B），600–800 µA 是對 Wa=800 µm 的 B。
  3. Rz 對 100 pF 1 ns undershoot 的惡化（742→792–872 mV）。
  4. 原寫「記錄於報告限制節」時 REPORT.md 尚未存在——REPORT.md 將在第 3 輪後撰寫，限制節會包含這些項目。
- **本輪結論變動**：首選 A 不變；但支持 A 的理由再縮小——**PSRR 不再是排除 B 的理由**（只在 100 kHz 以下有差），A 的主要優勢歸結為「離散狀態（limit cycle、同步器、非同步路徑）的驗證風險」與「無時脈雜訊」。→ CONCLUSION_DRAFT v3。
